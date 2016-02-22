#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import base64
import hashlib
import random
import socket
import string
import struct
import time
import xml.etree.cElementTree as ET

from Crypto.Cipher import AES

from flask import Flask, make_response, render_template, request

from pkcs7 import PKCS7Encoder


app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')


@app.route('/', methods=['GET', 'POST'])
def index():
    if not request.args:
        return 'Hello WeChat'
    else:
        msg_signature = request.args.get('msg_signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')

    # validate the server
    if request.method == 'GET':
        echostr = request.args.get('echostr')
        decrypted_echostr = decrypt_message(msg_signature=msg_signature,
                                            timestamp=timestamp, nonce=nonce,
                                            echostr=echostr)
        if decrypted_echostr:
            return decrypted_echostr

    # handle coming messages
    elif request.method == 'POST':
        data = request.data
        xmlstr_received = ET.fromstring(data)
        message_received = parse_message(xmlstr=xmlstr_received)
        encrypted_message = message_received['Encrypt']
        decrypted_message = decrypt_message(msg_signature=msg_signature,
                                            timestamp=timestamp, nonce=nonce,
                                            msg_encrypt=encrypted_message)
        try:
            decrypted_xml = ET.fromstring(decrypted_message)
            message_dict = parse_message(xmlstr=decrypted_xml)
            user_input = get_user_input(message_dict)
        except Exception as e:
            app.logger.error('parse decrypted message error: ' + str(e))

        message_dict['Time'] = str(int(time.time()))
        message_dict['Content'] = generate_reply(user_input)
        message_body = render_template('message.xml', message=message_dict)

        encrypted_message = encrypt_message(message_body)
        signature_list = [app.config['WECHAT_TOKEN'], timestamp,
                          nonce, encrypted_message]
        message_signature = generate_signature(signature_list)

        template = render_template('response.xml', message=encrypted_message,
                                   signature=message_signature,
                                   timestamp=timestamp, nonce=nonce)
        response = make_response(template)
        response.headers['Content-Type'] = 'application/xml'
        return response


def get_user_input(message):
    return message['Content']


def generate_reply(user_input):
    return user_input


def parse_message(xmlstr):
    message = {}
    if xmlstr.tag == 'xml':
        for child in xmlstr:
            message[child.tag] = child.text
    return message


def decrypt_message(**kwargs):
    msg_signature = kwargs.get('msg_signature')
    timestamp = kwargs.get('timestamp')
    nonce = kwargs.get('nonce')

    echostr = kwargs.get('echostr')
    msg_encrypt = kwargs.get('msg_encrypt')
    msg_content = echostr or msg_encrypt
    token = app.config['WECHAT_TOKEN']

    signature_list = [token, timestamp, nonce, msg_content]
    raw_signature = generate_signature(signature_list)
    if raw_signature != msg_signature:
        app.logger.error('error: signatures do not match')
        return None
    else:
        try:
            plain_text = decrypt_plain_text(msg_content)
        except Exception as e:
            app.logger.error('decrypt plaint text error: ' + str(e))
            return None
        try:
            xml_content = decrypt_xml_content(plain_text)
            return xml_content
        except Exception as e:
            app.logger.error('decrypt xml content error: ' + str(e))
            return None


def decrypt_plain_text(msg_content):
    key = base64.b64decode(app.config['WECHAT_ENCODINGAESKEY'] + '=')
    cryptor = AES.new(key, AES.MODE_CBC, key[:16])
    plain_text = cryptor.decrypt(base64.b64decode(msg_content))
    return plain_text


def decrypt_xml_content(plain_text):
    pad = ord(plain_text[-1])
    content = plain_text[16:-pad]
    xml_len = socket.ntohl(struct.unpack('I', content[:4])[0])
    xml_content = content[4: xml_len + 4]
    server_corpid = content[xml_len + 4:]
    local_corpid = app.config['WECHAT_CORPID']
    if server_corpid != local_corpid:
        app.logger.error('error: corporate IDs do not match')
        return None
    return xml_content


def generate_signature(signature_list):
    signature_list.sort()
    sha = hashlib.sha1()
    sha.update(''.join(signature_list))
    signature = sha.hexdigest()
    return signature


def encrypt_message(message):
    key = base64.b64decode(app.config['WECHAT_ENCODINGAESKEY'] + '=')
    random_string = generate_random_string(16)
    local_corpid = app.config['WECHAT_CORPID']
    try:
        packed_binary = struct.pack('I', socket.htonl(len(message)))
        message = random_string + packed_binary + message + local_corpid
    except Exception as e:
        app.logger.error('encrypt message error: ' + str(e))
        return None
    pkcs7 = PKCS7Encoder()
    message = pkcs7.encode(message)
    cryptor = AES.new(key, AES.MODE_CBC, key[:16])
    try:
        ciphertext = cryptor.encrypt(message)
        base64text = base64.b64encode(ciphertext)
        return base64text
    except Exception as e:
        app.logger.error('encrypt message error: ' + str(e))
        return None


def generate_random_string(digits):
    source = string.ascii_uppercase + string.digits
    random_string = ''.join(random.choice(source) for _ in range(digits))
    return random_string


def detect_configuration():
    token = app.config['WECHAT_TOKEN']
    aeskey = app.config['WECHAT_ENCODINGAESKEY']
    corpid = app.config['WECHAT_CORPID']

    if (token and aeskey and corpid) is None:
        raise Exception('missing wechat enterprise app keys!')


if __name__ == '__main__':
    detect_configuration()
    app.run(host='0.0.0.0', port=8080, debug=True)
