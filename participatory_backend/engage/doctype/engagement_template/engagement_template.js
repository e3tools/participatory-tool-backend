// Copyright (c) 2023, Steve Nyaga and contributors
// For license information, please see license.txt

frappe.ui.form.on("Engagement Template", {
	refresh(frm) {
	},
    setup: function(frm) { 
        frm.set_query('doctype_item', 'items', function() {
            return {
                filters: {
                    'istable': 0
                }
            };
        });
    }
});

frappe.ui.form.on("Engagement Template Item", "doctype_item", function(frm, dt, dn) {
    var child = locals[dt][dn];
    frappe.model.set_value(dt, dn, "display_name", child.doctype_item);
});

