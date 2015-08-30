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
import werkzeug.exceptions
import os

from ConfigFiles import *

######################################################################################################
# Global Variables.
######################################################################################################

VM_IMAGES = {} # Stores all the VM images given as input.
PM_ADDRS = {}  # Stores the IPs of all available Physical Machines

######################################################################################################
# Flask Application Initializer.
######################################################################################################

app = FlaskAPI(__name__)

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
                    "List Physical Machines" : "http://localhost:5000/pm/list",
                    "Create VM" : "http://localhost:5000/vm/create?name=<vm-name>&instance_type=<type-id>&image_id=<image-id>",
                    "List Images" : "http://localhost:5000/image/list"
                }
        }
    ]
    return homeString

######################################################################################################
# Virtual Machine CRUD functions.
######################################################################################################

@app.route("/vm/create", methods=['GET','POST'])
def VMCreate():
    """
    Creates a new Virtual Machine of the requested type.
    """
    config_vars = request.args
    try: 
        vm_name = str(config_vars['name'])
        vm_typeid = int(config_vars['instance_type'])
        vm_imageid = str(config_vars['image_id'])
    except:
        raise werkzeug.exceptions.BadRequest('[ERROR] : Check the parameters sent. Name/InstanceId/ImageID not found.')

    vm_type_details = GetVMTypeDetails(vm_typeid)

    vm_cpu = vm_type_details['cpu']
    vm_ram = vm_type_details['ram']
    vm_disk = vm_type_details['disk']

    for vm_id in VM_IMAGES:
        if vm_id == vm_imageid:
            vm_imagepath = VM_IMAGES[vm_id]['path']

    alloted_pm_id = Scheduler(vm_cpu, vm_ram, vm_disk)

    TransferImage(alloted_pm_id, vm_imagepath)

    out = [vm_name, vm_typeid, vm_imageid, vm_cpu, vm_ram, vm_disk, vm_imagepath, PM_ADDRS[alloted_pm_id]]
    return out

@app.route("/vm/types", methods=['GET'])
def VMTypes():
    """
    Returns the types of VMs available.
    """
    return vm_types

@app.route("/pm/list", methods=['GET'])
def ListPM():
    """
    Returns all available Physical Machines.
    """
    return PM_ADDRS

@app.route("/image/list", methods=['GET'])
def ListImages():
    """
    Returns all available OS Images with their respective IDs.
    """
    return VM_IMAGES

######################################################################################################
# Virtual Machine CRUD-helper functions.
######################################################################################################

def Scheduler(cpu, ram, disk):
    """
    Returns a physical machine ID based on the cpu, ram and disk space required.
    """
    alloted = 0
    while not alloted:
        pm_id = random.choice(list(PM_ADDRS.keys()))
        os.system(" ssh " + PM_ADDRS[pm_id]['ip'] +" uname >> temp/os_type")

        with open('temp/os_type') as f:
            os_type = f.readline().strip()
            #----- Mac OS --------#
            if os_type == 'Darwin':
                os.system(" ssh " + PM_ADDRS[pm_id]['ip'] +" sysctl hw.memsize | awk '{ print $2 }' >> temp/pm_data")
                os.system(" ssh " + PM_ADDRS[pm_id]['ip'] +" sysctl hw.ncpu | awk '{ print $2 }' >> temp/pm_data")
            #----- GNU/Linux -----#    
            else:
                os.system(" ssh " + PM_list[pms] +" free -k | grep 'Mem:' | awk '{ print $4 }' >> data")
                os.system(" ssh " + PM_list[pms] +" grep processor /proc/cpuinfo | wc -l >> data")

        with open('temp/pm_data') as f:
            pm_ram = f.readline().strip()
            pm_cpu = f.readline().strip()
            print "RAM : %s, CPU : %s" % (pm_ram, pm_cpu)
            os.system("rm -rf temp/*")
            if int(pm_cpu) >= int(cpu):
                if int(pm_ram) >= int(ram):
                    alloted = 1
                    alloted_pm_id = pm_id

    return alloted_pm_id

