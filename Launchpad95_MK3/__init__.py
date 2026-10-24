from _Framework.Capabilities import CONTROLLER_ID_KEY, PORTS_KEY, NOTES_CC, SCRIPT, SYNC, REMOTE, controller_id, inport, outport
from Launchpad95_typed.LP_MK3 import LP_MK3

def create_instance(c_instance):
	""" Creates and returns the Launchpad script """
	return LP_MK3(c_instance=c_instance)

def get_capabilities():
	return {
		CONTROLLER_ID_KEY: controller_id(
			vendor_id = 4661,
			product_ids = [
				275 # Launchpad Mini MK3
			],
			model_name =
			[
				'Launchpad Mini MK3'
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
