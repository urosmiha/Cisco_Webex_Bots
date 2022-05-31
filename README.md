NOTE: Documentation is still work in progress and not fully finished. I'm a lazy developer. I'm sorry :cry:

# Cisco_Webex_Bots
Collection of random Cisco Webex Bots I play around in my spare time.

Each branch relates to one BoT. At the moment there are two Bots:

1. Make My Day
2. Quizy (work in progress)

Master branch contains main python files for each Bot, so if you clone master you can run each bot. Although, I would recommend to checkout the relevant branch for each Bot.

Note: __config.json__ is used by all Bots and can be configured for one Bot at a time. Hence, one of the reasons to use inidividual branches.
  
Some files are common for all Bots and work regardless of the Bot you are using. These include:

* __apiHandler.py__
* __tokenHandler.py__
* __webHookHandler.py__

* __requirements.txt__ is (as usual) used to install python dependencies. Refer to Getting Starter section for more info on this.

# Getting Started

Here are a few things you would need to get started. Everything is well documented by each provider and fairly straight forward, so I would not be re-itterating, just follow the links.

## Git (duh...)

or maybe not really actually. You can always just download zip file... and have multiple versions 50 differet folders? Please don't do that.

Since you are here I assume you already know about Git and know how to install it. But just in case here is the link: [Download GitHub](https://git-scm.com/downloads)

You can also use GitHub Desktop if you do not like git bash: [GitHub Desktop](https://desktop.github.com/). I won't judge... I promise. Sometimes guilty myself.

## IDE

My choice: VS Code: [Download VS Code](https://code.visualstudio.com/download)

Any IDE works, or even nano or vim (if you are that extreme). Any IDE works, but your choice of IDE would just dictate my respect for you (_looking at you Eclipse users_)

Just kidding of course!

## Python 3

Note: Recommended is to use __Python 3__. Python 2 is depreciated.

Downlaod and install Python: [Download Python](https://www.python.org/downloads/)

## Ngrok

Create account and download it: [How to Set Up Ngrok](https://dashboard.ngrok.com/get-started/setup)

Instructions should be quite clear. You can get your token from here btw: https://dashboard.ngrok.com/auth/your-authtoken

Also, quick tip for Mac users, I would recommend unzipping ngrok in _/usr/local/bin_ directory. Just makes life easier. So assuming you downloaded ngrok zip to _Downloads_ directory. In __Terminal__ run:

``` unzip ~/usr/local/bin ~/Downloads/ngrok-stable-darwin-amd64.zip ```

Or whatver the name of your ngrok zip file is at the time.

## Cisco Webex

### Get your account
If you already do not have one.
Got to https://www.webex.com/ and open account. It's free!

### Cisco Webex Teams

IMPORTANT: This is Cisco messaging and team collaboration platform. You would need it to send messages to and receive messages from your Bot.
You can download desktop app or just use web-based app on https://www.webex.com/. Either works.

Couple of things you need to do once you have your webex account. Head over to https://developer.webex.com

### Lets create a Bot

Go to https://developer.webex.com/ and sign in. When offered choices just use Cisco Webex option, or Cisco SSO if you are Cisco employess.

You can read more about Bots and how they work here: https://developer.webex.com/docs/bots - There is also a button there to go and create a Bot.

You can name your Bot anything you want. It does not need to be the same as mine. But make sure you remember... well it would be kinda hard to remember this... maybe copy it straight away. You need to get Bot ID, and copy it to a __config/config.json__ file, that you previously created.

IMPORTANT: You can only see Bot token here once, after you close this page or you get logged out token will be hidden and you would need to generate a new one.

### Lets set up WebHooks

Once you have a Bot token you can just run __webHookHandler.py__

In your Terminal in your Python environment run: ``` python webHookHandler.py``` you will be greeted with the following options:
```
1. Create Web Hook
2. Udate
3. list
4. delete
```

**** No more for now... sorry... documentation working in progress ...


