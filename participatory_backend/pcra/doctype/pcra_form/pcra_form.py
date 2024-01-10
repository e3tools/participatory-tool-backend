# Copyright (c) 2023, Steve Nyaga and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
import random

class PCRAForm(Document):
	pass


@frappe.whitelist()
def get_events(start, end, filters=None):
	"""Returns events for Gantt / Calendar view rendering.
	:param start: Start date-time.
	:param end: End date-time.
	:param filters: Filters (JSON).
	"""
	# def _is_employee_selected():
	# 	emp = [x for x in filters if x[1] == 'employee']
	# 	if emp:
	# 		return emp[0][3]
	# 	return None
	
	filters = json.loads(filters)
	"""
	employee = _is_employee_selected() 
	if approval_status.ACCOUNTS_APPROVER_ROLE not in frappe.get_roles():	
		#If not an ACCOUNTS_APPROVER_ROLE, check validate reports to
		logged_in_employee = get_employee_by_user(frappe.session.user)
		if not employee:
			# If no employee filter, get emp_id of current user
			if not logged_in_employee:
				frappe.msgprint(_("There is no employee associated with the current user. Specify an employee to view timesheets"))
				return []
		else:
			if employee != logged_in_employee:
				# check if the selected employee reports to the loggedin employee
				reports_to = frappe.db.exists("Employee", {"name": employee, "reports_to": logged_in_employee})
				if not reports_to:
					frappe.msgprint(_("The selected employee does not report to you"))
					return []
				
	valid_emps = employee if isinstance(employee, list) else [employee] 
	"""
	from frappe.desk.calendar import get_event_conditions

	"""
	# remove employee filter
	filters = [x for x in filters if x[1] != 'employee']
	# set employee filter
	filters.append(['Time Ledger', 'employee', 'in', valid_emps, False])
	start_date_filter = [x for x in filters if x[1] == 'start_date']
	if start_date_filter:
		start = start_date_filter[0][3]
	end_date_filter = [x for x in filters if x[1] == 'end_date']
	if end_date_filter:
		end = end_date_filter[0][3]
	"""
	filters = str(json.dumps(filters))
	conditions = get_event_conditions("PCAR Form", filters)

	vals = frappe.db.sql(
		"""select 
			/*`tabPCRA Form`.employee,
			`tabPCRA Form`.employee_name,*/
			`tabPCRA Form`.docstatus as approval_status,
			`tabPCRA Form`.name as name,
			`tabPCRA Form`.docstatus as status, 
			NULL as parent,
			`tabPCRA Form`.posting_date as start_date, 
			12 as hours, 
			/*activity_type,*/
			`tabPCRA Form`.ward as project, 
			DATE_ADD(`tabPCRA Form`.posting_date, INTERVAL 12 HOUR) as end_date,
			CONCAT(`tabPCRA Form`.ward, ' (', ROUND(12,2),' hrs) ') as title
		from `tabPCRA Form`
		where  `tabPCRA Form`.docstatus < 2 
			and (posting_date >= %(start)s and posting_date <= %(end)s)
			/*(posting_date <= %(end)s and posting_date >= %(start)s)*/ {conditions} 
		""".format(
			conditions=conditions
		),
		{"start": start, "end": end, "docstatus": ("!=", 2)},
		as_dict=True,
		update={"allDay": 1}, debug=False
		# set allDay to 1 to disable displayng the time from and to time
	)
	# assign colors
	colors = ['#0d0887', '#220690', '#330597', '#43039e', '#5102a3', '#6001a6', '#6c00a8', '#7a02a8', '#8707a6', '#9410a2', '#a01a9c', '#ab2494', '#b42e8d', '#be3885', '#c7427c', '#cf4c74', '#d7566c', '#de6164', '#e56a5d', '#eb7556', '#f0804e', '#f58c46', '#f9983e', '#fca537', '#fdb130', '#febe2a', '#fccd25', '#f9dc24', '#f5eb27', '#f0f921']
	color_mp = {}
	for proj in vals:
		color = random.choice(colors)
		if proj['project'] in color_mp:
			proj['color'] = color_mp[proj['project']]
		else:
			proj['color'] = color
			color_mp[proj['project']] = color
		# proj['color'] = color
	
	return vals
