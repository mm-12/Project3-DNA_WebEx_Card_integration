import json
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder



# API Key is obtained from the Webex Teams developers website.
api_key = 'NmVkYzY3ZmEtYmIwYi00MGEwLWI5YmEtNzQ3ZmQyZTFlNjFlMTRkMjA4MjEtOTBj_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f'
# Webex Teams messages API endpoint
base_url = 'https://webexapis.com/v1'

class Messenger():
    # When init Messanger class prepare url, key, headers, bot_id
    def __init__(self, base_url=base_url, api_key=api_key):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.bot_id = requests.get(f'{self.base_url}/people/me', headers=self.headers).json().get('id')



    # RETRIVE A MESSAGE
    # Retrieve a specific message posted by user -> str, using message_id
    def get_txt_message(self, message_id): 
        received_message_url = f'{self.base_url}/messages/{message_id}'

        self.message_structure = requests.get(received_message_url, headers=self.headers).json().get('text')

    # Retrieve a specific card submitted by  user -> dict, using message_id
    def get_card_message(self, message_id):
        received_message_url = f'{self.base_url}/attachment/actions/{message_id}'
        self.message_structure =requests.get(received_message_url, headers=self.headers).json().get('inputs')
      
    
    # POST A MESSAGE
    # Post a message to a Webex Teams space (to email address send a message)
    def post_message_email(self, person_email, message):
        data = {
            "toPersonEmail": person_email,
            "text": message,
            }
        post_message_url = f'{self.base_url}/messages'
        requests.post(post_message_url,headers=self.headers,data=json.dumps(data))

    # Post a message to a Webex Teams space (to roomId send a message)
    def post_message_roomId(self, room_id, message):
        data = {
            "roomId": room_id,
            "text": message,
            } 
        post_message_url = f'{self.base_url}/messages'
        requests.post(post_message_url,headers=self.headers,data=json.dumps(data))

    def post_message_roomId_file(self, room_id, parent_id, message, file_path, file):
      
        post_message_url = f'{self.base_url}/messages'

        m = MultipartEncoder({'roomId': room_id,
                      'parentId': parent_id,
                      'text': message,
                      'files': (file, open(file_path, 'rb'),
                      'text/plain')})
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type" : m.content_type
        }

        requests.post(post_message_url,headers=headers,data=m)
        

    # Post a card to a Webex Teams space (to roomID)
    def post_message_card(self, room_id, message, card):
        data = {
            "roomId": room_id,
            "text": message,
            "attachments": card
            } 
        post_message_url = f'{self.base_url}/messages'
        response = requests.post(post_message_url,headers=self.headers,data=json.dumps(data))
        
        self.messageParentId = response.json().get("id")


    def _get_webhook_urls(self):
        webhook_urls_res = []
        webhooks_api = f'{self.base_url}/webhooks'
        webhooks = requests.get(webhooks_api, headers=self.headers)
        if webhooks.status_code != 200:
                webhooks.raise_for_status()
        else:
            for webhook in webhooks.json()['items']:
                webhook_urls_res.append((webhook['targetUrl'],webhook['resource']))
        return webhook_urls_res      

    def _create_webhook(self,targetUrl,resource):
        webhooks_api = f'{self.base_url}/webhooks'
        data = { 
            "name": f"Webhook to ChatBot - {resource}",
            "resource": resource,
            "event": "created",
            "targetUrl": f"{targetUrl}"
            }
        webhook = requests.post(webhooks_api, headers=self.headers, data=json.dumps(data))
        
        if webhook.status_code != 200:
            webhook.raise_for_status()

    def registerWebhook(self, ngrok_url):

        ngrok_url_msg=[(ngrok_url,"messages")]
        ngrok_url_att=[(ngrok_url,"attachmentActions")]

        webhook_urls = self._get_webhook_urls()

        intersect_msg = list(set(ngrok_url_msg) & set(webhook_urls))
        intersect_att = list(set(ngrok_url_att) & set(webhook_urls))

        if not intersect_msg:
            self._create_webhook(ngrok_url, "messages")
            
        if not intersect_att:
            self._create_webhook(ngrok_url, "attachmentActions")
    
    
                



            