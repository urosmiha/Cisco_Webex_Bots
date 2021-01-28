import json
import requests
import random
from flask import Flask, request
from requests_toolbelt.multipart.encoder import MultipartEncoder

app = Flask(__name__)
# Import helper functions
from apiHandler import apiCallReturnJSON
from tokenHandler import getBotToken, getBotEmail, doesFileExist

# The config file will hold sensitive data, such as API tokens. Note that this is ignored by git so you would need to create one on your own.
CONFIG_FILE = "mmd_config.json"
# Base URL for API calls
BASE_URL = "https://webexapis.com/v1"
# Used to retrieve random image baed on the topic
RANDOM_API_URL = "https://some-random-api.ml"
# These are the animals the user can ask for
VALID_ANIMALS = ['panda', 'koala', 'dog', 'cat']


@app.route("/", methods=["POST"])
def getHook():
    '''
    Simply listen for POST request from a webhook.

    Responsinble for processing and acting upon a reaquest by calling appropriate functions.
    '''
    # Read URL request that comes in as a JSON file.
    # It will contain information about room ID and type of hook it is (i.e. message or action)
    # Room ID will allow you to query the excact message since webhook does not include message just the notification.
    hook_info = request.json
    hook_resource = hook_info["resource"]
    room_id = hook_info["data"]["roomId"]

    # TODO: proper logging
    # print(json.dumps(hook_info, indent=4, sort_keys=True))

    if hook_resource == "messages":
        message_info = getMsgInfo(hook_info["data"]["id"])

        # Lower_case the text for easier handling - it does not metter if animal is spelled with uppercase or lowercase.
        message_text = message_info["text"].lower()
        sender_email = hook_info["data"]["personEmail"]

        # response = getRoomInfo(room_id)
        # For debug purposes - TODO: Replace with proper logging
        # print(json.dumps(response, indent=4, sort_keys=True))

        # Make sure the message did not come from a Bot so it does not enter endless loop.
        # I believe the WebHook filter cannot specify from which user NOT to accept notification.
        if sender_email != BOT_EMAIL:
            
            # If 'help' or 'control' is received send appropriate response and just exit/return so we don't need to look for animals.
            if message_text == "help" or message_text == "control":
                # img_url = getRandomImgURL(random.choice(VALID_ANIMALS))
                img_url = ""
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

    # Whenever a user clicks on the Card it is registered as attachement action
    elif hook_resource == "attachmentActions":
        action_info = getActionInfo(hook_info["data"]["id"])

        # Debug TODO: logging
        # print(json.dumps(action_info, indent=4, sort_keys=True))

        # Each input field can have an id to identify and retrieve value from the Card
        # Refer to sendCard() function to see Card IDs and values.
        user_wish = action_info["inputs"]["userWish"]
        next_animal = action_info["inputs"]["nextAnimal"]

        # If user has specified what they want to see then just tell them we cannot do it cause we are not capable yet
        # Maybe if I buy google API or build large database of images... I might implement this feature but I'm poor and ain't got time for collecting images.
        if user_wish:
            message = "Sorry, I'm not that smart. You'll still need to choise one of the options"
            sendMessage(room_id, message)
        # Whatever they selected from the drop down use as the next animal to retrieve an random image - otherwise just pick a random animal
        if next_animal:
            img_url = getRandomImgURL(next_animal)
        else:
            img_url = getRandomImgURL(random.choice(VALID_ANIMALS))

        # print(img_url)

        sendImgFromURL(room_id, img_url, "")

    return ""


@app.after_request
def add_header(response):
    '''
    Caching control
    '''
    response.cache_control.max_age = 300
    return response


def getRandomImgURL(rndm_api_topic):
    ''' 
    Relies on open source "https://some-random-api.ml" API to retrieve random mage based on the topic.
    Does not require any auth or headers, just simle get method.

    Returns a link to a random image.
    '''

    payload = {}
    headers = {}
    url = "{}/{}/{}".format(RANDOM_API_URL, "img", rndm_api_topic)

    response = requests.request("GET", url=url, headers=headers, data=payload)
    response = json.loads(response.text)
    
    return response["link"]


def getRandomFact(rndm_api_topic):
    ''' 
    Relies on open source "https://some-random-api.ml" API to retrieve random fact based on the topic.
    Does not require any auth or headers, just simle get method.

    Returns a random fact.
    '''

    payload = {}
    headers = {}
    url = "{}/{}/{}".format(RANDOM_API_URL, "facts", rndm_api_topic)

    response = requests.request("GET", url=url, headers=headers, data=payload)
    response = json.loads(response.text)

    return response["fact"]


def sendImgFromURL(room_id, img_url, message):
    '''
    Image cannot be sent as a URL if send as a message.
    So I thought, why not just download the image from the URL first, and then save it as tmp.png
    And then attach it to a message and send it. Very messy but it works!

    Side note: Cards support URL images but are very strict about size of an image so it does not work most of the time.

    Send a message with image to a specified room.
    '''
    # Get image URL
    image_response = requests.get(img_url)
    # Save it to a tmp file
    file = open("tmp.png", "wb")
    file.write(image_response.content)
    file.close()

    # Need to add messages to base url to indicate we are sending a message
    url = "{}/messages".format(BASE_URL)

    # When attaching image payload needs to be MultipartEncoder encodded
    payload = MultipartEncoder({
        "roomId": room_id,
        "text": message,
        "files": ('tmp.png', open('tmp.png', 'rb'),'image/png')
    })
    # Make sure payload is appropriate as well
    content_type = payload.content_type

    # Do a post to send a message
    response = apiCallReturnJSON("POST", url, BOT_TOKEN, content_type, payload)
    # print(json.dumps(response, indent=4, sort_keys=True))


def sendCard(room_id, img_url):
    '''
    Send a Card to a specified room.

    At the moment I have disabled image attachement. But it can include image from URL.
    Note it does worry about size of the image so it does get annoying.
    '''

    url = "{}/messages".format(BASE_URL)

    # Payload is based on Adaptive Cards, which is sent as attachement.
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
                    # {
                    #     "type": "Image",
                    #     "altText": "",
                    #     "url": "{}".format(img_url)
                    # },
                    {
                        "type": "TextBlock",
                        "text": "In the chat just type one of the following: panda, dog, cat",
                        "wrap": True
                    },
                    {
                        "type": "TextBlock",
                        "text": "Otherwise just select from dropdown menu below!",
                        "wrap": True
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
    # Payload is still send as JSON
    payload = json.dumps(payload)

    response = apiCallReturnJSON("POST", url, BOT_TOKEN, "application/json", payload)
    # print(json.dumps(response, indent=4, sort_keys=True))


def getMsgInfo(message_id):
    '''
    Get information about specific message.
    '''

    url = "{}/messages/{}".format(BASE_URL, message_id)
    payload = {}

    return apiCallReturnJSON("GET", url, BOT_TOKEN, "application/json", payload)


def getActionInfo(action_id):
    '''
    Get information about specific atttachement
    '''

    url = "{}/attachment/actions/{}".format(BASE_URL, action_id)
    payload = {}

    return apiCallReturnJSON("GET", url, BOT_TOKEN, "application/json", payload)


def sendMessage(room_id, message):
    '''
    Just send a message to specified room
    '''

    url = "{}/messages".format(BASE_URL)
    payload = {
        "roomId": room_id,
        "text": message
    }
    payload = json.dumps(payload)

    response = apiCallReturnJSON("POST", url, BOT_TOKEN, "application/json", payload)
    # print(json.dumps(response, indent=4, sort_keys=True))


def getRoomInfo(room_id):
    '''
    Return everything about the room.
    '''
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