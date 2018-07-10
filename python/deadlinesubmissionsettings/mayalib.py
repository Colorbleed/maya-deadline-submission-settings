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
        log.error("No node found callen '{}'".format(instance))
        return

    instances = cmds.ls("*:{}".format(instance))
    if len(instances) > 1:
        raise RuntimeError("Found multiple rendergloablDefault instances, "
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
    machine_list = settings.get("Whitelist", settings.get("Blacklist"))
    cmds.setAttr("{}.whitelist".format(instance), "Whitelist" in settings)

    cmds.setAttr("{}.suspendPublishJob".format(instance),
                 settings["suspendPublishJob"])
    cmds.setAttr("{}.includeDefaultRenderLayer".format(instance),
                 settings["includeDefaultRenderLayer"])

    cmds.setAttr("{}.extendFrames".format(instance), settings["extendFrames"])

    cmds.setAttr("{}.priority".format(instance), settings["priority"])

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

    suspend_attr = "{}.suspendPublishJob".format(instance)
    extend_attr = "{}.extendFrames".format(instance)
    settings["suspendPublishJob"] = cmds.getAttr(suspend_attr)
    settings["extendFrames"] = extend_attr
    settings["priority"] = cmds.getAttr("{}.priority".format(instance))

    include_def_layer = "{}.includeDefaultRenderLayer".format(instance)
    settings["includeDefaultRenderLayer"] = cmds.getAttr(include_def_layer)

    if cmds.getAttr("{}.whitelist".format(instance)):
        settings["Whitelist"] = ""

    return settings
