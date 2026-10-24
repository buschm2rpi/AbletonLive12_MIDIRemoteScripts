from _Framework.Capabilities import CONTROLLER_ID_KEY, PORTS_KEY, NOTES_CC, SCRIPT, SYNC, REMOTE, controller_id, inport, outport
from Launchpad95_typed.LP_X import LP_X

def create_instance(c_instance):
	""" Creates and returns the Launchpad script """
	return LP_X(c_instance=c_instance)

def get_capabilities():
	return {
		CONTROLLER_ID_KEY: controller_id(
			vendor_id = 4661,
			product_ids = [
				259 # Launchpad X
			],
			model_name =
			[
				'Launchpad X'
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
