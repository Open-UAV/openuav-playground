from django.shortcuts import render
from django.http import HttpResponse
import urllib.request
import time
import subprocess

SIM_CONTAINER_PORT = '31819'

def index(request):
	return HttpResponse("Hey!! What are you up to?")


####################################################################
####################################################################
####################################################################

# docker run -it --net=openuavproject_default --name=openauv2 -v /tmp/.X11-unix:/tmp/.X11-unix -v /home/abhijeet/Documents/openuav/samples/leader-follower/simulation:/simulation -e DISPLAY=$DISPLAY --entrypoint "/simulation/run_this.sh" openuavproject_openuav

# nvidia-docker run -it --net=openuavproject_default --name=openuavproject_openauv3 -v /tmp/.X11-unix:/tmp/.X11-unix -v /home/abhsingh/Laptop/openuav/samples/leader-follower/simulation:/simulation -e DISPLAY=$DISPLAY --entrypoint "/simulation/run_this.sh" openuavproject_openuav

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
	return output.decode('UTF-8').strip()

def ipToViewNum(ip):
	# 172.28.0.6 corresponds to view-1.openuav.us - we return the number '1' here
	lastOctetStr = ip.split('.')[-1]
	lastOctetInt = int(lastOctetStr)
	return str(lastOctetInt - 5)


def console(request):
	num_uav_str=''
	measuresUp = 0

	try:
		simulation_hostname = 'openuavproject_' + request.GET.get('user','openuav_1')
		# simulation_hostname = 'openuavproject_openuav_1'
		simulation_ip = hostnameToIP(simulation_hostname)
		# simulation_ip = '172.28.0.3'
		simulation_viewDomainName = 'view-' + ipToViewNum(simulation_ip) + '.openuav.us:8001'
		simulation_rosDomainName = 'ros-' + ipToViewNum(simulation_ip) + '.openuav.us:8001'
	except Exception as e:	
		return HttpResponse(render(request, 'sim/error.html', {'error' : '400 Bad Request'}))

	try:
		while num_uav_str=='':
			results = urllib.request.urlopen('http://' + simulation_ip + ':' + SIM_CONTAINER_PORT + '/query/numUavs').read()
			num_uav_str=str(results.decode('UTF-8').split('#')[0])
			time.sleep(1)
		num_uavs = int(num_uav_str)
		while measuresUp<2:
			results = urllib.request.urlopen('http://' + simulation_ip + ':' + SIM_CONTAINER_PORT + '/query/measures').read()
			measuresUp=int(str(results.decode('UTF-8').split('#')[0]))
			time.sleep(1)

		# num_uavs = 2
		return HttpResponse(render(request, 'sim/dev_console.html', {'range' : range(int(num_uavs)), 'num_uavs' : num_uavs, 'viewDomainName' : simulation_viewDomainName, 'rosDomainName' : simulation_rosDomainName}))
	except Exception as e:
		return HttpResponse(render(request, 'sim/error.html', {'error' : '500 Internal Server Error. Contact the admin.'}))

def adminconsole(request):
	try:
		simulation_hostname = 'openuavproject_' + request.GET.get('user','openuav_1')
		# simulation_hostname = 'openuavproject_openuav_1'
		simulation_ip = hostnameToIP(simulation_hostname)
		# simulation_ip = '172.19.0.3'
		simulation_viewDomainName = simulation_ip+ ':80'
		simulation_rosDomainName = simulation_ip + ':9090'
		num_uav_str=''
		measuresUp = 0

		while num_uav_str=='':
			results = urllib.request.urlopen('http://' + simulation_ip + ':' + SIM_CONTAINER_PORT + '/query/numUavs').read()
			num_uav_str=str(results.decode('UTF-8').split('#')[0])
			time.sleep(1)
		num_uavs = int(num_uav_str)
		while measuresUp<2:
			results = urllib.request.urlopen('http://' + simulation_ip + ':' + SIM_CONTAINER_PORT + '/query/measures').read()
			measuresUp=int(str(results.decode('UTF-8').split('#')[0]))
			time.sleep(1)

		# num_uavs = 2
		return HttpResponse(render(request, 'sim/dev_console.html', {'range' : range(int(num_uavs)), 'num_uavs' : num_uavs, 'viewDomainName' : simulation_viewDomainName, 'rosDomainName' : simulation_rosDomainName}))
	except Exception as e:
		return HttpResponse(render(request, 'sim/error.html', {'error' : str(e)}))
