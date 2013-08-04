"""
Overseer main component
Based on a skeleton component

Requirements (in orders):
- openflow.discovery
- openflow.host_tracker

Works with:
- openflow.spanning_tree

This component implement bandwidth/latency-aware OpenFlow controller.
More information coming soon. E-heh!
"""

# Import some POX stuff
from pox.core import core                     # Main POX object
import pox.lib.util as poxutil                # Various util functions
import overseer                               # Overseer

# Create a logger for this component
log = core.getLogger()


def register_components ():
  if not core.hasComponent(overseer.Overseer._core_name):
    log.info("Overseer registered")
    core.registerNew(overseer.Overseer)


@poxutil.eval_args
def launch ():
  # Waiting for dependencies
  core.call_when_ready(register_components, ["openflow_discovery", "host_tracker"])
