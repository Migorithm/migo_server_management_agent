from flask import Flask,request,jsonify
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from utils import AgentUtils
import os
import yaml
import time



app = Flask(__name__)
AgentUtils.load_service()

@app.route("/es/command/restart",methods=["POST"])
def es_restart():
    AgentUtils.ELASTICSEARCH_SERVICE.Restart("replace")
    return "Executed", 200


@app.route("/es/command/configuration",methods=["POST"])
@AgentUtils.token_check
def es_config() -> tuple:
    try:
        with open(os.getenv("FILEPATH"),"w",encoding="UTF-8") as file:
            res:dict = request.get_json().get("data")
            yaml.dump(res,file) #put res into file 
            return "Executed",200 #Status Code 200
    except Exception as e:
        return "Failed",400


@app.route('/redis/command/restart', methods=["POST"])
@AgentUtils.token_check
def redis_restart():
    port= str(request.get_json().get("port")) #In case we have a couple of redis nodes
    for attr in AgentUtils.__dict__:
        if port in attr:
            service = AgentUtils.__dict__.get(attr)
            break
    else:
        return "Failed",400
    service.Restart("replace")
    while service.ActiveState != b"active":
        AgentUtils.log("Current status of service - "+ service.ActiveState.decode("utf-8"))
        print(service.ActiveState)
        time.sleep(3)
    AgentUtils.log("Service turned active")
    return "Executed", 200

@app.route("/redis/command/get_config",methods=["POST"])
@AgentUtils.token_check
def redis_get_config():
    port= request.get_json().get("port")
    data = AgentUtils.redis_config(port)
    if data:
        return jsonify(dict(AgentUtils.redis_config(port)))
    else:
        return "Failed", 400
    

@app.route("/redis/command/set_config",methods=["POST"])
@AgentUtils.token_check
def redis_set_config():
    port= request.get_json().get("port")
    data= request.get_json().get("data")
    with open(f"/etc/redis/redis_{port}.conf","w") as file:
        for k,v in data.items():
            line= " ".join((k,v)) + "\n"
            file.write(line)
    return "Executed", 200