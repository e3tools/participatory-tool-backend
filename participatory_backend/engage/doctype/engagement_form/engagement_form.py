# Copyright (c) 2024, Steve Nyaga and contributors
# For license inengagement_formation, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint, get_url
from frappe import _
import datetime
from frappe.desk.form.linked_with import get as get_links 
from frappe.desk.form.linked_with import get_linked_docs, get_linked_doctypes
from participatory_backend.utils.common import get_initials, scrub
from participatory_backend.utils.translator import generate_form_translations
import json
import ast
from participatory_backend.utils.qrcode import get_qrcode
from frappe.utils import random_string, get_url, image_to_base64
import re
from frappe.core.doctype.file.file import get_local_image
from frappe import safe_decode
from participatory_backend.engage.doctype.engagement_form_field.engagement_form_field import EngagementFormField

SELECT_MULTIPLE = 1
TABLE_MULTISELECT = 2
OPTION_NAME_FIELD = 'option_name'
MODULE_NAME = 'Engage'
DOCTYPE_MAX_LENGTH = 61
FIELD_NAME_MAX_LENGTH = frappe.db.MAX_COLUMN_LENGTH - 3
ALLOWED_FORMULA_FIELD_TYPES = ["Currency", "Data", "Date", "Datetime", "Int", "Float", "Text", "Time"]
ALLOWED_FILTER_FIELD_TYPES = ["Link"]

LINK_FIELD_DOC_FILTER_PATTERN = re.compile(r'(\"|\')(doc\..*?)(\"|\')')
WEB_FORM_LINK_FIELD_DOC_FILTER_PATTERN = re.compile(r'(\"|\')(web_form_values\..*?)(\"|\')')
DOC_PREFIX_FORMULA = 'doc.'

class CascadeFilter:
	source_field: str
	target_field: str
	# filters_plain: str
	filters_parsed: list
	depends_on_form_field_value: bool # does the filter depend on values specified in the current form_field

