# Copyright (c) 2024, Steve Nyaga and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from frappe import _
from gis.enums import DatasetTypeEnum
from gis.analyzers.vector import ShapeFileAnalyzer
from gis.analyzers.raster import RasterAnalyzer
from gis.utils.common import extract_fields_from_formula
from participatory_backend.enums import TechnicalAnalysisTypeEnum
from participatory_backend.utils import get_technical_analysis_type

class TechnicalAnalysis(Document):
	def validate(self):
		# self.validate_organization_level()
		if self.datasource_type == DatasetTypeEnum.VECTOR:
			self.infer_analysis_type()
			if not self.description_field:
				frappe.throw(_("You must specify the field to use for {0}".format(self.meta.get_field('description_field').label)))
		self.analyze()

	def infer_analysis_type(self):
		if self.analysis_based_on == 'Single Field':
			self.formula = "{" + self.analysis_field + "}"
		fields = extract_fields_from_formula(self.formula, return_enclosed=False)		
		data_types = []
		data_source = frappe.get_doc("Technical Data Source", self.data_source) 
		data_types = [x.table_field_data_type for x in data_source.attributes if x.attribute_name in fields]
		if len(list(set(data_types))) > 1:
			frappe.throw(_("Formula includes fields of different data types"))
		elif len(list(set(data_types))) == 0:
			frappe.throw(_("Formula must include at lease one field"))
		self.analysis_type = get_technical_analysis_type(data_types[0]) 

	@frappe.whitelist()
	def analyze(self):
		res, parent_json = None, None
		self.result_items = []
		if self.datasource_type == DatasetTypeEnum.VECTOR.value:
			doc = ShapeFileAnalyzer(analysis_doc=self)
			res, parent_json = doc.analyze()
			if res:
				self.geom = parent_json
				for itm in res:
					result = frappe._dict(itm)
					geom = itm.geom
					result.pop('doctype', None)
					result.pop('geom', None)
					self.append('result_items', {
						'doctype': 'Technical Analysis Result Item',
						'description': itm.get(self.description_field),
						'result': json.dumps(result),
						'geom': json.dumps(geom)
					}) 
		if self.datasource_type == DatasetTypeEnum.TABULAR.value:
			pass
		if self.datasource_type == DatasetTypeEnum.RASTER.value:
			doc = RasterAnalyzer(analysis_doc=self) 
			# out_image, file_url, nodata = doc.analyze()
			# res = out_image
			stats_obj = doc.analyze()
			res = stats_obj
		
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



