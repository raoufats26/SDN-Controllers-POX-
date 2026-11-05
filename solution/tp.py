"""
Composant POX du TP 3 : routage multi-chemins sur la topologie en losange.
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()


VOISINS = {
  1: {2: 'eth3', 4: 'eth2'},
  2: {1: 'eth3', 3: 'eth2'},
  3: {2: 'eth2', 4: 'eth3'},
  4: {1: 'eth2', 3: 'eth3'},
}


LIEN_HAUT = {3: 2, 4: 1}

HOTES = {
  '00:00:00:00:10:01': 1,
  '00:00:00:00:20:01': 2,
  '00:00:00:00:30:01': 3,
  '00:00:00:00:40:01': 4,
}

IDLE_TIMEOUT = 10
HARD_TIMEOUT = 30


class Diamond (object):
  """
  A Diamond object is created for each switch that connects.
  A Connection object for that switch is passed to the __init__ function.
  """
  def __init__ (self, connection):

    self.connection = connection

    connection.addListeners(self)

    self.mac_to_port = {}


    self.dpid = connection.dpid
    self.numero = {}
    for p in connection.features.ports:
      self.numero[p.name] = p.port_no

    self.port_hote = None
    self.port_haut = None
    self.vers_voisin = {}
    if self.dpid in LIEN_HAUT:
      self.port_hote = self.port('eth1')
      for voisin, suffixe in VOISINS[self.dpid].items():
        self.vers_voisin[voisin] = self.port(suffixe)
      self.port_haut = self.vers_voisin[LIEN_HAUT[self.dpid]]
      log.info("s%i : hote=%s haut=%s voisins=%s", self.dpid, self.port_hote,
               self.port_haut, self.vers_voisin)
    else:
      log.info("s%i : commutateur a apprentissage classique", self.dpid)


  def port (self, suffixe):
    return self.numero['s%i-%s' % (self.dpid, suffixe)]


  def resend_packet (self, packet_in, out_port):
    """
    Instructs the switch to resend a packet that it had sent to us.
    "packet_in" is the ofp_packet_in object the switch had sent to the
    controller due to a table-miss.
    """
    msg = of.ofp_packet_out()
    msg.data = packet_in

    action = of.ofp_action_output(port = out_port)
    msg.actions.append(action)

    self.connection.send(msg)


  def act_like_hub (self, packet, packet_in):
    """
    Implement hub-like behavior -- send all packets to all ports besides
    the input port.
    """
    self.resend_packet(packet_in, of.OFPP_ALL)


  def installer_flux (self, in_port, dst, out_port):
    """
    Installe un flux (port d'entree, MAC destination) -> port de sortie.
    Sans port de sortie, le flux supprime les paquets.
    """
    msg = of.ofp_flow_mod()
    msg.match = of.ofp_match(in_port = in_port, dl_dst = dst)
    msg.idle_timeout = IDLE_TIMEOUT
    msg.hard_timeout = HARD_TIMEOUT
    if out_port is not None:
      msg.actions.append(of.ofp_action_output(port = out_port))
    self.connection.send(msg)


  def apprendre_et_inonder (self, packet, packet_in):
    """
    Comportement d'un commutateur a apprentissage (switches hors s3 et s4).
    """
    self.mac_to_port[packet.src] = packet_in.in_port
    if not packet.dst.is_multicast and packet.dst in self.mac_to_port:
      out_port = self.mac_to_port[packet.dst]
      if out_port != packet_in.in_port:
        self.resend_packet(packet_in, out_port)
    else:
      self.resend_packet(packet_in, of.OFPP_ALL)


  def act_less_stupidly (self, packet, packet_in):
    """
    Implement a more intelligent behavior for the switch to take benefit of the multi routes
    """
    if self.dpid not in LIEN_HAUT:
      self.apprendre_et_inonder(packet, packet_in)
      return

    entree = packet_in.in_port
    dst = str(packet.dst)
    connu = dst in HOTES

    if packet.dst.is_multicast or not connu:

      if entree == self.port_hote:
        sortie = self.port_haut
      elif entree == self.port_haut:
        sortie = self.port_hote
      else:
        sortie = None
      if packet.dst.is_multicast:
        self.installer_flux(entree, packet.dst, sortie)
    else:
      switch_dest = HOTES[dst]
      if switch_dest == self.dpid:
        sortie = self.port_hote
      elif entree != self.port_hote:
        sortie = None
      elif switch_dest in self.vers_voisin:
        sortie = self.vers_voisin[switch_dest]
      else:
        sortie = self.port_haut
      self.installer_flux(entree, packet.dst, sortie)

    if sortie is not None:
      self.resend_packet(packet_in, sortie)


  def _handle_PacketIn (self, event):
    """
    Handles packet in messages from the switch.
    """

    packet = event.parsed 
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp 

    self.act_less_stupidly(packet, packet_in)



def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Diamond(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
