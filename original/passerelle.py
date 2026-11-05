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
                          'forwarding.l2_learning' ),
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

setLogLevel( 'info' )

def multiControllerNet():
   "Create a network from semi-scratch with multiple controllers."
c1 = CustomPOX ('pox', ip='127.0.0.1', port=6633)
c2 = Controller ('c2',  port=6633)

cmap = {'s1': c1, 's2': c2}


net = Mininet( switch=CustomSwitch, build=False, waitConnected=True )

info( "*** Creating (reference) controllers\n" )
for c in [ c1, c2 ]:
	net.addController(c)

info( "*** Creating switches\n" )
s1 = net.addSwitch( 's1' )
s2 = net.addSwitch( 's2' )


info( "*** Creating hosts\n" )
h1 = net.addHost('host1', mac='00:00:00:00:10:01', ip='10.0.10.1/24')
h2 = net.addHost('host2', mac='00:00:00:00:20:01', ip='10.0.30.1/24')

info( "*** Creating links\n" )
net.addLink( s1, h1 )
net.addLink( s2, h2 )
net.addLink( s1, s2 )

info( "*** Starting network\n" )
net.build()
c1.start()
c2.start()
s1.start( [ c1 ] )
s2.start( [ c2 ] )

info( "*** Testing network\n" )
net.pingAll()

info( "*** Running CLI\n" )
CLI( net )

info( "*** Stopping network\n" )
net.stop()


if __name__ == '__main__':
	setLogLevel( 'info' )  # for CLI output
	multiControllerNet()
