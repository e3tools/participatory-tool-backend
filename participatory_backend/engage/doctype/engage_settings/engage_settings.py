# Copyright (c) 2024, Steve Nyaga and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class EngageSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		app_introduction: DF.SmallText
		app_name: DF.Data
		app_slogan: DF.Data
		column_1_details: DF.SmallText | None
		column_1_title: DF.Data | None
		column_2_details: DF.SmallText | None
		column_2_title: DF.Data | None
		column_3_details: DF.SmallText | None
		column_3_title: DF.Data | None
		county_name: DF.Data
		county_slogan: DF.Data
		data_consent_statement: DF.TextEditor | None
		logo: DF.AttachImage | None
		socket: DF.Data | None
		watermark_image: DF.AttachImage | None
	# end: auto-generated types
	def validate(self):
		if self.column_1_title and not self.column_1_details:
			frappe.throw(_("You must specify Column 1 Contents"))
		if self.column_2_title and not self.column_2_details:
			frappe.throw(_("You must specify Column 2 Contents"))
		if self.column_3_title and not self.column_3_details:
			frappe.throw(_("You must specify Column 3 Contents"))
