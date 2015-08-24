"""
Author : Mohit Jain
RollNo : 201202164
"""

from flask import request, jsonify
from flask.ext.api import FlaskAPI
import random
import string

app = FlaskAPI(__name__)

@app.route("/", methods=['GET'])
def homepage():
    return "Cloud Orchestration Layer"

@app.route("/id", methods=['GET'])
def create_id(size=8, chars=string.ascii_uppercase+string.digits):
    return ''.join(random.choice(chars) for x in range(size))

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
