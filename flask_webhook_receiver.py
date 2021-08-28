from flask import Flask, request, json
from messenger import Messenger
import re
from dna import Dna
from jinja2 import Template
from datetime import datetime

from pyngrok import conf, ngrok

from console_logging import logger

from werkzeug.serving import is_running_from_reloader


import os

from Card import CardInput, CardMain, CardOutput, CardToggle, CardInputShowCard


app = Flask(__name__)
port = 5005

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST' and 'Content-Type' in request.headers and 'application/json' in request.headers.get('Content-Type'):

        data = request.get_json()    
        
        #we got POST from Webex teams
        if "data" in data: 
        
            # Check if msg came from BOT itself and then ignore. 
            if msg.bot_id == data.get('data').get('personId'):
                return 'Message from self ignored'

            roomId=data.get('data').get('roomId')
            messageId=data.get('data').get('id')
            messageType=data.get('data').get('type')

            # Card
            if messageType=="submit":
                
                msg.get_card_message(messageId)

                if "main" in msg.message_structure:
                    showcard_selected_in_main(roomId)

                elif "input_" in msg.message_structure["card_name"]:
                    showcard_after_input_type(roomId)
                    
                elif "toggle_" in msg.message_structure["card_name"]:
                    showcard_after_toggle_type(roomId)

                elif "inputshowcard_" in msg.message_structure["card_name"]:
                    showcard_after_inputshowcard_type(roomId)

                elif msg.message_structure["card_name"]=="main":                    
                    showcard_main_menu(roomId)

                else:
                    print ("that card still not implemented")
            
            # Message
            else:
                
                msg.get_txt_message(messageId)

                if "hello" in msg.message_structure.lower():
                    showcard_main_menu(roomId)
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
        return msg_text

def card_json_from_variables(card_file,vard=None):

    file_path=os.path.join(DIR,f"Cards/{card_file}")

    with open(file_path) as fp:
        text = fp.read()
    
    if vard:
       t = Template(text)
       r= t.render(vard)
       return json.loads(r)
    else:
        return json.loads(text)

def showcard_warning(roomId, cardOptionTitle, cardOptionText):
    cardName="card_output_generic.json"  
    cardMessage="Warning"
    
    vard={"var1": cardOptionTitle, "var2": cardOptionText, \
                            "colour1": "Attention","colour2": "Attention","colour3": "Attention"}

    msg.post_message_card(roomId,cardMessage,card_json_from_variables(cardName,vard))

def showcard_nothing_selected(roomId):
    cardOptionTitle="None selected"
    cardOptionText="None of the options selected.\\nPlease select at least one option!"
    showcard_warning(roomId, cardOptionTitle, cardOptionText)
    
def showcard_selected_in_main(roomId):
    cardMessage="Card for " + msg.message_structure['button']
    cardName="card_" + msg.message_structure['button'] + ".json"
                    
    vard = None
    msg.post_message_card(roomId,cardMessage, card_json_from_variables(cardName, vard))

def showcard_output_as_attach(roomId, cardOptionText, ListOfCommands):
    cardName="card_output_generic.json"
    now = datetime.now()
    datetime_string = now.strftime("%d%m%Y%H%M%S")

    if len(ListOfCommands)==1:
        command_format = ListOfCommands[0].replace("_"," ") + " " + datetime_string
    else:
        command_format = "Multiple commands " + datetime_string

    cardMessage="Card for option " + command_format
    cardOptionTitle="Option " + command_format + " selected" 

    file_path=os.path.join(DIR,f"Attach/{command_format}.doc")
                        
    with open(file_path, "w") as tf:
        tf.write(cardOptionText)
                        
    vard={"var1": cardOptionTitle, "var2": "Check attachment for details", \
                                "colour1": "Accent","colour2": "Good","colour3": "Dark"}
                        
    msg.post_message_card(roomId,cardMessage, card_json_from_variables(cardName,vard))
    msg.post_message_roomId_file(roomId, msg.messageParentId, cardMessage, file_path, command_format)

def showcard_output_as_inline(roomId, cardOptionText, command):
    cardName="card_output_generic.json"
    
    command_format = command.replace("_"," ")
    cardMessage="Card for option " + command_format            
    cardOptionTitle="Option " + command_format + " selected"
                                                        
    vard={"var1": cardOptionTitle, "var2": cardOptionText, \
        "colour1": "Accent","colour2": "Good","colour3": "Dark"}

    msg.post_message_card(roomId,cardMessage,card_json_from_variables(cardName,vard))

