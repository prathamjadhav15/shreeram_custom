import frappe

ATTRIBUTE_FIELDS = [
	"custom_product",
	"custom_density",
	"custom_thickness",
	"custom_layer",
	"custom_size",
	"custom_dia_id",
	"custom_facing",
	"custom_wn_side",
	"custom_wn",
]


def before_save(doc, method):
	parts = []
	for field in ATTRIBUTE_FIELDS:
		value = doc.get(field)
		if value:
			attribute_value = frappe.db.get_value("Item Attributes", value, "attribute_value")
			if attribute_value:
				parts.append(attribute_value)

	if parts:
		item_code = " ".join(parts)
		doc.item_code = item_code
		doc.item_name = item_code
