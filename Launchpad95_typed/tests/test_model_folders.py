"""Per-model script folders (Phases 4-5 of plan_launchpad_base_refactor.md).

Each folder is a self-contained Live script package: Live imports the folder,
calls ``create_instance`` and gets the statically configured class for that
model (no runtime detection). All four folders now contain only ``__init__.py``
and import their class from ``Launchpad95_typed``.

Folders map to the concrete classes in ``Launchpad95_typed``:

- ``Launchpad95_MK1`` -> ``LP_MK1`` (product ids 14 / 32 / 54)
- ``Launchpad95_MK2`` -> ``LP_MK2`` (product ids 105-120)
- ``Launchpad95_MK3`` -> ``LP_MK3`` (product id 275)
- ``Launchpad95_X``   -> ``LP_X``   (product id 259)
"""

import importlib

import pytest

from _Framework.Capabilities import CONTROLLER_ID_KEY, PORTS_KEY

# (folder, expected class name)
NEW_FOLDERS = [
    ("Launchpad95_MK1", "LP_MK1"),
    ("Launchpad95_MK2", "LP_MK2"),
    ("Launchpad95_MK3", "LP_MK3"),
    ("Launchpad95_X", "LP_X"),
]

# product ids each folder claims (only its own hardware)
PRODUCT_IDS = {
    "Launchpad95_MK1": [14, 32, 54],
    "Launchpad95_MK2": list(range(105, 121)),
    "Launchpad95_MK3": [275],
    "Launchpad95_X": [259],
}


@pytest.mark.parametrize("folder,class_name", NEW_FOLDERS)
def test_create_instance_returns_static_class(host, folder, class_name):
    module = importlib.import_module(folder)
    surface = module.create_instance(host)
    assert type(surface).__name__ == class_name
    # per-model classes build eagerly; no handshake-deferred construction
    assert surface._init_done is True


@pytest.mark.parametrize("folder,class_name", NEW_FOLDERS)
def test_capabilities(host, folder, class_name):
    module = importlib.import_module(folder)
    caps = module.get_capabilities()
    controller_id = caps[CONTROLLER_ID_KEY]
    assert controller_id["vendor_id"] == 4661
    assert controller_id["product_ids"] == PRODUCT_IDS[folder]
    # one model name per product id (the legacy folders' catch-all list
    # does not guarantee this, which is why the new folders stay per-model)
    assert len(controller_id["product_ids"]) == len(controller_id["model_names"])
    # every folder keeps the shared proven port set
    assert len(caps[PORTS_KEY]) == 4


def test_mk2_folder_uses_typed_class(host):
    # Phase 5 dedupe: the folder no longer ships its own LaunchpadBase/LP_MK2;
    # it re-exports the statically configured class from Launchpad95_typed.
    from Launchpad95_typed.LP_MK2 import LP_MK2

    module = importlib.import_module("Launchpad95_MK2")
    surface = module.create_instance(host)
    assert type(surface) is LP_MK2
    assert surface._selector is not None
    assert surface._mk2_rgb is True
