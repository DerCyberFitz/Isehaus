#!/usr/bin/env python

###########################################################################
#                                                                         #
# This script demonstrates how to use the ISE ERS API to verify           #
# reachability of network devices by executing a Python script.           #
# The script is configured to use TLS v1.2 and assumes a Windows OS.      #
# It can easily be modified for another environment.                      #
#                                                                         #
# Usage:                                                                  #
# python ping_all_net_devices.py <ISE host> <user> <password> <command>   #
#                                                                         #
###########################################################################

import base64
import http.client
import json
import platform
import os
import ssl
import subprocess
import sys

def deleteObject(devType,id):
    conn.request("DELETE", "/ers/config/" + devType + '/' + id, headers=headers)
    res_d = conn.getresponse()
    data_d = res_d.read()
    status = json.loads(data)
    return status
    
def pingStat(device,ip, resource_id):
    response = os.popen(f"ping {ip}").read()
    #print(response)
    if "TTL Expired in transit" in response:
        string = resource_id + '\t' + device + '\t' + ip + '\n'
        downFile.write(string)
        return("TTL Expired") 
    elif "Received = 4" in response:
        return "UP 4/4"
    elif "Received = 3" in response:
        return "Up 3/4"
    elif "Received = 2" in response:
        return "Marginal 2/4"
    elif "Recieved = 1" in response:
        return "Marginal 1/4"
    else:
        string = resource_id + '\t' + device + '\t' + ip + '\n'
        downFile.write(string)
#        x = deleteObject('networkdevice',resource_id)
#        print(x)
        return("DOWN 0/4")


downFile = open('isedown-2-6.txt', 'w') #open output file

#host and authentication credentials
host = sys.argv[1] 
user = sys.argv[2] 
password = sys.argv[3]
#command = sys.argv[4] !future use


# we require TLS v1.2.  YMMV
conn = http.client.HTTPSConnection("{}:9060".format(host), context=ssl.SSLContext(ssl.PROTOCOL_TLSv1_2))
creds = str.encode(':'.join((user, password)))
encodedAuth = bytes.decode(base64.b64encode(creds))

headers = {
    'accept': "application/json",
    'authorization': " ".join(("Basic",encodedAuth)),
    'Content-Type': 'application/json',
    'cache-control': "no-cache"
    }
device_list = [] # This dict will contain the entire inventory of Network Devices

#get initial page, assuming more than one page of devices
conn.request("GET", "/ers/config/networkdevice/", headers=headers)
res = conn.getresponse()
data = res.read()
devices = json.loads(data)

#print("Status: {}".format(res.status))
#print("\nHeader:\n{}".format(res.headers))
#print("Body:\n{}".format(data.decode("utf-8")))

#the first page 'SearchResult' is a dictionary with three members:
# 'total' - the total count of devices that exist
# 'resources' - a dictionary of the first 20 devices
# 'nextPage' a dictionary of the next page to be returned
# note that the default page size is 20 devices.  We're not going to futz with that.
# Max is 100, in case we decide to do something later.
    
total = devices['SearchResult']['total'] # The first page has the count of all devices in inventory
pagesize = 20 #This is the default size.  Max is 100/page

#figure out how many pages exist.
if total % pagesize == 0:
    numGets = int(total/pagesize)
else:
    numGets = int(total/pagesize) + 1  
#print (numGets) # the total number of pages

print('A total of',total,'network devices exist.\ncollecting...')

for n in devices['SearchResult']['resources']:
    device = {}
    device['id'] = n['id']
    device['name'] = n['name']
    device['link'] = n['link']['href']
    device_list.append(device)
    if 'nextPage' in devices['SearchResult']:
        href = devices['SearchResult']['nextPage']['href']
        
if numGets > 1: #now go get the rest of the pages
    for i in range(2,numGets+1):
        conn.request("GET", href, headers=headers)
        res = conn.getresponse()
        data = res.read()
        devices = json.loads(data)    
        for n in devices['SearchResult']['resources']:
   #        print(n['name'])
            device = {}
            device['id'] = n['id']
            device['name'] = n['name']
            device['link'] = n['link']['href']
            device_list.append(device)
        if 'nextPage' in devices['SearchResult']:
            #print(devices['SearchResult']['nextPage'])
            href = devices['SearchResult']['nextPage']['href']
    print()
    print('This script will collect the number of Network Access Devices')
    print('from ISE and attempt to contact each NAD via PING.')
    print('Ff the "delete" option is specified, it will delete any NAD')
    print('that fails to respond.  FOR THIS REASON, it is a good idea to')
    print('EXPORT the entire NAD listing into a CSV file via the ISE GUI')
    print('Administration -> Network Resources -> Network Devices -> Export.\n')
    input("Press Enter to continue...")
#    
# device_list is now fully populated.
#
# iterate through the list.  Each device has at least one IP address.
# Each IP is pinged and status is recorded.
# The ping command is generating 4 attempts.  A different OS might perform diferently
# All IPs with 0/4 responses are also written to the output file.
#
for i in range(len(device_list)-1690):
    getStr = device_list[i]['link'][35:]
 #   try:
    conn.request("GET",getStr, headers=headers)
    resp = conn.getresponse()
    data=resp.read()
    out = json.loads(data)
    ips = out['NetworkDevice']['NetworkDeviceIPList']
    print(i, out['NetworkDevice']['name'])
    for j in range(len(ips)):
        print('\t',ips[j]['ipaddress'],'\t', pingStat(out['NetworkDevice']['name'],ips[j]['ipaddress'],out['NetworkDevice']['id']))
#    except:
        
downFile.close()
