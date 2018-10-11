import os
import subprocess
import socket
import netifaces
import sys
import argparse
import time

def ping(addr):
    # on linux -c rather than -n
    #subprocess.run("ping -n 1 " + addr, stderr=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0] == 0:
    #if subprocess.Popen("ping -n 1 " + addr).communicate()[0] == 0:
    #if os.system("ping -n 1 " + addr)==0:
    #   return True
    #return False
    with open(os.devnull, 'w') as DEVNULL:
        try:
            subprocess.check_call(
                ['ping', '-n', '1', addr],
                stdout=DEVNULL,  # suppress output
                stderr=DEVNULL
            )
            return True
        except subprocess.CalledProcessError:
            return False
    return False

def pingping(addr, c, t, error):
    fail = False
    for p in range(0,c):
        time.sleep(t)
        myprint(' [ ]\b\b')
        if ping(addr):
            myprint('.]')
        else:
            myprint('X]')
            fail = True

    if fail:
        myprint('\n****** FAIL : ' + error + '')

    myprint('\n')

    if fail:
        return 1
    return 0

def myprint(s):
    sys.stdout.write(s)
    sys.stdout.flush

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

# See https://stackoverflow.com/questions/11735821/python-get-localhost-ip for source may need to look at this RE non windows
try:
    localip = socket.gethostbyname(socket.gethostname())
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
