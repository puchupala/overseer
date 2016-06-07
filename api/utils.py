#from overseer.overseer.utils import create_path_identifier
from overseer.overseer.path_preference_table import PathPreferenceTable


def create_response(result=""):
    return {"result": result}


def swap_key_values(dictionary):
    return dict(zip(dictionary.values(), dictionary.keys()))


def serialize_path_identifier(path_identifier):
    path_identifier = [u"*" if field is PathPreferenceTable.WILDCARD else field for field in path_identifier]
    return (str(path_identifier[0]), path_identifier[1], str(path_identifier[2]), path_identifier[3])


def deserialize_path_identifier(quintet):
    # Convert any "*" to PathPreferenceTable.WILDCARD
    quintet = [PathPreferenceTable.WILDCARD if field == "*" else field for field in quintet]
    return PathPreferenceTable.create_path_identifier(quintet[0], quintet[1], quintet[2], quintet[3])

