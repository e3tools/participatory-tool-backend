// Copyright (c) 2024, Steve Nyaga and contributors
// For license information, please see license.txt

const ALLOWED_TITLE_FIELD_TYPES = [
  "Data",
  "Date",
  "Datetime",
  "Link",
  "Linked Field",
  "Select",
]; 

frappe.ui.form.on("Engagement Form", {
  setup(frm) {
    frm.set_query("field_child_doctype", "form_fields", function () {
      return {
        filters: {
          istable: 1,
          //'custom': 1,
          //'module': 'Engage'
        },
      };
    });

    frm.set_query("field_doctype", "form_fields", function () {
      return {
        filters: {
          istable: 0,
          //'custom': 1,
          //'module': 'Engage'
        },
      };
    });
  },
  refresh(frm) {
    if (!frm.is_new() && !frm.doc.field_is_table) {
      // force all forms to have web-form enabled
      frappe.model.set_value(
        frm.doc.doctype,
        frm.doc.name,
        "enable_web_form",
        1
      );
      if (frm.doc.issingle) {
        frm.add_custom_button(__("Go to {0}", [__(frm.doc.name)]), () => {
          window.open(`/app/${frappe.router.slug(frm.doc.name)}`);
        });
      } else {
        // frm.add_custom_button(__("Go to {0} List", [__(frm.doc.name)]), () => {
        // 	window.open(`/app/${frappe.router.slug(frm.doc.name)}`);
        // });

        frm.add_custom_button(
          __("New", [__(frm.doc.name)]),
          () => {
            window.open(`/app/${frappe.router.slug(frm.doc.name)}/new`);
          },
          __("View")
        );

        frm.add_custom_button(
          __("List", [__(frm.doc.name)]),
          () => {
            window.open(`/app/${frappe.router.slug(frm.doc.name)}`);
          },
          __("View")
        );

        frm.add_custom_button(
          __("Dashboard"),
          () => {
            window.open(
              `/app/${frappe.router.slug(frm.doc.name)}/view/dashboard`
            );
          },
          __("View")
        );

        frm.add_custom_button(
          __("Report", [__(frm.doc.name)]),
          () => {
            window.open(`/app/${frappe.router.slug(frm.doc.name)}/view/report`);
          },
          __("View")
        );
      }
    }
    if (!frm.is_new()) {
    }
    frm.trigger("enable_web_form");
    frm.trigger("set_public_url");
    // if(!frm.is_new() && frm.doc.enable_web_form && !frm.doc.field_is_table) {
    // 	frm.add_custom_button(__("See on website", [__(frm.doc.name)]), () => {
    // 		window.open(`/${frm.doc.route}`);
    // 	}, null);
    // }
    frm.set_query(
      "linked_form_property",
      "form_fields",
      function (frm, cdt, cdn) {
        let child = locals[cdt][cdn];
        let parent = null;
        frm.form_fields?.forEach((field) => {
          if (field.field_name == child.linked_form) {
            parent = field.field_doctype;
          }
        });
        return {
          fields: ["fieldname"],
          filters: [
            ["parenttype", "=", "DocType"], // Adjust the filter criteria as needed
            ["parent", "=", parent],
          ],
        };
      }
    ); 
    frm.events.show_qrcode(frm);
  },
  onload_post_render(frm) {
    set_title_field_options(frm);
    frm.events.show_qrcode(frm);
  },
  enable_web_form(frm) {
    if (!frm.is_new() && !frm.doc.field_is_table) {
      if (frm.doc.enable_web_form) {
        frm.add_custom_button(
          __("See on website", [__(frm.doc.name)]),
          () => {
            window.open(`/${frappe.router.slug(frm.doc.route)}/new`);
          },
          __("Actions")
        );
      } else {
        frm.remove_custom_button(__("See on website"), __("Actions"));
      }

      frm.add_custom_button(
        __("Create engagement", [__(frm.doc.name)]),
        () => {
          frm.events.make_engagement(frm);
        },
        __("Actions")
      );
    }
  },
  set_public_url(frm) {
    // if(frm.doc.enable_web_form){
    // 	frappe.model.set_value(frm.doc.doctype, frm.doc.name, 'public_url', `/${frappe.router.slug(frm.doc.route)}/new`);
    // }
  },
  validate: function (frm) {},
  form_fields_add: function (frm) {
    set_title_field_options(frm);
  },
  form_fields_remove: function (frm) {
    set_title_field_options(frm);
  },
  // show_title_field_in_link(frm) {
  // 	set_title_field_options(frm);
  // }
  make_engagement(frm) {
    frappe.call({
      method:
        "participatory_backend.engage.doctype.engagement_form.engagement_form.make_engagement",
      args: { 
        form_name: frm.doc.name,
        description: frm.doc.description,
      },
      callback: (r) => {
        if (r.message) {
          var doc = frappe.model.sync(r.message);
          frappe.set_route("Form", doc[0].doctype, doc[0].name);
        }
      },
    });
  },
  show_qrcode(frm) {
    let template = '<img src="" />';
    if (!frm.doc.__islocal && !frm.doc.field_is_table && frm.doc.qr_code) {
      template = `<img src="${frm.doc.qr_code}" width="240px"/>`;
    }
    frm.set_df_property('qr_code_preview', 'options', frappe.render_template(template));
    frm.refresh_field('qr_code_preview');
  }
});

