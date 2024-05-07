# Copyright (c) 2024, Steve Nyaga and contributors
# For license inengagement_formation, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint
from frappe import _
import datetime
from frappe.desk.form.linked_with import get as get_links 
from frappe.desk.form.linked_with import get_linked_docs, get_linked_doctypes

SELECT_MULTIPLE = 1
TABLE_MULTISELECT = 2
OPTION_NAME_FIELD = 'option_name'
MODULE_NAME = 'Engage'

class EngagementForm(Document):
	def validate(self):
		if not self.form_fields:
			frappe.throw(_("You must specify at lease one field"))
		if not cint(self.field_is_table) and not self.form_permissions:
			frappe.throw(_("You must specify at lease one permission"))
		self.validate_fields()
		self.make_doctype()

	def after_rename(self, old_name, new_name, merge=False):
		frappe.rename_doc("DocType", old=old_name, new=new_name)

	def on_trash(self):
		doctype = frappe.db.exists("DocType", self.name)
		if doctype:
			frappe.delete_doc("DocType", doctype, ignore_permissions=True, delete_permanently=True)

	def validate_fields(self):
		for fld in self.form_fields:
			if fld.field_type in ['Table', 'Table MultiSelect', 'Select Multiple']:
				fld.field_in_list_view = 0 #Table and multiselect fields are not allowed to have In List View
			if not fld.field_name:
				fld.field_name = frappe.scrub(fld.field_label)
			fld.field_name = fld.field_name.lower()
			if fld.field_type in ['Link', 'Table MultiSelect']: 
				#Table MultiSelect are associated with Non-Table DocTypes. The system will handle creation of corresponding child tables
				if not fld.field_doctype:
					frappe.throw(_("Row {0}. You must specify the Form for field {1}".format(fld.idx, fld.field_label)))
			if fld.field_type in ['Table']: 
				if not fld.field_child_doctype:
					frappe.throw(_("Row {0}. You must specify the Child Form for field {1}".format(fld.idx, fld.field_label)))
			if fld.field_type == 'Select':
				if not fld.field_choices.strip():
					frappe.throw(_("Row {0}. You must specify the choices for field {1}".format(fld.idx, fld.field_label)))

	def _get_naming_rule(self):
		"""
		Get naming rule 
		Return of the form SDD.-.YYYY.-.#####
		"""
		prefix = str(self.record_id_prefix).strip()
		# res = "format:{0}-{1}-{2}".format(prefix, "{YYYY}", "{#####}")
		res = "{0}.-.{1}.-.{2}".format(prefix, "YYYY", "#####")
		format = res.replace(" ", "").replace("--", "-")
		self.naming_format = "{0} e.g {1}".format(format, format.replace("format:", "").replace("{YYYY}", str(datetime.date.today().year)).replace("{#####}", "00001"))
		return format

	def make_doctype(self):
		fields = []
		self.cleanup_multiselect()
		for field in self.form_fields:
			if field.field_type == 'Select Multiple':
				fields.append(self.handle_multi_select(field, SELECT_MULTIPLE))
			elif field.field_type == 'Table MultiSelect':
				fields.append(self.handle_multi_select(field, TABLE_MULTISELECT))
			else:
				fields.append(self._get_docfield(field))

		if self.is_new():
			doc = frappe.new_doc("DocType")
			doc.name = self.name
		else:
			doc = frappe.get_doc("DocType", self.name)
		
		doc.fields = []
		for field in fields:
			doc.append('fields', field)

		doc.permissions = []
		doc.states = [] 	
		doc.custom = 1
		doc.module = MODULE_NAME
		doc.naming_rule = 'Expression (old style)'
		doc.autoname = self._get_naming_rule()
		doc.track_changes = 1
		doc.allow_rename = 0
		doc.allow_import = 1
		doc.hide_toolbar = 1
		doc.istable = self.field_is_table
		self._set_roles(doc)
		self._set_states(doc)
		doc.save(ignore_permissions=True)

	def _set_states(self, doc):
		colors = [
			{
				'state': 'Draft', 
				'color': 'Orange'
			},
			{
				'state': 'Submitted', 
				'color': 'Green'
			},
			{
				'state': 'Cancelled', 
				'color': 'Red'
			}
		]
		for mp in colors:
			doc.append("states", {
				"doctype": "DocType State",
				"title": mp['state'],
				"color": mp['color'] 
			})

	def _set_roles(self, doc):
		if cint(self.field_is_table):		
			return #if child table, no permissions as the child table will inherit parent form's permissions

		for perm in self.form_permissions:
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

	def _get_docfield(self, form_field):
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

		field = {
			'doctype': 'DocField', 
			'label': form_field.field_label if form_field.field_type not in ['Column Break'] else '',
			'fieldname': form_field.field_name or frappe.scrub(form_field.field_label),
			'fieldtype': form_field.field_type,
			'precision': form_field.field_precision,
			'length': form_field.field_length,
			'reqd': form_field.field_reqd,
			'non_negative': form_field.field_non_negative,
			'default': form_field.field_default,
			'in_list_view': form_field.field_in_list_view,
			'options': _get_options(),
		}
		return field

	def make_ref_doctype_name(self, form_field):
		"""
		Get name to call DocType that will store options when field is Select Multiple
		"""
		return "{0} {1}".format(self.form_name, form_field.field_label.title())

	def make_child_doctype_name(self, form_field):
		"""
		Get name to use for Child DocType that will allow multiselection of ref_doctype_name values 
		"""
		reference_doctype_name = self.make_ref_doctype_name(form_field)
		return "{0} Item".format(reference_doctype_name)

	def handle_multi_select(self, form_field, select_type):
		"""
		Frappe does not natively support multi-select dropdown
		To achieve this, we have to use Table Multi Select option
		To do this, we will do the following. Step 1 and 2 are only relevant when we are selecting from static options and not from a Link
			1. Create a `Normal DocType` named after the field label. Concatenate `Form Name` with `Field Label`
			2. For each specified option, create it as a record of the `Normal DocType` just created
			3. Create a `Child DocType` and add a link field to it referencing the entries in the `Normal DocType`
			4. Create a Table MultiSelect and link it the current doctype
		When selecting multiple from an exisiting table, the source table must not be a child table, so we will create a corresponding child table

		"""
		if select_type == SELECT_MULTIPLE:
			reference_doctype_name = self.make_ref_doctype_name(form_field)
			child_doctype_name = self.make_child_doctype_name(form_field)		
			exists = frappe.db.exists("DocType", reference_doctype_name)
			deleted = True
			if exists:
				deleted = self.delete_doctype(exists)
				# frappe.delete_doc("DocType", exists)
			# Step 1   
			ref_doc = frappe.new_doc("DocType") if deleted else frappe.get_doc("DocType", reference_doctype_name)
			ref_doc.fields = []
			ref_doc.permissions = []
			ref_doc.name = reference_doctype_name
			ref_doc.naming_rule = "By fieldname"
			ref_doc.autoname = "field:{0}".format(OPTION_NAME_FIELD)
			ref_doc.custom = 1
			ref_doc.module = MODULE_NAME
			ref_doc.append('fields', {
				'doctype': 'DocField', 
				'label': form_field.field_label,
				'fieldname': OPTION_NAME_FIELD,
				'fieldtype': "Data",
				'reqd': 1
			})
			self._set_roles(ref_doc) # append same permissions as the form being designed
			ref_doc.save(ignore_permissions=True)

			# Step 2
			options = form_field.field_choices.split('\n')
			for opt in options:
				if not opt:
					continue
				if not frappe.db.exists(reference_doctype_name, opt):
					# it is possible an option was not deleted because it is already linked to existing data
					frappe.get_doc({
						'doctype': reference_doctype_name,
						OPTION_NAME_FIELD: opt
					}).insert(ignore_permissions=True)
		elif select_type == TABLE_MULTISELECT:
			# Table MultiSelect allows selection from existing Non-Table DocTypes
			# So use the source table as the reference_doctype_name
			reference_doctype_name = form_field.field_doctype
			child_doctype_name = self.make_child_doctype_name(form_field)
			
		# Step 3
		exists = frappe.db.exists("DocType", child_doctype_name)
		if exists:
			frappe.delete_doc("DocType", exists, ignore_permissions=True)

		ref_doc = frappe.get_doc({
			'doctype': 'DocType',
			'name': child_doctype_name,
			'module': MODULE_NAME,
			'istable': 1,
			'custom': 1,
			'fields': [{
				'doctype': 'DocField',
				'fieldname': OPTION_NAME_FIELD,
				'label': form_field.field_label,
				'reqd': 1,
				'in_list_view': 1,
				'fieldtype': "Link",
				'options': reference_doctype_name
			}]
		}).insert(ignore_permissions=True)
		

		# Step 4
		field = {
			'doctype': 'DocField', 
			'label': form_field.field_label if form_field.field_type not in ['Column Break'] else '',
			'fieldname': form_field.field_name or frappe.scrub(form_field.field_label),
			'fieldtype': 'Table MultiSelect',
			'precision': form_field.field_precision,
			'length': form_field.field_length,
			'reqd': form_field.field_reqd,
			'non_negative': form_field.field_non_negative,
			'default': form_field.field_default,
			'in_list_view': form_field.field_in_list_view,
			'options': child_doctype_name,
		}
		return field

	def cleanup_multiselect(self):
		"""
		Delete any child tables created as a result of Select Multiple.
		NB: Do not delete any child table if the field type is Table MultiSelect as such
		    child doctypes are those already existing in the system 
		"""   
		if not self.is_new():
			exists = [x for x in self._doc_before_save.form_fields if x.field_type in ['Table MultiSelect', 'Select Multiple']]
			for fld in exists:
				child_doctype = self.make_child_doctype_name(form_field=fld)
				# self.delete_doctype(child_doctype) 
				if fld.field_type == 'Select Multiple':
					# if it is Select Multiple, delete the reference. For Table MultiSelect, do not delete the reference doctype
					ref_table = self.make_ref_doctype_name(form_field=fld)
					deleted = self.delete_doctype(ref_table) 
					if deleted:
						# If there are no references for the child table, delete the table also
						self.delete_doctype(child_doctype) 

	def delete_doctype(self, doctype):
		"""
		Delete using this so that it validates existing links 
		"""
		if not frappe.db.table_exists(doctype, False):
			return
		lst = frappe.db.get_all(doctype, fields=['name'])
		error = False
		for itm in lst:
			# There may be links with existing data
			# links = get_links(doctype, itm.name)
			# results = get_linked_docs("Role", "System Manager", linkinfo=get_linked_doctypes("Role"))
			links = get_linked_docs(doctype, itm.name, linkinfo=get_linked_doctypes(doctype))
			if not links:
				frappe.delete_doc(doctype, itm.name, ignore_permissions=True, delete_permanently=True)
			else:
				error = True 
		if not error: # drop tables if there are no existing links with existing data
			frappe.delete_doc("DocType", doctype, ignore_permissions=True, delete_permanently=True)
			frappe.db.sql_ddl(f"DROP TABLE IF EXISTS `tab{doctype}`")
		return not error