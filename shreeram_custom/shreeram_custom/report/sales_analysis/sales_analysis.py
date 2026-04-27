import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{
			"fieldname": "inv_no",
			"label": _("Inv No."),
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 130,
		},
		{
			"fieldname": "inv_date",
			"label": _("Inv Date"),
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"fieldname": "po_no",
			"label": _("So. No."),
			"fieldtype": "Data",
			"width": 130,
		},
		{
			"fieldname": "customer_name",
			"label": _("Customer Name"),
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"fieldname": "specification",
			"label": _("Specification"),
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"fieldname": "item",
			"label": _("Item"),
			"fieldtype": "Data",
			"width": 180,
		},
		{
			"fieldname": "qty",
			"label": _("Qty"),
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"fieldname": "rate",
			"label": _("Rate"),
			"fieldtype": "Currency",
			"width": 100,
		},
		{
			"fieldname": "amount",
			"label": _("Amount"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "qty_in_kg",
			"label": _("Qty In Kg"),
			"fieldtype": "Float",
			"width": 110,
		},
	]


def get_data(filters):
	conditions = "si.docstatus = 0"

	if filters.get("from_date"):
		conditions += " AND si.posting_date >= %(from_date)s"
	if filters.get("to_date"):
		conditions += " AND si.posting_date <= %(to_date)s"
	if filters.get("customer"):
		conditions += " AND si.customer = %(customer)s"

	rows = frappe.db.sql(
		f"""
		SELECT
			si.name          AS inv_no,
			si.posting_date  AS inv_date,
			si.customer_name,
			si.po_no,
			sii.item_name AS specification,
			TRIM(SUBSTRING_INDEX(i.custom_product, '-', -1)) AS item,
			sii.qty,
			sii.rate,
			sii.amount,
			sii.total_weight AS qty_in_kg
		FROM `tabSales Invoice` si
		INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
		LEFT JOIN `tabItem` i ON i.name = sii.item_code
		WHERE {conditions}
		ORDER BY i.custom_product, si.posting_date, si.name, sii.idx
		""",
		filters,
		as_dict=True,
	)

	return add_subtotals(rows)


def add_subtotals(rows):
	result = []
	current_product = None
	group_qty = group_amount = group_kg = 0.0
	grand_qty = grand_amount = grand_kg = 0.0

	for row in rows:
		product = row.get("item") or ""

		if product != current_product:
			if current_product is not None:
				result.append({
					"specification": "Item SubTotal",
					"item": current_product,
					"qty": group_qty,
					"amount": group_amount,
					"qty_in_kg": group_kg,
					"bold": 1,
				})
			current_product = product
			group_qty = group_amount = group_kg = 0.0

		result.append(row)
		group_qty += row.get("qty") or 0
		group_amount += row.get("amount") or 0
		group_kg += row.get("qty_in_kg") or 0
		grand_qty += row.get("qty") or 0
		grand_amount += row.get("amount") or 0
		grand_kg += row.get("qty_in_kg") or 0

	if current_product is not None:
		result.append({
			"specification": "Item SubTotal",
			"item": current_product,
			"qty": group_qty,
			"amount": group_amount,
			"qty_in_kg": group_kg,
			"bold": 1,
		})

	result.append({
		"specification": "Grand Total",
		"qty": grand_qty,
		"amount": grand_amount,
		"qty_in_kg": grand_kg,
		"bold": 1,
	})

	return result
