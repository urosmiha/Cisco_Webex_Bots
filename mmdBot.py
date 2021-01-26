import json
import requests
import random
from flask import Flask, request
from requests_toolbelt.multipart.encoder import MultipartEncoder

app = Flask(__name__)

from apiHandler import apiCallReturnJSON
from tokenHandler import getBotToken, getBotEmail, doesFileExist

CONFIG_FILE = "mmd_config.json"
BASE_URL = "https://webexapis.com/v1"

VALID_ANIMALS = ['panda', 'koala', 'dog', 'cat']


@app.route("/", methods=["POST"])
def getHook():

    hook_info = request.json
    hook_resource = hook_info["resource"]

    # TODO: proper logging
    # print(json.dumps(hook_info, indent=4, sort_keys=True))

    if hook_resource == "messages":
        message_info = getMsgInfo(hook_info["data"]["id"])

        # Lower_case the text for easier handling - it does not metter if animal is spelled with uppercase or lowercase.
        message_text = message_info["text"].lower()
        room_id = hook_info["data"]["roomId"]
        sender_email = hook_info["data"]["personEmail"]

        # response = getRoomInfo(room_id)
        # For debug purposes - TODO: Replace with proper logging
        # print(json.dumps(response, indent=4, sort_keys=True))

        # Make sure the message did not come from a Bot so it does not enter endless loop.
        # I believe the WebHook filter cannot specify from which user NOT to accept notification.
        if sender_email != BOT_EMAIL:
            
            # If 'help' or 'hello' is received send appropriate respinse and just exit/return so we don't need to look for animals.
            if message_text == "help":
                message = "Detail help is on the way - meaning whenever developer feels like it. Just type hello, panda, cat or dog. It's a simple Bot."
                sendMessage(room_id, message)
                return ""
            # If you receive "hello" then send the Card not just the image - Card provides extra options
            elif message_text == "hello":
                # Just pick a random URL
                img_url = getRandomImgURL(random.choice(VALID_ANIMALS))
                sendCard(room_id, img_url)
                return ""

            # Check which animal did user specify - THE LAZY and not entirely accurate approach
            # Just so we don't check spelling for every animal, simply have a list of valid animals
            # and if user input contains any of these accept it as a valid choise.
            # Also each of the animals in the VALID_ANIMAL list is actually used as the topic value for the random API call
            rndm_api_topic = ""
            for animal in VALID_ANIMALS:
                if animal in message_text:
                    rndm_api_topic = animal         

            # If we can recognise the animal from user input then just send them a picture
            if rndm_api_topic:
                img_url = getRandomImgURL(rndm_api_topic)
                # Send just an image with no text
                sendImgFromURL(room_id, img_url, "")
            else:
                sendMessage(room_id, "Sorry I'm not build for that. Maybe check your spelling or type: help")

    elif hook_resource == "attachmentActions":
        action_info = getActionInfo(hook_info["data"]["id"])

        print(json.dumps(action_info, indent=4, sort_keys=True))
    

    return ""


@app.after_request
def add_header(response):
    response.cache_control.max_age = 300
    return response


def getRandomImgURL(rndm_api_topic):

    rndm_base_url = "https://some-random-api.ml"
    rndm_api_type = "img"

    payload = {}
    headers = {}
    url = "{}/{}/{}".format(rndm_base_url, rndm_api_type, rndm_api_topic)

    response = requests.request("GET", url=url, headers=headers, data=payload)

    response = json.loads(response.text)
    return response["link"]


def getRandomFact(rndm_api_topic):

    rndm_base_url = "https://some-random-api.ml"
    rndm_api_type = "facts"

    payload = {}
    headers = {}
    url = "{}/{}/{}".format(rndm_base_url, rndm_api_type, rndm_api_topic)

    response = requests.request("GET", url=url, headers=headers, data=payload)

    response = json.loads(response.text)
    return response["fact"]


def sendImgFromURL(room_id, img_url, message):

    image_response = requests.get(img_url)

    file = open("tmp.png", "wb")
    file.write(image_response.content)
    file.close()

    url = "{}/messages".format(BASE_URL)

    payload = MultipartEncoder({
        "roomId": room_id,
        "text": message,
        "files": ('tmp.png', open('tmp.png', 'rb'),'image/png')
    })

    content_type = payload.content_type

    apiCallReturnJSON("POST", url, BOT_TOKEN, content_type, payload)


def sendCard(room_id, img_url):

    url = "{}/messages".format(BASE_URL)

    payload = {
        "roomId": room_id,
        "text": " ",
        "attachments": [
        {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "type": "AdaptiveCard",
                "version": "1.0",
                "body": [
                    {
                        "type": "Image",
                        "altText": "",
                        "url": "{}".format(img_url)
                    },
                    {
                        "type": "Input.ChoiceSet",
                        "placeholder": "What would you like to see next?",
                        "choices": [
                            {
                                "title": "Panda",
                                "value": "panda"
                            },
                            {
                                "title": "Dog",
                                "value": "dog"
                            },
                            {
                                "title": "Cat",
                                "value": "cat"
                            },
                            {
                                "title": "I'm Aussie",
                                "value": "koala"
                            }
                        ],
                        "value": "",
                        "id": "nextAnimal" 
                    },
                    {
                        "type": "TextBlock",
                        "text": "Would you like to see something else?"
                    },
                    {
                        "type": "Input.Text",
                        "id": "userWish",
                        "placeholder": "Type what would you like to see..."
                    },
                    {
                        "type": "ActionSet",
                        "actions": [
                            {
                                "type": "Action.Submit",
                                "title": "Give me another one"
                            }
                        ]
                    }
                ],
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json"
            }
        }
        ]
    }

    payload = json.dumps(payload)

    response = apiCallReturnJSON("POST", url, BOT_TOKEN, "application/json", payload)
    print(json.dumps(response, indent=4, sort_keys=True))


def getMsgInfo(message_id):
    
    url = "{}/messages/{}".format(BASE_URL, message_id)
    payload = {}

    return apiCallReturnJSON("GET", url, BOT_TOKEN, "application/json", payload)


def getActionInfo(action_id):

    url = "{}/attachment/actions/{}".format(BASE_URL, action_id)
    payload = {}

    return apiCallReturnJSON("GET", url, BOT_TOKEN, "application/json", payload)


def sendMessage(room_id, message):

    url = "{}/messages".format(BASE_URL)

    payload = {
        "roomId": room_id,
        "text": message
    }

    payload = json.dumps(payload)

    apiCallReturnJSON("POST", url, BOT_TOKEN, "application/json", payload)


def getRoomInfo(room_id):
    url = "{}/rooms/{}".format(BASE_URL, room_id)
    return apiCallReturnJSON("GET", url, BOT_TOKEN, "application/json", {})


if __name__ == "__main__":

    print("\n")
    # If the file does not even exist just exit
    if not doesFileExist(CONFIG_FILE):
        print("\n Sort your configs out please... Bye Bye\n")
        exit()

    global BOT_TOKEN
    global BOT_EMAIL

    BOT_TOKEN = getBotToken(CONFIG_FILE)
    BOT_EMAIL = getBotEmail(CONFIG_FILE)

    # Hosted on localhost port 5004 - Remember to run "ngrok http 5004"
    app.run(host="0.0.0.0", port=8000, debug=False)