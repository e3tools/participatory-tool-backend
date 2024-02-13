import frappe
import datetime
from participatory_backend.enums import EngagementStatusEnum
from frappe.desk.form.linked_with import get_linked_docs, get_linked_doctypes
from frappe.utils import cint

def update_engagement_entry_status(engagement_entry_name, status: EngagementStatusEnum):
	"""
	Discard draft records that are not completed. will set the status to CANCELLED
	"""
	linked_records = get_linked_docs("Engagement Entry", engagement_entry_name, linkinfo=get_linked_doctypes("Engagement Entry"))
	for doctype in linked_records:
		for doc in linked_records[doctype]:
			frappe.db.set_value(doctype, doc.name, "engagement_entry_status", status.value)
	frappe.db.set_value("Engagement Entry", engagement_entry_name, "status", status.value) 


def discard_draft_engagement_entry(engagement_entry_name):
	"""
	Discard draft records that are not completed. will set the status to CANCELLED
	"""
	update_engagement_entry_status(engagement_entry_name, EngagementStatusEnum.CANCELLED) 


def is_engagement_entry_ready_to_submit(engagement_entry_name, engagement_name=None, engagement_entry_doc=None):
	"""Check if all the doctypes linked with the template have data and thus ready to submit

	Args:
		engagement_entry_name: Name of Engagement Entry
		engagement_name. Name of engagement. Defaults to None.
		engagement_entry_record: Data entered by user against an engagement. Defaults to None.
	"""
	if not engagement_name:
		engagement_name = frappe.db.get_value("Engagement Entry", engagement_entry_name, "engagement_name")
	doctypes = get_engagement_doctypes(engagement_name)
	if not engagement_entry_doc:
		engagement_entry_doc = get_engagement_entry_records()

	if not engagement_entry_doc:
		return False 
	
	required_doctypes = get_engagement_doctypes(engagement_name)
	for doctype in required_doctypes:
		if doctype not in engagement_entry_doc: # if doctype is missing, then it is not ready for submit
			return False
	return True


def get_engagement_doctypes(engagement_name):
	"""Get doctypes that are required to capture data related to an engagement

	Args:
		engagement_name: Name of the engagement 
	"""
	doctypes = []
	# get the engagement
	engagement = frappe.get_doc("Engagement", engagement_name)
	if cint(engagement.has_data_forms):
		# get the template
		template = frappe.get_doc("Engagement Template", engagement.data_forms_template)
		doctypes = [x.doctype_item for x in template.items]
	return doctypes


def save_engagement_entry():
	"""
	Save engagement entry
	The object has DocType as the keys
	"""
	def save_doctype_entry(doctype, entry):
		# entry['engagement_entry'] = engagement_entry.name
		# entry['engagement_name'] = engagement_entry.status
		if 'name' in entry and entry['name'] != None:
			doc = frappe.get_doc(doctype, entry['name'])
		else:
			doc = frappe.new_doc(doctype)
		
		doc.update(entry)
		doc.engagement_entry = engagement_entry.name
		doc.engagement_entry_status = engagement_entry.status		
		doc.save(ignore_permissions=True) #if entry.name else doc.insert(ignore_permissions=True) 

	data = frappe.form_dict.entry
	engagement_name = data['Engagement']['name'] if isinstance(data['Engagement'], object) else data['Engagement']
	engagement = frappe.get_doc("Engagement", engagement_name)	
	engagement_entry = None
	engagement_entry_name = None
	if 'Engagement Entry' in data:
		engagement_entry_name = data['Engagement Entry']['name'] if isinstance(data['Engagement Entry'], object) else data['Engagement Entry']
	if 'Engagement Entry' in data: # is an edit
		engagement_entry = frappe.get_doc("Engagement Entry", engagement_entry_name)
	else: # is a first time entry
		engagement_entry = frappe.new_doc("Engagement Entry")
		rec = {
			"doctype": "Engagement Entry",
			'engagement': engagement.name,
			'engagement_name': engagement.engagement_name,
			'entered_by': frappe.session.user,
			'entered_on': datetime.datetime.now(),
			'status': EngagementStatusEnum.DRAFT.value
		}
		engagement_entry.update(rec)
	engagement_entry.save(ignore_permissions=True)

	submit = is_engagement_entry_ready_to_submit(engagement_entry_name=engagement_entry.name, 
											  engagement_name=engagement.name, 
											  engagement_entry_doc=data)
	if submit:
		engagement_entry.status = EngagementStatusEnum.SUBMITTED.value
		engagement_entry.save(ignore_permissions=True)

	for doctype in data:
		if doctype not in ['Engagement', 'Engagement Entry']:
			save_doctype_entry(doctype, data[doctype])
	return engagement_entry.name

def get_engagement_entry_records(engagement_entry_name):
	"""
	Get all records associated with an engagement entry
	"""
	record_mp = {}
	engagement_entry = frappe.db.exists("Engagement Entry", engagement_entry_name)
	if engagement_entry:
		# get engagement entry
		entry = frappe.get_doc("Engagement Entry", engagement_entry)
		record_mp['Engagement Entry'] = entry.as_dict()
		# get the engagement
		engagement = frappe.get_doc("Engagement", entry.engagement)
		if engagement.has_data_forms:
			# get the template
			template = frappe.get_doc("Engagement Template", engagement.data_forms_template)
			# get doctypes making up the template
			for item in template.items:
				exists = frappe.db.exists(item.doctype_item, {"engagement_entry": engagement_entry})
				if exists:
					record_mp[item.doctype_item] = frappe.get_doc(item.doctype_item, exists).as_dict()
	return record_mp