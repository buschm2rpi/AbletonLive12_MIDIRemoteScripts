# Decompiled with pycdc from Ableton Live 12 (Python 3.11).
# Some functions may be partial: pycdc cannot fully decompile 3.11 bytecode.

# Source Generated with Decompyle++
# File: __init__.pyc (Python 3.11)

from ableton.v3.control_surface.capabilities import AUTO_LOAD_KEY, CONTROLLER_ID_KEY, NOTES_CC, PORTS_KEY, SCRIPT, controller_id, inport, outport
from Osmose import OsmoseBase, Specification

def get_capabilities():
    return {
        AUTO_LOAD_KEY: True,
        PORTS_KEY: [
            inport(props = []),
            inport(props = []),
            inport(props = [
                NOTES_CC,
                SCRIPT]),
            outport(props = []),
            outport(props = []),
            outport(props = [
                SCRIPT])],
        CONTROLLER_ID_KEY: controller_id(vendor_id = 11796, product_ids = [
            27,
            29], model_name = [
            'Osmose CE 49',
            'Osmose CE 61']) }


def create_instance(c_instance):
    return Osmose_CE(specification = Specification, c_instance = c_instance)


class Osmose_CE(OsmoseBase):
    pass
