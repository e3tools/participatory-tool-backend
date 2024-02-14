// Copyright (c) 2024, Steve Nyaga and contributors
// For license information, please see license.txt

frappe.ui.form.on("Technical Data Source", {
    setup: function (frm) {        
		frm.set_query("county_field", function () {
            if(!frm.doc.datasource_type){
                frappe.throw(__("Select Dataset Type first"))
            }
            if(frm.doc.datasource_type == 'Vector' && !frm.doc.shape_file){
                frappe.throw(__("Select the shape file first"))
            }
            if(frm.doc.datasource_type == 'Tabular' && !frm.doc.statistics_file){
                frappe.throw(__("Select the statistics file"))
            }           
			return {
				filters: {
					parent: frm.doc.technical_data,
					//'is_company_account': 1
				},
			};
		}); 
	},
	refresh(frm) {
        if(!frm.doc.__islocal){
			frm.add_custom_button(__("Analyze"), function() {
				frappe.call({
                    doc: frm.doc,
                    freeze: true,
                    freeze_message: __('Analyzing. Please wait...'),
                    method: 'analyze',
                    callback: function(r) {
                        if(!r.exc){
                            debugger
                        }
                    }
                })
			});
		}
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
