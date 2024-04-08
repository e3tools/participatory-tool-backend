// Copyright (c) 2024, Steve Nyaga and contributors
// For license information, please see license.txt

frappe.ui.form.on("Technical Data", {
	refresh(frm) {

	},
    shape_file(frm) {
        frm.clear_table("attributes");
        if(frm.doc.shape_file){
            frappe.call({
                method: 'gis.gis.doctype.shape_file.shape_file.get_shape_file_field_mappings',
                freeze: true,
                freeze_message: __('Please wait...'),
                args: {
                    'shape_file': frm.doc.shape_file
                },
                callback: function(r) {
                    if(!r.exc){ 
                        let recs = r.message  
                        $.each(r.message.field_mappings || [], function(i, itm) {
                            var child = cur_frm.add_child('attributes');							
                            frappe.model.set_value(child.doctype, child.name, "attribute_name", itm.attribute);
                            frappe.model.set_value(child.doctype, child.name, "data_type", itm.attribute_data_type);
                            frappe.model.set_value(child.doctype, child.name, "table_field", itm.table_field); 
                            frappe.model.set_value(child.doctype, child.name, "table_field_data_type", itm.table_field_data_type);
                        });
                        cur_frm.refresh_field('attributes');
                    }
                }
            })
        }
    }
});
