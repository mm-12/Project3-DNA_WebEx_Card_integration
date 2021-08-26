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
        
        
        if "data" in data:
            #we got POST from Webex teams

            # Check if msg came from BOT itself and then ignore. 
            if msg.bot_id == data.get('data').get('personId'):
                return 'Message from self ignored'

            roomId=data.get('data').get('roomId')
            messageId=data.get('data').get('id')
            messageType=data.get('data').get('type')
        
            # Call Dna class to login to DNA
            dn = Dna()

            if messageType=="submit":
                # Check if there was a text message or card submitted in Webex. submit -> card, None -> text
                
                msg.get_card_message(messageId)

                # need to check in which Card which button was pressed and based on that to show coresponding card
                if "main" in msg.message_structure:
                    showCardSelectedInMain(roomId)

                elif "input_" in msg.message_structure["card_name"]:
                    command = msg.message_structure["cmd"]
                    ListOfCommands=[]

                    if command=="":
                        showCardNothingSelected(roomId)
                    else:
                        ListOfCommands=[command]
                        cardOptionText=dn.commands(ListOfCommands)
                        showCardOutputAsAttach(roomId, cardOptionText, ListOfCommands)

                elif "toggle_" in msg.message_structure["card_name"]:
                    none_selected=True
                    ListOfCommands=[]
                    cardOptionText=""
                    attach=msg.message_structure["Attachemnt"]

                    print ("PPPP ", msg.message_structure)
                    for command, flag in msg.message_structure.items():
                        xxx=""
                        yyy=""
                        
                        if flag=="true" and command!="Attachemnt":
                            xxx, yyy=getattr(dn, command)()
                            if attach=="true":
                                cardOptionText = cardOptionText + yyy
                                ListOfCommands.append(command)
                            else:
                                cardOptionText = xxx
                                showCardOutputAsInline(roomId, cardOptionText, command)
                            none_selected=False
                            
                        
                    if none_selected:
                        showCardNothingSelected(roomId)
                    elif attach=="true":
                        showCardOutputAsAttach(roomId, cardOptionText, ListOfCommands)
                    
                        

                elif msg.message_structure["card_name"]=="main":                    
                    showCardMainMenu(roomId)
                
            else:
                # message received is text message
                
                msg.get_txt_message(messageId)

                # If Hello is sent, show the cards
                if "hello" in msg.message_structure.lower():
                    showCardMainMenu(roomId)
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
def cardJSONFromVariables(card_file,vard=None):

    file_path=os.path.join(DIR,f"Cards/{card_file}")

    with open(file_path) as fp:
        text = fp.read()
    
    if vard:
       t = Template(text)
       r= t.render(vard)
       return json.loads(r)
    else:
        return json.loads(text)

def showCardNothingSelected(roomId):
    cardName="card_output_generic.json"  
    cardMessage="Nothing selected"
    cardOptionTitle="None selected"
    cardOptionText="None of the options selected.\\nPlease select at least one option!"

    vard={"var1": cardOptionTitle, "var2": cardOptionText, \
                            "colour1": "Attention","colour2": "Attention","colour3": "Attention"}

    msg.post_message_card(roomId,cardMessage,cardJSONFromVariables(cardName,vard))

def showCardSelectedInMain(roomId):
    cardMessage="Card for " + msg.message_structure['button']
    cardName="card_" + msg.message_structure['button'] + ".json"
                    
    vard = None
                    
    msg.post_message_card(roomId,cardMessage, cardJSONFromVariables(cardName, vard))

def showCardOutputAsAttach(roomId, cardOptionText, ListOfCommands):
    cardName="card_output_generic.json"
    
    if len(ListOfCommands)==1:
        command_format = ListOfCommands[0].replace("_"," ")
    else:
        command_format="Multiple commands"

    cardMessage="Card for option " + command_format
    cardOptionTitle="Option " + command_format + " selected" 

    file_path=os.path.join(DIR,f"Attach/{command_format}.doc")
                        
    with open(file_path, "w") as tf:
        tf.write(cardOptionText)
                        
    vard={"var1": cardOptionTitle, "var2": "Check attachment for details", \
                                "colour1": "Accent","colour2": "Good","colour3": "Dark"}
                        
    msg.post_message_card(roomId,cardMessage, cardJSONFromVariables(cardName,vard))
    msg.post_message_roomId_file(roomId, msg.messageParentId, cardMessage, file_path, command_format)

def showCardOutputAsInline(roomId, cardOptionText, command):
    cardName="card_output_generic.json"
    
    command_format = command.replace("_"," ")
    cardMessage="Card for option " + command_format            
    cardOptionTitle="Option " + command_format + " selected"
                                                        
    vard={"var1": cardOptionTitle, "var2": cardOptionText, \
        "colour1": "Accent","colour2": "Good","colour3": "Dark"}

    msg.post_message_card(roomId,cardMessage,cardJSONFromVariables(cardName,vard))

def showCardMainMenu(roomId):
    cardMessage="Card for main manu"
    cardName="card_main_menu.json"

    vard=None

    msg.post_message_card(roomId,cardMessage,cardJSONFromVariables(cardName,vard))


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

"""
#Card 4
subTitle = "test test test"
options = { "opt a" : "opt_a", "opt  b" : "opt_b"}
cardIdName = "opt"

c4=CardToggle(subTitle, options, cardIdName)


#Card 5
subTitle = "multiple ch"
options = { "A" : "A", "B" : "B"}
cardIdName = "AB"

c5=CardInput(subTitle, options, cardIdName)

"Resting" : c4.display()
"Conecting" : c5.display()
"""

#Card main
#id of the card needs to be one of above created.
subTitle = "Chatbot demo assisting with configuring, monitoring and analysing data."
options = { "CONFIGURE" : {"🌐 Command runner" : c1.display() }, \
            "MONITOR" : { "🚑 Health" : c2.display(), },  \
            "ANALYSE" : {"🧪 Testing" : c3.display()} \
            }
cardIdName = "menu"

cMain=CardMain(subTitle, options, cardIdName)


#Card output/dynamic.
cardIdName = "generic"

cOutput=CardOutput(cardIdName)

app.run(host="0.0.0.0", port=port, debug=True)
