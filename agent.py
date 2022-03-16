from flask import Flask,request,make_response
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from utils import AgentUtils
import os
from functools import wraps
import yaml

app = Flask(__name__)
AgentUtils.load_service()

@app.route("/command/restart",methods=["POST"])
def restart():
    AgentUtils.ELASTICSEARCH_SERVICE.Restart("replace")
    return "Executed", 200

@app.route("/command/configuration",methods=["POST"])
@AgentUtils.token_check
def config() -> tuple:
    try:
        with open(os.getenv("FILEPATH"),"w",encoding="UTF-8") as file:
            res:dict = request.get_json().get("data")
            yaml.dump(res,file) #put res into file 
            return "Executed",200 #Status Code 200
    except Exception as e:
        return "Failed",400


