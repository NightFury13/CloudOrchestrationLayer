"""
Author : Mohit Jain
RollNo : 201202164
"""

from flask import request, jsonify
from flask.ext.api import FlaskAPI
import random
import string
import sys

from ConfigFiles import *

app = FlaskAPI(__name__)

@app.route("/", methods=['GET'])
def homepage():
    homeString = {}
    homeString["Cloud Orchestration Layer"] = [
        {
            "Author" : "Mohit Jain", 
            "ver" : "1.0", 
            "Options" : 
                {
                    "List VM Types" : "http://localhost:5000/vm/types",
                    "List Physical Machines" : "http://localhost:5000/pm/list"
                }
        }
    ]
    return homeString


@app.route("/id", methods=['GET'])
def create_id(size=8, chars=string.ascii_uppercase+string.digits):
    return ''.join(random.choice(chars) for x in range(size))

@app.route("/vm/types", methods=['GET'])
def VMTypes():
    return vm_types

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "[ERROR] : Incorrect input parameters.\nUsage : $> python server.py pm_file image_file"
    else:
        print "Args List :", sys.argv
        app.run(host='0.0.0.0', debug=True)
