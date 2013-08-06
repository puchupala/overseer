"""
Overseer Topology

Requirements (in orders):
- openflow.discovery
- openflow.host_tracker

This component provide automatic network sensing and topology
data structure creation as well as keeping it updated
"""

# Import some POX stuff
from pox.core import core                     # Main POX object
# import pox.lib.util as poxutil                # Various util functions
import topology                               # Overseer

# Create a logger for this component
# log = core.getLogger()


def register ():
  if not core.hasComponent(topology.Topology._core_name):
    core.registerNew(topology.Topology)


# @poxutil.eval_args
def launch ():
  # Waiting for dependencies
  core.call_when_ready(register, ["openflow_discovery", "host_tracker"])
