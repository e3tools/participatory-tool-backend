# Copyright (c) 2024, Steve Nyaga and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class EngageSettings(Document):
	def validate(self):
		if self.column_1_title and not self.column_1_details:
			frappe.throw(_("You must specify Column 1 Contents"))
		if self.column_2_title and not self.column_2_details:
			frappe.throw(_("You must specify Column 2 Contents"))
		if self.column_3_title and not self.column_3_details:
			frappe.throw(_("You must specify Column 3 Contents"))
