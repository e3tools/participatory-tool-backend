import frappe
from participatory_backend.engage.utils import get_active_engagements
import datetime
from frappe.utils import formatdate, getdate, get_url
from participatory_backend.www.engage.engage_base import get_context as get_base_context

def get_context(context):
	get_base_context(context)
	context.no_cache = 1
	context.engagement = {}
	context.days_left = None
	context.new_doc_link = None
	if frappe.form_dict.name:
		doc = frappe.get_doc("Engagement", frappe.form_dict.name)
		context.engagement = doc
		context.days_left = get_days_left(doc.closing_date)
		context.closing_date = formatdate(doc.closing_date)
		context.is_open = getdate(doc.closing_date) >= getdate()

		if doc.has_data_forms:
			if doc.engagement_form:
				engagement_form = frappe.get_doc("Engagement Form", doc.engagement_form)
				context.new_doc_link = get_url(engagement_form.route) + '/new'


def get_days_left(closing_date: datetime.date):
	if not closing_date:
		return 0
	days = (datetime.date.today() - closing_date).days
	return max(0, days)