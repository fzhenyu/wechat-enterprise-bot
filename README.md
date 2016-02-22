WeChat Enterprise Bot
==============================

> A silly parrot bot that repeats user input for WeChat Enterprise account powered by Python (2.7) Flask


## Get Started

Step 1. Clone this repo
```bash
$ git clone https://github.com/j1wu/wechat-enterprise-bot.git
```
Step 2. Add your wechat enterprise app keys to `instance/config.py` (replace `None`)

Step 3. Install virtualenv
```bash
$ sudo easy_install virtualenv
```
Step 4. Create a new virtual environment
```bash
$ virtualenv venv
```
Step 5. Activate the new virtual environment
```bash
$ source venv/bin/activate
```
Step 6. Install app dependencies within the virtual environment
```bash
(venv) $ cd wechat-enterprise-bot
(venv) $ pip install -r requirements.txt
```
Step 7. Start app
```bash
(venv) $ python app.py
```


## Host The Bot Locally

Step 1. Install [ngrok](https://github.com/inconshreveable/ngrok)

Step 2. Create an account on [ngrok.com](https://ngrok.com/signup)

Step 3. Install ngrok authtoken
```bash
./ngrok authtoken your_authentication_key
```
Step 4. Start Flask app first
```bash
(venv) $ python app.py
```
Step 5. Start ngrok
```bash
$ ./ngrok http 8080
```
Step 6. Configure your wechat app with the ngrok fowarding url

![](https://cloud.githubusercontent.com/assets/5327840/13206716/0e3de920-d93f-11e5-97b8-0773d1656ae9.png)

![](https://cloud.githubusercontent.com/assets/5327840/13206743/7b4ba8f4-d93f-11e5-8d1a-0cf99712b043.png)

Step 7. Verify it

Now you'll be able to see the traffic coming from the wechat server :)

![](https://cloud.githubusercontent.com/assets/5327840/13206782/3b14a60e-d940-11e5-9c8d-0acef9a1646e.png)


## Host The Bot with Heroku

Step 1. Install [heroku toolbelt](https://toolbelt.heroku.com/)

Step 2. Create an account on [heroku](https://signup.heroku.com/)

Step 3. Create a new heroku app
```bash
$ heroku login
$ heroku keys:add
$ heroku apps:create your_app_name
``` 
Step 4. Install [foreman](https://github.com/ddollar/foreman)
```bash
$ gem install foreman
```
Step 5. Local test run with foreman
```bash
# make sure to activate the virtual environment first
(venv) $ foreman start
```
Step 6. Deploy to heroku
```bash
(venv) $ git add .
(venv) $ git commit -m "initial deployment"
(venv) $ git push heroku master
```
Step 7. Update your wechat app configuration with the heroku app url


###Acknowledgments

Thanks to [Bob](https://github.com/iambocai)'s [Python connector weixin qy](https://github.com/iambocai/python-connector-weixin-qy) project to make my bot possible :)