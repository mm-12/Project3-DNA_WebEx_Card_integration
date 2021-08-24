from flask import Flask, request, json
import requests
from messenger import Messenger
import re
from dna import Dna
from jinja2 import Template
import pystache

from console_logging import logger

import os


app = Flask(__name__)
port = 5005

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST' and 'Content-Type' in request.headers and 'application/json' in request.headers.get('Content-Type'):
        
        # Extract data from received POST
        data = request.get_json()
        logger.info("POST received")
                
        # Determine if POST came from DNA or WEBEX teams. So far 2 options possible data(webex) or xxxx present in body
        if "data" in data:
            
            #we got POST from Webex teams
            logger.info("POST from webex teams")

            # Check if msg came from BOT itself and then ignore. 
            if msg.bot_id == data.get('data').get('personId'):
                return 'Message from self ignored'

            # Collect the roomId from the notification, so you know where to post the response
            roomId=data.get('data').get('roomId')
            logger.debug("Room ID: %s",roomId)
            logger.debug("Person ID: %s",data.get('data').get('personId'))
            logger.debug("Raw msg: %s",json.dumps(data.get('data'),indent=4))

            # Collect the message id from the notification, so you can fetch the message content or card content
            messageId=data.get('data').get('id')
            logger.debug("MSG ID: %s",messageId)
            
            # Get the type of the received message. So far 2 types possible: submit(card), None(text)
            messageType=data.get('data').get('type')
            logger.debug("MSG type: %s",messageType)
            

            # Call Dna class to login to DNA
            dn = Dna()

            # Check if there was a text message or card submitted in Webex. submit -> card, None -> text
            if messageType=="submit":
                
                # message received is a card message
                msg.get_card_message(messageId)
                logger.debug("This is the submit content of a Card that we got from the webhook: %s",json.dumps(msg.message_structure,indent=4))
                logger.debug("This is the type of the submit got from the webhook: %s", type(msg.message_structure))
                

                # need to check in which Card which button was pressed and based on that to show coresponding card
                if "main" in msg.message_structure:
                    # Main menu card
                    
                    #Define cardMessage, cardName, vard
                    cardMessage="Card for " + msg.message_structure['button']
                    cardName="card_" + msg.message_structure['button'] + ".json"
                    
                    vard = None
                    print("ovde si")
                    msg.post_message_card(roomId,cardMessage, card_jsonAttach(cardName, vard))
                    print("i ovde si")
                    logger.debug("Izabrana opcija/card: %s", msg.message_structure['button'])


                elif "input_" in msg.message_structure["card_name"]:
                    # New command runner
                    
                    #Define cardName. cardMessage, vard, cardOptionTitle, cardOptionText latter
                    cardName="card_output_generic.json"
                    command = msg.message_structure["cmd"]

                    if command=="":
                        cardMessage="Nothing selected"
                        
                        cardOptionTitle="Nothing selected"
                        cardOptionText="Please select at least one option from the list"
                        
                        
                        vard={"iconURL": iconURL, "mainTitle": mainTitle, \
                            "var1": cardOptionTitle, "var2": cardOptionText, \
                            "colour1": "Attention","colour2": "Attention","colour3": "Attention"}
                    else:
                        command_format = command.replace("_"," ")
                        cardMessage="Card for option " + command_format

                        cardOptionTitle="Option " + command_format + " selected"
                        
                        cardOptionText=getattr(dn, command)()
                        

                        file_path=os.path.join(DIR,f"Attach/{command_format}.doc")
                        
                        with open(file_path, "w") as tf:
                            tf.write(cardOptionText[command_format])
                        
                        vard={"iconURL": iconURL, "mainTitle": mainTitle, \
                                "var1": cardOptionTitle, "var2": "Check attachment for details", \
                                "colour1": "Accent","colour2": "Good","colour3": "Dark"}
                        
                    msg.post_message_card(roomId,cardMessage, card_jsonAttach(cardName,vard))
                    msg.post_message_roomId_file(roomId, msg.messageParentId, cardMessage, file_path, command_format)

                    logger.debug("Izabrana opcija/card: %s", command)

                elif "toggle_" in msg.message_structure["card_name"]:
                    # Show card
                    
                    # Initially nothing is selected
                    none_selected=True

                    cardName="card_output_generic.json"
                    
                    for command, flag in msg.message_structure.items():
                        if flag=="true":
                            cardMessage=command
                            cardOptionTitle=command.replace("_"," ") + " option selected"
                            cardOptionText=getattr(dn, command)()
                            
                            vard={"iconURL": iconURL, "mainTitle": mainTitle, \
                            "var1": cardOptionTitle, "var2": cardOptionText, \
                            "colour1": "Accent","colour2": "Good","colour3": "Dark"}

                            msg.post_message_card(roomId,cardMessage,card_jsonAttach(cardName,vard))

                            logger.debug("Izabrana opcija/card: %s", command)

                            none_selected=False
                    
                    
                    if none_selected:
                        # Nothing selected

                        cardMessage="Nothing selected"
                        
                        cardOptionTitle="None selected"
                        cardOptionText="None of the options selected.\\nPlease select at least one option!"

                        vard={"iconURL": iconURL, "mainTitle": mainTitle, \
                            "var1": cardOptionTitle, "var2": cardOptionText, \
                            "colour1": "Attention","colour2": "Attention","colour3": "Attention"}

                        msg.post_message_card(roomId,cardMessage,card_jsonAttach(cardName,vard))

                        logger.warning("Nothing selected")
                    


                elif msg.message_structure["card_name"]=="backup":
                    # Backup card
                    
                    cardMessage="backup"
                    cardName="card_output_generic.json"

                    cardOptionTitle="Backup option selected"
                    #cardOptionText="Backup is starting!!!"
                    cardOptionText="test fdlmf ldf\\ntest fdlmf ldf\\ntest fdlmf ldf\\ntest fdlmf ldf\\ntest fdlmf ldf\\ntest fdlmf ldf\\ntest fdlmf ldf\\ntest fdlmf ldf\\ntest fdlmf ldf\\ntest fdlmf ldf\\ntest fdlmf ldf\\ntest fdlmf ldf\\ntest fdlmf ldf\\ntest fdlmf ldf\\ntest fdlmf ldf\\ntest fdlmf ldf\\ntest fdlmf ldf\\ntest fdlmf ldf\\ntest fdlmf ldf\\ntest fdlmf ldf\\ntest fdlmf ldf\\ntest fdlmf ldf\\ntest fdlmf ldf\\ntest fdlmf ldf\\ntest fdlmf ldf\\ntest fdlmf ldf\\ntest fdlmf ldf\\ntest fdlmf ldf\\ntest fdlmf ldf\\n"

                    vard={"iconURL": iconURL, "mainTitle": mainTitle, \
                        "var1": cardOptionTitle, "var2": cardOptionText, \
                        "colour1": "Accent","colour2": "Good","colour3": "Dark"}

                    msg.post_message_card(roomId,cardMessage,card_jsonAttach(cardName,vard))

                    logger.info("Start backup")

                elif msg.message_structure["card_name"]=="main":
                    # Home/main menu button pressed

                    cardMessage="Card for main manu"
                    cardName="card_main_menu.json"

                    vard=None

                    msg.post_message_card(roomId,cardMessage,card_jsonAttach(cardName,vard))

                    logger.info("Back to main menu")            
                
            else:
                # message received is text message
                
                msg.get_txt_message(messageId)
                logger.debug("This is the msg content got from the webhook: %s",msg.message_structure)
                logger.debug("This is the type of the msg got from the webhook: %s", type(msg.message_structure))

            
                # If Hello is sent, show the cards
                if "hello" in msg.message_structure.lower():
                    cardMessage="Card for main manu"
                    cardName="card_main_menu.json"
                    vard=None

                    msg.post_message_card(roomId,cardMessage, card_jsonAttach(cardName,vard))
                else:
                    msg.post_message_roomId(roomId,"Type hello to start")           
        
        else:
            #we got POST from DNA
            
            severity=data["severity"]
            message=data["message"]
            component=data["consumed_events"][0]["component"]
            system_ip=data["consumed_events"][0]["system-ip"]
            hostname=data["consumed_events"][0]["host-name"]
            vpn_id=data["consumed_events"][0]["vpn-id"]

            msg_text=f"Severity: {severity} from hosname: {hostname} with IP: {system_ip} and VPN ID: {vpn_id}, on COMPONENT: {component} with the message:\n{message}"
            for person_email in person_emails:
                msg.post_message_email(person_email, msg_text)

            logger.info("post sa DNA")
            logger.debug("Raw json: %s", json.dumps(data,indent=4))
        return data

    else: 
        msg_text = "We got GET or POST from CURL or something is wrong"
        logger.warning(msg_text)

        for person_email in person_emails:
            msg.post_message_email(person_email, msg_text)
        return None


