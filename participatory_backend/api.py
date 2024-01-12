
import frappe
from frappe.core.doctype.user.user import generate_keys
from frappe.desk.form.load import getdoctype
from frappe.desk.doctype.dashboard_chart.dashboard_chart import get as get_chart
from frappe.desk.doctype.dashboard.dashboard import get_permitted_charts
import datetime
import participatory_backend.engage.utils as EngageUtil
from participatory_backend.gis.utils.raster import clip_raster

@frappe.whitelist(allow_guest=True)
def login(**kwargs):
    try:
        #usr, pwd, cmd = frappe.form_dict.values()
        usr, pwd = None, None
        if frappe.form_dict.values():
            values = frappe.form_dict.values().mapping.get('_value')
            if values:
                usr, pwd = values.get('usr'), values.get('pwd')
        if not usr or not pwd:
            values = frappe.form_dict
            usr, pwd = values.get('usr'), values.get('pwd')

        auth = frappe.auth.LoginManager()
        auth.authenticate(user=usr, pwd=pwd)
        auth.post_login()
        msg = {
            'status_code':200,
            'text':frappe.local.response.message,
            'user': frappe.session.user
        }
        user = frappe.get_doc('User', frappe.session.user)
        if(user.api_key and user.api_secret):
            msg['token'] = f"{user.api_key}:{user.get_password('api_secret')}"
        else:
            generate_keys(user.name)
            user.reload()
            msg['token'] = f"{user.api_key}:{user.get_password('api_secret')}"
        return msg
    except frappe.exceptions.AuthenticationError:
        return {'status_code':401, 'text':frappe.local.response.message}
    except Exception as e:
        return {'status_code':500, 'text':str(e)}

@frappe.whitelist()
def get_doctype(doctype: str, with_parent: int = 0):
    return getdoctype(doctype, with_parent=with_parent)

@frappe.whitelist()
def new_doc(doctype: str):
    return frappe.new_doc(doctype, as_dict=True)

@frappe.whitelist()
def get_dashboards(**kwargs):
    """
    Get dashboards
    """    
    return frappe.db.get_list("Dashboard")

@frappe.whitelist()
def get_dashboard_charts(**kwargs):
    """
    Get permitted charts for a dashboard
    """
    dashboard_name = frappe.form_dict['dashboard_name']
    return get_permitted_charts(dashboard_name)

@frappe.whitelist()
def get_dashboard_chart(
    chart_name=None,
	chart=None,
	no_cache=None,
	filters=None,
	from_date=None,
	to_date=None,
	timespan=None,
	time_interval=None,
	heatmap_year=None,
	refresh=None,
):
    """
    Get dashboard chart data
    """
    res = get_chart(chart_name=chart_name,
                    chart=None,
                    no_cache=no_cache,
                    filters=filters,
                    from_date=from_date,
                    to_date=to_date,
                    timespan=timespan,
                    time_interval=time_interval,
                    heatmap_year=heatmap_year,
                    refresh=refresh,
        )
    return res
 
@frappe.whitelist()
def save_engagement_entry():
    """
    Save engagement entry
    The object has DocType as the keys
    """
    return EngageUtil.save_engagement_entry()    

@frappe.whitelist()
def discard_draft_engagement_entry(engagement_entry_name):
    """
    Discard draft records that are not completed. will set the status to CANCELLED
    """
    EngageUtil.discard_draft_engagement_entry(engagement_entry_name) 
 
@frappe.whitelist()
def get_engagement_entry_records(engagement_entry_name):
    """
    Get all records associated with an engagement entry
    """
    return EngageUtil.get_engagement_entry_records(engagement_entry_name)

@frappe.whitelist()
def get_raster(vector):
    return clip_raster('/home/sftdev/frappe-bench-15/participatory-frontend/src/data/raster/result.tiff', vector)