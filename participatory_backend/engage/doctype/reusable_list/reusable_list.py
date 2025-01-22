# Copyright (c) 2024, Steve Nyaga and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint
from frappe import _
from participatory_backend.enums import DefaultRolesEnum

MODULE_NAME = 'Engage'

class ReusableList(Document):
	def validate(self):
		if self.is_new():
			pi = frappe.db.exists(self.doctype, {"name": ("=", self.name), "docstatus": ("<", 2)})
			if pi:
				frappe.throw(_("Another list with the name {0} exists").format(frappe.bold(self.name)))
			self.name = self.list_name.strip()

		self.make_doctype()

	def after_rename(self, old_name, new_name, merge=False):
		frappe.rename_doc("DocType", old=old_name, new=new_name)

	def on_trash(self):
		# only delete custom doctypes
		doctype = frappe.db.exists("DocType", self.name)
		if doctype:
			"""@TODO - Delete tables that were generated by multiselect fields"""
			frappe.delete_doc("DocType", doctype, ignore_permissions=True, delete_permanently=True) 

	def make_doctype(self):
		"""
		Create corresponding custom doctype
		"""
		def _upsert_items(doctype):
			old_items = [x.name for x in frappe.db.get_all(doctype)]
			new_items = [x.item_name for x in self.items]
			# to delete
			to_delete = [x for x in old_items if x not in new_items]
			to_create = [x for x in new_items if x not in old_items]

			# for delete, if there is an existing link, the deletion will fail
			for itm in to_delete:
				frappe.delete_doc(doctype, itm, delete_permanently=True)

			for item in to_create:
				frappe.get_doc({
					"doctype": doctype,
					"list_name": item
				}).insert(ignore_permissions=True)

		def _upsert_doctype():
			user = frappe.session.user
			frappe.set_user("Administrator")
			# create doctype and upsert items
			if self.is_new():
				doc = frappe.new_doc("DocType")
				doc.name = self.name
			else:
				doc = frappe.get_doc("DocType", self.name)
			
			doc.fields = []		 
			doc.append('fields', {
				"doctype": "DocField",
				'label': "List Item",
				'fieldname': "list_name",
				'fieldtype': "Data", 
				'reqd': 1,  
			})
			doc.permissions = []
			doc.states = [] 	
			doc.custom = 1
			doc.module = MODULE_NAME
			doc.naming_rule = 'By fieldname'
			doc.autoname = "field:list_name"
			doc.track_changes = 1
			doc.allow_rename = 0
			doc.allow_import = 1
			doc.hide_toolbar = 1
			doc.istable = 0
			self._set_roles(doc)
			doc.flags.ignore_permissions = True
			res = doc.save(ignore_permissions=True)

			frappe.set_user(user)
			return res

		dc = _upsert_doctype()
		_upsert_items(doctype=dc.name)

	def _set_roles(self, doc): 
		for role in [DefaultRolesEnum.DATA_CAPTURE.value, DefaultRolesEnum.GUEST.value]:
			r = frappe._dict()
			r['role'] = role
			r['doctype'] = 'DocPerm'
			r["select"] = 1
			r["read"] = 1 		
			doc.append("permissions", r)		

		for role in [DefaultRolesEnum.FORM_DESIGNER_USER.value, DefaultRolesEnum.FORM_DESIGNER_MANAGER.value]:
			r = frappe._dict()
			r['role'] = role
			r['doctype'] = 'DocPerm'
			r["select"] = 1
			r["read"] = 1
			r["write"] = 1
			r["create"] = 1
			r["delete"] = 1
			r["report"] = 1
			r["export"] = 1
			r["import"] = 1
			r["print"] = 1		
			doc.append("permissions", r)  

		# for role in [DefaultRolesEnum.FORM_DESIGNER_USER.value, DefaultRolesEnum.DATA_CAPTURE.value]:
		# 	r = frappe._dict()
		# 	r['role'] = role
		# 	r['doctype'] = 'DocPerm'
		# 	r["select"] = 1
		# 	r["read"] = 1
		# 	# r["write"] = 1
		# 	# r["create"] = 1
		# 	# r["delete"] = 1
		# 	# r["report"] = 1
		# 	# r["export"] = 1
		# 	# r["import"] = 1
		# 	# r["print"] = 1		
		# 	doc.append("permissions", r)  

	def _set_roles_old(self, doc):
		all_selected = False
		for perm in self.permissions:
			if perm.role == "All":
				all_selected = True
			r = frappe._dict()
			r['role'] = perm.role
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

		if not all_selected: #grant read permissions to all
			r = frappe._dict()
			r['role'] = "All"
			r['doctype'] = 'DocPerm'
			r["select"] = 1
			r["read"] = 1
			doc.append("permissions", r)
