import frappe
from participatory_backend.engage.utils import get_active_engagements
from participatory_backend.www.engage.engage_base import get_context as get_base_context

def get_context(context):
	get_base_context(context)
	context.no_cache = 1
	context.engagements = get_active_engagements()