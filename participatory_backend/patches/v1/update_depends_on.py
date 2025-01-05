
import frappe

def execute():
	"""
	Update depends_on fields by triggering save
	Publish all Engagement Forms 
	"""
	engagement_forms = frappe.db.get_list("Engagement Form", order_by='modified asc')
	for form in engagement_forms:
		print(f"Processing form: {form.name}")
		doc = frappe.get_doc('Engagement Form', form.name)
		if doc.field_is_table:
			pass
		else:
			doc.enable_web_form = True
		doc.save()