import logging

import maya.cmds as cmds
import avalon
from avalon.maya import lib

log = logging.getLogger("DSS Maya Lib")


def lock_attr(attribute):
    cmds.setAttr(attribute, lock=True)


def unlock_attr(attribute):
    cmds.setAttr(attribute, lock=False)


def validate_render_instance(instance):
    """Validate if the attributes are correct"""

    data = lib.read(instance)

    assert data["id"] == "avalon.renderglobals", ("Node '%s' is not a "
                                                  "renderglobal node"
                                                  % instance)
    assert data["family"] == "colorbleed.renderglobals", ("Family is not"
                                                          "renderglobals")

    machine_list_attr = "{}.machineList".format(instance)
    locked_list = cmds.getAttr(machine_list_attr, lock=True)
    if not locked_list:
        lock_attr(machine_list_attr)


def find_render_instance():
    """Find the current render settings instance

    Returns:
        str
    """

    instance = "renderglobalsDefault"
    if not cmds.objExists(instance):
        log.error("No node found called '{}'".format(instance))
        return

    instances = cmds.ls("*:{}".format(instance))
    if len(instances) > 1:
        raise RuntimeError("Found multiple renderglobalDefault instances, "
                           "there can only be one")

    # Ensure attributes are
    validate_render_instance(instance)

    return instance


def apply_settings(instance, settings):
    """Set the attributes of the instance based on the UI settings

    Args:
        instance(str): name of the renderglobalsDefault instance
        settings(dict): values from the

    """

    ignore = ["cbId", "id", "family", "machineList", "useLegacyRenderLayers"]
    attributes = [a for a in cmds.listAttr(instance, userDefined=True)
                  if a not in ignore]

    for attr in attributes:
        attribute = "{}.{}".format(instance, attr)
        if attr == "whitelist":
            value = "Whitelist" in settings
        elif attr not in settings:
            log.error("Attribute '%s' missing in 'renderglobalDefault'! "
                      "Please re-create the instance" % attr)
            continue
        else:
            value = settings[attr]

        # Check if attribute is enum
        attr_type = cmds.attributeQuery(attr, node=instance, attributeType=True)
        if attr_type == "enum":
            # Returns ["stuff:is:different"]
            enums = cmds.attributeQuery(attr, node=instance, listEnum=True)
            enum_list = enums[0].split(":")
            idx = enum_list.index(value)
            value = idx

        if isinstance(value, basestring):
            cmds.setAttr(attribute, value, type="string")
        else:
            cmds.setAttr(attribute, value)

    machine_list = settings.get("Whitelist", settings.get("Blacklist"))

    # Unlock and set value, relock after setting
    machine_list_attr = "{}.machineList".format(instance)
    unlock_attr(machine_list_attr)
    cmds.setAttr(machine_list_attr, machine_list, type="string")
    lock_attr(machine_list_attr)


def read_settings(instance):
    """Read the render globals instance settings

    Args:
        instance(str): name of the node

    Returns:
        dict
    """

    settings = dict()

    # Get attributes of instance
    ignore = ["family", "id"]
    user_defined = cmds.listAttr(instance, userDefined=True)
    attributes = [attr for attr in user_defined if attr not in ignore]

    for attr in attributes:
        atrribute = "{}.{}".format(instance, attr)
        if attr == "whitelist":
            attr = attr.title()
        settings[attr] = cmds.getAttr(atrribute)

    return settings


def create_renderglobals_node():
    """Create renderglobals node for scene"""

    log.info("Creating renderglobals node")

    asset = avalon.Session["AVALON_ASSET"]
    name = "renderglobalsDefault"
    family = "colorbleed.renderglobals"

    avalon.api.create(name=name, asset=asset, family=family)

    return name