class EngagementForm(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from participatory_backend.engage.doctype.engagement_form_field.engagement_form_field import EngagementFormField
		from participatory_backend.engage.doctype.engagement_form_permission.engagement_form_permission import EngagementFormPermission

		anonymous: DF.Check
		description: DF.TextEditor | None
		enable_web_form: DF.Check
		field_is_table: DF.Check
		form_design_permissions: DF.Table[EngagementFormPermission]
		form_fields: DF.Table[EngagementFormField]
		form_group: DF.Link | None
		form_image: DF.AttachImage | None
		form_image_base_64: DF.TextEditor | None
		form_name: DF.Data
		form_permissions: DF.Table[EngagementFormPermission]
		include_logo_in_web_form: DF.Check
		naming_field: DF.Data | None
		naming_format: DF.Data | None
		public_url: DF.Data | None
		qr_code: DF.AttachImage | None
		record_id_prefix: DF.Data | None
		route: DF.Data | None
		show_data_processing_consent_statement: DF.Check
		show_title_field_in_link: DF.Check
		show_watermark_image: DF.Check
		success_message: DF.SmallText | None
		title_field: DF.Literal[None]
		use_field_to_generate_id: DF.Check
		web_title: DF.Data | None
	# end: auto-generated types
	
	@property
	def form_url(self):
		return self.get_route(fqdn=True)
	
	def validate(self): 
		# from gis.shapefile_loader import load_cascaded_county_admins
		# load_cascaded_county_admins()
		# return
		self.link_filters_map: list[type[CascadeFilter]] = []
		self.form_name = frappe.unscrub(self.form_name)
		if not self.form_fields:
			frappe.throw(_("You must specify at lease one field"))
		if not cint(self.field_is_table) and not self.form_permissions:
			frappe.throw(_("You must specify at lease one permission"))
		if self.record_id_prefix:
			self.record_id_prefix = self.record_id_prefix.upper()
		self.web_title = self.web_title or ''
		if not self.web_title:
			self.web_title = self.form_name
		self.validate_fields()
		self.route = self.get_route() # self.web_title.lower().replace(" ", "-") if self.web_title else None
		self.public_url = self.get_route(fqdn=True)
		self.create_data_protection_fields()
		self.make_doctype()
		if self.field_is_table:
			self.enable_web_form = False
		self.generate_image_fields()
		self.publish_form()


	def generate_image_fields(self):
		if not self.field_is_table:
			form_image = None # self.get_form_image() # do not overlay an image. the data generated is too long		
			self.qr_code = get_qrcode(self.form_url, form_image) # if form_image else None
		
		if self.form_image:
			image, filename, extn = get_local_image(self.form_image)
			base64str = image_to_base64(image, extn)
			base64str = f"data:image/{extn};base64,{safe_decode(base64str)}"
			self.form_image_base_64 = base64str
		else:
			self.form_image_base_64 = None
		
	def before_save(self): 
		if self.field_is_table:
			self.qr_code = None
			self.form_image_base_64 = None
		# else: 
		# 	form_image = self.get_form_image()
		# 	# logo_files = frappe.get_all("File",
		# 	# 	fields=["name", "file_name", "file_url", "is_private"],
		# 	# 	filters={"attached_to_name": self.name, "attached_to_field": "form_image",  "attached_to_doctype": self.doctype },
		# 	# )
		# 	# form_image = None
		# 	# if logo_files:
		# 	# 	print(logo_files)
		# 	# 	print(frappe.local.sites_path)
		# 	# 	form_image = frappe.utils.get_files_path(logo_files[0].file_name, is_private=logo_files[0].is_private)
			
		# 	self.qr_code = get_qrcode(self.form_url, form_image) if form_image else None
		# 	image, filename, extn = get_local_image(self.form_image)
		# 	self.form_image_base_64 = image_to_base64(image, extn)

	def get_form_image(self):
		logo_files = frappe.get_all("File",
				fields=["name", "file_name", "file_url", "is_private"],
				filters={"attached_to_name": self.name, "attached_to_field": "form_image",  "attached_to_doctype": self.doctype },
			) 
		if logo_files:
			print(logo_files)
			print(frappe.local.sites_path)
			return frappe.utils.get_files_path(logo_files[0].file_name, is_private=logo_files[0].is_private)
		return None

	def after_rename(self, old_name, new_name, merge=False):
		frappe.rename_doc("DocType", old=old_name, new=new_name)
		try:
			self.web_title = new_name # set this to ensure that web forms are generated also
			# self.validate() 
			self.save()#do this to set the correct naming convention
		except:
			pass

	def on_update(self):
		self.set_form_title_field()
		self.validate_linked_fields()
		#generate_form_translations(self.name) 

	def after_insert(self):
		self.set_form_title_field()
		self.validate_linked_fields()

	def on_trash(self):
		doctype = frappe.db.exists("DocType", self.name)
		if doctype:
			"""@TODO - Delete tables that were generated by multiselect fields"""
			frappe.delete_doc("DocType", doctype, ignore_permissions=True, delete_permanently=True)

	def set_form_title_field(self):
		if not self.title_field or not cint(self.show_title_field_in_link):
			frappe.db.set_value('DocType', self.name, 'show_title_field_in_link', False)
			frappe.db.set_value('DocType', self.name, 'title_field', None)
			return
		
		# on the frontend, we are only setting labels since we may not have the field_names generated on the frontend yet
		fld = [x for x in self.form_fields if x.field_label == self.title_field]
		if fld:
			self.db_set('title_field', fld[0].field_name)
			if cint(self.show_title_field_in_link):
				frappe.db.set_value('DocType', self.name, 'title_field', fld[0].field_name)
				frappe.db.set_value('DocType', self.name, 'show_title_field_in_link', True) 
	
	def validate_fields(self): 
		for fld in self.form_fields:
			if fld.field_type in ['Table', 'Table MultiSelect', 'Select Multiple']:
				fld.field_in_list_view = 0 #Table and multiselect fields are not allowed to have In List View
			if not fld.field_name:
				fld.field_name = scrub(fld.field_label)
			fld.field_name = fld.field_name.lower()
			if fld.field_type in ['Link', 'Table MultiSelect']: 
				#Table MultiSelect are associated with Non-Table DocTypes. The system will handle creation of corresponding child tables
				if not fld.field_doctype:
					frappe.throw(_("Row {0}. You must specify the Form for field {1}".format(fld.idx, fld.field_label)))
				fld.field_filters = self.sanitize_filters(fld.field_filters_plain)		
				self.make_web_form_on_change_link_function(fld)
			if fld.field_type in ['Table']: 
				if not fld.field_child_doctype:
					frappe.throw(_("Row {0}. You must specify the Child Form for field {1}".format(fld.idx, fld.field_label)))
			if fld.field_type == 'Select':
				if not fld.field_choices.strip():
					frappe.throw(_("Row {0}. You must specify the choices for field {1}".format(fld.idx, fld.field_label)))
			# if fld.field_type == 'Linked Field':
			# 	self.validate_linked_field(fld)

	def validate_linked_fields(self):
		fields = [x for x in self.form_fields if x.field_type == 'Linked Field']
		for field in fields:
			self.validate_linked_field(field)

	def validate_linked_field(self, field):
		"""
		Validate that the linked field references an existing field and that the property exists in the referenced doctype 
		"""
		linked_form = field.linked_form
		parent_forms = [x for x in self.form_fields if x.field_name == linked_form]
		form = ''
		if parent_forms:
			form = parent_forms[0].field_doctype
		docfield = field.linked_form_property
		# check if doctype and docfield are valid 
		if not frappe.db.exists("DocType", form):
			frappe.throw(_("Row {0}. The specified linked form {1} does not exist".format(field.idx, linked_form)))
		form = frappe.get_doc("DocType", form)
		if not [x for x in form.fields if x.fieldname == docfield]:
			frappe.throw(_("Row {0}. The specified linked form propery {1} does not exist in form {2}".format(field.idx, field.linked_form_property, linked_form)))
			
	def _get_naming_rule(self):
		"""
		Get naming rule 
		Return of the form SDD.-.YYYY.-.#####
		"""
		if cint(self.field_is_table):
			return None #if child table, no setting naming rule
		if cint(self.use_field_to_generate_id):
			return f'field:{self.naming_field}'
		initials = get_initials(self.form_name)
		prefix = str(self.record_id_prefix).strip() if self.record_id_prefix else None
		# res = "format:{0}-{1}-{2}".format(prefix, "{YYYY}", "{#####}")
		# res = "{3}.-.{0}.-.{1}.-.{2}".format(prefix, "YYYY", "#####", initials)
		if prefix:
			res = "{0}.-.{1}.-.{2}".format(prefix, "YYYY", "#####")
		else:
			res = "{0}.-.{1}.-.{2}".format(initials, "YYYY", "#####") 
		format = res.replace(" ", "").replace("--", "-")
		self.naming_format = "{0} e.g {1}".format(format, format.replace("format:", "").replace("YYYY", str(datetime.date.today().year)).replace("#####", "00001").replace(".", ""))
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
				if field.formula: # if has formula, make field read_only
					fields[-1]['read_only'] = True

		if self.is_new():
			doc = frappe.new_doc("DocType")
			doc.name = self.name
		else:
			doc = frappe.get_doc("DocType", self.name)
		
		doc.fields = []
		for field in fields:
			doc.append('fields', field)

		# set search fields
		search_fields = ','.join([x.field_name for x in self.form_fields if x.field_is_search_field])

		doc.search_fields = search_fields
		doc.permissions = []
		doc.states = [] 	
		doc.custom = 1
		doc.module = MODULE_NAME
		# if self.record_id_prefix:
		# 	doc.naming_rule = 'Expression (old style)'
		# 	doc.autoname = self._get_naming_rule()
		# else:
		# 	doc.naming_rule = ""
		# 	doc.autoname = ""
		# 	self.naming_format = ""
		doc.naming_rule = 'Expression (old style)'
		doc.autoname = self._get_naming_rule()
		doc.allow_rename = 0
		if cint(self.use_field_to_generate_id):
			doc.naming_rule = 'By fieldname'
			doc.allow_rename = 1
		doc.track_changes = 1
		doc.allow_import = 1
		doc.hide_toolbar = 1
		doc.istable = self.field_is_table
		self._set_roles(doc)
		self._set_states(doc)
		doc.save(ignore_permissions=True)
		self.make_server_script()
		self.make_client_script()	

	def make_server_script(self):
		"""
		For formula fields, handle them via Server Script
		"""
		def _create_script(field):
			doc = frappe.get_doc({
				"doctype": "Server Script",
				"__newname": f'{self.form_name} - {field.field_label}',
				"script_type": "DocType Event",			
				"reference_doctype": self.form_name,
				"doctype_event": "Before Save",
				"module": MODULE_NAME,
				"script": f'{DOC_PREFIX_FORMULA}{field.field_name}={field.formula}'
			}).insert(ignore_permissions=True)

		# delete scripts in case they exist
		frappe.db.delete("Server Script", {"reference_doctype": self.form_name})
		# make Server Script
		formula_fields = [x for x in self.form_fields if x.formula and x.field_type in ALLOWED_FORMULA_FIELD_TYPES]
		for field in formula_fields:
			_create_script(field)

	def sanitize_filters(self, filters):
		"""
		Replace any quotation marks that may exist infront of or after doc.XXXXXX
		"""
		if not filters:
			return filters
				
		matches = LINK_FIELD_DOC_FILTER_PATTERN.findall(filters) # returns list of tuples as [('"', 'doc.admin_1', '"'), ('"', 'doc.admin_2', '"')]		
		for match in matches:
			filterVal = match[1]
			filters = re.sub(r'(\"|\')' + filterVal + '(\"|\')', filterVal, filters) 

		return filters
	 
	def make_web_form_on_change_link_function(self, field: EngagementFormField): #, filter_map: list[type[CascadeFilter]]):
		"""Make an on change function for Web Form for handling change of the field values. 
		This is especially so for cascaded filters 
		"""
		if not field.field_filters_plain:
			return
		# filters = field.field_filters_plain 
		# loop through the determinant form field values
		parsed_filters = frappe.safe_eval(field.field_filters_plain)
		for filter in parsed_filters:
			filter_str = str(filter)
			matches = LINK_FIELD_DOC_FILTER_PATTERN.findall(filter_str) # returns list of tuples as [('"', 'doc.admin_1', '"'), ('"', 'doc.admin_2', '"')]		
			for match in matches: 
				filterVal = match[1]
				# filters = re.sub(r'(\"|\')' + filterVal + '(\"|\')', filterVal, filter_str) 
				fltr = CascadeFilter()
				fltr.source_field = filterVal.replace(DOC_PREFIX_FORMULA, '')
				fltr.target_field = field.field_name
				fltr.filters_parsed = filter
				fltr.depends_on_form_field_value = True
				self.link_filters_map.append(fltr)

		# check if there are other filters that do not depend on form field values
		# filters = frappe.safe_eval(field.field_filters_plain) # will return values e.g [['Admin 2', 'parent_admin', '=', 'doc.admin_1']]
		for filter in parsed_filters:
			if str(filter[3]).find(DOC_PREFIX_FORMULA) == -1: # there is no occurrence of doc.
				fltr = CascadeFilter()
				fltr.target_field = field.field_name
				fltr.source_field = None # filterVal.replace(DOC_PREFIX_FORMULA, '') # no source_field. This is an absolute filter value
				fltr.filters_parsed = filter 
				fltr.depends_on_form_field_value = False
				self.link_filters_map.append(fltr)

	def make_client_script(self): 
		"""
		For Link field filters, create a Client Script
		"""		
		def _create_script(script):
			doc = frappe.get_doc({
				"doctype": "Client Script",
				"__newname": f'{self.form_name}',
				"dt": self.form_name,			
				"view": "Form",
				"enabled": True,
				"module": MODULE_NAME,
				"script": script
			}).insert(ignore_permissions=True)

		NEWLINE = '\r\n'
		OPEN_BRACKET = "{"
		CLOSE_BRACKET = "}"
		# delete scripts in case they exist
		frappe.db.delete("Client Script", {"dt": self.form_name})
		# make client Script
		filter_fields = [x for x in self.form_fields if x.field_filters_plain and x.field_type in ALLOWED_FILTER_FIELD_TYPES] 
		full_script = f'frappe.ui.form.on("{self.form_name}", {OPEN_BRACKET}{NEWLINE}onload: function(frm) {OPEN_BRACKET}'
		for field in filter_fields:
			filter = '''frm.set_query("{field_name}", function() {open_bracket}
					return {open_bracket}
							"filters": {filters}
						{close_bracket};
					{close_bracket});'''.format(field_name=field.field_name, 
				   				  filters=self.sanitize_filters(field.field_filters_plain),
								  open_bracket=OPEN_BRACKET,
								  close_bracket=CLOSE_BRACKET)
			filter = filter.replace(DOC_PREFIX_FORMULA, "frm.doc.")
			full_script += filter
		full_script += CLOSE_BRACKET

		full_script += f''', {NEWLINE}refresh: function(frm) {OPEN_BRACKET}'''
		if cint(self.show_data_processing_consent_statement):
			# retrieve data consent statement
			retrieve = f'''{NEWLINE}
						//if(frm.doc.__islocal){OPEN_BRACKET}
							frappe.call({OPEN_BRACKET}
								method: "participatory_backend.engage.doctype.engagement_form.engagement_form.get_data_processing_consent_statement", 
								freeze: true,
								callback: function (r) {OPEN_BRACKET}
									let fields = [];
									if (r.message) {OPEN_BRACKET} 
										// $(frm.fields_dict.data_consent_statement.wrapper).find('#data-consent-statement').html(r.message);
										$("#data-consent-statement").html(r.message);
									{CLOSE_BRACKET}
								{CLOSE_BRACKET},
							{CLOSE_BRACKET});
						//{CLOSE_BRACKET}
						'''
			full_script += retrieve
		
		full_script += CLOSE_BRACKET

		# check data consent
		validate = ''
		if cint(self.show_data_processing_consent_statement):
			validate += f''', {NEWLINE}
						validate: function(frm){OPEN_BRACKET}
							if(!frm.doc.grant_data_processing_consent) {OPEN_BRACKET}
								frappe.throw("You must agree to grant data processing consent");
							{CLOSE_BRACKET}
						{CLOSE_BRACKET}'''
			full_script += validate

		# close script	
		full_script += "});"
			
		_create_script(full_script)

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

	def _get_docfield(self, form_field: EngagementFormField):
		def _get_options():
			if form_field.field_type == 'HTML':
				return form_field.data_field_html
			if form_field.field_type == 'Data':
				return form_field.data_field_options
			if form_field.field_type == 'Link':
				return form_field.field_doctype
			if form_field.field_type in ['Table', 'Table MultiSelect']:
				return form_field.field_child_doctype
			if form_field.field_type in ['Select', 'Select Multiple']:
				if not form_field.field_choices.strip().startswith("\n"):
					form_field.field_choices = '\n' + str(form_field.field_choices).strip("\n")
				if form_field.field_choices.strip() == '':
					frappe.throw(_("Field {} in row {}. You must specify the choices for the Select Field".format(form_field.field_label, form_field.idx)))
				return form_field.field_choices
			return None
		
		def _set_depends_on(exp: str, ref_field:dict, ref_field_property: str):
			"""
			Set depends on expression 
			"""
			if not exp:
				return ''
			exp = exp.strip()
			if exp.lower().startswith("eval:"):
				return exp
			else:
				return convert_depends_on_conditions_to_js_format(eval(exp), ref_field, ref_field_property) #return f"eval:{exp}"
			
		def _get_field_type(field_type: str):
			if field_type == 'Linked Field':
				return "Read Only"
			return field_type
		
		def _get_fetch_from(field: str):
			if field.field_type == 'Linked Field':
				return field.field_linked_field
			return None
				
		def _sanitize_field():
			if cint(form_field.field_reqd):
				# If mandatory_depends_on is set, then the field cannot be required
				if form_field.mandatory_depends_on:
					form_field.field_reqd = 0
				# If field is hidden, then the field cannot be required
				if form_field.field_hidden:
					form_field.field_reqd = 0
				# If field is readonly, then the field cannot be required
				if form_field.field_readonly:
					form_field.field_reqd = 0

				if form_field.depends_on: # if field is required, it cannot be shown optionally depending on conditions
					bold = frappe.bold("Display Depends On")
					frappe.throw(f"Row {form_field.idx}. The field cannot be required yet the value of {bold} has been set.")
		
		_sanitize_field()
		form_field.field_name = form_field.field_name.strip()

		# set depends on
		form_field.depends_on = _set_depends_on(exp=form_field.depends_on_plain, ref_field=form_field, ref_field_property='Display Depends On')
		form_field.mandatory_depends_on = _set_depends_on(exp=form_field.mandatory_depends_on_plain, ref_field=form_field, ref_field_property='Mandatory Depends On')
		form_field.read_only_depends_on = _set_depends_on(exp=form_field.read_only_depends_on_plain, ref_field=form_field, ref_field_property='Readonly Depends On')
 
		field = {
			'doctype': 'DocField', 
			'label': form_field.field_label.strip() if form_field.field_label else '', # if form_field.field_type not in ['Column Break'] else '',
			'fieldname': self.get_field_name(form_field),
			'fieldtype': _get_field_type(form_field.field_type),
			'precision': form_field.field_precision,
			'length': form_field.field_length,
			'reqd': form_field.field_reqd,
			'non_negative': form_field.field_non_negative,
			'default': form_field.field_default,
			'in_list_view': form_field.field_in_list_view,
			'depends_on': form_field.depends_on,
			'mandatory_depends_on': form_field.mandatory_depends_on,
			'read_only_depends_on': form_field.read_only_depends_on,
			'options': _get_options(),
			'read_only': form_field.field_readonly,
			'fetch_from': _get_fetch_from(form_field),
			'description': form_field.description,
			'max_height': form_field.max_height,
			'hidden': form_field.field_hidden,
		}
		return field

	def make_ref_doctype_name(self, form_field, max_length=DOCTYPE_MAX_LENGTH):
		"""
		Get name to call DocType that will store options when field is Select Multiple
		"""
		# name = "{0} {1}".format(self.form_name, form_field.field_label.title()) 
		kid_name = frappe.unscrub(form_field.field_name or form_field.field_label)
		# first try use the field_name
		name = "{0} {1}".format(self.form_name, kid_name)
		name = name.strip()
		if len(name) > max_length:
			if len(name) > max_length:
				# if field_name will not resolve, then concat form initials with field_name
				form_initials = "".join([x[0] for x in self.form_name.replace("  ", " ").split(" ")]).upper()
				name = "{0} {1}".format(form_initials, kid_name)
		return name	

	def make_child_doctype_name(self, form_field):
		"""
		Get name to use for Child DocType that will allow multiselection of ref_doctype_name values 
		"""
		reference_doctype_name = self.make_ref_doctype_name(form_field, max_length=DOCTYPE_MAX_LENGTH - len(" Item"))
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
		def handle_as_normal_table_field():
			"""
			Frappe does not as yet support multi-select for Web Form.
			For multiselect and multi-table select fields, we can have a work around where we create the field as 
			a normal Table field without the need to create other doctypes storing the options

			To do this, we will do the following. Step 1 and 2 are only relevant when we are selecting from static options and not from a Link
				1. Create a Child Table with a single field. Create a `Normal DocType` named after the field label. 
					- Concatenate `Form Name` with `Field Label` to generate the Child Doctype name
					- If the form name is changed, rename the child doctype instead of deleting so as to preserve any existing data. We track 
					  a related table by using the description field in the DocType document
					- To generate the single field
						* If the options are static (Multi-Select), create a Select field 
						* If the options are a Link (Multi-Select Table), create a Link field
				2. Create a new Field of type Table and set the options as the table you just generated 
			"""

			def make_field():
				field = None
				if select_type == SELECT_MULTIPLE:
					field = {
						'doctype': 'DocField', 
						'label': form_field.field_label,
						'fieldname': OPTION_NAME_FIELD,
						'fieldtype': "Select",
						'options': form_field.field_choices,
						'reqd': 1,
						'in_list_view': 1
					}
				elif select_type == TABLE_MULTISELECT:
					field = {
						'doctype': 'DocField', 
						'label': form_field.field_label,
						'fieldname': OPTION_NAME_FIELD,
						'fieldtype': "Link",
						'options': form_field.field_doctype,
						'reqd': 1,
						'in_list_view': 1
					}
				return field
 
			# Step 1. Make Child Doctype
			"""
			It is not possible to have duplicate child doctypes since the name is generated by
			concatenating name of engagement form with the field name. If field_name is changed,
			that becomes a new Child DocType
			"""
			child_doctype_name = self.make_child_doctype_name(form_field)		
			child_doctype_exists = frappe.db.exists("DocType", child_doctype_name)
			
			# Step 1   
			child_doc = frappe.new_doc("DocType") if not child_doctype_exists else frappe.get_doc("DocType", child_doctype_name)
			child_doc.name = child_doctype_name
			child_doc.istable = 1
			child_doc.fields = []
			child_doc.permissions = []
			child_doc.naming_rule = "By fieldname"
			# child_doc.autoname = "field:{0}".format(OPTION_NAME_FIELD) # comment this otherwise select/link fields cannot be unique so cannot be used to autoname
			child_doc.custom = 1
			child_doc.allow_import = 1
			child_doc.module = MODULE_NAME
			child_doc.append('fields', make_field())
			# self._set_roles(child_doc) # append same permissions as the form being designed
			child_doc.save(ignore_permissions=True)

			# Step 2. Create the field
			field = {
				'doctype': 'DocField', 
				'label': form_field.field_label if form_field.field_type not in ['Column Break'] else '',
				'fieldname': self.get_field_name(form_field),
				'fieldtype': 'Table',
				'precision': form_field.field_precision,
				'length': form_field.field_length,
				'reqd': form_field.field_reqd,
				'non_negative': form_field.field_non_negative,
				'default': form_field.field_default,
				'in_list_view': form_field.field_in_list_view,
				'options': child_doctype_name,
			}
			return field

		def handle_with_doctypes():
			"""
			Frappe does not as yet support multi-select for Web Form.
			For multiselect and multi-table select fields, we handle this by creating Doctypes to store the options 
			so that we can handle this as a multi-table field. New doctypes are created in this regard
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
				ref_doc.allow_import = 1
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
				'allow_import': 1,
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
				'fieldname': self.get_field_name(form_field),
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
		
		# return handle_with_doctypes()
		return handle_as_normal_table_field()

	def cleanup_multiselect(self):
		"""
		Delete any child tables created as a result of Select Multiple.
		NB: Do not delete any child table if the field type is Table MultiSelect as such
			child doctypes are those already existing in the system 
		"""   
		if not self.is_new() and hasattr(self, '_doc_before_save'): #when renaming, the value of self._doc_before_save is None
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
	
	def get_route(self, fqdn=False):
		"""
		Get route for the published form 

		Args:
			fdqn: return a fully qualified domain name
		"""
		if self.field_is_table:
			return None
		# route = self.web_title.lower().replace(" ", "-") if not self.route else self.route
		route = scrub(self.name).replace("_", "-").strip("-") # if not self.route else self.route
		if route and fqdn:
			route = get_url(route)
		return route
	
	def get_field_name(self, form_field):
		name = form_field.field_name or scrub(form_field.field_label)
		return name[:FIELD_NAME_MAX_LENGTH]

	def publish_form(self):
		"""
		Publishes the form to allow capturing of data from a website
		"""
		def _make_web_form_css():
			css = '''
				.web-form-title h1 {
					font-size: 20px !important; 
				}

				.web-form-banner-image {
					z-index: 2 !important;
					margin-bottom: -3rem !important;
					height: 150px !important;
					width: 150px !important;
					text-align: center !important;
				}

				.page-header {
					text-align: center;
				}
				'''
			if self.show_watermark_image:
				watermark_img = frappe.db.get_singles_value('Engage Settings', 'watermark_image')
				if watermark_img:
					css += '''
					.page-content-wrapper {{ 
						background-image: url({watermark_img});
						background-repeat: no-repeat;
						background-attachment: fixed;
						background-size: cover;
						background-position: center;
					}}
					'''.format(watermark_img=watermark_img)
			return css
		
		def _make_web_form_script():
			field_scripts = ''
			if len(self.link_filters_map) > 0:
				# First make the functions for target fields. Later make triggers for source fields
				# get unique targets
				target_fields = set([x.target_field for x in self.link_filters_map])
				trigger_functions = []
				for target in target_fields:
					engagement_form_field = [x for x in self.form_fields if x.field_name == target]
					final_field_filters = []
					# get the filters
					filters = [x for x in self.link_filters_map if x.target_field == target]
					for filter in filters:
						if filter.depends_on_form_field_value:
							filter_val = filter.filters_parsed[3] # filter is of the form [['Admin 2', 'parent_admin', '=', 'doc.admin_1']]
							filter_val = filter_val.replace(DOC_PREFIX_FORMULA, 'web_form_values.')
							final_field_filters.append([filter.filters_parsed[0], filter.filters_parsed[1], filter.filters_parsed[2], filter_val])
						else:
							final_field_filters.append(filter.filters_parsed)

					func_name, func_script = _make_target_field_function(engagement_form_field[0], filters=final_field_filters)
					trigger_functions.append(func_name)
					field_scripts += func_script

				# get unique sources in order to make trigger functions for them 
				source_fields = set([x.source_field for x in self.link_filters_map if x.source_field])
				
				for source in source_fields:
					# get the targets to ensure all targets are fired when the source field value changes
					targets = set([x.target_field for x in self.link_filters_map if x.source_field == source])
					for target in targets:
						field_scripts = _make_source_field_function(
											source_field_name=source, 
											target_field_name=target) + '\n\n' + field_scripts 

				# ensure trigger functions are called on load
				if trigger_functions:
					on_load_script = """frappe.web_form.after_load = () => { """
					for func in trigger_functions:
						on_load_script += """\n{func}();""".format(func=func)
					on_load_script += """\n}\n\n"""

					field_scripts = on_load_script + field_scripts # ensure trigger functions are triggered on_load

			return field_scripts

		def _make_target_field_function(engagement_form_field: EngagementFormField, filters: list[type[list[type[str]]]]):
			final_filter = sanitize_web_filters(str(filters))
			function_name = _get_trigger_function_name(engagement_form_field.field_name)

			func_script = """const {trigger_function} = () => {{
					frappe.web_form.fields_dict.{target_field}.set_data([]); // rest as we wait to load from backend
					const web_form_values = frappe.web_form.get_values(true, false);
					const filters = {filters};
					frappe.call({{
						method:"participatory_backend.api.get_list",
						args: {{
							doctype: '{field_doctype}',
							filters: filters,
							fields: ["name"],
							limit_page_length: 0,
							// parent: "Item Attribute",
							order_by: "name",
						}},
						callback: (r) => {{
							if (r.message) {{
							const options = [];
							for (var i = 0; i < r.message.length; i++) {{
								options.push(r.message[i].name) 
							}}
							frappe.web_form.fields_dict.{target_field}.set_data(options)
						  }}
						}},
						}});
					}}
				""".format(target_field=engagement_form_field.field_name, 
			   				field_doctype=engagement_form_field.field_doctype,
							filters=final_filter,
							trigger_function=function_name)
			return function_name, func_script
		
		def _make_source_field_function(source_field_name: str, target_field_name: str):
			func = """frappe.web_form.on('{source_field}', (field, value) => {{ 
						frappe.web_form.set_value('{target_field}', ''); // reset the value of target
						{trigger_function}() 
					}});
			""".format(source_field=source_field_name, 
					   target_field=target_field_name,
					   trigger_function=_get_trigger_function_name(target_field_name))
			return func
		
		def _get_trigger_function_name(target_field):
			return f"trigger_{target_field}"
		
		exists = frappe.db.exists("Web Form", {"doc_type": self.name})
		if exists: 
			doc = frappe.get_doc("Web Form", exists)			
		else:
			doc = frappe.new_doc("Web Form")
		
		# if no web-form delete if existing
		if not cint(self.enable_web_form):
			if exists:
				frappe.delete_doc("Web Form", exists)
			return 

		backend_only_fields = [x for x in self.form_fields if x.field_is_backend_field]
		doctype = frappe.get_doc("DocType", self.name) 
		introduction_text = self.description or ''
		# if cint(self.include_logo_in_web_form) and self.form_image_base_64:
		# 	# image_html = '<div alt="Logo" style="text-align: center;"> <img src="https://seeklogo.com/images/N/nyeri-county-logo-CD6A94CBC7-seeklogo.com.png" style="height:150px;"> </div>'
		# 	image_html = f'<div alt="Logo" style="text-align: center;"> <img src="{self.form_image_base_64}" style="height:150px;"> </div>'
		# 	introduction_text = f'<div>{image_html} </br> {introduction_text} </div>'
			
		r = { 
			"title": self.name,
			"doc_type": self.name,
			"published": self.enable_web_form,
			"module": doctype.module,
			"is_standard": False, 
			"introduction_text": introduction_text, #self.description,
			"success_message": self.success_message,
			"web_form_fields": [],
			"button_label": "Submit",
			"route": self.get_route(),
			"allow_incomplete": True if backend_only_fields else False, #only allow incomplete if there are backend only fields
			"banner_image": self.form_image if cint(self.include_logo_in_web_form) else None,
			"anonymous": self.anonymous,
			"custom_css": _make_web_form_css(),
			"client_script": _make_web_form_script()
			
		}
 
		webform_supported_fields = frappe.get_meta("Web Form Field").get_field("fieldtype").options.split('\n')

		for df in [x for x in doctype.fields if x.fieldname not in [x.field_name for x in backend_only_fields]]:# excluse backend fields
			field_type = df.fieldtype
			if field_type not in webform_supported_fields:
				continue

			if field_type == 'Tab Break':
				field_type = 'Page Break'

			r['web_form_fields'].append({
				'doctype': 'Web Form Field',
				'fieldname': df.fieldname,
				'label': df.label,
				'fieldtype': field_type,
				'options': df.options,
				'reqd': df.reqd,
				'default': df.default,
				'read_only': df.read_only,
				'depends_on': df.depends_on or '',
				'mandatory_depends_on': df.mandatory_depends_on or '',
				'read_only_depends_on': df.read_only_depends_on or '',
				'description': df.description,
			})
		doc.update(r)
		doc.save(ignore_permissions=True)
		if self.name != self.web_title:
			# web form uses title as the name. In our case we want the form_name as the web form name but then web_title to be 
			# the title to be displayed on a web form
			doc.title = self.web_title
			doc.save()

		#self.route = doc.route
		#self.save()
		#frappe.db.set_value(self.doctype, self.name, "route", doc.route)
	
	def create_data_protection_fields(self):
		def remove_field(field_name):
			fields = [x for x in self.form_fields if x.field_name != field_name]
			self.form_fields = fields

		def add_data_consent_statement_field():
			self.append('form_fields', {
					"doctype": "Engagement Form Field",
					"field_label": "Data Consent Statement",
					"field_type": "HTML",
					"field_name": "data_consent_statement",
					# "depends_on": "doc.grant_data_processing_consent",
					"data_field_html": '<div id="data-consent-statement" style="height:200px; overflow: scroll"></div>'
				})

		if cint(self.show_data_processing_consent_statement):
			remove_field('data_consent_statement') # remove the terms to ensure it always comes after the checkbox
			remove_field('grant_data_processing_consent')# remove the terms to ensure it always comes before the data consent terms
			add_data_consent_statement_field()
			self.append('form_fields', {
				"doctype": "Engagement Form Field",
				"field_label": "Grant consent for data processing?",
				"field_type": "Check",
				"field_name": "grant_data_processing_consent",
			})
			
		else:
			remove_field('grant_data_processing_consent')
			remove_field('data_consent_statement')

def sanitize_web_filters(filters):
	"""
	Replace any quotation marks that may exist infront of or after doc.XXXXXX
	"""
	if not filters:
		return filters
			
	matches = WEB_FORM_LINK_FIELD_DOC_FILTER_PATTERN.findall(filters) # returns list of tuples as [('"', 'doc.admin_1', '"'), ('"', 'doc.admin_2', '"')]		
	for match in matches:
		filterVal = match[1]
		filters = re.sub(r'(\"|\')' + filterVal + '(\"|\')', filterVal, filters) 

	return filters

def convert_depends_on_conditions_to_js_format(conditions: list, ref_field:dict, ref_field_property: str) -> str:
	"""Convert filters entry as set by the Filters Dialog into js format i.e the format with eval:doc....
	Args:
		conditions (list): condition e.g [["Test Form Five","sample_gender","=","Male"]] 
	"""
	if(len(conditions) <= 0):
		return ""
	
	res = "eval:"
	for i, condition in enumerate(conditions):
		res += '(' + construct_depends_on_js_expression(condition, ref_field, ref_field_property) + ')'
		if i != len(conditions) - 1:
			exp += " && "
		
	return res; 
 
def construct_depends_on_js_expression(condition: list, ref_field:dict, ref_field_property: str) -> str :
	"""Construct a JS expression given a filter condition

	Args:
		condition (list): condition e.g ["Test Form Five","sample_gender","=","Male"] 
	"""
	if len(condition) < 4 : # condition has 4 parts
		return ""

	field = condition[1]
	if field == ref_field.field_name:
		frappe.throw(f"Row {ref_field.idx}. {frappe.bold(ref_field.field_label)}. You cannot reference {frappe.bold(ref_field.field_name)} as a condition in {frappe.bold(ref_field_property)} property as you are self-referencing the same field. A field cannot depend on itself")
	operator = condition[2]
	value = condition[3]
	exp = '';  
	if isinstance(value, str):
		value = '"' + value + '"'

	if operator == "=":
		exp = f'{DOC_PREFIX_FORMULA}{field}=={value}'
		
	if operator == "!=":
		exp = f'{DOC_PREFIX_FORMULA}{field}!={value}'
		
	if operator == "like":
		exp = f'{DOC_PREFIX_FORMULA}{field}.indexOf({value}) != -1'
		
	if operator == "not like":
		exp = f'{DOC_PREFIX_FORMULA}{field}.indexOf({value}) == -1'
		
	if operator == "in":
		exp += ''
		for i, val in enumerate(value):
			exp += f'{DOC_PREFIX_FORMULA}{field} == {val}' 
			if (i != len(value) - 1):
				exp += ' || '
		
	if operator == "not in":
		exp += ""
		for i, val in enumerate(value):
			exp += f'{DOC_PREFIX_FORMULA}{field} != {val}' 
			if (i != len(value) - 1):
				exp += ' && '
		
	if operator == "is":
		if value == 'set':
			exp = f'{DOC_PREFIX_FORMULA}{field}' 
		elif value == 'not set':
			exp = f'!{DOC_PREFIX_FORMULA}{field}'
		
	if operator == ">":
		exp = f'{DOC_PREFIX_FORMULA}{field}>{value}'
		
	if operator == "<":
		exp = f'{DOC_PREFIX_FORMULA}{field}<{value}'
		
	if operator == ">=":
		exp = f'{DOC_PREFIX_FORMULA}{field}>={value}'
		
	if operator == "<=":
		exp = f'{DOC_PREFIX_FORMULA}{field}<={value}'
		
	if operator == "Between":
		exp = f'{DOC_PREFIX_FORMULA}{field}>={value[0]} && {DOC_PREFIX_FORMULA}{field}<={value[1]}'
		
	if operator == "Timespan": 
		pass

	return exp

def doctype_to_engagement_form(doctype: str = 'Sample Test Form'):
	"""
	Make an Engagement Form based on a DocType 
	"""
	doc = frappe.get_doc("DocType", doctype)
	form = frappe.new_doc("Engagement Form")
	for field in doc.fields:
		r = field.as_dict()
		r['doctype'] = "Engagement Form Field"
		form.append("fields", r)

	form.save(ignore_permissions=True)

@frappe.whitelist()
#@frappe.validate_and_sanitize_search_inputs
# def get_docfields(doctype, txt, searchfield, start, page_len, filters):
def get_docfields(doctype):  
	res = frappe.get_all(
		"DocField",
		{
			'parenttype': 'DocType', 'parent': doctype
		},
		['name', 'fieldname', 'label'],
	)
	docs = [{'fieldname': r.fieldname, 'label': r.label} for r in res] 
	return [d for d in docs] 

@frappe.whitelist()
def get_data_processing_consent_statement():
	statement = frappe.db.get_singles_value("Engage Settings", 'data_consent_statement')
	return statement

@frappe.whitelist()
def make_engagement(form_name, description):
	engagement = frappe.new_doc("Engagement")
	details = {
		'engagement_type': 'Survey',
		'status': 'Open',
		'is_published': True,
		'has_data_forms': True,
		'engagement_form': form_name,
		'description': description
	}
	engagement.update(details) 
	return engagement.as_dict()