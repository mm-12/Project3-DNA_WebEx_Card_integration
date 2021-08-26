import os
import requests
import json



# To stop the warrnings when doing get/post to https
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings()


# Define dna host, user, pass as eviromental variable
#export dna_host = IP/FQDN
#export dna_username = username
#export dna_password = password

dna_host = os.environ.get("dna_host")
dna_username = os.environ.get("dna_username")
dna_password = os.environ.get("dna_password")

base_url = f"https://{dna_host}"



class Dna():
    def __init__(self, base_url=base_url, dna_host=dna_host, dna_username=dna_username, dna_password=dna_password):
        self.base_url = base_url

        if dna_host is None or dna_username is None or dna_password is None:
            print("some envs are missing. it is mandatory to set those env before running the app")
            exit()

        self.dna_host = dna_host
        self.dna_username = dna_username
        self.dna_password = dna_password

        self.token = self.get_token()
        
        if self.token is not None:
            self.header={"X-Auth-Token": self.token, "Content-type": "application/json"}
        else:
            print("issues with logging it. Run the app again")
            exit()

        print("pripremio header/ulogovao se")
            
    # Try to get token
    def get_token(self):
        api = "/dna/system/api/v1/auth/token"
        url = self.base_url + api      
        
        headers = {"content-type": "application/json"}
        

        response = requests.post(url=url,auth=(self.dna_username,self.dna_password),headers=headers,verify=False)
    

        if response.status_code == 200:
            return response.json()["Token"]
        else:
            print(response.status_code, response)
            return None


    def show_devices(self):
        # Get device list 

        url = self.base_url + "/dna/intent/api/v1/network-device"
        s = ""

        response = requests.get(url=url, headers=self.header,verify=False)
        
        if response.status_code == 200:
            items = response.json()["response"]
        else:
            s = f"Failed to get list of devices {str(response.text)}"
            return s


        for item in items:
            s = s + f"- **Device ID:** {item.get('id')} \\n Hosname: {item.get('hostname')} \\n IP address: {item.get('managementIpAddress')}\\n\\n"
        return s , "show devices\n" + json.dumps(items,indent=4)

    
    def show_site_health(self):
        # Get site health

        url = self.base_url + "/dna/intent/api/v1/site-health"
        s = ""

        response = requests.get(url=url, headers=self.header,verify=False)
        
        if response.status_code == 200:
            items = response.json()["response"]
        else:
            s = f"Failed to get site health {str(response.text)}"
            return s

        for item in items:
            s = s + f"- **Site:** {item.get('siteName')} \\n Health: {item.get('networkHealthAverage')}\\n\\n"
        return s, "show site health\n" + json.dumps(items,indent=4)

    
    def show_network_health(self):
        # Get network health

        url = self.base_url + "/dna/intent/api/v1/network-health"
        s = ""

        response = requests.get(url=url, headers=self.header,verify=False)
        
        if response.status_code == 200:
            items = response.json()["response"]
        else:
            s = f"Failed to get network health {str(response.text)}"
            return s
        
        s = s + f"- **Good:** {items[0].get('goodCount')} \\n Bad: {items[0].get('badCount')} \\n Health score: {items[0].get('healthScore')}\\n\\n"
        
        return s, "show network health\n" + json.dumps(items[0],indent=4)

    
    def show_client_health(self):
        # Get client health

        url = self.base_url + "/dna/intent/api/v1/client-health"
        s = ""

        response = requests.get(url=url, headers=self.header,verify=False)
        
        if response.status_code == 200:
            items = response.json()["response"]
        else:
            s = f"Failed to get client health {str(response.text)}"
            return s
        
        for item in items[0].get('scoreDetail'):
            s = s + f"- **Type:** {item.get('scoreCategory').get('value')} \\n Count: {item.get('clientCount')} \\n Score: {item.get('scoreValue')}\\n\\n"
            
            try:
                for category in item.get('scoreList'):
                    s = s + f"\\t- Type: {category.get('scoreCategory').get('value')} \\n \\t Count: {category.get('clientCount')}\\n"
            except:
                pass
        
        return s, "show client health\n" + json.dumps(items[0].get('scoreDetail'),indent=4)

    def commands(self, commands):
        # Get command
        commands_formatted=[]

        for c in commands:
            command_formatted = c.replace("_"," ")
            commands_formatted.append(command_formatted)

        url = self.base_url + "/dna/intent/api/v1/network-device-poller/cli/read-request"
        
        param = {
        "name": "Commands",
        "commands": commands_formatted,
        "deviceUuids": ["f16955ae-c349-47e9-8e8f-9b62104ab604"]
        }
        
        response = requests.post(url=url, data=json.dumps(param),headers=self.header,verify=False)
        
        if response.status_code == 200 or response.status_code == 202:
            task_id = response.json()['response']['taskId']
        else:
            s = f"Failed to get cmd {str(response.text)}"
            return s
        
        return self._get_task_info(task_id, commands_formatted)

    def _get_task_info(self,task_id, commands_formatted):
        
        url = self.base_url + f"/api/v1/task/{task_id}"
        
        result = requests.get(url, headers=self.header)
        file_id = result.json()['response']['progress']
        
        if "fileId" in file_id:
            file_id=json.loads(file_id)["fileId"]
        else:  # keep checking for task completion
            self._get_task_info(task_id)
        
        return self._get_cmd_output(file_id, commands_formatted)
    
    def _get_cmd_output(self,file_id, commands_formatted):

        url = self.base_url + f"/api/v1/file/{file_id}"

        result = requests.get(url, headers=self.header)
        s=""
        print ("-----> ", result.json()[0]["commandResponses"])
        for i in commands_formatted:
            s = s+ \
                result.json()[0]["commandResponses"]["SUCCESS"].get(i,"") + \
                result.json()[0]["commandResponses"]["FAILURE"].get(i,"") + \
                result.json()[0]["commandResponses"]["BLACKLISTED"].get(i,"") + \
                "\n\n"

        return s


   
