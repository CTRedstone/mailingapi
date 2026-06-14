from flask import Flask, request, jsonify, redirect, url_for, make_response, send_from_directory, send_file, after_this_request
from copy import deepcopy as dc
from json import load as jsload, dump as jsdump, dumps as jsdumpstr, loads as jsloadstr
from werkzeug.utils import secure_filename
import os
import smtplib
from email.mime.text import MIMEText

def log(msg): print(msg.upper())

ret = lambda value,_type,msg: {"value":"succeeded" if value == True else "failed","type":_type.lower(),"detail":msg}

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
        sslport = 465
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

    log("Trying to send email")
    try:
        with smtplib.SMTP_SSL(serv,sslport) as svr:
            svr.login(sendaddr,sendpwd)
            svr.sendmail(sendaddr,[toaddr],msg.as_string())
    except Exception as exc:
        print(f"ERROR WHILE SENDING MAIL ({exc})")
        return ret(False,"error",f"Could not send mail: {exc}")
    log("Send EMail successfully")
    return ret(True,"ok","Email sent")

@app.route("/")
def homepage():
    with open("homepage.html","r") as fle: return ''.join(fle.readlines())

if __name__ == "__main__":
    log("Starting flask application")
    app.run(host="0.0.0.0")
