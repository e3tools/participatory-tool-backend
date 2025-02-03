// Copyright (c) 2025, Steve Nyaga and contributors
// For license information, please see license.txt

frappe.ui.form.on("Engagement Profile User Assignment", {
	refresh(frm) {
	},
    engagement_profile(frm){
      // open activities
      frappe.call({
        method:
          "participatory_backend.engage.doctype.engagement_profile_user_assignment.engagement_profile_user_assignment.get_engagement_profile",
        args: {
          engagement_profile: frm.doc.engagement_profile, 
        },
        callback: (r) => {
          if (!r.exc) {
            let html = '<b>Assigned Form Groups</b> <ol class="list-group">';
            for(var i=0; i < r.message.form_groups.length; i++) {
                const item = r.message.form_groups[i];
                html += `<li class="list-group-item">${item.engagement_form_group}</li>`;
            }
            html += '</ol>'
             frm.set_df_property("assigned_groups", "options", html);

            /*
            var activities_html = frappe.render_template("crm_activities", {
              tasks: r.message.tasks,
              events: r.message.events,
            });

            $(activities_html).appendTo(me.open_activities_wrapper);

            $(".open-tasks")
              .find(".completion-checkbox")
              .on("click", function () {
                me.update_status(this, "ToDo");
              });

            $(".open-events")
              .find(".completion-checkbox")
              .on("click", function () {
                me.update_status(this, "Event");
              });

            me.create_task();
            me.create_event();*/
          }
        },
      });
    }
});
