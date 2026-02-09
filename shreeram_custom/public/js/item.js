const ATTRIBUTE_FIELDS = [
	"custom_product",
	"custom_density",
	"custom_thickness",
	"custom_layer",
	"custom_size",
	"custom_dia_id",
	"custom_facing",
	"custom_wn",
	"custom_wn_side",
];

const FIELD_ATTRIBUTE_MAP = {
	custom_product: "Product",
	custom_thickness: "Thickness",
	custom_size: "Size",
	custom_wn: "WN",
	custom_facing: "Facing",
	custom_density: "Density",
	custom_layer: "Layer",
	custom_dia_id: "Dia/ ID",
	custom_wn_side: "WN Side",
};

function set_item_code(frm) {
	const promises = ATTRIBUTE_FIELDS.map((field) => {
		const value = frm.doc[field];
		if (value) {
			return frappe.db.get_value("Item Attributes", value, "attribute_value")
				.then((r) => r.message?.attribute_value || "");
		}
		return Promise.resolve("");
	});

	Promise.all(promises).then((values) => {
		const item_code = values.filter(Boolean).join(" ");
		if (item_code) {
			frm.set_value("item_code", item_code);
			frm.set_value("item_name", item_code);
		}
	});
}

const field_events = {
	setup(frm) {
		for (const [fieldname, attribute_type] of Object.entries(FIELD_ATTRIBUTE_MAP)) {
			frm.set_query(fieldname, () => ({
				filters: { attribute_type: attribute_type },
			}));
		}
	},
};

ATTRIBUTE_FIELDS.forEach((field) => {
	field_events[field] = function (frm) {
		set_item_code(frm);
	};
});

frappe.ui.form.on("Item", field_events);
