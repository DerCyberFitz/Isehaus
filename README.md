# Isehaus
Cisco ISE Repository
This repository will contain scripts and tools for using the ISE APIs to perform various tasks.
Use at your own risk.  Particular caveats will be noted in this README file.

Script 1 - Identify orphaned Netwiork Devices
  In an organization of some size, with multiple individuals performing the network management tasks, 
  it is quite easy to imagine that your ISE database has a number of entries for network devices that
  no longer exist, and therefore, should be removed.  This script grabs every network device from the 
  database and then proceeds to scan to see if each IP address assigned to the device is live.

  Version 1 of this script is written in Python3 and should run in most any environment that supports
  Python.  It will PING each IP address and if there no no response, make a note of that device.
  At the end, you'll have a file that could be used to actually delete these devices.

  The major caveat here is that the devices need to accept incoming PING requests, so your firewalls, 
  etc., need to allow this traffic.  Typically not a problem, as your IP addresses are all internal, right?

  Plans for future versions:
    1)  include SNMP support 
    2)  provide a menas of auto-deleting the devices that do not respond.  
    3)  better enumeration of network devices that have multiple IP addresses  
  
  Proposed enhancement 2) could be quite chaotic, so it is highly recommended that 
  you export your Network Devices PRIOR TO RUNNING THE SCRIPT in case you need to easily restore an object.

To run the script, user the ISE server, user credential and password as parameters:

python ping_all_net_devices.py <ise-server> <user-id> <password>
