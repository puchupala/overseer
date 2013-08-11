class PathPreferenceTable(object):
  # TODO: More comprehensive table implementation

  DEFAULT           = 0x01
  MAXIMUM_BANDWIDTH = 0x02
  MINIMUM_LATENCY   = 0x03

  # Used as path_identifier value
  WILDCARD = -1

  def __init__(self):
    self._table = dict()

  def match(self, path_identifier):
    """
    Sequence

    1. Try exact match
    2. Try IP + dest port match
    3. Try IP + src port match
    4. Try IP-only match
    5. See if there is all-wildcard entry in the table
    6. Return DEFAULT
    """
    try:  # Exact match
      return self._table[path_identifier]
    except KeyError:
      try:  # IP + dest port
        path_identifier = PathPreferenceTable.create_path_identifier(
          path_identifier[0], PathPreferenceTable.WILDCARD, path_identifier[2], path_identifier[3]
        )
        return self._table[path_identifier]
      except KeyError:
        try:  # IP + src port
          path_identifier = PathPreferenceTable.create_path_identifier(
            path_identifier[0], path_identifier[1], path_identifier[2], PathPreferenceTable.WILDCARD
          )
          return self._table[path_identifier]
        except KeyError:
          try:  # IP-only
            path_identifier = PathPreferenceTable.create_path_identifier(
              path_identifier[0], PathPreferenceTable.WILDCARD, path_identifier[2], PathPreferenceTable.WILDCARD
            )
            return self._table[path_identifier]
          except KeyError:
            try:  # User-defined default
              path_identifier = PathPreferenceTable.create_path_identifier(
                PathPreferenceTable.WILDCARD, PathPreferenceTable.WILDCARD, PathPreferenceTable.WILDCARD, PathPreferenceTable.WILDCARD
              )
              return self._table[path_identifier]
            except KeyError:
              return PathPreferenceTable.DEFAULT

  def add_entry(self, path_identifier, preference):
    self.update_entry(path_identifier, preference)

  def update_entry(self, path_identifier, preference):
    self._table[path_identifier] = preference

  def remove_entry(self, path_identifier):
    try:
      del self._table[path_identifier]
    except KeyError:
      pass

  @staticmethod
  def create_path_identifier(from_ip, from_port, to_ip, to_port):
    """
    Create path identifier to use with flow-preference table

    The identifier is just a tuple containing various information
    """
    return (from_ip, from_port, to_ip, to_port)
