from django.shortcuts import render
from django.http import HttpResponse
import urllib.request
import time
import subprocess
from django.views.decorators.csrf import csrf_exempt
from sim.exceptions import *

SIM_CONTAINER_PORT = '31819'
PROJECT_PREFIX = 'openuavapp_'
ERROR_LEVEL = 2

def index(request):
	return HttpResponse("Hey!! What are you up to?")


####################################################################
####################################################################
####################################################################

# docker run -it --net=openuavapp_default --name=openauv2 -v /tmp/.X11-unix:/tmp/.X11-unix -v /home/abhijeet/Documents/openuav/samples/leader-follower/simulation:/simulation -e DISPLAY=$DISPLAY --entrypoint "/simulation/run_this.sh" openuavproject_openuav

# nvidia-docker run -it --net=openuavapp_default --name=openuavapp_openauv3 -v /tmp/.X11-unix:/tmp/.X11-unix -v /home/jdas/openuav-playground/samples/leader-follower:/simulation -e DISPLAY=:0 --entrypoint "/home/setup.sh" openuavapp_openuav

def hostnameToIP(hostname):
	cmd = ''' nslookup hostname | sed -n '6p' | grep -o '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}'  '''
	p1 = subprocess.Popen(['nslookup', hostname], stdout=subprocess.PIPE)
	p2 = subprocess.Popen(['sed', '-n', '''6p'''], 
		stdin=p1.stdout, stdout=subprocess.PIPE)
	p1.stdout.close()
	p3 = subprocess.Popen(['grep', '-o', '''[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}'''],        
		stdin=p2.stdout,stdout=subprocess.PIPE)
	p2.stdout.close()
	output = p3.communicate()[0]
	outputStr = output.decode('UTF-8').strip()

	if outputStr == '':
		raise NoContainerExc('nslookup returns empty')

	return outputStr

def ipToViewNum(ip):
	# 172.28.0.5 corresponds to view-1.openuav.us - we return the number '1' here
	try:
		lastOctetStr = ip.split('.')[-1]
		lastOctetInt = int(lastOctetStr)
		return str(lastOctetInt - 4)
	except Exception as e:
		raise InvalidIPExc(str(e))

def getUserIDWithoutDefault(request):
	try:
		userid = request.GET['user']
		return userid
	except Exception as e:
		raise NoUserIDExc(str(e))

def getUserIDWithDefault(request):
	userid = request.GET.get('user','openuav_1')
	return userid

def getNumUAVs(simulation_ip):
	try:
		num_uav_str=''
		while num_uav_str=='':
			results = urllib.request.urlopen('http://' + simulation_ip + ':' + SIM_CONTAINER_PORT + '/query/numUavs').read()
			num_uav_str=str(results.decode('UTF-8').split('#')[0])
			if num_uav_str=='':
				time.sleep(1)
		num_uavs = int(num_uav_str)
		return num_uavs
	except Exception as e:
		raise ContainerInformationFetchExc(str(e))

def isSimReady(simulation_ip):
	measuresUp = 0
	try:
		while measuresUp < 2:
			results = urllib.request.urlopen('http://' + simulation_ip + ':' + SIM_CONTAINER_PORT + '/query/measures').read()
			measuresUp=int(str(results.decode('UTF-8').split('#')[0]))
			if measuresUp < 2:
				time.sleep(1)
		time.sleep(2)
		return True
	except Exception as e:
		raise ContainerInformationFetchExc(str(e))

def getErrorBasedOnLevel(str, e):
	if ERROR_LEVEL == 2:
		return str + '\nDebug: ' + e
	elif ERROR_LEVEL == 1:
		return str
	else:
		return 'Some error occured. Contact the admin.'

def getSecureDomainNames(simNodeIP):
	vdn = 'view-' + ipToViewNum(simNodeIP) + '.openuav.us'
	rdn = 'ros-' + ipToViewNum(simNodeIP) + '.openuav.us'
	tdn = 'term-' + ipToViewNum(simNodeIP) + '.openuav.us'
	return vdn, rdn, tdn

def getUnsecureDomainNames(simNodeIP):
	vdn = simNodeIP + ':80'
	rdn = simNodeIP + ':9090'
	tdn = simNodeIP + ':3000'
	return vdn, rdn, tdn

########################################################
########################################################
########################################################
########################################################


