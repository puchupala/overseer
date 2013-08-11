"""
Overseer REST API

Requirements (in orders):
- overseer.overseer
- web.webcore

REST API to Overseer component

"""

# Import some POX stuff
from pox.core import core          # Main POX object
import apihandler                         # Overseer API


def set_handlers ():
  core.WebServer.set_handler("/api", apihandler.ApiHandler, dict())

def launch ():
  # Waiting for dependencies
  core.call_when_ready(set_handlers, ["WebServer"])
