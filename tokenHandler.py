import json
import requests


def getParameters():
    json_file = open('config/mmd_config.json', 'r')
    parameters = json.load(json_file)
    json_file.close()

    return parameters


def getBotToken():

    parameters = getParameters()
    return parameters['bot_token']


if __name__ == "__main__":
    print("This just returns BOT token \n")
    print("Bot Token: {}\n".format(getBotToken()))
    print("There you go! Bye...\n")
    pass