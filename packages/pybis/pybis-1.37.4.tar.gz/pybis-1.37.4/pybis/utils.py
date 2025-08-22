#   Copyright ETH 2018 - 2025 Zürich, Scientific IT Services
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
import math
import re
from datetime import datetime

# display messages when in a interactive context (IPython or Jupyter)
try:
    get_ipython()
except Exception:
    VERBOSE = False
else:
    VERBOSE = True


def parse_jackson(input_json):
    """openBIS uses a library called «jackson» to automatically generate the JSON RPC output.
    Objects that are found the first time are added an attribute «@id».
    Any further findings only carry this reference id.
    This function is used to dereference the output.
    """
    interesting = [
        "tags",
        "registrator",
        "modifier",
        "owner",
        "type",
        "parents",
        "children",
        "containers",  # 'container',
        "properties",
        "experiment",
        "sample",
        "project",
        "space",
        "propertyType",
        "entityType",
        "propertyType",
        "propertyAssignment",
        "externalDms",
        "roleAssignments",
        "user",
        "person",
        "creatorPerson",
        "users",
        "authorizationGroup",
        "vocabulary",
        "validationPlugin",
        "dataSetPermId",
        "dataStore",
        "sampleType"
    ]
    found = {}

    def build_cache(graph):
        if isinstance(graph, list):
            for item in graph:
                build_cache(item)
        elif isinstance(graph, dict) and len(graph) > 0:
            for key, value in graph.items():
                if key in interesting:
                    if isinstance(value, dict):
                        if "@id" in value:
                            found[value["@id"]] = value
                        build_cache(value)
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                if "@id" in item:
                                    found[item["@id"]] = item
                                build_cache(item)
                elif isinstance(value, dict):
                    build_cache(value)
                elif isinstance(value, list):
                    build_cache(value)

    def deref_graph(graph):
        if isinstance(graph, list):
            for i, list_item in enumerate(graph):
                if isinstance(list_item, int):
                    # try: # TODO: use "if list_item in found" with found.get()
                    #     graph[i] = found[list_item]
                    # except KeyError:
                    #     pass
                    if list_item in found:
                        graph[i] = found.get(list_item)
                else:
                    deref_graph(list_item)
        elif isinstance(graph, dict) and len(graph) > 0:
            for key, value in graph.items():
                if key in interesting:
                    if isinstance(value, dict):
                        deref_graph(value)
                    elif isinstance(value, int):
                        graph[key] = found.get(value)
                    elif isinstance(value, list):
                        for i, list_item in enumerate(value):
                            if isinstance(list_item, int):
                                if list_item in found:
                                    value[i] = found[list_item]
                                else:
                                    value[i] = list_item
                elif isinstance(value, dict):
                    deref_graph(value)
                elif isinstance(value, list):
                    deref_graph(value)

    build_cache(input_json)
    deref_graph(found)
    deref_graph(input_json)


def check_datatype(type_name, value, is_multi_value=False):
    if is_multi_value:
        if type_name == "INTEGER":
            return all([isinstance(x, int) and not math.isnan(x) for x in value])
        if type_name == "REAL":
            return all([isinstance(x, (int, float)) and not math.isnan(x) for x in value])
        if type_name == "BOOLEAN":
            return all([isinstance(x, bool) for x in value])
        if type_name == "VARCHAR":
            return all([isinstance(x, str) for x in value])
    else:
        if type_name == "INTEGER":
            return isinstance(value, int) and not math.isnan(value)
        if type_name == "REAL":
            return isinstance(value, (int, float)) and not math.isnan(value)
        if type_name == "BOOLEAN":
            return isinstance(value, bool)
        if type_name == "VARCHAR":
            return isinstance(value, str)
        if type_name is not None and type_name.startswith("ARRAY"):
            return isinstance(value, list)
    return True


def split_identifier(ident):
    bla = []
    bla = ident.upper().split("/")
    results = {}
    try:
        if bla[0] == "":
            bla.pop(0)
        if bla[-1] == "":
            bla.pop(-1)
        results["space"] = bla.pop(0)
        results["code"] = bla.pop(-1)
        results["experiment"] = bla.pop(0)
    except Exception:
        pass

    return results


def format_timestamp(ts):
    if ts is None:
        return ""
    if ts != ts:  # test for NaN
        return ""
    return datetime.fromtimestamp(round(ts / 1000)).strftime("%Y-%m-%d %H:%M:%S")


