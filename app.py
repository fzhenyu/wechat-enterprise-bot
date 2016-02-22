#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import sys
import time
import xml.etree.cElementTree as ET

from WXBizMsgCrypt import WXBizMsgCrypt

from flask import Flask, Response, render_template, request


app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')


@app.route('/', methods=['GET', 'POST'])
def index():
    if not request.args:
        return 'Hello WeChat'
    else:
        wxcryptor = WXBizMsgCrypt(app.config['WECHAT_TOKEN'],
                                  app.config['WECHAT_ENCODINGAESKEY'],
                                  app.config['WECHAT_CORPID'])

        msg_signature = request.args.get('msg_signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')

    # validate the server
    if request.method == 'GET':
        echostr = request.args.get('echostr')

        ret, echostr = wxcryptor.VerifyURL(msg_signature, timestamp,
                                           nonce, echostr)
        if (ret != 0):
            sys.exit(1)
        else:
            return echostr

    # handle coming messages
    elif request.method == 'POST':
        data = request.data
        ret, decrypted_message = wxcryptor.DecryptMsg(data, msg_signature,
                                                      timestamp, nonce)
        decrypted_xml = ET.fromstring(decrypted_message)
        message = parse_message(xmlstr=decrypted_xml)
        user_input = get_user_input(message)

        reply = generate_reply(user_input)

        response = generate_response(message, reply)
        ret, encrypted_message = wxcryptor.EncryptMsg(response,
                                                      nonce, timestamp)

        return Response(encrypted_message,
                        content_type='text/xml; charset=utf-8')


def get_user_input(message):
    return message['Content']


def generate_reply(user_input):
    return user_input


def generate_response(message, reply):
    message['Time'] = str(int(time.time()))
    message['Content'] = reply
    response = render_template('message.xml', message=message)
    return response


def parse_message(xmlstr):
    message = {}
    if xmlstr.tag == 'xml':
        for child in xmlstr:
            message[child.tag] = child.text
    return message


def detect_configuration():
    token = app.config['WECHAT_TOKEN']
    aeskey = app.config['WECHAT_ENCODINGAESKEY']
    corpid = app.config['WECHAT_CORPID']

    if (token and aeskey and corpid) is None:
        raise Exception('missing wechat enterprise app keys!')


if __name__ == '__main__':
    detect_configuration()
    app.run(host='0.0.0.0', port=8080, debug=True)
