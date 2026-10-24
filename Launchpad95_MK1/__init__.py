from _Framework.Capabilities import CONTROLLER_ID_KEY, PORTS_KEY, NOTES_CC, SCRIPT, SYNC, REMOTE, controller_id, inport, outport
from Launchpad95_typed.LP_MK1 import LP_MK1

def create_instance(c_instance):
	""" Creates and returns the Launchpad script """
	return LP_MK1(c_instance=c_instance)

def get_capabilities():
	return {
		CONTROLLER_ID_KEY: controller_id(
			vendor_id = 4661,
			product_ids = [
				14, # Launchpad
				32, # Launchpad S
				54  # Launchpad Mini
			],
			model_name =
			[
				'Launchpad',
				'Launchpad S',
				'Launchpad Mini'
			]
		),
		PORTS_KEY:
			[
				inport(props = [NOTES_CC, REMOTE]),
				inport(props = [NOTES_CC, REMOTE, SCRIPT]),
				outport(props = [NOTES_CC, SYNC, REMOTE]),
				outport(props = [NOTES_CC, SYNC, REMOTE, SCRIPT])
			]
	}
