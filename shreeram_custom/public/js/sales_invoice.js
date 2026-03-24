frappe.ui.form.on("Sales Invoice", {
	refresh(frm) {
		// render_additional_amount_button(frm);
	},
	// custom_freight_amount(frm) {
	// 	calculate_grand_total(frm);
	// 	render_additional_amount_button(frm);
	// },
	// custom_packaging_amount(frm) {
	// 	calculate_grand_total(frm);
	// 	render_additional_amount_button(frm);
	// },
	// total(frm) {
	// 	calculate_grand_total(frm);
	// },
});

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

function calculate_qty(_frm, cdt, cdn) {
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

function calculate_grand_total(frm) {
	const freight = flt(frm.doc.custom_freight_amount);
	const packaging = flt(frm.doc.custom_packaging_amount);
	const base_total = flt(frm.doc.total);
	frm.set_value("custom_grand_total", base_total + freight + packaging);
}

function render_additional_amount_button(frm) {
	const $wrapper = frm.fields_dict.custom_additional_amount_tax &&
		frm.fields_dict.custom_additional_amount_tax.$wrapper;
	if (!$wrapper) return;

	$wrapper.find(".btn-additional-amount").remove();

	$(`<button class="btn btn-xs btn-default btn-additional-amount" style="margin-top:6px">
		Additional Amount
	</button>`)
		.appendTo($wrapper)
		.on("click", function () {
			const freight = flt(frm.doc.custom_freight_amount);
			const packaging = flt(frm.doc.custom_packaging_amount);
			const tax_rate = flt(frm.doc.custom_additional_amount_tax);
			const tax_multiplier = 1 + tax_rate / 100;

			function upsert_row(account_head, amount) {
				const existing = (frm.doc.taxes || []).find(
					(r) => r.account_head === account_head
				);
				if (existing) {
					frappe.model.set_value(existing.doctype, existing.name, "tax_amount", amount);
				} else {
					const row = frappe.model.add_child(frm.doc, "Sales Taxes and Charges", "taxes");
					row.charge_type = "Actual";
					row.account_head = account_head;
					row.tax_amount = amount;
				}
			}

			if (freight) upsert_row("Freight and Forwarding Charges - SREPL", freight * tax_multiplier);
			if (packaging) upsert_row("Packaging Charges - SREPL", packaging * tax_multiplier);

			frm.refresh_field("taxes");
		});
}
