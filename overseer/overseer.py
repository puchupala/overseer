# Import some POX stuff
from pox.core import core                     # Main POX object
import pox.openflow.libopenflow_01 as of      # OpenFlow 1.0 library
# import pox.lib.packet as pkt                  # Packet parsing/construction
# from pox.lib.addresses import EthAddr         # Address types
# import pox.lib.revent as revent               # Event library
# import pox.lib.recoco as recoco               # Multitasking library
import networkx as nx
import utils
from path_preference_table import PathPreferenceTable
from mst import maximum_spanning_tree


class Overseer (object):
  """
  Overseer - POX Component Implementing Bandwith/Latency-aware OpenFlow Controller
  """

  # LATENCY_WEIGHT_LABEL = "latency"
  # BANDWIDTH_WEIGHT_LABEL = "inversed_bandwidth"

  _core_name = "overseer"  # We want to be core.overseer

  def __init__(self, flow_idle_timeout=10, flow_hard_timeout=30,
                default_latency=1, default_bandwidth=100):
    core.listen_to_dependencies(self)

    self.log = core.getLogger()
    # self.path_preference_table = PathPreferenceTable.Instance()
    self.path_preference_table = PathPreferenceTable()
    self.flow_idle_timeout = flow_idle_timeout
    self.flow_hard_timeout = flow_hard_timeout
    self.default_latency = default_latency  # Milliseconds
    self.default_bandwidth = default_bandwidth  # Megabits
    self.path_preferences = dict()

  def _handle_overseer_topology_LinkUp(self, event):
    graph = core.overseer_topology.graph

    # dpid1 -> dpid2
    graph.edge[event.dpid1][event.dpid2][PathPreferenceTable.MAXIMUM_BANDWIDTH] = self.default_bandwidth
    graph.edge[event.dpid1][event.dpid2][PathPreferenceTable.MINIMUM_LATENCY] = self.default_latency
    graph.edge[event.dpid1][event.dpid2][PathPreferenceTable.DEFAULT] = 1

    # dpid2 -> dpid1
    graph.edge[event.dpid2][event.dpid1][PathPreferenceTable.MAXIMUM_BANDWIDTH] = self.default_bandwidth
    graph.edge[event.dpid2][event.dpid1][PathPreferenceTable.MINIMUM_LATENCY] = self.default_latency
    graph.edge[event.dpid2][event.dpid1][PathPreferenceTable.DEFAULT] = 1

  def _handle_openflow_PacketIn(self, event):
    # TODO: Refactor this method
    packet = event.parsed
    source = packet.src
    destination = packet.dst

    if destination.is_multicast:
      # Flood the packet
      # TODO: Install new flow instead of crafting new packet (hold down?)
      message = of.ofp_packet_out()
      message.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
      message.buffer_id = event.ofp.buffer_id
      # message.data = event.ofp
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

    path = self.get_path(from_host.dpid, to_host.dpid, packet)
    match = of.ofp_match.from_packet(packet)
    match.in_port = None

    self.log.info("Installing path from host %s to host %s" % (source, destination))

    # Install flows
    # TODO: Handle buffer_id properly
    # first = True
    for from_switch, to_switch in utils.pairwise(path):
      self.log.info("Installing flow from switch %x to switch %x" % (from_switch, to_switch))
      portByDpid = core.overseer_topology.graph.get_edge_data(from_switch, to_switch)["portByDpid"]
      message = of.ofp_flow_mod()
      message.match = match
      message.idle_timeout = self.flow_idle_timeout
      message.hard_timeout = self.flow_hard_timeout
      message.actions.append(of.ofp_action_output(port=portByDpid[from_switch]))

      # if first:
        # message.buffer_id = event.ofp.buffer_id
        # first = False

      core.overseer_topology.graph.node[from_switch]['connection'].send(message)

    # Install final flow
    self.log.info("Installing final flow from switch %x to host %s" % (path[-1], destination))
    message = of.ofp_flow_mod()
    message.match = match
    message.idle_timeout = self.flow_idle_timeout
    message.hard_timeout = self.flow_hard_timeout
    message.actions.append(of.ofp_action_output(port=to_host.port))
    core.overseer_topology.graph.node[path[-1]]['connection'].send(message)

  def get_path(self, from_dpid, to_dpid, packet):
    # TODO: Support IPv6

    tcp_packet = packet.find("tcp")
    udp_packet = packet.find("udp")
    ip_packet = packet.find("ipv4")

    if tcp_packet is not None:
      path_identifier = PathPreferenceTable.create_path_identifier(
        ip_packet.srcip, tcp_packet.srcport, ip_packet.dstip, tcp_packet.dstport
      )
    elif udp_packet is not None:
      path_identifier = PathPreferenceTable.create_path_identifier(
        ip_packet.srcip, udp_packet.srcport, ip_packet.dstip, udp_packet.dstport
      )
    elif ip_packet is not None:
      path_identifier = PathPreferenceTable.create_path_identifier(
        ip_packet.srcip, PathPreferenceTable.WILDCARD, ip_packet.dstip, PathPreferenceTable.WILDCARD
      )
    else:
      path_identifier = PathPreferenceTable.create_path_identifier(
        PathPreferenceTable.WILDCARD, PathPreferenceTable.WILDCARD, PathPreferenceTable.WILDCARD, PathPreferenceTable.WILDCARD
      )

    preference = self.path_preference_table.match(path_identifier)
    if preference is PathPreferenceTable.MAXIMUM_BANDWIDTH:
      # Interim solution: use path on maximum spanning tree for max bw path
      # graph = maximum_spanning_tree(core.overseer_topology.graph, PathPreferenceTable.MAXIMUM_BANDWIDTH)
      # return nx.shortest_path(graph, from_dpid, to_dpid, preference)
      from weighted import dijkstra_path as maximin_path
      return maximin_path(core.overseer_topology.graph, from_dpid, to_dpid, preference)
    else:
      return nx.shortest_path(core.overseer_topology.graph, from_dpid, to_dpid, preference)

  def _handle_openflow_ErrorIn(self, event):
    # Log all OpenFlow errors
    self.log.error("OF:%s" % event.asString())

  def _handle_overseer_topology_Update(self, event):
    # TODO: Update all-pair shortest paths using Floyd-Warshall algorithm
    pass
