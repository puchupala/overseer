"""
Fires up overseer and related components
"""


def launch ():
  # import pox.openflow
  # pox.openflow.launch()
  import pox.openflow.discovery
  pox.openflow.discovery.launch()
  import pox.misc.gephi_topo
  pox.misc.gephi_topo.launch()
  import pox.host_tracker
  pox.host_tracker.launch()
  import overseer.overseer
  overseer.overseer.launch()
  import pox.openflow.spanning_tree
  pox.openflow.spanning_tree.launch(no_flood=True, hold_down=True)
