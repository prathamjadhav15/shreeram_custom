# Copyright (c) 2026, Prathamesh Jadhav and contributors
# For license information, please see license.txt

import frappe
from frappe import _


MONTHS = {
	"January": 1, "February": 2, "March": 3, "April": 4,
	"May": 5, "June": 6, "July": 7, "August": 8,
	"September": 9, "October": 10, "November": 11, "December": 12,
}


def execute(filters=None):
	filters = filters or {}
	products = get_all_products()
	columns = get_columns(products)
	data = get_data(filters, products)
	return columns, data


def get_all_products():
	result = frappe.db.sql(
		"""
		SELECT DISTINCT attribute_value
		FROM `tabItem Attributes`
		WHERE attribute_type = 'Product'
		ORDER BY attribute_value
		""",
		as_dict=True,
	)
	return [r.attribute_value for r in result]


def get_columns(products):
	columns = [
		{
			"fieldname": "month",
			"label": _("Month"),
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"fieldname": "customer_name",
			"label": _("Customer Name"),
			"fieldtype": "Data",
			"width": 200,
		},
	]
	for product in products:
		fieldname = frappe.scrub(product)
		columns.append({
			"fieldname": fieldname,
			"label": _(product),
			"fieldtype": "Float",
			"width": 130,
		})
	columns.append({
		"fieldname": "total_qty",
		"label": _("Total"),
		"fieldtype": "Float",
		"width": 120,
	})
	return columns


def get_data(filters, products):
	conditions = "si.docstatus IN (0, 1)"

	if filters.get("from_date"):
		conditions += " AND si.posting_date >= %(from_date)s"
	if filters.get("to_date"):
		conditions += " AND si.posting_date <= %(to_date)s"
	if filters.get("customer"):
		conditions += " AND si.customer = %(customer)s"
	if filters.get("month"):
		month_num = MONTHS.get(filters.get("month"))
		if month_num:
			conditions += f" AND MONTH(si.posting_date) = {month_num}"

	rows = frappe.db.sql(
		f"""
		SELECT
			DATE_FORMAT(si.posting_date, '%%M %%Y') AS month,
			MONTH(si.posting_date)                AS month_num,
			YEAR(si.posting_date)                 AS year_num,
			si.customer_name,
			TRIM(SUBSTRING_INDEX(i.custom_product, '-', -1)) AS product,
			SUM(sii.qty) AS qty
		FROM `tabSales Invoice` si
		INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
		LEFT JOIN `tabItem` i ON i.name = sii.item_code
		WHERE {conditions}
		GROUP BY month, si.customer_name, i.custom_product
		ORDER BY year_num, month_num, si.customer_name, i.custom_product
		""",
		filters,
		as_dict=True,
	)
	return build_pivot(rows, products)


def build_pivot(rows, products):
	order = []
	seen = set()
	data_map = {}

	for row in rows:
		month = row.get("month") or ""
		customer = row.get("customer_name") or ""
		product = row.get("product") or ""
		qty = row.get("qty") or 0.0

		key = (month, customer)
		if key not in seen:
			seen.add(key)
			order.append(key)
		if key not in data_map:
			data_map[key] = {}
		data_map[key][product] = data_map[key].get(product, 0.0) + qty

	result = []
	grand_total = {frappe.scrub(p): 0.0 for p in products}
	grand_total_qty = 0.0

	for (month, customer) in order:
		product_qtys = data_map[(month, customer)]
		row_dict = {"month": month, "customer_name": customer}
		total_qty = 0.0
		for product in products:
			fieldname = frappe.scrub(product)
			qty = product_qtys.get(product, 0.0)
			row_dict[fieldname] = qty if qty else ""
			grand_total[fieldname] += qty
			total_qty += qty
		row_dict["total_qty"] = total_qty
		grand_total_qty += total_qty
		result.append(row_dict)

	grand_row = {
		"month": "Grand Total",
		"customer_name": "",
		"total_qty": grand_total_qty,
		"bold": 1,
	}
	for product in products:
		fieldname = frappe.scrub(product)
		grand_row[fieldname] = grand_total[fieldname]
	result.append(grand_row)

	return result

def _make_month_subtotal(month, products, month_totals):
	subtotal_row = {
		"month": f"{month} - SubTotal",
		"customer_name": "",
		"bold": 1,
		"total_qty": month_totals.get(month, {}).get("__total__", 0.0),
	}
	for product in products:
		fieldname = frappe.scrub(product)
		subtotal_row[fieldname] = month_totals.get(month, {}).get(product, 0.0)
	return subtotal_row