def console(request):
	try:
		userid = getUserIDWithoutDefault(request)
		simNodeHostname = PROJECT_PREFIX + userid
		simNodeIP = hostnameToIP(simNodeHostname)
		viewDomainName, rosDomainName, terminalDomainName = getSecureDomainNames(simNodeIP)
		numUAVs = getNumUAVs(simNodeIP)
		isSimReady(simNodeIP)
		return HttpResponse(render(request, 'sim/dev_console.html', {'terminalDomainName': terminalDomainName, 'range' : range(int(numUAVs)), 'num_uavs' : numUAVs, 'viewDomainName' : viewDomainName, 'rosDomainName' : rosDomainName}))
	except NoContainerExc as e:
		return HttpResponse(render(request, 'sim/error.html', {'error' : getErrorBasedOnLevel('Container not present.', str(e))}))
	except ContainerInformationFetchExc as e:
		return HttpResponse(render(request, 'sim/error.html', {'error' : getErrorBasedOnLevel('Simulation node not responding or responding incorrectly.', str(e))}))
	except NoUserIDExc as e:
		return HttpResponse(render(request, 'sim/error.html', {'error' : getErrorBasedOnLevel('No User ID present.', str(e))}))
	except InvalidIPExc as e:
		return HttpResponse(render(request, 'sim/error.html', {'error' : getErrorBasedOnLevel('Invalid IP.', str(e))}))
	except Exception as e:	
		return HttpResponse(render(request, 'sim/error.html', {'error' : getErrorBasedOnLevel('Internal Server Error.', str(e))}))


def unsecure_console(request):
	try:
		userid = getUserIDWithDefault(request)
		simNodeHostname = PROJECT_PREFIX + userid
		simNodeIP = hostnameToIP(simNodeHostname)
		viewDomainName, rosDomainName, terminalDomainName = getUnsecureDomainNames(simNodeIP)
		numUAVs = getNumUAVs(simNodeIP)
		isSimReady(simNodeIP)
		return HttpResponse(render(request, 'sim/dev_console_unsecure.html', {'terminalDomainName': terminalDomainName, 'range' : range(int(numUAVs)), 'num_uavs' : numUAVs, 'viewDomainName' : viewDomainName, 'rosDomainName' : rosDomainName}))
	except NoContainerExc as e:
		return HttpResponse(render(request, 'sim/error.html', {'error' : getErrorBasedOnLevel('Container not present.', str(e))}))
	except ContainerInformationFetchExc as e:
		return HttpResponse(render(request, 'sim/error.html', {'error' : getErrorBasedOnLevel('Simulation node not responding or responding incorrectly.', str(e))}))
	except NoUserIDExc as e:
		return HttpResponse(render(request, 'sim/error.html', {'error' : getErrorBasedOnLevel('No User ID present.', str(e))}))
	except InvalidIPExc as e:
		return HttpResponse(render(request, 'sim/error.html', {'error' : getErrorBasedOnLevel('Invalid IP.', str(e))}))
	except Exception as e:	
		return HttpResponse(render(request, 'sim/error.html', {'error' : getErrorBasedOnLevel('Internal Server Error.', str(e))}))

def console1(request):
	try:
		userid = getUserIDWithoutDefault(request)
		simNodeHostname = PROJECT_PREFIX + userid
		simNodeIP = hostnameToIP(simNodeHostname)
		viewDomainName, rosDomainName, terminalDomainName = getSecureDomainNames(simNodeIP)
		numUAVs = getNumUAVs(simNodeIP)
		return HttpResponse(render(request, 'sim/dev_console_first.html', {'terminalDomainName': terminalDomainName, 'userid': userid, 'range' : range(int(numUAVs)), 'num_uavs' : numUAVs, 'viewDomainName' : viewDomainName, 'rosDomainName' : rosDomainName}))
	except NoContainerExc as e:
		return HttpResponse(render(request, 'sim/error.html', {'error' : getErrorBasedOnLevel('Container not present.', str(e))}))
	except ContainerInformationFetchExc as e:
		return HttpResponse(render(request, 'sim/error.html', {'error' : getErrorBasedOnLevel('Simulation node not responding or responding incorrectly.', str(e))}))
	except NoUserIDExc as e:
		return HttpResponse(render(request, 'sim/error.html', {'error' : getErrorBasedOnLevel('No User ID present.', str(e))}))
	except InvalidIPExc as e:
		return HttpResponse(render(request, 'sim/error.html', {'error' : getErrorBasedOnLevel('Invalid IP.', str(e))}))
	except Exception as e:	
		return HttpResponse(render(request, 'sim/error.html', {'error' : getErrorBasedOnLevel('Internal Server Error.', str(e))}))

