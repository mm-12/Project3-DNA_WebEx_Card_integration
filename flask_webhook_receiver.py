from flask import Flask, request, json
from messenger import Messenger
import re
from dna import Dna
from jinja2 import Template

from console_logging import logger

import os

from Card import CardInput, CardMain, CardOutput, CardToggle


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
            # Collect the message id from the notification, so you can fetch the message content or card content
            # Get the type of the received message. So far 2 types possible: submit(card), None(text)
            roomId=data.get('data').get('roomId')
            messageId=data.get('data').get('id')
            messageType=data.get('data').get('type')
            logger.debug("MSG type: %s",messageType)
            logger.debug("MSG ID: %s",messageId)
            logger.debug("Room ID: %s",roomId)
            logger.debug("Person ID: %s",data.get('data').get('personId'))
            logger.debug("Raw msg: %s",json.dumps(data.get('data'),indent=4))


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
                    
                    msg.post_message_card(roomId,cardMessage, card_jsonAttach(cardName, vard))
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
                        
                        vard={"var1": cardOptionTitle, "var2": cardOptionText, \
                            "colour1": "Attention","colour2": "Attention","colour3": "Attention"}

                        msg.post_message_card(roomId,cardMessage, card_jsonAttach(cardName,vard))

                    else:
                        cardOptionText=getattr(dn, command)()

                        command_format = command.replace("_"," ")
                        cardMessage="Card for option " + command_format
                        cardOptionTitle="Option " + command_format + " selected"
                        
                        file_path=os.path.join(DIR,f"Attach/{command_format}.doc")
                        
                        with open(file_path, "w") as tf:
                            tf.write(cardOptionText[command_format])
                        
                        vard={"var1": cardOptionTitle, "var2": "Check attachment for details", \
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
                            
                            vard={"var1": cardOptionTitle, "var2": cardOptionText, \
                            "colour1": "Accent","colour2": "Good","colour3": "Dark"}

                            msg.post_message_card(roomId,cardMessage,card_jsonAttach(cardName,vard))

                            logger.debug("Izabrana opcija/card: %s", command)

                            none_selected=False
                    
                    
                    if none_selected:
                        # Nothing selected

                        cardMessage="Nothing selected"
                        
                        cardOptionTitle="None selected"
                        cardOptionText="None of the options selected.\\nPlease select at least one option!"

                        vard={"var1": cardOptionTitle, "var2": cardOptionText, \
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

                    vard={"var1": cardOptionTitle, "var2": cardOptionText, \
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

#This function is to return card json variable with all varibales populated. 
def card_jsonAttach(card_file,vard=None):

    file_path=os.path.join(DIR,f"Cards/{card_file}")

    with open(file_path) as fp:
        text = fp.read()
    
    if vard:
       t = Template(text)
       r= t.render(vard)
       return json.loads(r)
    else:
        return json.loads(text)



person_emails = ["mmiletic@cisco.com"]


DIR = os.path.dirname(os.path.abspath(__file__))    


#Register a webhook for Webex teams. one for messages and one for attachments(cards)
msg = Messenger()
ngrok_url="http://cd6c-109-133-255-223.eu.ngrok.io"
msg.registerWebhook(ngrok_url)


#Card 1
subTitle = "Command runner options"
options = { "Show version" : "show_version", "Show inventory" : "show_inventory"}
cardIdName = "cmdRunnertest"

c1=CardInput(subTitle, options, cardIdName)

#Card 2
subTitle = "Show commnad options"
options = { "show client health" : "show_client_health", "show network health" : "show_network_health", \
                            "show site health": "show_site_health", "show devices":"show_devices"}
cardIdName = "show"

c2=CardToggle(subTitle, options, cardIdName)

#Card 3
subTitle = "Show config options"
options = { "confgig a" : "config_a", "config  b" : "config_b"}
cardIdName = "config"

c3=CardToggle(subTitle, options, cardIdName)


#Card main
#id of the card needs to be one of above created.
subTitle = "Chatbot demo assisting with configuring, monitoring and analysing data."
options = { "CONFIGURE" : {"🌐 Command runner" : c1.display()}, \
            "MONITOR" : { "🚑 Health" : c2.display()},  \
            "ANALYSE" : {"🔍 Backup" : "backup", "🧪 Testing" : c3.display()} \
            }
cardIdName = "menu"

cMain=CardMain(subTitle, options, cardIdName)


#Card output/dynamic.
cardIdName = "generic"

cOutput=CardOutput(cardIdName)

app.run(host="0.0.0.0", port=port, debug=True)
