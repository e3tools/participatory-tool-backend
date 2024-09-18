// Copyright (c) 2024, Steve Nyaga and contributors
// For license information, please see license.txt

frappe.ui.form.on("Engagement Form", {
    setup(frm) {
        frm.set_query("field_child_doctype", "form_fields", function() {
			return {
				filters: {
					'istable': 1,
					'custom': 1,
					//'module': 'Engage'
				}
			};
		});

		frm.set_query("field_doctype", "form_fields", function() {
			return {
				filters: {
					'istable': 0,
					'custom': 1,
					//'module': 'Engage'
				}
			};
		});
    },
	refresh(frm) { 
        if (!frm.is_new() && !frm.doc.field_is_table) {
			if (frm.doc.issingle) {
				frm.add_custom_button(__("Go to {0}", [__(frm.doc.name)]), () => {
					window.open(`/app/${frappe.router.slug(frm.doc.name)}`);
				});
			} else {
				// frm.add_custom_button(__("Go to {0} List", [__(frm.doc.name)]), () => {
				// 	window.open(`/app/${frappe.router.slug(frm.doc.name)}`);
				// });
				
				frm.add_custom_button(__("New", [__(frm.doc.name)]), () => {			
					window.open(`/app/${frappe.router.slug(frm.doc.name)}/new`);
				}, __('View'));

				frm.add_custom_button(__("List", [__(frm.doc.name)]), () => {			
					window.open(`/app/${frappe.router.slug(frm.doc.name)}`);
				}, __('View'));
		
				frm.add_custom_button(__('Dashboard'), () => {			
					window.open(`/app/${frappe.router.slug(frm.doc.name)}/view/dashboard`);
				}, __('View'));
		
				frm.add_custom_button(__("Report", [__(frm.doc.name)]), () => { 
					window.open(`/app/${frappe.router.slug(frm.doc.name)}/view/report`);
				}, __('View')); 
			}
		}
		frm.trigger('enable_web_form');
		frm.trigger('set_public_url');
		// if(!frm.is_new() && frm.doc.enable_web_form && !frm.doc.field_is_table) {
		// 	frm.add_custom_button(__("See on website", [__(frm.doc.name)]), () => { 
		// 		window.open(`/${frm.doc.route}`);
		// 	}, null); 
		// }
	},
	enable_web_form(frm) {
		if(!frm.is_new() && !frm.doc.field_is_table) {
			if(frm.doc.enable_web_form){
				frm.add_custom_button(__("See on website", [__(frm.doc.name)]), () => { 
					window.open(`/${frappe.router.slug(frm.doc.route)}/new`);
				}, null); 
			} else {
				frm.remove_custom_button(__("See on website"), null);
			}
		}
	},
	set_public_url(frm) {
		// if(frm.doc.enable_web_form){
		// 	frappe.model.set_value(frm.doc.doctype, frm.doc.name, 'public_url', `/${frappe.router.slug(frm.doc.route)}/new`);
		// }
	}
});