frappe.ui.form.on("Engagement Form Field", {
  form_render: function (frm, cdt, cdn) {
    frm.trigger("field_type", cdt, cdn);
  },
  field_type: function (frm, cdt, cdn) {
    var child = locals[cdt][cdn];
    if (child.field_type == "Linked Field") {
      let link_fields = [];
      let val = child[child.field_name];
      frm.doc.form_fields?.forEach((field) => {
        if (field.field_type == "Link") {
          link_fields.push({
            label: `${field.field_label} - ${field.field_doctype}`,
            value: field.field_name,
            selected: field.field_name === val,
          });
        }
      });
      frm.set_df_property(
        "form_fields",
        "options",
        link_fields,
        frm.doc.name,
        "linked_form",
        cdn
      );
      frm.trigger("linked_form", cdt, cdn);
    }
  },
  linked_form: function (frm, cdt, cdn) {
    var child = locals[cdt][cdn];
    frappe.model.set_value(cdt, cdn, "linked_form", child.linked_form);
    if (child.linked_form) {
      const doctype = get_linked_form_doctype(frm, child.linked_form);
      frappe.call({
        method:
          "participatory_backend.engage.doctype.engagement_form.engagement_form.get_docfields",
        args: {
          doctype: doctype,
        },
        freeze: true,
        callback: function (r) {
          let fields = [];
          if (r.message) {
            r.message.forEach((el) => {
              fields.push({ label: el.label, value: el.fieldname });
            });
            frm.set_df_property(
              "form_fields",
              "options",
              fields,
              frm.doc.name,
              "linked_form_property",
              cdn
            );

            frm.trigger("set_linked_field_value", cdt, cdn);
          }
        },
      });
    }
  },
  linked_form_property: function (frm, cdt, cdn) {
    var child = locals[cdt][cdn];
    frappe.model.set_value(
      cdt,
      cdn,
      "linked_form_property",
      child.linked_form_property
    );
    frm.trigger("set_linked_field_value", cdt, cdn);
  },
  set_linked_field_value: function (frm, cdt, cdn) {
    let child = locals[cdt][cdn];
    let parent = child.linked_form;
    let property = child.linked_form_property;
    let val = "";
    if (parent && property) {
      val = `${parent}.${property}`;
    }
    frappe.model.set_value(cdt, cdn, "field_linked_field", val);
  },
  set_filters: function (frm, cdt, cdn) {
    debugger;
    let child = locals[cdt][cdn];
    if (!child.field_doctype) {
      frappe.throw("You must select the Form first");
    }
    edit_filters(frm, child);
  },
});

function edit_filters(frm, child) {
  let field_doctype = child.field_doctype;
  //   const { frm } = store;
  make_filters_dialog(frm, child);
  make_filters_area(frm, field_doctype);
  frappe.model.with_doctype(field_doctype, () => {
    frm.dialog.show();
    add_existing_filter(frm, child);
  });
}

const set_title_field_options = function (frm) {
  const val = frm.doc.title_field;
  let label_val = "";
  const fields = [];
  frm.doc.form_fields?.forEach((field) => {
    if(ALLOWED_TITLE_FIELD_TYPES.includes(field.field_type)) {
      fields.push({
        label: field.field_label,
        value: field.field_label,
        selected: field.field_name === val,
      });
    }
    if (field.field_name === val) {
      label_val = field.field_label;
    }
  });
  frm.set_df_property("title_field", "options", fields, frm.doc.name);
  frappe.model.set_value(
    frm.doc.doctype,
    frm.doc.name,
    "title_field",
    label_val
  );
};

const get_linked_form_doctype = (frm, field_name) => {
  let doctype = null;
  frm.doc.form_fields?.forEach((field) => {
    if (field.field_type == "Link" && field.field_name == field_name) {
      doctype = field.field_doctype;
    }
  });
  return doctype;
};

function make_filters_dialog(frm, child) {
  debugger;
  frm.dialog = new frappe.ui.Dialog({
    title: __("Set Filters"),
    fields: [
      {
        fieldtype: "HTML",
        fieldname: "filter_area",
      },
    ],
    primary_action: () => {
      //let fieldname = props.field.df.fieldname;
      //   let field_option = props.field.df.options;
      let filters = frm.filter_group.get_filters().map((filter) => {
        // last element is a boolean which hides the filter hence not required to store in meta
        filter.pop();

        // filter_group component requires options and frm.set_query requires fieldname so storing both
        // filter[0] = field_option;
        return filter;
      });

      let link_filters = JSON.stringify(filters);
      //   store.form.selected_field = props.field.df;
      frappe.model.set_value(
        child.doctype,
        child.name,
        "field_filters",
        link_filters
      );
      frm.dialog.hide();
    },
    primary_action_label: __("Apply"),
  });
}

function make_filters_area(frm, doctype) { 
  frm.filter_group = new frappe.ui.FilterGroup({
    parent: frm.dialog.get_field("filter_area").$wrapper,
    doctype: doctype,
    on_change: () => {},
  });
}

function add_existing_filter(frm, child) {
  if (child.field_filters) {
    let filters = JSON.parse(child.field_filters);
    if (filters) {
      frm.filter_group.add_filters_to_filter_group(filters);
    }
  }
}

// frappe.ui.form.on("Engagement Form Field", "linked_form", function(frm, cdt, cdn) {
// 	var child = locals[cdt][cdn];
// 	if(child.field_type == 'Linked Field') {
// 		let link_fields = [];
// 		frm.doc.form_fields?.forEach(field => {
// 			if(field.field_type == 'Link'){
// 				link_fields.push({'label': `${field.field_label} - ${field.field_doctype}`, 'value': field.field_name});
// 			}
// 		});
// 		//frm.fields_dict['linked_form'].options=link_fields;
// 		//frm.set_df_property("linked_form", "options", link_fields, frm.doc.name, 'form_fields', cdn);
// 		frm.set_df_property("form_fields", "options", link_fields, frm.doc.name, 'linked_form', cdn);

// 		//set_df_property(fieldname, property, value, docname, table_field, table_row_name = null)

// 		console.log("Link fields: ", link_fields)
// 	}
// 	console.log(child.field_type);
// });
