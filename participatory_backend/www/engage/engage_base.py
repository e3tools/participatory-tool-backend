import frappe
from participatory_backend.engage.utils import get_active_engagements
import datetime
from frappe.utils import cint

def get_context(context):
	context.no_cache = 1
	settings = frappe.db.get_singles_dict("Engage Settings")
	context.settings = settings
	footer_columns = (1 if settings.column_1_title else 0 ) + (1 if settings.column_2_title else 0 ) + (1 if settings.column_3_title else 0)   
	context.footer_col_width = cint(12 / footer_columns if footer_columns else 12)