def card_jsonAttach(card_file,vard=None):
    with open(f'Cards/templates/{card_file}') as fp:
        text = fp.read()
    
    if vard:
       
       # logger.debug(f"This is how unparsed card will look like: {r}")
       
       t = Template(text)
       r= t.render(vard)

       return json.loads(r)

    else:
        return json.loads(text)

def create_webhook(url,resource):
    webhooks_api = f'{msg.base_url}/webhooks'
    data = { 
        "name": f"Webhook to ChatBot - {resource}",
        "resource": resource,
        "event": "created",
        "targetUrl": f"{url}"
        }
    webhook = requests.post(webhooks_api, headers=msg.headers, data=json.dumps(data))
    if webhook.status_code != 200:
        webhook.raise_for_status()
        logger.error("Cannot register webhook")
    else:
        logger.debug(f'Webhook to {url} created for ChatBot - {resource}')


def get_webhook_urls():
    webhook_urls_res = []
    webhooks_api = f'{msg.base_url}/webhooks'
    webhooks = requests.get(webhooks_api, headers=msg.headers)
    if webhooks.status_code != 200:
            webhooks.raise_for_status()
    else:
        for webhook in webhooks.json()['items']:
            webhook_urls_res.append((webhook['targetUrl'],webhook['resource']))
    return webhook_urls_res

