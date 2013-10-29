# Import some POX stuff
from pox.core import core                     # Main POX object
import pox.openflow.libopenflow_01 as of      # OpenFlow 1.0 library
# import pox.lib.packet as pkt                  # Packet parsing/construction
# from pox.lib.addresses import EthAddr         # Address types
# import pox.lib.revent as revent               # Event library
from pox.lib.revent import EventMixin
# import pox.lib.recoco as recoco               # Multitasking library
import networkx as nx
import events


class Topology (EventMixin):
  """
  Overseer Topology

  Automatic network topology sensing and graph data structure creation
  powered by NetworkX
  """

  _core_name = "overseer_topology"  # We want to be core.overseer_topology

  _eventMixin_events = [
    events.LinkUp,
    events.LinkDown,
    events.SwitchUp,
    events.SwitchDown,
    events.Update,
  ]

  def __init__ (self):
    core.listen_to_dependencies(self)

    self.log = core.getLogger()
    self.graph = nx.DiGraph()  # Use dpid as node

  def _handle_openflow_discovery_LinkEvent (self, event):
    # added/removed may be duplicated as links are two-way
    if event.added:
      self.__handle_openflow_discovery_LinkUp(event)
    else:
      self.__handle_openflow_discovery_LinkDown(event)

  def __handle_openflow_discovery_LinkUp (self, event):
    """
    Handle for LinkUp psuedo-event

    method name was deliberatly spell like this to keep  automatic
    event handling with self.listen_to_dependencies(self) happy.
    openflow_discovery don't actually have LinkUp but we
    want to write it this way to keep the code tidy.
    """
    link = event.link
    # Note that dpid might be Int or Long or perhaps something else entirely!
    # We may need to care about their types if problems arise
    dpid1 = link.dpid1
    dpid2 = link.dpid2

    if self.graph.has_edge(dpid1, dpid2) and self.graph.has_edge(dpid2, dpid1):
      # Duplicated event
      return

    # dpid1 -> dpid2
    if not self.graph.has_edge(dpid1, dpid2):
      self.graph.add_edge(dpid1, dpid2, portByDpid={
        dpid1: link.port1,
        dpid2: link.port2,
      })

    # dpid2 -> dpid1
    if not self.graph.has_edge(dpid2, dpid1):
      self.graph.add_edge(dpid2, dpid1, portByDpid={
        dpid2: link.port2,
        dpid1: link.port1,
      })

    self.log.info("Link Up: %s - %s" % (dpid1, dpid2))
    self.raiseEvent(events.LinkUp, dpid2, dpid1)

  def __handle_openflow_discovery_LinkDown (self, event):
    """
    Handle for LinkDown psuedo-event

    method name was deliberatly spell like this to keep  automatic
    event handling with self.listen_to_dependencies(self) happy.
    openflow_discovery don't actually have LinkDown but we
    want to write it this way to keep the code tidy.
    """
    link = event.link
    # Note that dpid might be Int or Long or perhaps something else entirely!
    # We may need to care about their types if problems arise
    dpid1 = link.dpid1
    dpid2 = link.dpid2

    self.log.info("Link Down: %s - %s" % (dpid1, dpid2))

    try:
      self.graph.remove_edge(dpid1, dpid2)
    except nx.NetworkXError as e:
      # Edge was already removed
      self.log.info(e.message)
      return

    try:
      self.graph.remove_edge(dpid2, dpid1)
    except nx.NetworkXError as e:
      # Edge was already removed
      self.log.info(e.message)
      return

    # Clear the entire flow table of all switches!
    clear = of.ofp_flow_mod(command=of.OFPFC_DELETE)
    for switch in self.graph.nodes():
      self.graph.node[switch]["connection"].send(clear)

    # TODO: Remove isolated node if any
    self.raiseEvent(events.LinkDown, dpid1, dpid2)

  def _handle_openflow_ConnectionUp (self, event):
    self.log.info("Connection Up: %s" % event.dpid)
    self.graph.add_node(event.dpid, connection=event.connection)

    # Clear the entire flow table of the switches!
    event.connection.send(of.ofp_flow_mod(command=of.OFPFC_DELETE))

    self.raiseEvent(events.SwitchUp, event.dpid)

  def _handle_openflow_ConnectionDown (self, event):
    self.log.info("Connection Down: %s" % event.dpid)
    self.graph.remove_node(event.dpid)
    self.raiseEvent(events.SwitchDown, event.dpid)

  def raiseEvent (self, event, *args, **kw):
    """
    Whenever we raise any event, we also raise an Update, so we extend
    the implementation in EventMixin.

    Modified from the one in topology component
    """
    rv = super(Topology, self).raiseEvent(event, *args, **kw)
    if type(event) is not events.Update:
      super(Topology, self).raiseEvent(events.Update, event)
    return rv
