# Import some POX stuff
# from pox.core import core                     # Main POX object
# import pox.lib.packet as pkt                  # Packet parsing/construction
# from pox.lib.addresses import EthAddr         # Address types
# import pox.lib.recoco as recoco               # Multitasking library
# from pox.web.webcore import SplitRequestHandler
from pox.web.jsonrpc import JSONRPCHandler


class ApiHandler (JSONRPCHandler):
  """
  Overseer API

  """
  def _exec_ping(self):
    return {"result": "pong"}

  def _exec_echo(self, message="Goodbye, sad world!"):
    return {"result": message}
