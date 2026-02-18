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


def get_item_code(doc):
	parts = []
	for field in ATTRIBUTE_FIELDS:
		value = doc.get(field)
		if value:
			attribute_value = frappe.db.get_value("Item Attributes", value, "attribute_value")
			if attribute_value:
				parts.append(attribute_value)
	return " ".join(parts) if parts else None


def before_save(doc, _method):
	item_code = get_item_code(doc)
	if item_code:
		doc.item_code = item_code
		doc.item_name = item_code
		if doc.is_new():
			doc.name = item_code


def after_save(doc, _method):
	item_code = get_item_code(doc)
	if item_code and doc.name != item_code:
		frappe.rename_doc("Item", doc.name, item_code, force=True)
