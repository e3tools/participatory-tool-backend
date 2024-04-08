# Copyright (c) 2024, Steve Nyaga and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe import _
from participatory_backend.enums import EngagementActionTaskUpdateTypeEnum

class EngagementActionTask(Document):
	def validate(self):
		self.validate_resources()
		self.validate_assignees()
		self.validate_dependencies()

	def validate_resources(self):
		for item in self.resources:
			if item.unit_type in ['Number', 'Person', 'Money']:
				res = flt(item.resource_details)
				if not res:
					frappe.throw(_("Resources row {}. The value specified is not a number".format(item.idx)))

	def validate_assignees(self):
		for item in self.assignees:
			if item.assignee_type == 'System User':
				if not item.system_user:
					frappe.throw(_("Assignees row {}.You must specify the system user".format(item.idx)))
				else:
					item.assignee = item.system_user

	def validate_dependencies(self):
		this_task = [x for x in self.dependencies if x.task == self.name]
		this_task = this_task[0] if this_task else None
		if this_task:
			frappe.throw(_("Dependencies row {}. Task is set to depend on itself. Please remove task {} from the list of dependencies".format(this_task.idx, frappe.bold(this_task.task_name))))

	
	def update_action_task(self, update_action_task_doc):
		"""Update action task

		Args:
			update_action_task_doc (doctype): An instance of Engagement Action Task Update
		"""  
		BULK = 'Multiple Fields At Once'

		updated = False
		updater = update_action_task_doc
		if updater.remarks:
			self.latest_update = update_action_task_doc.remarks
		if updater.update_type in [EngagementActionTaskUpdateTypeEnum.PERCENTAGE_PROGRESS.value, EngagementActionTaskUpdateTypeEnum.BULK.value] and updater.new_progress:
			self.progress = updater.new_progress
			updated = True
		if updater.update_type in [EngagementActionTaskUpdateTypeEnum.TASK_STATUS.value, EngagementActionTaskUpdateTypeEnum.BULK.value] and updater.new_status:
			self.status = updater.new_status
			updated = True
		if updater.update_type in [EngagementActionTaskUpdateTypeEnum.START_DATE.value, EngagementActionTaskUpdateTypeEnum.BULK.value] and updater.new_start_date:
			self.start_date = updater.new_start_date
			updated = True
		if updater.update_type in [EngagementActionTaskUpdateTypeEnum.END_DATE.value, EngagementActionTaskUpdateTypeEnum.BULK.value] and updater.new_end_date:
			self.start_date = updater.new_end_date
			updated = True
		
		self.flags.updater_ref = {
			'doctype': updater.doctype,
			'docname': updater.name,
			"label": _(f"Via {updater.doctype}"),
		}
		self.save(ignore_permissions=True)