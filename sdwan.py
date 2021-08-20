import os
import requests




# To stop the warrnings when doing get/post to https
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings()


# Define vmanage host, port, user, pass as eviromental variable
#export vmanage_host=IP/FQDN
#export vmanage_port=port
#export vmanage_username=username
#export vmanage_password=password

vmanage_host = os.environ.get("vmanage_host")
vmanage_port = os.environ.get("vmanage_port")
vmanage_username = os.environ.get("vmanage_username")
vmanage_password = os.environ.get("vmanage_password")

base_url = f"https://{vmanage_host}:{vmanage_port}"

url_logout = base_url + "/logout?nocache=1234"


class Sdwan():
    def __init__(self, base_url=base_url, url_logout=url_logout, vmanage_host=vmanage_host, vmanage_port=vmanage_port, vmanage_username=vmanage_username, vmanage_password=vmanage_password):
        self.base_url = base_url
        self.url_logout=url_logout

        if vmanage_host is None or vmanage_port is None or vmanage_username is None or vmanage_password is None:
            print("some envs are missing. it is mandatory to set those env before running the app")
            exit()

        self.vmanage_host= vmanage_host
        self.vmanage_port=vmanage_port
        self.vmanage_username=vmanage_username
        self.vmanage_password=vmanage_password

        self.sessionid = self.get_jsessionid()
        self.token = self.get_token()
        if self.token is not None:
            self.header = {'Content-Type': "application/json",'Cookie': self.sessionid, 'X-XSRF-TOKEN': self.token}
        else:
            self.header = {'Content-Type': "application/json",'Cookie': self.sessionid}
        print("pripremio header/ulogovao se")
        
    # Try to get cookie
    def get_jsessionid(self):
        api = "/j_security_check"
        url = self.base_url + api
        
        payload = {'j_username' : self.vmanage_username, 'j_password' : self.vmanage_password}
        
        response = requests.post(url=url, data=payload, verify=False)

        try:
            cookies = response.headers["Set-Cookie"]
            jsessionid = cookies.split(";")
            return(jsessionid[0])
        except:
            print("No valid JSESSION ID returned")
            exit()
    
    # Try to get token
    def get_token(self):
        api = "/dataservice/client/token"
        url = self.base_url + api      
        
        headers = {'Cookie': self.sessionid}

        response = requests.get(url=url, headers=headers, verify=False)
        
        if response.status_code == 200:
            return(response.text)
        else:
            return None


    def show_users(self):
        #random GET API for users list 

        url = self.base_url + "/dataservice/admin/user"
        s=""

        response = requests.get(url=url, headers=self.header,verify=False)
        if response.status_code == 200:
            items = response.json()['data']
        else:
            s= f"Failed to get list of users {str(response.text)}"
            return s


        for item in items:
            s=s+f"- Username: {item.get('userName')} \\n Group: {item.get('group')} \\n Description: {item.get('description')}\\n\\n"
    
        return s

    def show_devices(self):
        #random GET API for device list 

        url = self.base_url + "/dataservice/device"
        s=""

        response = requests.get(url=url, headers=self.header,verify=False)
        if response.status_code == 200:
            items = response.json()['data']
        else:
            s= f"Failed to get list of devices {str(response.text)}"
            return s


        for item in items:
            s=s+f"- Device ID: {item.get('deviceId')}\\n"
    
        return s    


    def show_controllers(self):
        #random GET API for controller list 

        url = self.base_url + "/dataservice/system/device/controllers"
        s=""

        response = requests.get(url=url, headers=self.header,verify=False)
        if response.status_code == 200:
            items = response.json()['data']
        else:
            s= f"Failed to get list of controllers {str(response.text)}"
            return s


        for item in items:
            s=s+f"- Controller: {item.get('deviceType')}\\n"
        
        return s 

    def show_vedges(self):
        #random GET API for vEdges list 

        url = self.base_url + "/dataservice/system/device/vedges"
        s=""

        response = requests.get(url=url, headers=self.header,verify=False)
        if response.status_code == 200:
            items = response.json()['data']
        else:
            s= f"Failed to get list of vEdges {str(response.text)}"
            return s

        for item in items:
            s=s+f"vEdge: {item.get('serialNumber')}\\n"
        
        return s

    def show_bfd(self, deviceId):
        #random GET API for BFD  

        url = self.base_url + f"/dataservice/device/bfd/sessions?deviceId={deviceId}"
        s=""

        response = requests.get(url=url, headers=self.header,verify=False)
        if response.status_code == 200:
            items = response.json()['data']
        else:
            s= f"Failed to get BFD sessions {str(response.text)}"
            return s

        for item in items:
            s=s+f"BFD session: {item}\\n"
        
        return s

    def show_ipsec(self,deviceId):
        #random GET API for IPSEC  

        url = self.base_url + f"/dataservice/device/ipsec/outbound?deviceId={deviceId}"
        s=""

        response = requests.get(url=url, headers=self.header,verify=False)
        if response.status_code == 200:
            items = response.json()['data']
        else:
            s= f"Failed to get ipsec sessions {str(response.text)}"
            return s

        for item in items:
            s=s+f"IPSEC session: {item}\\n"
        
        return s

    def logout(self):
        # Logout
        requests.get(url=self.url_logout, headers=self.header, verify=False,allow_redirects=False)
        print("izlogovao se")