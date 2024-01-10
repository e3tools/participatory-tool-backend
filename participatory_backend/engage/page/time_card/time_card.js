frappe.pages['time-card'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Time Card'),
		single_column: true
	});	

	page.set_primary_action(__('Save Time'), () => create_new(), 'octicon octicon-plus')

	page.add_button(__('Reset'), () => page.capacity_dashboard.refresh(), 'reset');
	page./*set_secondary_action*/add_button(__('Refresh'), () => page.capacity_dashboard.refresh(), 'refresh');
	// debugger;
	// page.add_dropdown_button(__('Reset'), __("View Monthly Timesheet"), () => {
	// }, 'report')

	// page.add_dropdown_button(__('Reset'), __("Submit Monthly Timesheet"), () => {

	// }, 'report')

	page.add_menu_item(__('View Monthly Timesheet'), () => open_email_dialog(), true)
	page.add_menu_item(__('Submit Monthly Timesheet'), () => open_email_dialog(), true)


	// page.add_button('New Post', () => new_post(), 'Make')
	// page.add_button('New Post2', () => new_post(), 'Make')

	// page.add_dropdown_item('label', () => new_post(), 1, 'Make', '', true, 'icon')
	//page.add_custom_button_group('label2', 'icon', 'Make')
 
	// dd_dropdown_button(parent, label, click, icon)
	// page.add_custom_button_group(__('View Monthly Timesheet'), function() {
	// 	frm.trigger('monthlyView');
	// },__('Actions'));

	// page.add_custom_button_group(__('Submit Monthly Timesheet'), function() {
	// 	frm.trigger('doSubmit');
	// },__('Actions'));

	page.period_field = page.add_field({
		label: 'Period',
		fieldtype: 'HTML',
		fieldname: 'timecard_period',
		// columns: 5,
		width: 300,
		options: ` <div class="flex page-actions">
					<div class="standard-actions flex">
						<button class="text-muted btn btn-default prev-doc icon-btn" type="button">
							<span class=""><svg class="icon  icon-sm" style="">
								<use class="" href="#icon-left"></use>
							</svg></span></button>
							<h3 id="period-label" style="padding:5px">August 2023</h3>
							<button class="text-muted btn btn-default next-doc icon-btn" type="button">
								<span class=""><svg class="icon  icon-sm" style="">
								<use class="" href="#icon-right"></use>
							</svg></span></button></div>
					</div>`
	} /*, frm.fields_dict['time_card_period'].wrapper*/); //frm.page.page_form);// 

	// Hide labels in the top-most section where employee and time range are displayed
	$('[data-fieldname="timecard_period"]').removeClass('col-md-2').addClass('col-md-5');
	$('[data-fieldname="timecard_period"]').parents('.section-body').find('.control-label').addClass('hidden')

	page.employee_field = page.add_field({
		fieldname: 'employee',
		label: __('Employee'),
		fieldtype: 'Link',
		options: 'Employee',
		default: frappe.route_options && frappe.route_options.employee,
		change: function() {
			page.time_grid.refresh()
		}
	})

	page.employee_field = page.add_field({
		fieldname: 'employee',
		label: __('Employee'),
		fieldtype: 'Link',
		options: 'Employee',
		default: frappe.route_options && frappe.route_options.employee,
		change: function() {
			page.time_grid.refresh()
		}
	})

	page.sort_selector = new frappe.ui.SortSelector({
		parent: page.wrapper.find('.page-form'),
		args: {
			sort_by: 'project',
			sort_order: 'asc',
			options: [
				{fieldname: 'project', label: __('Project')},
				{fieldname: 'total_hours', label: __('Total hours')}
			]
		},
		change: function(sort_by, sort_order) {
			page.time_grid.sort_by = sort_by
			page.time_grid.sort_order = sort_order
			page.time_grid.refresh()
		}
	})
}