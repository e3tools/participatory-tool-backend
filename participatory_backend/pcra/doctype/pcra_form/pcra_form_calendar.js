frappe.views.calendar['PCRA Form'] = {
    // field_map: {
    //     start: 'starts_on',
    //     end: 'ends_on',
    //     id: 'name',
    //     allDay: 'all_day',
    //     title: 'subject',
    //     status: 'event_type',
    //     color: 'color'
    // },
    // style_map: {
    //     Public: 'success',
    //     Private: 'info'
    // },
    // order_by: 'ends_on',
    // get_events_method: 'frappe.desk.doctype.event.event.get_events'
    field_map: {
		"start": "start_date",
		"end": "end_date",
		"name": "parent",
		"id": "name",
		"allDay": "allDay",
		"child_name": "name",
		"title": "title",
		"color": "color"
	},
	style_map: {
		"0": "info",
		"1": "standard",
		"2": "danger"
	},
	gantt: true,
	filters: [
		// {
		// 	"fieldtype": "Link",
		// 	"fieldname": "county",
		// 	"options": "Administrative Level",
		// 	"label": __("Administrative Level")
		// },
		// {
		// 	"fieldtype": "Link",
		// 	"fieldname": "employee",
		// 	"options": "Employee",
		// 	"label": __("Employee")
		// }
	],
	defaults: { displayEventTime: false},
	get_events_method: "participatory_backend.pcra.doctype.pcra_form.pcra_form.get_events",

}