@csrf_exempt
def console2(request):
	try:
		userid = getUserIDWithoutDefault(request)
		simNodeHostname = PROJECT_PREFIX + userid
		simNodeIP = hostnameToIP(simNodeHostname)
		viewDomainName, rosDomainName, terminalDomainName = getSecureDomainNames(simNodeIP)
		numUAVs = getNumUAVs(simNodeIP)
		isSimReady(simNodeIP)
		return HttpResponse(render(request, 'sim/dev_console_second.html', {'terminalDomainName': terminalDomainName, 'range' : range(int(numUAVs)), 'num_uavs' : numUAVs, 'viewDomainName' : viewDomainName, 'rosDomainName' : rosDomainName}))
	except NoContainerExc as e:
		return HttpResponse(render(request, 'sim/error.html', {'error' : getErrorBasedOnLevel('Container not present.', str(e))}))
	except ContainerInformationFetchExc as e:
		return HttpResponse(render(request, 'sim/error.html', {'error' : getErrorBasedOnLevel('Simulation node not responding or responding incorrectly.', str(e))}))
	except NoUserIDExc as e:
		return HttpResponse(render(request, 'sim/error.html', {'error' : getErrorBasedOnLevel('No User ID present.', str(e))}))
	except InvalidIPExc as e:
		return HttpResponse(render(request, 'sim/error.html', {'error' : getErrorBasedOnLevel('Invalid IP.', str(e))}))
	except Exception as e:	
		return HttpResponse(render(request, 'sim/error.html', {'error' : getErrorBasedOnLevel('Internal Server Error.', str(e))}))

def unsecure_console1(request):
	try:
		userid = getUserIDWithDefault(request)
		simNodeHostname = PROJECT_PREFIX + userid
		simNodeIP = hostnameToIP(simNodeHostname)
		viewDomainName, rosDomainName, terminalDomainName = getUnsecureDomainNames(simNodeIP)
		numUAVs = getNumUAVs(simNodeIP)
		return HttpResponse(render(request, 'sim/dev_console_unsecure_first.html', {'terminalDomainName': terminalDomainName, 'userid': userid, 'range' : range(int(numUAVs)), 'num_uavs' : numUAVs, 'viewDomainName' : viewDomainName, 'rosDomainName' : rosDomainName}))
	except NoContainerExc as e:
		return HttpResponse(render(request, 'sim/error.html', {'error' : getErrorBasedOnLevel('Container not present.', str(e))}))
	except ContainerInformationFetchExc as e:
		return HttpResponse(render(request, 'sim/error.html', {'error' : getErrorBasedOnLevel('Simulation node not responding or responding incorrectly.', str(e))}))
	except NoUserIDExc as e:
		return HttpResponse(render(request, 'sim/error.html', {'error' : getErrorBasedOnLevel('No User ID present.', str(e))}))
	except InvalidIPExc as e:
		return HttpResponse(render(request, 'sim/error.html', {'error' : getErrorBasedOnLevel('Invalid IP.', str(e))}))
	except Exception as e:	
		return HttpResponse(render(request, 'sim/error.html', {'error' : getErrorBasedOnLevel('Internal Server Error.', str(e))}))

@csrf_exempt
def unsecure_console2(request):
	try:
		userid = getUserIDWithDefault(request)
		simNodeHostname = PROJECT_PREFIX + userid
		simNodeIP = hostnameToIP(simNodeHostname)
		viewDomainName, rosDomainName, terminalDomainName = getUnsecureDomainNames(simNodeIP)
		numUAVs = getNumUAVs(simNodeIP)
		isSimReady(simNodeIP)
		return HttpResponse(render(request, 'sim/dev_console_unsecure_second.html', {'terminalDomainName': terminalDomainName, 'range' : range(int(numUAVs)), 'num_uavs' : numUAVs, 'viewDomainName' : viewDomainName, 'rosDomainName' : rosDomainName}))
	except NoContainerExc as e:
		return HttpResponse(render(request, 'sim/error.html', {'error' : getErrorBasedOnLevel('Container not present.', str(e))}))
	except ContainerInformationFetchExc as e:
		return HttpResponse(render(request, 'sim/error.html', {'error' : getErrorBasedOnLevel('Simulation node not responding or responding incorrectly.', str(e))}))
	except NoUserIDExc as e:
		return HttpResponse(render(request, 'sim/error.html', {'error' : getErrorBasedOnLevel('No User ID present.', str(e))}))
	except InvalidIPExc as e:
		return HttpResponse(render(request, 'sim/error.html', {'error' : getErrorBasedOnLevel('Invalid IP.', str(e))}))
	except Exception as e:	
		return HttpResponse(render(request, 'sim/error.html', {'error' : getErrorBasedOnLevel('Internal Server Error.', str(e))}))

