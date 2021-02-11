'''
    This script helps you handle Web Hooks. It relies on web hook APIs and allows you to:
        1. Create New Hook
        2. Update URL for existing hook
        3. List all available hooks for your user token listed in config file.
        4. Get info about specific hook
        5. Delete specific hook

    Every time you press ENTER at the end, the choices will re-apprear.
    To end the script just KILL IT !

    Oh also, note that it will ask you for the config file for your application.
    This would be the .json file you created for your Bot.
    This script is meant to be used used by all Bot applications you design hence it needs to handle different config files.
    PRO TIP: You can always hard code this before you run the script haha.
'''

import requests
import json

from apiHandler import apiCallReturnJSON
from tokenHandler import getBotToken, getWebHookId, getBotEmail, doesFileExist

BASE_URL = "https://webexapis.com/v1/webhooks"

def getHookConfig():
    '''
    Returns config information for generating the webhook.
    If you want to create a new web hook make sure you change webhook_config.json
    '''
    json_file = open('config/webhook_config.json', 'r')
    config = json.load(json_file)
    json_file.close()

    return config


def createWebHook(bot_token):
    '''
    Use information from webhook_config.json to create a new Web Hook.
    Display information about the new Web Hook.
    '''
    payload = json.dumps(getHookConfig())
    response = apiCallReturnJSON("POST", BASE_URL, bot_token, "application/json", payload)
    print(json.dumps(response, indent=4, sort_keys=True))


def getWebHook(webhook_id, bot_token):
    '''
    Get infomration about specifi web hook.
    '''
    url = "{}/{}".format(BASE_URL, webhook_id)
    return apiCallReturnJSON("GET", url, bot_token, "application/json", {})


def updateWebHook(webhook_id, targetUrl, bot_token):
    '''
    Updates only the targetUrl for the specific web hook.
    This is mostly used if you are using free version of ngrok and have different url everytime you run the code.
    The Web Hook will reach out to this targetUrl when triggered.
    '''
    webhook = getWebHook(webhook_id, bot_token)
    # All the changes are specified in the body of the request.
    body = {
        "name": "{}".format(webhook["name"]),
        "targetUrl" : "{}".format(targetUrl)
    }
    
    payload = json.dumps(body)
    url = "{}/{}".format(BASE_URL, webhook_id)

    # Update the Web Hook and display response for user reference.
    response = apiCallReturnJSON("PUT", url, bot_token, "application/json", payload)
    print(json.dumps(response, indent=4, sort_keys=True))


def listWebHooks(bot_token):
    '''
    Simply list all the available Web Hooks
    '''
    response = apiCallReturnJSON("GET", BASE_URL, getBotToken(config_file), "application/json", {})
    print(json.dumps(response, indent=4, sort_keys=True))


def deleteWebHook(webhook_id, config_file):
    '''
    Delete specified web hook
    '''
    url = "{}/{}".format(BASE_URL, webhook_id)
    apiCallReturnJSON("DELETE", url, bot_token, "application/json", {})


if __name__ == "__main__":
    '''
    Keep looping until user kills the code. If you want to end the script just kill it.
    There is no error handling - yes I was lazy. But the script is fairly simple.
    '''
    print("\n Welcome to Web Hook Handler... ")
    # Note that config file must be json type !
    # config_file = input("Enter the name of the json config file for the application: ")

    # If you need something quick but less generic you can just hard code this.
    # *************************
    config_file = 'bot_config.json'
    # *************************

    # If the file does not even exist just exit
    if not doesFileExist(config_file):
        exit()

    # Get all relevant information from config
    webhook_id = getWebHookId(config_file)
    bot_token = getBotToken(config_file)
    bot_email = getBotEmail(config_file)

    # This one is a bit weird, but if at the end user just press ENTER (i.e. no input) then they will get choices displayed again.
    # Reger to the end of the script where user is asked for the input.
    continue_program = ''

    # To kill the scipt just use ctrl+c (windows) or control+c (mac)
    while(not continue_program):

        print("What would you like to do?\n")
        print("1 - Create Web Hook\n")
        print("2 - Update Web Hook URL\n")
        print("3 - List all Web Hooks\n")
        print("4 - Get Info about specific Web Hook\n")
        print("5 - Delete a Web Hook\n")
        user_input = input("Enter appropriate number: ")
        choice = int(user_input)

        # For choices that require web hook ID ask user to either enter one or use one form bot_config.json
        if choice == 2 or choice == 4 or choice == 5:
            webhook_id = input("Enter the Web Hook ID : ")

        # You can just hard code webhook id yourself here if want
        # webhook_id = "My Web Hook ID"

        # Based on choise call appropriate function
        # CREATE WEB HOOK
        if choice == 1:
            print("\n Note You are about to create a new Web Hook. config/webhook_config.json will be used to config the web hook. \n")
            user_input = input("Continue (Y/n): ")

            if user_input in "Y" or user_input in "y":
                print("\n")
                createWebHook(bot_token)

            else:
                print("Bye Bye then")
        # ----------------- UPDATE URL for WEB HOOK
        elif choice == 2:
            # You can also hard code this if easier or often used
            # target_url = "...."
            target_url = input("Enter New TargetUrl: ")

            updateWebHook(webhook_id, target_url, bot_token)
        # ----------------- LIST ALL WEB HOOKS
        elif choice == 3:
            listWebHooks(bot_token)
        # ----------------- UPDATE WEB HOOK
        elif choice == 4:
            response = getWebHook(webhook_id, bot_token)
            print(json.dumps(response, indent=4, sort_keys=True))
        # -----------------  DELETE WEB HOOK
        elif choice == 5:
            print("\n Note You are about to DELETE {} \n".format(webhook_id))
            confirm = input("You sure? (Y/n): ")

            if confirm in "Y" or confirm in "y":
                deleteWebHook(webhook_id, bot_token)
                print("Deleting...")
            else:
                print("hmmm don't think so. Bye Bye then.")
                pass
        else:
            print("Sorry but that ain't one of the options.")

        continue_program = input("\nPress Enter Key to go again or just kill the script: ")