def TransferImage(pm_id, image_path):
    """
    Copies the Image file to the client machine if host and client are not same.
    """
    # --- Client and Host are same --- #
    if PM_ADDRS[pm_id]['ip'] == image_path.split(':')[0]:
        return

    os.system('scp '+image_path+' '+PM_ADDRS[pm_id]['ip']+'~/')
    return

def GetVMTypeDetails(typeid=None):
    """
    Returns the CPU, RAM and DISK allocations for a specific typeid.
    """
    types_list = [vm['tid'] for vm in vm_types['types']]
    if typeid in types_list:
        return vm_types['types'][types_list.index(typeid)]
    else:
        raise werkzeug.exceptions.NotFound('[ERROR] : instance_type not found. Please check instances at /vm/types')

######################################################################################################
# Initializer functions.
######################################################################################################

def LoadImagesFromFile(filename=None):
    """
    Loads Images from input Image File and stores them in Global Dictionary : VM_IMAGES
    """
    if not os.path.isfile(filename):
        print "[ERROR] File does not exist : %s" % filename
        return 1

    global VM_IMAGES
    with open(filename, 'r') as f:
        for line in f.readlines():
            try:
                image_path = line.strip()
                image_name = image_path.split(':')[-1].split('/')[-1]

                vm_id = CreateUID()
                VM_IMAGES[vm_id] = {'name': image_name, 'path': image_path}
                print "[SUCCESS] : loading %s from %s" % (image_name, image_path)
            except:
                print "[FAILED] : loading %s" % (line)
                return 1

    return 0

def GetPhysicalMachines(filename=None):
    """
    Stores the list of Physical Machines from pm_file to the Global Dictionary : PM_ADDRS
    """
    if not os.path.isfile(filename):
        print "[ERROR] File does not exist : %s " % filename
        return 1

    global PM_ADDRS
    with open(filename, 'r') as f:
        for line in f.readlines():
            try:
                PM_ADDRS[CreateUID()] = {'ip': (line.strip())}
                print "[SUCCESS] : storing machine %s" % line.strip()
            except:
                print "[FAILED] : storing machine %s" % line.strip()
                return 1

    return 0


######################################################################################################
# Initializer-Helper functions.
######################################################################################################

def CreateUID(size=7, chars=string.ascii_uppercase + string.digits):
    """
    Creates a string unique_id of length 'size' and type 'chars'.
    """
    return ''.join(random.choice(chars) for x in range(size))

######################################################################################################
# Initializer statements.
######################################################################################################

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "[ERROR] : Incorrect input parameters.\nUsage : $> python server.py pm_file image_file"
    else:
        print "######################################################################################"
        print "                                         Welcome                                      "
        print "######################################################################################\n"
        
        print "Args List : %s\n" % (sys.argv)

        status_fl =0

        # ------- Store Machines from pm_file -------- #    
        print "Fetching available Physical Machines..."
        status_fl = GetPhysicalMachines(sys.argv[1])
        if status_fl == 0:
            print "Physical Machines stored successfully!\n"
        else:
            print "Failed to store Physical Machines.\n"

        # ------- Load Images from image_file -------- #
        print "Loading OS Images from Image File..."
        status_fl = LoadImagesFromFile(sys.argv[2])
        if status_fl==0 :
            print "Images loaded successfully!\n"
        else:
            print "Failed to load Images.\n"

        # ------- Creating temp folder -------- #
        if not os.path.isdir("temp"):
            os.mkdir("temp")
            print "Creating 'temp' folder for server manipulations...\n"

        # ------- Start the Flask Server -------- #
        if status_fl == 0:
            app.run(host='0.0.0.0', debug=True)
        else:
            print "[ERROR] : Failed to load server!"