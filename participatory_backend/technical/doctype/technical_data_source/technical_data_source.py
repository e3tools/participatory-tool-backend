# Copyright (c) 2024, Steve Nyaga and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from gis.enums import DatasetTypeEnum
from gis.analyzers.vector import ShapeFileAnalyzer

class TechnicalDataSource(Document):
	def validate(self):
		self.validate_organization_level()

	@frappe.whitelist()
	def analyze(self):
		res = None
		if self.datasource_type == DatasetTypeEnum.VECTOR.value:
			doc = ShapeFileAnalyzer(self.name)
			res = doc.analyze()
		if self.datasource_type == DatasetTypeEnum.TABULAR.value:
			pass
		if self.datasource_type == DatasetTypeEnum.RASTER.value:
			pass
		return res

	def validate_organization_level(self):
		def _is_an_attribute(attribute_name, label):
			exists = [x for x in self.attributes if x.table_field == attribute_name]	
			if not exists:
				frappe.throw(_(f"Attribute value [{frappe.bold(attribute_name)}] for [{frappe.bold(label)}] is not listed as an attribute in the Attributes table"))
 
		if self.datasource_type == DatasetTypeEnum.VECTOR.value:
			county_field = [x for x in self.meta.fields if x.fieldname == 'shape_file_county_field'][0]
			sub_county_field = [x for x in self.meta.fields if x.fieldname == 'shape_file_sub_county_field'][0]
			ward_field = [x for x in self.meta.fields if x.fieldname == 'shape_file_ward_field'][0]

			if self.shape_file_county_field:  
				_is_an_attribute(self.shape_file_county_field, county_field.label)

			if self.shape_file_sub_county_field:		 
				_is_an_attribute(self.shape_file_sub_county_field, sub_county_field.label)

			if self.shape_file_ward_field: 
				_is_an_attribute(self.shape_file_ward_field, ward_field.label)

		# if self.lowest_organization_level == "County": 
		# 	if not self.county_field:
		# 		frappe.throw(_(f"You must select the {county_field.label}"))
		# 	_is_an_attribute(self.county_field, county_field.label)

		# if self.lowest_organization_level == "Sub-County":
		# 	if not self.county_field:
		# 		frappe.throw(_(f"You must select the {county_field.label}"))
		# 	_is_an_attribute(self.county_field, county_field.label)
 
		# 	if not self.sub_county_field:				
		# 		frappe.throw(_(f"You must select the {sub_county_field.label}"))
		# 	_is_an_attribute(self.sub_county_field, sub_county_field.label)

		# if self.lowest_organization_level == "Ward": 
		# 	if not self.county_field: 
		# 		frappe.throw(_(f"You must select the {county_field.label}"))
		# 	_is_an_attribute(self.county_field, county_field.label)
 
		# 	if not self.sub_county_field:				
		# 		frappe.throw(_(f"You must select the {sub_county_field.label}"))
		# 	_is_an_attribute(self.sub_county_field, sub_county_field.label)
 
		# 	if not self.ward_field: 
		# 		frappe.throw(_(f"You must select the {ward_field.label}"))
		# 	_is_an_attribute(self.ward_field, ward_field.label)


