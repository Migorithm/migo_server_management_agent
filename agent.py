from flask import Flask,request
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from utils import AgentUtils
import os


app = Flask(__name__)
AgentUtils.load_service()

@app.route("/command/restart",methods=["POST"])
def restart():
    #confirmation
    if request.method =="POST":
        #On the other side, it will post things in the following form
        # requests.post("http://nodeip:port/command/restart",json={"token":token})
        byte_token = request.get_json()["token"]
        token = AgentUtils.token_loader(byte_token)
        if token.get("confirm"):
            print(AgentUtils.ELASTICSEARCH_SERVICE.ActiveState)
            
