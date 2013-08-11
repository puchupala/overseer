from pox.lib.revent import Event


class LinkEvent (Event):
  """Abstrack class for LinkUp and LinkDown"""
  def __init__ (self, dpid1, dpid2):
    super(LinkEvent, self).__init__()
    self.dpid1 = dpid1
    self.dpid2 = dpid2


class LinkUp (LinkEvent):
  """LinkUp Event"""
  pass


class LinkDown (LinkEvent):
  """LinkUp Event"""
  pass


class SwitchEvent (Event):
  """Abstract class for SwitchUp and SwitchDown"""
  def __init__ (self, dpid):
    super(SwitchEvent, self).__init__()
    self.dpid


class SwitchUp (SwitchEvent):
  """SwitchUp Event"""
  pass


class SwitchDown (SwitchEvent):
  """SwitchDown Event"""
  pass