def createCard(card_type, iconURL, mainTitle, subTitle, options, card_name_p):
    if card_type == "input":
        cardName_template="card_inputChoiceSet_template.json"
        print(f"Reminder that you need to spcify functions {options.values()} in file dna.py if not already")
    elif card_type == "toggle":
        cardName_template="card_toggle_template.json"
        print(f"Reminder that you need to spcify functions {options.values()} in file dna.py if not already")
    elif card_type == "main":
        cardName_template="card_mainmenu_template.json"
        for v in options.values():
            for vl in v.values():
                all_manu_buttons.append(vl)

        if list(set(all_manu_buttons) - set(cards)):
            print ("There is still button defined in main menu, that is not defined as a card", list(set(all_manu_buttons) - set(cards)))
        if list(set(cards) - set(all_manu_buttons)):
            print ("There is still card defined, that is not defined in the main menu", list(set(cards) - set(all_manu_buttons)))



    else:
        print("Wrong card type!")
        exit()


    vard={"iconURL": iconURL, "mainTitle": mainTitle, \
            "subTitle": subTitle, \
            "toggle_choiceset": options, \
            "card_name": card_type+"_"+card_name_p  }
    
    cardName="card_"+vard["card_name"]+".json"
    
    file_path=os.path.join(DIR,f"Cards/templates/{cardName}")
    
    with open(file_path, "w") as tf:
        tf.write(json.dumps(card_jsonAttach(cardName_template,vard),indent=4))
    
    cards.append(vard["card_name"])
    




msg = Messenger()
person_emails = ["mmiletic@cisco.com"]


DIR = os.path.dirname(os.path.abspath(__file__))    


ngrok_url="http://cd6c-109-133-255-223.eu.ngrok.io"
ngrok_url_msg=[(ngrok_url,"messages")]
ngrok_url_att=[(ngrok_url,"attachmentActions")]

webhook_urls = get_webhook_urls()

logger.debug("set msg: %s", set(ngrok_url_msg))
logger.debug("set att: %s", set(ngrok_url_att))
logger.debug("set urls: %s", set(webhook_urls))

intersect_msg = list(set(ngrok_url_msg) & set(webhook_urls))
intersect_att = list(set(ngrok_url_att) & set(webhook_urls))

logger.debug("intersect_msg: %s",intersect_msg)
logger.debug("intersect_att: %s",intersect_att)


if intersect_msg:
    logger.info(f'Already registered webhook for Msg: {intersect_msg[0]}')
else: 
    logger.warning("There is no webhook for messages yet. Creating a new one")
    create_webhook(ngrok_url, "messages")
    

if intersect_att:
    logger.info(f'Already registered webhook for Att: {intersect_att[0]}')
else: 
    logger.warning("There is no webhook for cards yet. Creating a new one")
    create_webhook(ngrok_url, "attachmentActions")
    





# CARDS
cards=[]
all_manu_buttons=[]

iconURL="https://community.cisco.com/legacyfs/online/fusion/117586_DNA%20Center%20Graphic.png"
mainTitle="1000s Demo"

card_type="input"
subTitle = "Command runner options"
options = { "Show version" : "show_version", "Show inventory" : "show_inventory"}
card_name = "cmdRunnertest"

createCard(card_type, iconURL, mainTitle, subTitle, options, card_name)


card_type="toggle"
subTitle = "Show commnad options"
options = { "show client health" : "show_client_health", "show network health" : "show_network_health", \
                            "show site health": "show_site_health", "show devices":"show_devices"}
card_name = "show"

createCard(card_type, iconURL, mainTitle, subTitle, options, card_name)

card_type="toggle"
subTitle = "Show config options"
options = { "confgig a" : "config_a", "config  b" : "config_b"}
card_name = "config"

createCard(card_type, iconURL, mainTitle, subTitle, options, card_name)

card_type="main"
subTitle = "Chatbot demo assisting with configuring, monitoring and analysing data."
options = { "CONFIGURE" : {"🌐 Command runner" : "input_cmdRunnertest"}, \
            "MONITOR" : { "🚑 Health" : "toggle_show"},  \
            "ANALYSE" : {"🔍 Backup" : "backup", "🧪 Testing" : "toggle_config"} \
            }
card_name = "menu"

createCard(card_type, iconURL, mainTitle, subTitle, options, card_name)




app.run(host="0.0.0.0", port=port, debug=True)