def showcard_main_menu(roomId):
    cardMessage="Card for main manu"
    cardName="card_main_menu.json"

    vard = None

    msg.post_message_card(roomId,cardMessage,card_json_from_variables(cardName,vard))

def showcard_after_input_type(roomId):
    command = msg.message_structure["cmd"]
    ListOfCommands = []
    attach = msg.message_structure["attachment"]

    if command=="":
        showcard_nothing_selected(roomId)
    else:
        fnc=getattr(dn, command, None)
        if fnc:
            if attach=="true":
                ListOfCommands=[command]
                inlineMsg, attachmentMsg = fnc()
                showcard_output_as_attach(roomId, attachmentMsg, ListOfCommands)
            else:
                inlineMsg, attachmentMsg = fnc()
                showcard_output_as_inline(roomId, inlineMsg, command)
        else:
            if attach=="true":
                ListOfCommands=[command]
                cardOptionText=dn.commands(ListOfCommands)
                showcard_output_as_attach(roomId, cardOptionText, ListOfCommands)
            else:
                showcard_warning(roomId, "WARNING!", f"Command/function <{command}> not implemented yet!")

def showcard_after_toggle_type(roomId):
    none_selected=True
    ListOfCommands=[]
    cardOptionText=""
    attach=msg.message_structure["attachment"]

    for command, flag in msg.message_structure.items():
        
        if flag=="true" and command!="attachment":
            fnc=getattr(dn, command, None)
            none_selected=False

            if fnc:
                if attach=="true":
                    inlineMsg, attachmentMsg = fnc()
                    cardOptionText = cardOptionText + attachmentMsg +"\n\n"
                    ListOfCommands.append(command)
                else: 
                    inlineMsg, attachmentMsg = fnc()
                    showcard_output_as_inline(roomId, inlineMsg, command)
            else:
                if attach=="true":
                    cardOptionText = cardOptionText + f"Command/function <{command}> not implemented yet!" + "\n\n"
                    ListOfCommands.append(command)
                else:
                    showcard_warning(roomId, "WARNING!", f"Command/function <{command}> not implemented yet!")
            
        
    if none_selected:
        showcard_nothing_selected(roomId)
    else:
        if attach=="true":
            showcard_output_as_attach(roomId, cardOptionText, ListOfCommands)

def showcard_after_inputshowcard_type(roomId):
    showcard_warning(roomId, "WARNING!", f"This card is not implemented yet!")


person_emails = ["mmiletic@cisco.com"]


DIR = os.path.dirname(os.path.abspath(__file__))    


#Register a webhook for Webex teams. one for messages and one for attachments(cards)
msg = Messenger()


#ngrok_url="http://2182-109-133-255-223.eu.ngrok.io"

if is_running_from_reloader():
    conf.get_default().region = "eu"

    ngrok_url = ngrok.connect(5005).public_url

    print (ngrok_url)
    print (ngrok.get_tunnels())
    
    msg.register_webhook(ngrok_url)


# Call Dna class to login to DNA
dn = Dna()

#Card 1
subTitle = "Command runner options"
options = { "Show version" : "show_version", "Show inventory" : "show_inventory"}
cardIdName = "cmdRunnertest"

c1=CardInput(subTitle, options, cardIdName)

#Card 2
subTitle = "Show commnad options"
options = { "show client health" : "show_client_health", "show network health" : "show_network_health", \
            "show site health": "show_site_health", "show devices":"show_devices", "show none" : "show_none"}
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

"""
#Card 5
subTitle = "multiple ch"
options = { "A" : "A", "B" : "B"}
cardIdName = "AB"

c5=CardInput(subTitle, options, cardIdName)



#Card 6
subTitle = "Device queries"
options = { "0" : {"Device 1" : "device1", "Device 2" : "device2", "Device 3" : "device3"}, \
            "1" : {"show version" : "show_v","show run" : "show_run"} }
cardIdName = "devicecommands"

c6=CardInputShowCard(subTitle, options, cardIdName)


#Card main
#id of the card needs to be one of above created.
subTitle = "Chatbot demo assisting with configuring, monitoring and analysing data."
options = { "A1" : {"🌐 Command runner" : c1.display() }, \
            "A2" : { "🚑 Health" : c2.display(), },  \
            "A3" : {"🧪 Testing" : c3.display()}, \
            "A4" : {"🧪 Pest" : c5.display() , "🧪 Mest" : c6.display()}
            }
cardIdName = "menu"

cMain=CardMain(subTitle, options, cardIdName)


#Card output/dynamic.
cardIdName = "generic"

cOutput=CardOutput(cardIdName)

app.run(host="0.0.0.0", port=port, debug=True)
