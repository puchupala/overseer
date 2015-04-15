"""
Fires up overseer and related components
"""


def launch():
  import pox.log.level
  pox.log.level.launch(CRITICAL=True)
  import samples.pretty_log
  samples.pretty_log.launch()
  # import pox.openflow
  # pox.openflow.launch()
  import pox.openflow.discovery
  pox.openflow.discovery.launch()
  import pox.misc.gephi_topo
  pox.misc.gephi_topo.launch()
  import pox.host_tracker
  pox.host_tracker.launch()
  import overseer.topology
  overseer.topology.launch()
  import pox.openflow.spanning_tree
  pox.openflow.spanning_tree.launch(no_flood=True, hold_down=True)
  import overseer.overseer
  overseer.overseer.launch()
  import pox.web.webcore
  pox.web.webcore.launch()
  import overseer.api
  overseer.api.launch()
  import pox.py
  pox.py.launch()
