import frappe
from participatory_backend.enums import TechnicalAnalysisTypeEnum
from frappe import _
import re

def get_technical_analysis_type(data_type):
    mp = {
        'Float': TechnicalAnalysisTypeEnum.NUMERIC.value,
        'Integer': TechnicalAnalysisTypeEnum.NUMERIC.value,
        'String': TechnicalAnalysisTypeEnum.TEXT.value,
        'Date': TechnicalAnalysisTypeEnum.DATE.value
    }
    if data_type in mp:
        return mp[data_type]
    frappe.throw(_(f"Data type {data_type} not mapped to an analysis type"))

def get_initials(text: str):
    """
    Get initials given a string 
    """
    res = ''
    parts = text.strip().replace("  ", " ").split(" ")
    for part in parts:
        if part.isnumeric():
            res += part
        else:
            res += part[0]
    # return "".join([x[0].upper() for x in text.strip().replace("  ", " ").split(" ")])
    return res

def scrub(text: str):
    """
    Replace special characters then call frappe.scrub 
    """
    txt = '_'.join(re.findall(r'\b\w+\b', text))
    return frappe.scrub(txt)