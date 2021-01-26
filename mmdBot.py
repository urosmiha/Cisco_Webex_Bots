import json
import requests
from flask import Flask, request
from requests_toolbelt.multipart.encoder import MultipartEncoder

app = Flask(__name__)

from apiHandler import apiCallReturnJSON
from tokenHandler import getBotToken, getBotEmail, doesFileExist

CONFIG_FILE = "mmd_config.json"
BASE_URL = "https://webexapis.com/v1"


@app.route("/", methods=["POST"])
def getHook():

    hook_info = request.json

    print(json.dumps(hook_info, indent=4, sort_keys=True))

    hook_resource = hook_info["resource"]

    if hook_resource == "messages":
        message_info = getMsgInfo(hook_info["data"]["id"])

        message_text = message_info["text"]

        print("Message: {}".format(message_text))

        room_id = hook_info["data"]["roomId"]

        sender_email = hook_info["data"]["personEmail"]

        if sender_email != BOT_EMAIL:
            if message_text == "panda" or message_text == "Make panda":

                response = getRoomInfo(room_id)
                print(json.dumps(response, indent=4, sort_keys=True))

                img_url = getRandomImgURL()
                # img_msg = getRandomFact()
                # sendImgFromURL(room_id, img_url, "")
                sendCard(room_id, img_url)

            else:
                sendMessage(room_id, "Sorry I'm not build for that :'(")

    elif hook_resource == "attachmentActions":
        action_info = getActionInfo(hook_info["data"]["id"])

        print(json.dumps(action_info, indent=4, sort_keys=True))
    

    return ""


@app.after_request
def add_header(response):
    response.cache_control.max_age = 300
    return response


def getRandomImgURL():

    rndm_base_url = "https://some-random-api.ml"
    rndm_api_type = "img"
    rndm_api_topic = "panda"

    payload = {}
    headers = {}
    url = "{}/{}/{}".format(rndm_base_url, rndm_api_type, rndm_api_topic)

    response = requests.request("GET", url=url, headers=headers, data=payload)

    response = json.loads(response.text)
    return response["link"]


def getRandomFact():

    rndm_base_url = "https://some-random-api.ml"
    rndm_api_type = "facts"
    rndm_api_topic = "panda"

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