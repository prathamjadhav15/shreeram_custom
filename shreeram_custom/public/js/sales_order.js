frappe.ui.form.on("Sales Order", {
	custom_third_party_inspection: function (frm) {
		frm.set_value("custom_inspection_date", null);
		frm.set_value("custom_inspection_report", null);

		const is_required = frm.doc.custom_third_party_inspection ? 1 : 0;
		frm.set_df_property("custom_inspection_date", "reqd", is_required);
		frm.set_df_property("custom_inspection_report", "reqd", is_required);
	},
});
