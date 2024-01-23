import frappe
import requests
import json

#DATA_URL = 'https://kf.kobotoolbox.org/api/v2/assets/aQsYFP8rSEo6n9gay8aCnu/data.json'
API_PREFIX = '/api/v2/assets'

def get_metadata(connection):
	doc = frappe.get_doc("KoboToolbox", connection)
   #url = f'{self.url}{self.uuid}/submissions/?format=json'   
	url = f'{doc.base_url}{API_PREFIX}/{doc.form_uuid}.json'
	headers = {
		'Authorization': f'Token {doc.api_token}'
	}
	kobo = requests.get(url, headers=headers)
	data = json.loads(kobo.content)
	return data
	
def get_data(connection, format='json', query=None, start=0, limit=30000):
	"""Get submissions for a given Kobo connection

	Args:
		connection: Name of the connection
		format (str, optional): Format of data. Defaults to 'json'. Either xml, json or geojson
		query (JSON object, optional): Filter query. Format of query={"field":{"op": "value"}} or query={"field":"value"}. 
				Example 1: query={"_submission_time": {"$gt": "2019-09-01T01:02:03"}}' 
				Example 2: query={"__version__": "vWvkKzNE8xCtfApJvabfjG"}'				
				Defaults to None.
		start (int, optional): Start of pagination. Defaults to 0.
		limit (int, optional): Size of pagination. Maximum is 30000. Defaults to 30000. 
	"""
	doc = frappe.get_doc("KoboToolbox", connection)
	url = f'{doc.base_url}{API_PREFIX}/{doc.form_uuid}/data/?format={format}'
	if query:
		url += "&query=" + json.dumps(query)
	if start:
		url += f"&start={start}&limit={limit}"
	headers = {
		'Authorization': f'Token {doc.api_token}'
	} 
	kobo = requests.get(url, headers=headers)
	data = json.loads(kobo.content)
	return data