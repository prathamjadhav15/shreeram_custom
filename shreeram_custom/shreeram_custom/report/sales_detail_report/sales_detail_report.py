# Copyright (c) 2026, Prathamesh Jadhav and contributors
# For license information, please see license.txt


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
			"fieldname": "customer_name",
			"label": _("Customer Name"),
			"fieldtype": "Data",
			"width": 200,
		},
	
		{
			"fieldname": "item",
			"label": _("Row Labels"),
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
			"fieldname": "amount",
			"label": _("Amount"),
			"fieldtype": "Currency",
			"width": 120,
		},
	
	]


def get_data(filters):
	conditions = "si.docstatus IN (0, 1)"

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
	grand_qty = grand_amount = grand_kg = 0.0

	for row in rows:
		result.append(row)
		grand_qty += row.get("qty") or 0
		grand_amount += row.get("amount") or 0
		grand_kg += row.get("qty_in_kg") or 0

	result.append({
		"customer_name": "Grand Total",
		"item": "",
		"qty": grand_qty,
		"amount": grand_amount,
		"qty_in_kg": grand_kg,
		"bold": 1,
	})

	return result