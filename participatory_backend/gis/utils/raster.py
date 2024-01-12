import frappe
import rasterio
import rasterio.mask
import datetime 
from frappe.utils import call_hook_method, cint, get_files_path
from frappe.utils.file_manager import save_file, delete_file, save_file_on_filesystem #, remove_file_by_url
import tempfile

def clip_raster(raster_path, vector):
    raster_file = str(datetime.datetime.now()).replace(' ', '_').replace('-','').replace(':','').replace('.', '_') + '.png'# '.tif'
    output_raster_path = raster_file # get_files_path(raster_file, is_private=False)
    with rasterio.open(raster_path) as src:
        out_img, out_transform = rasterio.mask.mask(src, [vector], crop=True)
        out_meta = src.meta

    out_meta.update({
        #'driver': 'GTiff',
        'driver': 'PNG',
        'height': out_img.shape[1],
        'width': out_img.shape[2],
        'transform': out_transform
    })

    # enable compress
    out_meta.update({'compress': 'lzw'})   

    tmp_file = tempfile.NamedTemporaryFile().name
    with rasterio.open(tmp_file, 'w', **out_meta) as dest:
        dest.write(out_img)

    # save to frappe site files folder
    with open (tmp_file, "rb") as myfile:
        data_file=myfile.read()

    frappe.db.connect() #connect incase just to avoid risk of Lost connection error  
    #delete_file("files/" + report_name + ".zip") # delete old zip if it exists
    
    print ("Attaching file ...")
    fl = save_file_on_filesystem(output_raster_path, content=data_file)
    print ("File url", fl['file_url'])
    return fl['file_url']  