from flask import Flask, request, json
import requests
from messenger import Messenger
import re
from dna import Dna
from jinja2 import Template
from console_logging import logger


app = Flask(__name__)
port = 5005

msg = Messenger()
person_emails = ["mmiletic@cisco.com"]


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
                logger.warning("Message from self ignored")
                return 'Message from self ignored'

            # Collect the roomId from the notification, so you know where to post the response
            roomId=data.get('data').get('roomId')
            logger.debug("Room ID: %s",roomId)
            logger.debug("Person ID: %s",data.get('data').get('personId'))
            logger.debug("Raw msg: %s",json.dumps(data.get('data'),indent=4))

            # Collect the message id from the notification, so you can fetch the message content or card content
            messageId=data.get('data').get('id')
            logger.debug("Message ID: %s",messageId)
            
            # Get the type of the received message. So far 2 types possible: submit(card), None(text)
            messageType=data.get('data').get('type')
            logger.debug("MSG type: %s",messageType)
            
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

                    msg.post_message_card(roomId,cardMessage, card(cardName, vard))

                    logger.debug("Izabrana opcija/card: %s", msg.message_structure['button'])


                elif msg.message_structure["card_name"]=="newNetwork":
                    # New network card
                    
                    #Define cardName. cardMessage, vard, cardOptionTitle, cardOptionText latter
                    cardName="card_output_generic.json"

                    if msg.message_structure['network']=="":
                        cardMessage="Nothing selected"
                        
                        cardOptionTitle="Nothing selected"
                        cardOptionText="Please select at least one network"
                        
                        vard={"var1": cardOptionTitle, "var2": cardOptionText, \
                            "colour1": "Attention","colour2": "Attention","colour3": "Attention"}
                    else:
                        cardMessage="Card for option " + msg.message_structure['network']

                        cardOptionTitle="Option " + msg.message_structure['network'] + " selected"
                        cardOptionText="Some output for option " + msg.message_structure['network']
                        
                        vard={"var1": cardOptionTitle, "var2": cardOptionText, \
                                "colour1": "Accent","colour2": "Good","colour3": "Dark"}
                        
                    msg.post_message_card(roomId,cardMessage, card(cardName,vard))

                    logger.debug("Izabrana opcija/card: %s", msg.message_structure['network'])

                elif msg.message_structure["card_name"]=="show":
                    # Show card

                    # Call Dna class to login to DNA
                    dn = Dna()
                    
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

                            msg.post_message_card(roomId,cardMessage,card(cardName,vard))

                            logger.debug("Izabrana opcija/card: %s", command)

                            none_selected=False
                    
                    
                    if none_selected:
                        # Nothing selected

                        cardMessage="Nothing selected"
                        
                        cardOptionTitle="None selected"
                        cardOptionText="None of the show options selected.\\nPlease select at least one show output!"

                        vard={"var1": cardOptionTitle, "var2": cardOptionText, \
                            "colour1": "Attention","colour2": "Attention","colour3": "Attention"}

                        msg.post_message_card(roomId,cardMessage,card(cardName,vard))

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

                    msg.post_message_card(roomId,cardMessage,card(cardName,vard))

                    logger.info("Start backup")

                elif msg.message_structure["card_name"]=="main":
                    # Home/main menu button pressed

                    cardMessage="Card for main manu"
                    cardName="card_menu.json"

                    vard=None

                    msg.post_message_card(roomId,cardMessage,card(cardName,vard))

                    logger.info("Back to main menu")            
                
            else:
                # message received is text message
                
                msg.get_txt_message(messageId)
                logger.debug("This is the msg content got from the webhook: %s",msg.message_structure)
                logger.debug("This is the type of the msg got from the webhook: %s", type(msg.message_structure))

            
                # If Hello is sent, show the cards
                if "hello" in msg.message_structure.lower():
                    cardMessage="Card for main manu"
                    cardName="card_menu.json"
                    vard=None

                    msg.post_message_card(roomId,cardMessage, card(cardName,vard))
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


def card(card_file,vard=None):
    with open(f'Cards/{card_file}') as fp:
        text = fp.read()
    
    if vard:
       t = Template(text) 
       r= t.render(vard)
       logger.error(r)
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

ngrok_url="http://faea97fe4531.eu.ngrok.io"
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
    logger.debug(f'Registered webhook for Msg: {intersect_msg[0]}')
else: 
    create_webhook(ngrok_url, "messages")
    logger.warning("There is no webhook for messages yet. Create a new one")

if intersect_att:
    logger.debug(f'Registered webhook for Att: {intersect_att[0]}')
else: 
    create_webhook(ngrok_url, "attachmentActions")
    logger.warning("There is no webhook for cards yet. Create a new one")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True)
