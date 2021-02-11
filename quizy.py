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
CONFIG_FILE = "bot_config.json"
# Base URL for API calls
BASE_URL = "https://webexapis.com/v1"


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
            
            # If user sends 'new' create a new quiz
            if message_text == "new":
                # Create a new Quiz
                quiz_id = createNewQuiz()
                if quiz_id:
                    # Send a card letting them know about the new quiz
                    sendCard(room_id, "newQuizCard", quiz_id)
                else:
                    print("Failed to create quiz. Quiz ID: ", quiz_id)
                    sendMessage(room_id, "Failed to create new quiz.")

            elif message_text == "help":
                sendCard(room_id, "helpCard", None)

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


def createNewQuiz():

    quiz_id = random.randint(1000,9999)

    return quiz_id


def sendCard(room_id, card_name, quiz_id):
    '''
    Send a Card to a specified room.

    At the moment I have disabled image attachement. But it can include image from URL.
    Note it does worry about size of the image so it does get annoying.
    '''

    url = "{}/messages".format(BASE_URL)

    json_file = open('cards/{}.json'.format(card_name), 'r')
    card_content = json.load(json_file)
    json_file.close()

    card_content['roomId'] = room_id

    if quiz_id:
        card_content['attachments'][0]['content']['body'][2]['columns'][1]['items'][0]['text'] = "{}".format(quiz_id)

    payload = json.dumps(card_content)

    # Payload is still send as JSON
    # payload = json.dumps(payload)

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