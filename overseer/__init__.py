"""
Overseer main component
Based on a skeleton component

Requirements (in orders):
- overseer.topology
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
# log = core.getLogger()


def register (*args, **kw):
  if not core.hasComponent(overseer.Overseer._core_name):
    # log.info("Overseer registered")
    core.registerNew(overseer.Overseer, *args, **kw)


@poxutil.eval_args
def launch ():
  # TODO: Get and pass params to Overseer object
  # Waiting for dependencies
  core.call_when_ready(register, ["overseer_topology", "host_tracker"])
