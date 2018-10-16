import os
import subprocess
import socket
import netifaces
import sys
import argparse
import time
from multiping import MultiPing

def ping(addr):
    mp = MultiPing([addr])
    mp.send()
    responses, no_responses = mp.receive(1)
    if no_responses:
        return False
    return True

def pingping(addr, c, t, error):
    fails = 0
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

    myprint('\n')

    if fails > 0:
        return 1
    return 0

def myprint(s):
    sys.stdout.write(s)
    sys.stdout.flush()

parser = argparse.ArgumentParser(description='Test network connection.')
parser.add_argument('dest', nargs='?', help='an optional destination for final ping.')
parser.add_argument('-p', '--pings', default=3, type=int, help='Number of pings to each destination.')
parser.add_argument('-t', '--time', default=.1, type=float, help='Time in seconds between each ping.')
parser.add_argument('-w', '--wait', dest='wait', action='store_const', const='WAIT', default='', help='Wait for user to press a key when finished.')

args = parser.parse_args()

result = 0

myprint('Discovery')

try:
    hostname = socket.gethostname()
    myprint('.')
except:
    hostname = None
    myprint('\n****** FAIL : Unable to get local hostname.')
    result+=1

try:
    # See https://stackoverflow.com/questions/11735821/python-get-localhost-ip
    # Windows only localip = socket.gethostbyname(socket.gethostname())
    # localip = netifaces.ifaddresses('wlp8s0'z).get(netifaces.AF_INET)[0]['addr']
    localip = '192.168.1.60'
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

myprint('\n')

#myprint('OS          : ' + os.name +'\n')

myprint('Loopback    : 127.0.0.1'.ljust(40))
result+=pingping('127.0.0.1', args.pings, args.time, 'Unable to ping loop back address, is network available?')

if localip != None :
    myprint(('Local IP    : ' + localip).ljust(40))
    result+=pingping(localip,args.pings, args.time, 'Unable to ping local ip address, is network configured, is DHCP working?')

if hostname != None :
    myprint(('Hostname    : ' + hostname).ljust(40))
    result+=pingping(hostname, args.pings, args.time, 'Unable to ping local hostname, is this assigned?')

if gateway != None :
    myprint(('Gateway     : ' + gateway).ljust(40))
    result+=pingping(gateway, args.pings, args.time, 'Unable to ping default gateway.')

if args.dest != None :
    myprint(('Address     : ' + args.dest).ljust(40))
    result+=pingping(args.dest, args.pings, args.time, 'Unable to ping supplied destination address.')

myprint('\n')

if args.wait=='WAIT':
    raw_input('Press Enter')

exit(result)
