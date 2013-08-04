# Import some POX stuff
from pox.core import core                     # Main POX object
import pox.openflow.libopenflow_01 as of      # OpenFlow 1.0 library
# import pox.lib.packet as pkt                  # Packet parsing/construction
from pox.lib.addresses import EthAddr         # Address types
# import pox.lib.revent as revent               # Event library
# import pox.lib.recoco as recoco               # Multitasking library
import networkx as nx
import utils


class Overseer (object):
  """
  Overseer - POX Component Implementing Bandwith/Latency-aware OpenFlow Controller
  """

  _core_name = "overseer"  # We want to be core.overseer

  def __init__ (self, flow_idle_timeout=60, flow_hard_timeout=180):
    core.listen_to_dependencies(self)

    self.log = core.getLogger()
    self.graph = nx.Graph()  # Use dpid as node
    self.flow_idle_timeout = flow_idle_timeout
    self.flow_hard_timeout = flow_hard_timeout

  def _handle_openflow_discovery_LinkEvent(self, event):
    link = event.link
    # Note that dpid might be Int or Long or perhaps something else entirely!
    # We may need to care about their types if problems arise
    switch1 = link.dpid1
    switch2 = link.dpid2

    if event.added:
      self.log.info("Link Up: %s - %s" % (switch1, switch2))
      self.graph.add_edge(switch1, switch2, portByDpid={
        switch1: link.port1,
        switch2: link.port2,
      })
    else:
      self.log.info("Link Down: %s - %s" % (switch1, switch2))
      # event.remove may be duplicated as links are two-way
      try:
        self.graph.remove_edge(switch1, switch2)
      except nx.NetworkXError as e:
        # Edge was already removed
        self.log.info(e.message)

      # Clear the entire flow table of all switches!
      clear = of.ofp_flow_mod(command=of.OFPFC_DELETE)
      for switch in self.graph.nodes():
        self.graph.node[switch]["connection"].send(clear)

      # Remove isolated node if any
      # if nx.is_isolate(self.graph, switch1):
      #   self.graph.remove_node(switch1)
      # if nx.is_isolate(self.graph, switch2):
      #   self.graph.remove_node(switch2)

  def _handle_openflow_ConnectionUp(self, event):
    self.graph.add_node(event.dpid, connection=event.connection)

    # Clear the entire flow table of the switches!
    event.connection.send(of.ofp_flow_mod(command=of.OFPFC_DELETE))

  def _handle_openflow_ConnectionDown(self, event):
    self.log.info("Connection Down: %s" % event.dpid)
    self.graph.remove_node(event.dpid)

  def _handle_openflow_PacketIn(self, event):
    """
    TODO: Refactor this method
    """
    packet = event.parsed
    source = packet.src
    destination = packet.dst

    if destination.is_multicast:
      # Flood the packet
      # TODO: Install new flow instead of crafting new packet (hold down?)
      message = of.ofp_packet_out()
      message.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
      message.data = event.ofp
      message.in_port = event.port
      event.connection.send(message)
      return

    entryByMAC = core.host_tracker.entryByMAC
    known_hosts = entryByMAC.keys()

    if (source not in known_hosts) or (destination not in known_hosts):
      # Ignore non-end-to-end packet
      return

    from_host = entryByMAC[source]
    to_host = entryByMAC[destination]

    path = nx.shortest_path(self.graph, from_host.dpid, to_host.dpid)
    match = of.ofp_match.from_packet(packet)
    match.in_port = None

    self.log.info("Installing path from host %s to host %s" % (source, destination))

    # Install flows
    # first = True
    for from_switch, to_switch in utils.pairwise(path):
      self.log.info("Installing flow from switch %s to switch %s" % (from_switch, to_switch))
      portByDpid = self.graph.get_edge_data(from_switch, to_switch)["portByDpid"]
      message = of.ofp_flow_mod()
      message.match = match
      message.idle_timeout = self.flow_idle_timeout
      message.hard_timeout = self.flow_hard_timeout
      message.actions.append(of.ofp_action_output(port=portByDpid[from_switch]))

      # if first:
        # message.buffer_id = event.ofp.buffer_id
        # first = False

      self.graph.node[from_switch]['connection'].send(message)

    # Install final flow
    self.log.info("Installing final flow from switch %s to host %s" % (path[-1], destination))
    message = of.ofp_flow_mod()
    message.match = match
    message.idle_timeout = self.flow_idle_timeout
    message.hard_timeout = self.flow_hard_timeout
    message.actions.append(of.ofp_action_output(port=to_host.port))
    self.graph.node[path[-1]]['connection'].send(message)

  def _handle_openflow_ErrorIn(self, event):
    # Log all OpenFlow errors
    self.log.error(event.asString())
