# http://docs.openstack.org/developer/python-novaclient/ref/v2/servers.html
import time, os, sys, random, re
import inspect
from os import environ as env

from  novaclient import client
import keystoneclient.v3.client as ksclient
from keystoneauth1 import loading
from keystoneauth1 import session


flavor = "ssc.medium" 
private_net = "UPPMAX 2024/1-4 Internal IPv4 Network"
floating_ip_pool_name = None
floating_ip = None
image_name = "31dbaaf8-2200-44bc-b4f2-44ab4be099ca"

identifier = random.randint(1000,9999)

loader = loading.get_plugin_loader('password')

auth = loader.load_from_options(auth_url=env['OS_AUTH_URL'],
                                username=env['OS_USERNAME'],
                                password=env['OS_PASSWORD'],
                                project_name=env['OS_PROJECT_NAME'],
                                project_domain_id=env['OS_PROJECT_DOMAIN_ID'],
                                #project_id=env['OS_PROJECT_ID'],
                                user_domain_name=env['OS_USER_DOMAIN_NAME'])

sess = session.Session(auth=auth)
nova = client.Client('2.1', session=sess)
print ("user authorization completed.")

image = nova.glance.find_image(image_name)

flavor = nova.flavors.find(name=flavor)

if private_net != None:
    net = nova.neutron.find_network(private_net)
    nics = [{'net-id': net.id}]
else:
    sys.exit("private-net not defined.")

#print("Path at terminal when executing this file")
#print(os.getcwd() + "\n")
cfg_file_path =  os.getcwd()+'/prod-cloud-cfg1.txt'
if os.path.isfile(cfg_file_path):
    userdata_prod = open(cfg_file_path)
else:
    sys.exit("prod-cloud-cfg1.txt is not in current working directory")
    
cfg_file_path =  os.getcwd()+'/dev-cloud-cfg1.txt'
if os.path.isfile(cfg_file_path):
    userdata_dev = open(cfg_file_path)
else:
    sys.exit("dev-cloud-cfg1.txt is not in current working directory")    


cfg_file_path1 =  os.getcwd()+'/prod-cloud-cfg2.txt'
if os.path.isfile(cfg_file_path1):
    userdata_prod1 = open(cfg_file_path1)
else:
    sys.exit("prod-cloud-cfg2.txt is not in current working directory")

cfg_file_path1 =  os.getcwd()+'/dev-cloud-cfg2.txt'
if os.path.isfile(cfg_file_path1):
    userdata_dev1 = open(cfg_file_path1)
else:
    sys.exit("dev-cloud-cfg2.txt is not in current working directory") 


secgroups = ['default']

print ("Creating instances ... ")
instance_prod1 = nova.servers.create(name="group4_prod1", image=image, flavor=flavor, key_name='mariia_chuprina',userdata=userdata_prod, nics=nics,security_groups=secgroups)
instance_dev1 = nova.servers.create(name="group4_dev1", image=image, flavor=flavor, key_name='mariia_chuprina',userdata=userdata_dev, nics=nics,security_groups=secgroups)
inst_status_prod1 = instance_prod1.status
inst_status_dev1 = instance_dev1.status

instance_prod2 = nova.servers.create(name="group4_dev2", image=image, flavor=flavor, key_name='mariia_chuprina',userdata=userdata_prod1, nics=nics,security_groups=secgroups)
instance_dev2 = nova.servers.create(name="group4_dev3", image=image, flavor=flavor, key_name='mariia_chuprina',userdata=userdata_dev1, nics=nics,security_groups=secgroups)
inst_status_prod2 = instance_prod2.status
inst_status_dev2 = instance_dev2.status
print ("waiting for 10 seconds.. ")
time.sleep(10)

while inst_status_prod1 == 'BUILD' or inst_status_dev1 == 'BUILD' or inst_status_prod2 == 'BUILD' or inst_status_dev2 == 'BUILD':
    print ("Instance: "+instance_prod1.name+" is in "+inst_status_prod1+" state, sleeping for 5 seconds more...")
    print ("Instance: "+instance_dev1.name+" is in "+inst_status_dev1+" state, sleeping for 5 seconds more...")
    print ("Instance: "+instance_prod2.name+" is in "+inst_status_prod2+" state, sleeping for 5 seconds more...")
    print ("Instance: "+instance_dev2.name+" is in "+inst_status_dev2+" state, sleeping for 5 seconds more...")
    time.sleep(5)
    instance_prod1 = nova.servers.get(instance_prod1.id)
    inst_status_prod1 = instance_prod1.status
    instance_dev1 = nova.servers.get(instance_dev1.id)
    inst_status_dev1 = instance_dev1.status
    instance_prod2 = nova.servers.get(instance_prod2.id)
    inst_status_prod2 = instance_prod2.status
    instance_dev2 = nova.servers.get(instance_dev2.id)
    inst_status_dev2 = instance_dev2.status


ip_address_prod1 = None
for network in instance_prod1.networks[private_net]:
    if re.match('\d+\.\d+\.\d+\.\d+', network):
        ip_address_prod1 = network
        break
if ip_address_prod1 is None:
    raise RuntimeError('No IP address assigned!')

ip_address_dev1 = None
for network in instance_dev1.networks[private_net]:
    if re.match('\d+\.\d+\.\d+\.\d+', network):
        ip_address_dev1 = network
        break
if ip_address_dev1 is None:
    raise RuntimeError('No IP address assigned!')


ip_address_prod2 = None

for network in instance_prod2.networks[private_net]:
    if re.match('\d+\.\d+\.\d+\.\d+', network):
        ip_address_prod2 = network
        break
if ip_address_prod2 is None:
    raise RuntimeError('No IP address assigned!')

ip_address_dev2 = None
for network in instance_dev2.networks[private_net]:
    if re.match('\d+\.\d+\.\d+\.\d+', network):
        ip_address_dev2 = network
        break
if ip_address_dev2 is None:
    raise RuntimeError('No IP address assigned!')

print ("Instance: "+ instance_prod1.name +" is in " + inst_status_prod1 + " state" + " ip address: "+ ip_address_prod1)
print ("Instance: "+ instance_dev1.name +" is in " + inst_status_dev1 + " state" + " ip address: "+ ip_address_dev1)
print ("Instance: "+ instance_prod2.name +" is in " + inst_status_prod2 + " state" + " ip address: "+ ip_address_prod2)
print ("Instance: "+ instance_dev2.name +" is in " + inst_status_dev2 + " state" + " ip address: "+ ip_address_dev2)



