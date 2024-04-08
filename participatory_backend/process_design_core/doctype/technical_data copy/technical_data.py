# Copyright (c) 2024, Steve Nyaga and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class TechnicalData(Document):
	def validate(self):
		self.validate_organization_level()

	def validate_organization_level(self):
		def _is_an_attribute(attribute_name, label):
			exists = [x for x in self.attributes if x.table_field == attribute_name]	
			if not exists:
				frappe.throw(_(f"Attribute value [{frappe.bold(attribute_name)}] for [{frappe.bold(label)}] is not listed as an attribute in the Attributes table"))

		county_field = [x for x in self.meta.fields if x.fieldname == 'county_field'][0]
		sub_county_field = [x for x in self.meta.fields if x.fieldname == 'sub_county_field'][0]
		ward_field = [x for x in self.meta.fields if x.fieldname == 'ward_field'][0]

		if self.lowest_organization_level == "County": 
			if not self.county_field:
				frappe.throw(_(f"You must select the {county_field.label}"))
			_is_an_attribute(self.county_field, county_field.label)

		if self.lowest_organization_level == "Sub-County":
			if not self.county_field:
				frappe.throw(_(f"You must select the {county_field.label}"))
			_is_an_attribute(self.county_field, county_field.label)
 
			if not self.sub_county_field:				
				frappe.throw(_(f"You must select the {sub_county_field.label}"))
			_is_an_attribute(self.sub_county_field, sub_county_field.label)

		if self.lowest_organization_level == "Ward": 
			if not self.county_field: 
				frappe.throw(_(f"You must select the {county_field.label}"))
			_is_an_attribute(self.county_field, county_field.label)
 
			if not self.sub_county_field:				
				frappe.throw(_(f"You must select the {sub_county_field.label}"))
			_is_an_attribute(self.sub_county_field, sub_county_field.label)
 
			if not self.ward_field: 
				frappe.throw(_(f"You must select the {ward_field.label}"))
			_is_an_attribute(self.ward_field, ward_field.label)