def is_identifier(ident):
    # assume we got a sample identifier e.g. /TEST/TEST-SAMPLE
    match = re.search("/", ident)
    if match:
        return True
    else:
        return False


def is_permid(ident):
    match = re.match("^\d+\-\d+$", ident)
    if match:
        return True
    else:
        return False


def nvl(val, string=""):
    if val is None:
        return string
    return val


def extract_permid(permid):
    if not isinstance(permid, dict):
        return str(permid)
    return permid["permId"]


def extract_data_type(obj):
    if not isinstance(obj, dict):
        return "" if obj is None else str(obj)
    return "" if obj["dataType"] is None else obj["dataType"]


def extract(obj, property_name):
    if not isinstance(obj, dict):
        return "" if obj is None else str(obj)
    return "" if obj[property_name] is None else obj[property_name]


def extract_code(obj):
    if not isinstance(obj, dict):
        return "" if obj is None else str(obj)
    return "" if obj["code"] is None else obj["code"]


def extract_downloadUrl(obj):
    if not isinstance(obj, dict):
        return "" if obj is None else str(obj)
    return "" if obj["downloadUrl"] is None else obj["downloadUrl"]


def extract_name(obj):
    if not isinstance(obj, dict):
        return "" if obj is None else str(obj)
    return "" if obj["name"] is None else obj["name"]


def extract_deletion(obj):
    del_objs = []
    for deleted_object in obj["deletedObjects"]:
        del_objs.append(
            {
                "reason": obj["reason"],
                "permId": deleted_object["id"]["permId"],
                "type": deleted_object["id"]["@type"],
                "deletionId": obj["id"]["id"]
            }
        )
    return del_objs


def extract_attr(attr):
    def attr_func(obj):
        if isinstance(obj, dict):
            return obj.get(attr, "")
        else:
            return str(obj)

    return attr_func


def extract_identifier(ident):
    if not isinstance(ident, dict):
        return "" if ident is None else str(ident)
    return "" if ident["identifier"] is None else ident["identifier"]


def extract_identifiers(items):
    if not items:
        return []
    try:
        return [
            data["identifier"]["identifier"]
            if "identifier" in data
            else data["permId"]["permId"]
            for data in items
        ]
    except TypeError:
        return []


def extract_nested_identifier(ident):
    if not isinstance(ident, dict):
        return "" if ident is None else str(ident)
    return "" if ident["identifier"]["identifier"] is None else ident["identifier"]["identifier"]


def extract_nested_permid(permid):
    if not isinstance(permid, dict):
        return "" if permid is None else str(permid)
    return "" if permid["permId"]["permId"] is None else permid["permId"]["permId"]


def extract_nested_permids(items):
    if not isinstance(items, list):
        return []

    return list(item["permId"]["permId"] for item in items)


def extract_property_assignments(pas):
    pa_strings = []
    for pa in pas:
        if not isinstance(pa["propertyType"], dict):
            pa_strings.append(pa["propertyType"])
        else:
            pa_strings.append(pa["propertyType"]["label"])
    return pa_strings


def extract_role_assignments(ras):
    ra_strings = []
    for ra in ras:
        ra_strings.append(
            {
                "role": ra["role"],
                "roleLevel": ra["roleLevel"],
                "space": ra["space"]["code"] if ra["space"] else None,
            }
        )
    return ra_strings


def extract_person(person):
    if not isinstance(person, dict):
        if person is None:
            return ""
        else:
            return str(person)
    return person["userId"]


def extract_person_details(person):
    if not isinstance(person, dict):
        return str(person)
    return "{firstName} {lastName} <{email}>".format(**person)


def extract_id(id):
    if not isinstance(id, dict):
        return str(id)
    else:
        return id["techId"]


def extract_userId(user):
    if isinstance(user, list):
        return ", ".join([u["userId"] for u in user])
    elif isinstance(user, dict):
        return "" if user["userId"] is None else user["userId"]
    else:
        return "" if user is None else str(user)


def is_number(value):
    """detects whether a given value
    is either an integer or a floating point number
    1, 2, 3,  etc.
    1.0, 2.1, etc.
    .5, .6    etc.
    """
    number_regex = re.compile(r"^(?=.)([+-]?([0-9]*)(\.([0-9]+))?)$")
    return number_regex.search(value)


def extract_username_from_token(token: str) -> str:
    if token.startswith("$pat"):
        match = re.search(r"^\$pat-(?P<username>.*?)-.*", token)
    else:
        match = re.search(r"(?P<username>.*?)-.*", token)
    if match:
        return match.groupdict().get("username")
