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

def pingping(description, host, c, t, error):
    fails = 0
    myprint('\n'+description.ljust(12) + ': ')
    myprint(host.ljust(20))

    myprint(' -> ')
    addr = getHostAddress(host)
    if addr!=None:
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
        myprint('\n****** FAIL : Could not get address for host ' + host + '.')
        fails += 1

    if fails > 0:
        return 1
    return 0

def myprint(s):
    sys.stdout.write(s)
    sys.stdout.flush()

parser = argparse.ArgumentParser(description='Test network connection.')
parser.add_argument('dest', nargs='*', help='an optional destinations to test.')
parser.add_argument('-p', '--pings', default=3, type=int, help='Number of pings to each destination. Default:3, minimum:1, maximum 20.')
parser.add_argument('-t', '--time', default=.2, type=float, help='Time in seconds between each ping, Default:0.2, minimum:0.2, maximum:60.')
parser.add_argument('-w', '--wait', dest='wait', action='store_const', const='WAIT', default='', help='Wait for user to press a key when finished.')

args = parser.parse_args()

result = 0

pings = args.pings
if pings < 1:
    pings=1
if pings > 20:
    pings=20

gap = args.time
if gap < 0.2:
    gap=0.2
if gap > 60:
    gap=60

myprint('Discovery')

try:
    localhostname = socket.gethostname()

    localip = getHostAddress(localhostname)

    if localip != None:
        if localip.startswith('127'):
            localip = getHostAddress(localhostname + '.local')
            if localip != None:
                if localip.startswith('127'):
                    localip = None
                else:
                    localhostname += '.local'

    myprint('.')
except:
    localhostname = None
    localip = None
    myprint('\n****** FAIL : Unable to get local hostname.')
    result+=1

if localip == None:
    try:
        # TODO decide what to do if more than one interface...
        # See https://stackoverflow.com/questions/11735821/python-get-localhost-ip
        # Windows only localip = socket.gethostbyname(socket.gethostname())
        # localip = netifaces.ifaddresses('enp2s0').get(netifaces.AF_INET)[0]['addr']
        localip = netifaces.ifaddresses(netifaces.gateways()['default'][netifaces.AF_INET][1]).get(netifaces.AF_INET)[0]['addr']
        myprint('.')
    except:
        localip = None
        myprint('\n****** FAIL : Unable to get local ip address.')
        result+=1

if localip.startswith('127'):
    myprint('\n****** FAIL : IP address is ' + localip + ', is network connected?')
    result+=1

# See https://pypi.org/project/netifaces/ for netifaces documentation
try:
    gateway = netifaces.gateways()['default'][netifaces.AF_INET][0]
    # myprint(netifaces.gateways()['default'][netifaces.AF_INET][1])
    myprint('.')
except:
    gateway = None
    myprint('\n****** FAIL : Unable to get default gateway.')
    result+=1

if result==0:
    myprint('ok.')

myprint('\nTesting...')

#myprint('OS          : ' + os.name +'\n')

result+=pingping('Loop back', '127.0.0.1', pings, gap, 'Unable to ping loop back address, is network available?')

if localip != None :
    result+=pingping('Local IP',localip, pings, gap, 'Unable to ping local ip address, is network configured, is DHCP working?')

if localhostname != None :
    result+=pingping('Hostname', localhostname, pings, gap, 'Unable to ping local hostname, is this assigned?')

if gateway != None :
    result+=pingping('Gateway', gateway, pings, gap, 'Unable to ping default gateway.')

if args.dest != None :
    for addr in args.dest:
        result+=pingping('Address', addr, pings, gap, 'Unable to ping ' + addr + '.')

myprint('\n')

if args.wait=='WAIT':
    raw_input('Press Enter')

exit(result)
