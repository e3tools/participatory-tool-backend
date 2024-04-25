# Copyright (c) 2024, Steve Nyaga and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Form(Document):
	def validate(self):
		if not self.form_fields:
			frappe.throw(_("You must specify at lease one field"))
		self.validate_fields()
		self.make_doctype()

	def after_rename(self, old_name, new_name, merge=False):
		frappe.rename_doc("DocType", old=old_name, new=new_name)

	def on_trash(self):
		doctype = frappe.db.exists("DocType", self.name)
		if doctype:
			frappe.delete_doc("DocType", doctype)

	def validate_fields(self):
		for fld in self.form_fields:
			if not fld.field_name:
				fld.field_name = frappe.scrub(fld.field_label)
			fld.field_name = fld.field_name.lower()

	def make_doctype(self):
		if self.is_new():
			doc = frappe.new_doc("DocType")
			doc.name = self.name
		else:
			doc = frappe.get_doc("DocType", self.name)
		
		doc.fields = []
		doc.permissions = []
		for field in self.form_fields:
			self._get_docfield(doc, field)
		
		doc.custom = 1
		doc.module = 'Engage'
		doc.naming_rule = 'Autoincrement'
		doc.autoname = 'autoincrement'
		doc.track_changes = 1
		doc.allow_rename = 0
		self._set_roles(doc)
		doc.save(ignore_permissions=True)

	def _set_roles(self, doc):
		for perm in self.form_permissions:
			r = perm.as_dict()
			r['doctype'] = 'DocPerm'
			r["select"] = perm.perm_select
			r["read"] = perm.perm_read
			r["write"] = perm.perm_write
			r["create"] = perm.perm_create
			r["delete"] = perm.perm_delete
			r["report"] = perm.perm_report
			r["export"] = perm.perm_export
			r["import"] = perm.perm_import
			r["print"] = perm.perm_print			
			doc.append("permissions", r)

		if not self.form_permissions:
			kid = doc.append("permissions", {
				"doctype": "DocPerm",
				"select": 1,
				"read": 1,
				"write": 1,
				"create": 1,
				"delete": 1,
				"report": 1,
				"export": 1,
				"import": 1,
				"print": 1,
			})

	def _get_docfield(self, doc, form_field):
		def _get_options():
			if form_field.field_type == 'Data':
				return form_field.data_field_options
			if form_field.field_type == 'Link':
				return form_field.field_doctype
			if form_field.field_type == 'Table':
				return form_field.field_child_doctype
			if form_field.field_type == 'Select':
				return form_field.field_choices
			return None

		field = doc.append('fields', {
			'doctype': 'DocField', 
			'label': form_field.field_label,
			'fieldname': form_field.field_name, # frappe.scrub(form_field.field_label if form_field.field_label else form_field.field_name),
			'fieldtype': form_field.field_type,
			'precision': form_field.field_precision,
			'length': form_field.field_length,
			'reqd': form_field.field_reqd,
			'non_negative': form_field.field_non_negative,
			'default': form_field.field_default,
			'in_list_view': form_field.field_in_list_view,
			'options': _get_options(),
		})
