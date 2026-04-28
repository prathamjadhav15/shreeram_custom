// Copyright (c) 2026, Prathamesh Jadhav and contributors
// For license information, please see license.txt

frappe.query_reports["Monthly Sales Analysis Report"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_start(),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_end(),
			reqd: 1,
		},
		{
			fieldname: "month",
			label: __("Month"),
			fieldtype: "Select",
			options: [
				"", "January", "February", "March", "April",
				"May", "June", "July", "August", "September",
				"October", "November", "December"
			].join("\n"),
		},
		{
			fieldname: "customer",
			label: __("Customer"),
			fieldtype: "Link",
			options: "Customer",
		},
	],
};