# Copyright (c) 2024, Steve Nyaga and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import datetime
from frappe.utils import getdate
from frappe import _
from participatory_backend.enums import EngagementActionTaskUpdateTypeEnum

class EngagementActionTaskUpdate(Document):
	def validate(self):
		if getdate(self.as_at_date) > getdate():
			frappe.throw(_(f"As at Date cannot be a future date. Specify a date earlier or equal to {getdate()}"))
		
		# If we are updating multiple fields at once, then validate start and end dates
		if self.update_type == EngagementActionTaskUpdateTypeEnum.BULK:
			if self.new_start_date and self.new_end_date:
				if getdate(self.new_start_date) > getdate(self.new_end_date):
					frappe.throw(_("The start date must be earlier than the end date"))
		self.validate_media() 
		self.update_action_task()

	def validate_media(self):
		for item in self.media_files:
			self.set_media_type(item)

	def update_action_task(self):
		"""
		Update status of the action task
		"""
		if self.status != 'Approved':
			return			
		before_doc = self._doc_before_save
		# check if there was a status change
		if before_doc.status != self.status:
			# do update
			action_task = frappe.get_doc("Engagement Action Task", self.action_task)
			action_task.update_action_task(self)

	def set_media_type(self, item):
		"""
		Set media type
		"""
		# See https://stackoverflow.com/questions/55307951/check-if-a-file-type-is-a-media-file
		# See https://note.nkmk.me/en/python-mimetypes-usage/#:~:text=Use%20the%20guess_type()%20function,type%2C%20encoding)%20is%20returned.&text=The%20first%20element%20of%20the,compressed%20with%20gzip%20%2C%20for%20example.
		mimetyp = item.file_type
		item.media_type = mimetyp
		parts = item.name.split('.')
		if parts and len(parts) > 1:
			item.extension = parts[-1]
		if mimetyp.startswith('image'):
			item.media_category = 'Image'
		elif mimetyp.startswith('audio'):
			item.media_category = 'Audio'
		elif mimetyp.startswith('video'):
			item.media_category = 'Video'
		else:
			item.media_category = 'Other'
