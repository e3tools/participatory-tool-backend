// Copyright (c) 2024, Steve Nyaga and contributors
// For license information, please see license.txt

frappe.ui.form.on("KoboToolbox", {
	refresh(frm) {

	},
    btn_test_connection: function(frm) {
        frappe.call({ 
            doc: frm.doc,
		    freeze_message: __('Connecting...Please wait'),
            freeze: true,
            method: 'test_connection',
            callback: function(r){
                if(!r.exc){
                    console.log("Connected")
                }
            }
        })
    }
});
