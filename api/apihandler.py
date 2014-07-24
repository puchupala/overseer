# Import some POX stuff
from pox.core import core                     # Main POX object
# import pox.lib.packet as pkt                  # Packet parsing/construction
# from pox.lib.addresses import EthAddr         # Address types
# import pox.lib.recoco as recoco               # Multitasking library
# from pox.web.webcore import SplitRequestHandler
from pox.web.jsonrpc import JSONRPCHandler, make_error
from overseer.overseer.path_preference_table import PathPreferenceTable
import utils


class ApiHandler (JSONRPCHandler):
  """
  Overseer API

  """

  OPTIONS = {
    "shortest_path": PathPreferenceTable.DEFAULT,
    "maximum_bandwidth": PathPreferenceTable.MAXIMUM_BANDWIDTH,
    "minimum_latency": PathPreferenceTable.MINIMUM_LATENCY,
  }
  REVERSED_OPTIONS = utils.swap_key_values(OPTIONS)

  # def __init__(self, *args, **kw):
  #   super(ApiHandler, self).__init__(*args, **kw)

  def _exec_ping(self):
    return utils.create_response("pong")

  def _exec_echo(self, message="Goodbye, sad world!"):
    return utils.create_response(message)

  def _exec_get_options(self):
    return utils.create_response(ApiHandler.OPTIONS.keys())

  # def _exec_get_table(self):
  #   table = core.overseer.path_preference_table._table
  #   result = list()
  #   for path_identifier in table:
  #     result.append({
  #       "path_identifier": utils.serialize_path_identifier(path_identifier),
  #       "value": ApiHandler.REVERSED_OPTIONS[table[path_identifier]]
  #     })
  #   return utils.create_response(result)

  def _exec_get_table(self):
    table = core.overseer.path_preference_table._table
    result = [{
      "path_identifier": utils.serialize_path_identifier(path_identifier),
      "value": ApiHandler.REVERSED_OPTIONS[table[path_identifier]]
    } for path_identifier in table]
    return utils.create_response(result)

  def _exec_get_entry(self, quintet):
    try:
      path_identifier = utils.deserialize_path_identifier(quintet)
      entry = core.overseer.path_preference_table._table[path_identifier]
      return utils.create_response(ApiHandler.REVERSED_OPTIONS[entry])
    except KeyError:
      return make_error("No such entry in path preference table")

  def _exec_set_entry(self, quintet, option):
    try:
      path_identifier = utils.deserialize_path_identifier(quintet)
      core.overseer.path_preference_table._table[path_identifier] = ApiHandler.OPTIONS[option]
      return utils.create_response("")
    except KeyError:
      return make_error("No such entry in path preference table")

  def _exec_remove_entry(self, quintet):
    try:
      path_identifier = utils.deserialize_path_identifier(quintet)
      del core.overseer.path_preference_table._table[path_identifier]
      return utils.create_response("")
    except KeyError:
      return make_error("No such entry in path preference table")

  def _exec_update_bandwidth(self, dpid1, dpid2, bandwidth):
    return self._update_weight(dpid1, dpid2, ApiHandler.OPTIONS["maximum_bandwidth"], bandwidth)

  def _exec_update_latency(self, dpid1, dpid2, latency):
    return self._update_weight(dpid1, dpid2, ApiHandler.OPTIONS["minimum_latency"], latency)

  def _update_weight(self, dpid1, dpid2, weight="weight", value="1"):
    try:
      graph = core.overseer_topology.graph
      dpid1 = int(dpid1, 16)
      dpid2 = int(dpid2, 16)
      value = float(value)
      if graph.has_edge(dpid1, dpid2):
        graph[dpid1][dpid2][weight] = value
        return utils.create_response("")
      else:
        return make_error("Invalid link")
    except ValueError:
      return make_error("dpid must be hex and value must be float")
