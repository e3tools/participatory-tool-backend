// Copyright (c) 2023, Steve Nyaga and contributors
// For license information, please see license.txt

cur_frm.add_fetch('ward', 'parent_administrative_level', 'county')
frappe.ui.form.on("PCRA Form", {
	setup(frm) {
        frm.set_query("ward", function() {
			return {
				filters: {
					'is_group': 0
				}
			};
		});
    },
    refresh(frm) {

	},
	onload_post_render(frm){ 
		// override the permissions here otherwise the map in Child Tables will be read only
		if(!('Resource Item' in frappe.perm.doctype_perm)){			
			frappe.perm.doctype_perm['Resource Item'] = [frappe.perm.doctype_perm['PCRA Form'][0]];
		}
		if(!('Vulnerable Group Item' in frappe.perm.doctype_perm)){			
			frappe.perm.doctype_perm['Vulnerable Group Item'] = [frappe.perm.doctype_perm['PCRA Form'][0]];
		}
	}
});


frappe.ui.form.on("Resource Item", {
	onload(frm){
		// debugger;
	},
	// refresh: function (frm) {
    //            // Debug button, test field reload
	// 	frm.add_custom_button('Reload map', () => {
	// 		actualizaUbicacion(frm)
	// 	})
    //            // Debug button, test full form reload
	// 	frm.add_custom_button('Reload form', () => {
	// 		frm.refresh();
	// 	})
	// },
	resources_add: function(frm, cdt, cdn) { 
		// frappe.perm.doctype_perm['Resource Item'][0] = frappe.perm.doctype_perm['PCRA Form'][0];
		// debugger;
		// initialize_map(frm)
		// let d = new frappe.ui.Dialog({
		// 	title: 'Enter details',
		// 	fields: [
		// 		{
		// 			label: 'Check In',
		// 			fieldname: 'checkin_geolocation',
		// 			fieldtype: 'Geolocation',
		// 			default: '{"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {}, "geometry": {"type": "Point", "coordinates": [100001, 99999]}}]}'
		// 		}
		// 	],
		// 	primary_action_label: 'Submit',
		// 	primary_action(values) {
		// 		console.log(values);
		// 		d.hide();
		// 	}
		// });
		// d.show();
		// setTimeout(()=>{
		// 	d.refresh();
		// },1000);
	},
	onload_post_render(frm) {
		// debugger;
	   initialize_map(frm)
	},
	resource_type (frm, cdt, cdn){
		// frappe.perm.doctype_perm['Resource Item'][0] = frappe.perm.doctype_perm['PCRA Form'][0];			
	},
	refresh(frm) {
		debugger;
	//    initialize_map(frm)
	},
});

async function initialize_map(frm){
	setTimeout(()=> {
		debugger;
		console.log("Refresh ubicacion");
		frm.refresh_field("map");

		// let fld = frm.fi get_leaflet_controls
	}, 1000);
}