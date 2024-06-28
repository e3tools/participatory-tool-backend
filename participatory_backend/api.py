
import frappe
from frappe.core.doctype.user.user import generate_keys
from frappe.desk.form.load import getdoctype
from frappe.desk.doctype.dashboard_chart.dashboard_chart import get as get_chart
from frappe.desk.doctype.dashboard.dashboard import get_permitted_charts
import datetime
import participatory_backend.engage.utils as EngageUtil 
from gis.utils.raster import clip_raster_to_vector
from frappe.handler import upload_file, uploadfile
from frappe.desk.reportview import get_count as get_record_count
from gis.analyzers.raster import RasterAnalyzer
from gis.enums import DatasetTypeEnum
from gis.utils.vector import get_admin_tree, get_admin_doc, get_geojson_bounds
import json
from frappe.desk.reportview import export_query
from frappe.utils.file_manager import save_file_on_filesystem 
from frappe import ping as pinged
from frappe.utils.data import get_url
from frappe.frappeclient import FrappeClient

@frappe.whitelist(allow_guest=True)
def ping():
    return pinged()

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
        user = frappe.get_doc('User', frappe.session.user)
        msg = {
            'status_code':200,
            'text':frappe.local.response.message,
            'user': frappe.session.user,
            'token': None,
            'email': user.email,
            'full_name': user.full_name,
            'username': user.username,
            'name': user.name
        }
        if(user.api_key and user.api_secret):
            msg['token'] = f"{user.api_key}:{user.get_password('api_secret')}"
        else:
            generate_keys(user.name)
            user.reload()
            msg['token'] = f"{user.api_key}:{user.get_password('api_secret')}"
        return msg
    except frappe.exceptions.AuthenticationError:
        return {'status_code': 401, 'text':frappe.local.response.message}
    except Exception as e:
        print("Login error: ", str(e))
        return {'status_code': 500, 'text':str(e)}

@frappe.whitelist()
def get_doctype(doctype: str, with_parent: int = 0):
    getdoctype(doctype, with_parent=with_parent)
    if frappe.response.docs:
        return frappe.response.docs[-1] if frappe.response.docs[-1].name == doctype else None
    return None

@frappe.whitelist()
def new_doc(doctype: str):
    return frappe.new_doc(doctype, as_dict=True)

@frappe.whitelist()
def get_doc(doctype: str, docname: str):
    try:
        return frappe.get_doc(doctype, docname)
    except:
        return None

@frappe.whitelist()
def get_count(**kwargs):
    return get_record_count()

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
    return clip_raster_to_vector('/home/nyaga/frappe-bench-15/participatory-frontend/src/data/raster/result.tiff', vector)

@frappe.whitelist()
def get_all_admins(as_tree=True):
    """
    Get all admins with the children property set 
    """
    res = get_admin_tree(as_tree=as_tree)
    return res

@frappe.whitelist()
def get_admin(admin_id: str, admin_level: int):
    """Get admin object

    Args:
        admin_id (str): Admin id
        admin_level (int): Admin Level. One of 0, 1, 2, 3
    """ 
    doc = get_admin_doc(admin_id, admin_level)
    if not doc.bounds:
        doc.bounds = str(get_geojson_bounds(doc.geom))   
    return doc

@frappe.whitelist()
def get_computation(analysis_name, vector_id, admin_level):
    vector = None
    if admin_level:
        vector = frappe.db.get_value(f"Admin {admin_level}", vector_id, ['name', 'geom'], as_dict=True)
    
    doc = frappe.get_doc("Technical Analysis", analysis_name)
    res = None
    if doc.datasource_type == DatasetTypeEnum.RASTER.value:
        analyzer = RasterAnalyzer(analysis_name=analysis_name, analysis_doc=doc, vector=vector.geom if vector else None)
        stats_obj = analyzer.analyze()
        res = { "type": doc.datasource_type, "result": stats_obj }
    if doc.datasource_type == DatasetTypeEnum.VECTOR.value:
        res = { "type": doc.datasource_type, "result": json.loads(doc.geom) }
    return res
    #return clip_raster_to_vector('/home/nyaga/frappe-bench-15/participatory-frontend/src/data/raster/result.tiff', vector)

@frappe.whitelist()
def change_password(user: str, password: str):
    from frappe.utils.password import update_password
    update_password(user, password)
    return {"res": True}
    

@frappe.whitelist()
def export_data():
    export_query()
    fl = save_file_on_filesystem(frappe.response["filename"], content=frappe.response["filecontent"])
    frappe.response["filename"] = fl['file_url']
    return {"file": fl['file_url'] }

@frappe.whitelist()
def upsert_doc():
    """Upsert a doctype

    Args:
        doc (_type_): _description_

    Returns:
        _type_: _description_
    """
    # site = frappe.utils.get_site_url(frappe.local.site)
    # client = FrappeClient(site)
    # client = FrappeClient(get_url())
    doc = frappe._dict(frappe.form_dict)
    doc = frappe.get_doc(doc).save()
    return doc
    # docname = frappe.form_dict['docname']
    # if doc.name:
    #     res = client.update(doc)
    # else:
    #     res = client.insert(doc)
    # check if there are files

@frappe.whitelist()
def sync_records(doctype: str, docs: list):
    """
    Synchronize records from the frontend

    Args:
        doctype (str): Doctype
        docs (list): Records to synchronize
    """
    fails, success = [], []
    if isinstance(docs, list):
        for rec in docs:
            try:
                doc = frappe.get_doc(rec)
                doc.save()
                success.append(rec['_name'])
            except Exception as e:
                fails.append({'rec': rec, 'error': str(e)})
                pass
    return {"res": len(fails) == 0 and len(docs) != 0, 'fail': fails, 'success': success} 

@frappe.whitelist()
def do_upload():
    """
    Upload file
    """
    return upload_file()