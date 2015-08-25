"""
Cloud Orchestration Layer

Author : Mohit Jain
RollNo : 201202164
"""

######################################################################################################
# Requirements import.
######################################################################################################
from flask import request, jsonify
from flask.ext.api import FlaskAPI
from flask.ext.pymongo import PyMongo
import subprocess
import random
import string
import sys

from ConfigFiles import *

######################################################################################################
# Flask Application Initializer.
######################################################################################################
app = FlaskAPI(__name__)
app.config.from_object(mongo_config)
try:
    mongo = PyMongo(app)
except:
    print "Running MongoDB requires superuser access."
    p = subprocess.Popen(['sudo', 'mkdir', '-p', '/data/db'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, errors = p.communicate()
    print "Creating /data/db directory to execute MongoDB connection...\n%s" % output
    p = subprocess.Popen(['sudo', 'mongod'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, errors = p.communicate()
    print "MongoDB server running successfully..."
    mongo = PyMongo(app)

######################################################################################################
# Homepage.
######################################################################################################

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
    return jsonify(homeString)

######################################################################################################
# Virtual Machine CRUD functions.
######################################################################################################

@app.route("/vm/create", methods=['GET','POST'])
def VMCreate():
    return

@app.route("/vm/types", methods=['GET'])
def VMTypes():
    return jsonify(vm_types)

######################################################################################################
# Initializer statements.
######################################################################################################

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "[ERROR] : Incorrect input parameters.\nUsage : $> python server.py pm_file image_file"
    else:
        print "Args List :", sys.argv
        app.run(host='0.0.0.0', debug=True)
