
import json
import os
from jinja2 import Template


DIR = os.path.dirname(os.path.abspath(__file__))    

iconURL="https://community.cisco.com/legacyfs/online/fusion/117586_DNA%20Center%20Graphic.png"
mainTitle="DNA Demo"

class Card():
    def __init__(self):
        self.iconURL=iconURL
        self.mainTitle=mainTitle
        
    def _createCardFile(self, cardFullId, cardTemplateFile, variables):
                 
        cardFullName="card_" + cardFullId + ".json"
        
        fileName_wpath=os.path.join(DIR,f"Cards/{cardFullName}")

        with open(fileName_wpath, "w") as tf:
            jsonString=self._cardJSONFromVariables(cardTemplateFile,variables)
            tf.write(json.dumps(jsonString,indent=4))
        


    def _cardJSONFromVariables(self, cardFileName, variables=None):

        fileName_wpath=os.path.join(DIR,f"Cards/templates/{cardFileName}")
        
        with open(fileName_wpath) as fp:
            text = fp.read()
        
        if variables:
            t = Template(text)
            r= t.render(variables)

            return json.loads(r)
        else:
            return json.loads(text)
    
    def display(self):
        return self.cardType+"_"+self.cardIdName

class CardInput(Card):
    def __init__(self, subTitle, options, cardIdName):
        super().__init__()
        self.subTitle=subTitle
        self.options=options
        self.cardIdName=cardIdName
        self.cardType="input"
        self.cardFullId=self.cardType + "_" + cardIdName
        self.variables={"iconURL": self.iconURL, "mainTitle": self.mainTitle, \
                "subTitle": self.subTitle, \
                "toggle_choiceset": self.options, \
                "card_name": self.cardFullId  }
        self.cardTemplateFile="card_inputChoiceSet_template.json"
        self._createCardFile(self.cardFullId, self.cardTemplateFile, self.variables)
        


class CardToggle(Card):
    def __init__(self, subTitle, options, cardIdName):
        super().__init__()
        self.subTitle=subTitle
        self.options=options
        self.cardIdName=cardIdName
        self.cardType="toggle"
        self.cardFullId=self.cardType + "_" + cardIdName
        self.variables={"iconURL": self.iconURL, "mainTitle": self.mainTitle, \
                "subTitle": self.subTitle, \
                "toggle_choiceset": self.options, \
                "card_name": self.cardFullId  }
        self.cardTemplateFile="card_toggle_template.json"
        self._createCardFile(self.cardFullId, self.cardTemplateFile, self.variables)
        


class CardMain(Card):
    def __init__(self, subTitle, options, cardIdName):
        super().__init__()
        self.subTitle=subTitle
        self.options=options
        self.cardIdName=cardIdName
        self.cardType="main"
        self.cardFullId=self.cardType + "_" + cardIdName
        self.variables={"iconURL": self.iconURL, "mainTitle": self.mainTitle, \
                "subTitle": self.subTitle, \
                "toggle_choiceset": self.options }
        self.cardTemplateFile="card_mainmenu_template.json"
        self._createCardFile(self.cardFullId, self.cardTemplateFile, self.variables)
        

class CardOutput(Card):
    def __init__(self, cardIdName):
        super().__init__()
        self.cardIdName=cardIdName
        self.cardType="output"
        self.cardFullId=self.cardType + "_" + cardIdName
        self.variables={"iconURL": self.iconURL, "mainTitle": self.mainTitle, \
                "var1": "{{ var1 }}", "var2": "{{ var2 }}", \
                "colour1": "{{ colour1 }}","colour2": "{{ colour2 }}","colour3": "{{ colour3 }}" }
        self.cardTemplateFile="card_output_generic_template.json"
        self._createCardFile(self.cardFullId, self.cardTemplateFile, self.variables)
        
