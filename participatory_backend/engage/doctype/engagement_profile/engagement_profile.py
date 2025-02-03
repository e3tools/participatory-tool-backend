# Copyright (c) 2025, Steve Nyaga and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class EngagementProfile(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from participatory_backend.engage.doctype.engagement_profile_item.engagement_profile_item import EngagementProfileItem

		form_groups: DF.Table[EngagementProfileItem]
		profile_name: DF.Data
	# end: auto-generated types
	pass

	def validate(self):
		# check duplicates
		for grp in self.form_groups:
			lst = [x.idx for x in self.form_groups if x.engagement_form_group == grp.engagement_form_group]
			if len(lst) > 1:
				frappe.throw(_(f"Form Group [{frappe.bold(grp.engagement_form_group)}] has been specified more than once in rows {lst}"))
