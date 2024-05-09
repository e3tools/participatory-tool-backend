import frappe
from frappe.core.doctype.user.user import generate_keys

def generate_user_api_keys():
    """
    Generate API Keys for users
    """
    or_filters = {"api_key": None, "api_secret": None, "api_key": "", "api_secret": "" }
    users = frappe.get_all("User", fields=["name", "enabled"], or_filters=or_filters)
    for usr in users:
        if(usr.enabled and usr.name not in ['Administrator', 'Guest']):
            generate_keys(usr.name)