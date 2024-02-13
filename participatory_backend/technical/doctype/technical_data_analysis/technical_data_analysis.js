// Copyright (c) 2024, Steve Nyaga and contributors
// For license information, please see license.txt

// cur_frm.add_fetch('analysis_field', 'data_type', 'data_type')

frappe.ui.form.on("Technical Data Analysis", { 
    setup: function (frm) {
		frm.set_query("analysis_field", function () {
            if(!frm.doc.technical_data){
                frappe.throw(__("Select the value of Technical Data first"))
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

	},
}); 