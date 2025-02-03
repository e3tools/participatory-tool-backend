# Copyright (c) 2025, Steve Nyaga and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EngagementProfileUserAssignment(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		engagement_profile: DF.Link
		engagement_user: DF.Link
		full_name: DF.ReadOnly | None
	# end: auto-generated types
	
	def validate(self):
		exists = frappe.db.exists(self.doctype, {"user": self.engagement_user})
		if exists and exists != self.name:
			frappe.throw(_("Another record for the selected user already exists"))
		
		self.delete_permissions()
		profile = frappe.get_doc("Engagement Profile", self.engagement_profile)
		for group in profile.form_groups:
			doc = frappe.get_doc({
				"doctype": "User Permission",
				"user": self.engagement_user,
				"allow": "Engagement Form Group",
				"for_value": group.engagement_form_group
			}).insert(ignore_permissions=True)

	def on_trash(self):
		self.delete_permissions()

	def delete_permissions(self):
		permissions = frappe.db.get_list("User Permission", {
										"user": self.engagement_user, 
										"allow": "Engagement Form Group"
									})
		# delete only those permissions that are exclusively to the rols in th
		for perm in permissions:
			frappe.delete_doc("User Permission", perm.name)
	
@frappe.whitelist()
def get_engagement_profile(engagement_profile: str):
	exists = frappe.db.exists("Engagement Profile", engagement_profile)
	if exists:
		doc = frappe.get_doc("Engagement Profile", exists)
		return doc.as_dict()
	return None