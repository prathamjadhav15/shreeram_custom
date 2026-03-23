frappe.ui.form.on("Sales Invoice", {
	refresh(frm) {
		render_additional_amount_button(frm);
	},
	custom_freight_amount(frm) {
		calculate_grand_total(frm);
		render_additional_amount_button(frm);
	},
	custom_packaging_amount(frm) {
		calculate_grand_total(frm);
		render_additional_amount_button(frm);
	},
	total(frm) {
		calculate_grand_total(frm);
	},
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
	const $wrapper = frm.fields_dict.custom_freight_amount &&
		frm.fields_dict.custom_freight_amount.$wrapper;
	if (!$wrapper) return;

	$wrapper.find(".btn-additional-amount").remove();

	$(`<button class="btn btn-xs btn-default btn-additional-amount" style="margin-top:6px">
		Additional Amount
	</button>`)
		.appendTo($wrapper)
		.on("click", function () {
			const amount = flt(frm.doc.custom_freight_amount) + flt(frm.doc.custom_packaging_amount);

			// Remove existing row with same account_head to avoid duplicates
			const existing = (frm.doc.taxes || []).find(
				(r) => r.account_head === "Freight and Forwarding Charges - SR"
			);
			if (existing) {
				frappe.model.set_value(
					existing.doctype, existing.name, "tax_amount", amount
				);
			} else {
				const row = frappe.model.add_child(frm.doc, "Sales Taxes and Charges", "taxes");
				row.charge_type = "Actual";
				row.account_head = "Freight and Forwarding Charges - SR";
				row.tax_amount = amount;
			}
			frm.refresh_field("taxes");
		});
}
