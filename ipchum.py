import os
import subprocess
import socket
import netifaces
import sys
import argparse
import time
from multiping import MultiPing

def getHostAddress(hostname):
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None

def ping(addr):
    mp = MultiPing([addr], ignore_lookup_errors = True)
    mp.send()
    responses, no_responses = mp.receive(1)
    for resaddr, rtt in responses.items():
        if resaddr==addr:
            return True

    return False

def pingping(description, addr, c, t, error):
    fails = 0
    myprint(description.ljust(12) + ': ')
    myprint(addr.ljust(20))

    addr = getHostAddress(addr)
    if addr!=None:
        myprint(' -> ')
        myprint(addr.ljust(20))

        for p in range(0,c):
            time.sleep(t)
            myprint(' [ ]\b\b')
            if ping(addr):
                myprint('.]')
            else:
                myprint('X]')
                fails += 1

        if fails == c:
            myprint('\n****** FAIL : ' + error + '')
        elif fails > 0:
            myprint('\n****** FAIL : Intermittent : ' + error + '')

    else:
        myprint('\n****** FAIL : Could not get Host Address.')
        fails += 1

    myprint('\n')

    if fails > 0:
        return 1
    return 0

def myprint(s):
    sys.stdout.write(s)
    sys.stdout.flush()

parser = argparse.ArgumentParser(description='Test network connection.')
parser.add_argument('dest', nargs='*', help='an optional destinations to test.')
parser.add_argument('-p', '--pings', default=3, type=int, help='Number of pings to each destination.')
parser.add_argument('-t', '--time', default=.2, type=float, help='Time in seconds between each ping.')
parser.add_argument('-w', '--wait', dest='wait', action='store_const', const='WAIT', default='', help='Wait for user to press a key when finished.')

args = parser.parse_args()

result = 0

myprint('Discovery')

try:
    localhostname = socket.gethostname()
    myprint('.')
except:
    localhostname = None
    myprint('\n****** FAIL : Unable to get local hostname.')
    result+=1

try:
    # See https://stackoverflow.com/questions/11735821/python-get-localhost-ip
    # Windows only localip = socket.gethostbyname(socket.gethostname())
    localip = netifaces.ifaddresses('enp2s0').get(netifaces.AF_INET)[0]['addr']
    myprint('.')
except:
    localip = None
    myprint('\n****** FAIL : Unable to get local ip address.')
    result+=1

if localip=='127.0.0.1':
    myprint('\n****** FAIL : IP address is 127.0.0.1, is network connected?')
    result+=1

# See https://pypi.org/project/netifaces/ for netifaces documentation
# SMELL My code needs to be a bit better here I think
try:
    gateway = netifaces.gateways()['default'][netifaces.AF_INET][0]
    myprint('.')
except:
    gateway = None
    myprint('\n****** FAIL : Unable to get default gateway.')
    result+=1

if result==0:
    myprint('ok.')

myprint('\nTesting...\n')

#myprint('OS          : ' + os.name +'\n')

result+=pingping('Loop back', '127.0.0.1', args.pings, args.time, 'Unable to ping loop back address, is network available?')

if localip != None :
    result+=pingping('Local IP',localip,args.pings, args.time, 'Unable to ping local ip address, is network configured, is DHCP working?')

if localhostname != None :
    result+=pingping('Hostname', localhostname, args.pings, args.time, 'Unable to ping local hostname, is this assigned?')

if gateway != None :
    result+=pingping('Gateway', gateway, args.pings, args.time, 'Unable to ping default gateway.')

if args.dest != None :
    for addr in args.dest:
        result+=pingping('Address', addr, args.pings, args.time, 'Unable to ping supplied destination address.')

myprint('\n')

if args.wait=='WAIT':
    raw_input('Press Enter')

exit(result)
