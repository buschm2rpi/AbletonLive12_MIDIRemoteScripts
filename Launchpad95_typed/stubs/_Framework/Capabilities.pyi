"""Type stub for ``_Framework.Capabilities`` (type-checking only)."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

GENERIC_SCRIPT_KEY: str
PORTS_KEY: str
CONTROLLER_ID_KEY: str
TYPE_KEY: str
FIRMWARE_KEY: str
AUTO_LOAD_KEY: str
VENDORID: str
PRODUCTIDS: str
MODEL_NAMES: str
DIRECTIONKEY: str
PORTNAMEKEY: str
MACNAMEKEY: str
PROPSKEY: str
HIDDEN: str
SYNC: str
SCRIPT: str
NOTES_CC: str
REMOTE: str
PLAIN_OLD_MIDI: str


def inport(port_name: str = "", props: List[str] = [],
           mac_name: Optional[str] = None) -> Dict[str, Any]:
    ...


def outport(port_name: str = "", props: List[str] = [],
            mac_name: Optional[str] = None) -> Dict[str, Any]:
    ...


def controller_id(vendor_id: int, product_ids: List[int],
                  model_name: Union[str, List[str]]) -> Dict[str, Any]:
    ...
