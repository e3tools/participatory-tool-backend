# Copyright (c) 2024, Steve Nyaga and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Form(Document):
	def validate(self):		
		self.make_doctype()

	def make_doctype(self):
		if self.is_new():
			doc = frappe.new_doc("DocType")
		else:
			doc = frappe.get_doc("DocType", self.name)
			doc.fields = []
		for field in self.fields:
			self._get_docfield(doc, field)
		doc.save(ignore_permissions=True)

	def _get_docfield(doc, form_field):
		def _get_options():
			if form_field.field_type == 'Data':
				return form_field.data_field_options
			if form_field.field_type == 'Link':
				return form_field.field_doctype
			if form_field.field_type == 'Table':
				return form_field.field_child_doctype
			return None

		field = doc.append('fields', {
			'doctype': 'DocField', 
			'fieldname': frappe.scrub(form_field.field_label if form_field.field_label else form_field.field_name),
			'fieldtype': form_field.field_type,
			'precision': form_field.field_precision,
			'length': form_field.field_length,
			'reqd': form_field.field_reqd,
			'non_negative': form_field.field_non_negative,
			'default': form_field.field_default,
			'options': _get_options(),
		})
