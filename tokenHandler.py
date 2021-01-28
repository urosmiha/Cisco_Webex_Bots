import json

def doesFileExist(config_file):
    try:
        json_file = open('config/{}'.format(config_file), 'r')
        json_file.close()
        return True
    except Exception as e:
        print("Error: {}".format(e))
        return False   


def getParameters(config_file):
    
    try:
        json_file = open('config/{}'.format(config_file), 'r')
        parameters = json.load(json_file)
        json_file.close()
    except Exception as e:
        print("Error: {}".format(e))
        return

    return parameters


def getBotToken(config_file):

    parameters = getParameters(config_file)
    try:
        return parameters['bot_token']
    except Exception as e:
        print("Error: {}".format(e))
        return
        

def getBotEmail(config_file):
    parameters = getParameters(config_file)
    try:
        return parameters['bot_email']
    except Exception as e:
        print("Error: {}".format(e))
        return


def getWebHookId(config_file):
    parameters = getParameters(config_file)
    try:
        return parameters['webhook_id']
    except Exception as e:
        print("Error: {}".format(e))
        return


if __name__ == "__main__":
    print("This does nothing on it's own. It's a helper funtion to be used by others. \n")
    print("There you go! Bye...\n")
    pass