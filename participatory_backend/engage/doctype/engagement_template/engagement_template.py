# Copyright (c) 2023, Steve Nyaga and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe.utils import cint
from frappe import _

class EngagementTemplate(Document):
	def validate(self):
		# check there are no child tables
		if self.items:
			for itm in self.items:
				exists = frappe.db.exists("DocType", itm.doctype_item)
				if not exists:
					frappe.throw(_(f"Row {itm.idx}. Doctype {itm.doctype_item} does not exist"))
				is_table = frappe.db.get_value("DocType", itm.doctype_item, "istable")
				if cint(is_table):
					frappe.throw(_(f"Row {itm.idx}. Doctype {itm.doctype_item} is a Child Table"))
