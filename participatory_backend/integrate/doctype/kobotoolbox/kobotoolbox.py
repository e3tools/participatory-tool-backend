# Copyright (c) 2024, Steve Nyaga and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import requests
import json
from frappe import _
from participatory_backend.integrate.utils.kobotoolbox import get_metadata, get_data

class KoboToolbox(Document):
	@frappe.whitelist()
	def test_connection(self):
		if get_data(self.name): # get_metadata(self.name):
			frappe.msgprint(_("Connection successful"))
		else:
			frappe.errprint(_("Connection could not be established"))