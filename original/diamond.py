# !/usr/bin/python

from mininet.log import setLogLevel, info
from mininet.net import Mininet
from mininet.topolib import TreeTopo
from mininet.cli import CLI
from mininet.node import Controller, OVSSwitch
from os import environ

# DO NOT MODIFY THIS PART 

POXDIR = environ[ 'HOME' ] + '/pox'

class CustomPOX( Controller ):
    "Custom POX() subclass that connects defines the POX component to load"
    def __init__( self, name, cdir=POXDIR,
                  command='python pox.py',
                  cargs=( 'openflow.of_01 --port=%s '
                          'forwarding.l3_learning' ),
                  **kwargs ):
        Controller.__init__( self, name, cdir=cdir,
                             command=command,
                             cargs=cargs, **kwargs )

# controllers={ 'pox': POX }

class CustomSwitch( OVSSwitch ):
    "Custom Switch() subclass that connects to different controllers"
    def start( self, controllers ):
        return OVSSwitch.start( self, [ cmap[ self.name ] ] )


# THIS PART CAN BE CHANGED AND ADAPTED IF REQUIRED 

setLogLevel( 'info' )  # for CLI output

info ("*** Creating a network from semi-scratch with multiple controllers\n")
cm = CustomPOX ('pox', ip='127.0.0.1', port=6633)
c = Controller ('c',  port=6633)

cmap = {'s1': cm, 's2': cm, 's3':cm, 's4' : c}

net = Mininet( switch=CustomSwitch, build=False, waitConnected=True )

info( "*** Creating (reference) controllers\n" )
for c in [ cm, c ]:
	net.addController(c)

info( "*** Creating switches with MAC, IP and DPID\n" )
s1 = net.addSwitch( 's1', listenPort=6631, dpid='1' )
s2 = net.addSwitch( 's2', listenPort=6631, dpid='2' )
s3 = net.addSwitch( 's3', listenPort=6631, dpid='3' )
s4 = net.addSwitch( 's4', listenPort=6631, dpid='4' )


info( "*** Creating hosts\n" )
h1 = net.addHost('host1', mac='00:00:00:00:10:01', ip='10.0.10.1/24')
h2 = net.addHost('host2', mac='00:00:00:00:20:01', ip='10.0.20.1/24')
h3 = net.addHost('host3', mac='00:00:00:00:30:01', ip='10.0.30.1/24')
h4 = net.addHost('host4', mac='00:00:00:00:40:01', ip='10.0.40.1/24')

info( "*** Creating links\n" )
net.addLink( s1, h1, intfName1='s1-eth1')
net.addLink( s1, s2, intfName1='s1-eth3', intfName2='s2-eth3')
net.addLink( s1, s4, intfName1='s1-eth2', intfName2='s4-eth2')

net.addLink( s2, h2, intfName1='s2-eth1')
net.addLink( s2, s3, intfName1='s2-eth2', intfName2='s3-eth2')

net.addLink( s3, h3, intfName1='s3-eth1')
net.addLink( s3, s4, intfName1='s3-eth3', intfName2='s4-eth3')

net.addLink( s4, h4, intfName1='s4-eth1')


info( "*** Assign MAC and IP adresses\n" )

s1.setMAC('00:00:00:00:10:02',   intf='s1-eth1')
s1.setMAC('00:00:00:00:20:01',   intf='s1-eth2')
s1.setMAC('00:00:00:00:30:01',   intf='s1-eth3')
s1.setIP('10.0.10.254',          intf='s1-eth1')
s1.setIP('10.0.50.1',            intf='s1-eth2')
s1.setIP('10.0.50.2',            intf='s1-eth3')

s2.setMAC('00:00:00:00:10:02',   intf='s2-eth1')
s2.setMAC('00:00:00:00:20:01',   intf='s2-eth2')
s2.setMAC('00:00:00:00:30:01',   intf='s2-eth3')
s2.setIP('10.0.20.254',          intf='s2-eth1')
s2.setIP('10.0.50.3',            intf='s2-eth2')
s2.setIP('10.0.50.4',            intf='s2-eth3')

s3.setMAC('00:00:00:00:10:02',   intf='s3-eth1')
s3.setMAC('00:00:00:00:20:01',   intf='s3-eth2')
s3.setMAC('00:00:00:00:30:01',   intf='s3-eth3')
s3.setIP('10.0.30.254',          intf='s3-eth1')
s3.setIP('10.0.50.5',            intf='s3-eth2')
s3.setIP('10.0.50.6',            intf='s3-eth3')

s4.setMAC('00:00:00:00:10:02',   intf='s4-eth1')
s4.setMAC('00:00:00:00:20:01',   intf='s4-eth2')
s4.setMAC('00:00:00:00:30:01',   intf='s4-eth3')
s4.setIP('10.0.40.254',          intf='s4-eth1')
s4.setIP('10.0.50.7',            intf='s4-eth2')
s4.setIP('10.0.50.8',            intf='s4-eth3')


info( "*** Starting network\n" )
net.build()
cm.start()
c.start()
s1.start( [ cm ] )
s2.start( [ cm ] )
s3.start( [ cm ] )
s4.start( [ c ] )

info( "*** Add defaults route to host1 and host2\n" )
h1.cmd("ip route add 10.0.20.0/24 dev eth0")
h2.cmd("ip route add 10.0.10.0/24 dev eth0")

#info( "*** Attach a new interface to switch s1\n")
#s1.attach('eth2')

net.pingAll()

info( "*** Running CLI\n" )
CLI( net )

info( "*** Stopping network\n" )
net.stop()

