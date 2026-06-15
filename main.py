from flask import Flask, request, jsonify, redirect, url_for, make_response, send_from_directory, send_file, after_this_request
from copy import deepcopy as dc
from json import load as jsload, dump as jsdump, dumps as jsdumpstr, loads as jsloadstr
from werkzeug.utils import secure_filename
import os
import smtplib
from email.mime.text import MIMEText
import socket

def log(msg): print(msg.upper())

ret = lambda value,_type,msg: {"value":"succeeded" if value == True else "failed","type":_type.lower(),"detail":msg}

def testConnection(ip:str,port:int):
    try:
        addr = socket.gethostbyname(ip)
        log(f"DNS address of {ip} could be resolved to {addr}")
    except: return None
    try: socket.create_connection((ip,port),timeout=5)
    except: return False
    return True

log("Creating FLask Instance")
app = Flask(__name__)

log("Creating service routes")
@app.route("/api/sendmail",methods=["POST"])
def sendmail():
    global ret
    req = request.get_json()
    if req == None: return ret(False,"error","Request did not contain any JSON data")

    # configuration variables
    try:
        serv = req["smtp_server"]
        if "smtp_port" in list(req.keys()):
            if type(req["smtp_port"]) == int: sslport = req["smtp_port"]
            elif type(req["smtp_port"]) == str:
                ports = {"ssl":"465","tls":"587"}
                try: sslport = ports[req["smtp_port"].lower()]
                except KeyError: return ret(False,"error",f"Invailid type of SMTP port selected: {repr(req['smtp_port'])}")
            else: return ret(False,"error","Unknown datatype for SMTP port")
        else: sslport = 465
        sendaddr = req["from_email"]
        sendpwd = req["from_password"]
        toaddr = req["to_email"]
        subject = req["subject"]
        content = req["content"]
    except KeyError as exc: return ret(False,"error",f"Missing JSON data for {repr(exc)}")

    msg = MIMEText(content,"html")
    msg["Subject"] = subject
    msg["From"] = sendaddr
    msg["To"] = toaddr

    log("Testing connection to E-Mail SMTP provider")
    testresult = testConnection(serv,sslport)
    if testresult == False:
        print("Connection timed out")
        return ret(False,"error","SMTP server port for SSL access is not reachable")
    elif testresult == None:
        print("Could not resolve hostname")
        return ret(False,"error","DNS address of server could not be found")
    print("Serverport for SMTP SSL access was reachable")

    log("Trying to send email")
    try:
        if sslport == 465: # for SSL communication
            with smtplib.SMTP_SSL(serv,sslport) as svr:
                svr.login(sendaddr,sendpwd)
                svr.sendmail(sendaddr,[toaddr],msg.as_string())
        else: # for TLS communication, normally port 587
            with smtplib.SMTP(serv,sslport) as svr:
                svr.starttls()
                svr.login(sendaddr,sendpwd)
                svr.sendmail(sendaddr,[toaddr],msg.as_string())
    except Exception as exc:
        print(f"ERROR WHILE SENDING MAIL ({exc})")
        return ret(False,"error",f"Could not send mail: {exc}")
    log("Send EMail successfully")
    return ret(True,"ok","Email sent")

@app.route("/")
def homepage():
    with open("./homepage.html","r") as fle: return ''.join(fle.readlines())

if __name__ == "__main__":
    log("Starting flask application")
    app.run(host="0.0.0.0")
