frappe.ui.form.on("Sales Invoice", {
	custom_freight_amount(frm) {
		calculate_grand_total(frm);
	},
	custom_packaging_amount(frm) {
		calculate_grand_total(frm);
	},
});

function calculate_grand_total(frm) {
	const freight = flt(frm.doc.custom_freight_amount);
	const packaging = flt(frm.doc.custom_packaging_amount);
	const net_total = flt(frm.doc.total);
	frm.set_value("grand_total", net_total + freight + packaging);
}

frappe.ui.form.on("Sales Invoice Item", {
	custom_bags(frm, cdt, cdn) {
		calculate_qty(frm, cdt, cdn);
		calculate_total_bags(frm);
	},
	custom_pack(frm, cdt, cdn) {
		calculate_qty(frm, cdt, cdn);
	},
	custom_factor(frm, cdt, cdn) {
		calculate_qty(frm, cdt, cdn);
	},
});

function calculate_qty(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	const bag = flt(row.custom_bags);
	const pack = flt(row.custom_pack);
	const factor = flt(row.custom_factor);
	if (bag && pack && factor) {
		frappe.model.set_value(cdt, cdn, "qty", bag * pack * factor);
	}
}

function calculate_total_bags(frm) {
	const total = (frm.doc.items || []).reduce((sum, row) => sum + flt(row.custom_bags), 0);
	frm.set_value("custom_total_bags", total);
}
