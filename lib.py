"""Library function for the Deadline Submission Setting application

Dependencies:
    - Avalon
"""

import logging

import avalon
from avalon.vendor import requests


log = logging.getLogger("DSS - Lib")


def query(argument):
    """Lazy wrapper for request.get"""

    response = requests.get(argument)
    if not response.ok:
        log.error("Non-script command is not available:'{}'".format(query))
        log.error("Details: {}".format(response.text))
        result = []
    else:
        result = response.json()

    return result


def get_machine_list(debug=None):
    """Fetch the machine list (slaves) from Deadline"""
    AVALON_SESSION = debug or avalon.Session["AVALON_DEADLINE"]
    argument = "{}/api/slaves?NamesOnly=true".format(AVALON_SESSION)
    return query(argument=argument)


def get_pool_list(debug=None):
    """Get all pools from Deadline"""
    AVALON_SESSION = debug or avalon.Session["AVALON_DEADLINE"]
    argument = "{}/api/pools?NamesOnly=true".format(AVALON_SESSION)
    return query(argument)


def get_group_list(debug=None):
    """Get all groups from Deadline"""
    AVALON_SESSION = debug or avalon.Session["AVALON_DEADLINE"]
    argument = "{}/api/groups?NamesOnly=true".format(AVALON_SESSION)
    return query(argument)


def get_machine_state():
    pass
