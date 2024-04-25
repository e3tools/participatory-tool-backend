// Copyright (c) 2024, Steve Nyaga and contributors
// For license information, please see license.txt

frappe.ui.form.on("Form", {
    setup(frm) {
        frm.set_query("field_child_doctype", "form_fields", function() {
			return {
				filters: {
					'istable': 1
				}
			};
		});
    },
	refresh(frm) {
        if (!frm.is_new() && !frm.doc.istable) {
			if (frm.doc.issingle) {
				frm.add_custom_button(__("Go to {0}", [__(frm.doc.name)]), () => {
					window.open(`/app/${frappe.router.slug(frm.doc.name)}`);
				});
			} else {
				frm.add_custom_button(__("Go to {0} List", [__(frm.doc.name)]), () => {
					window.open(`/app/${frappe.router.slug(frm.doc.name)}`);
				});
			}
		}
	},
});
