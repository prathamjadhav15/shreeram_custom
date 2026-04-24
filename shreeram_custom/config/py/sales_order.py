from erpnext.selling.doctype.sales_order.sales_order import SalesOrder
from frappe.utils import getdate
import frappe
from frappe import _


class CustomSalesOrder(SalesOrder):

    def validate_delivery_date(self):
        if self.order_type == "Sales" and not self.skip_delivery_note:
            delivery_date_list = [d.delivery_date for d in self.get("items") if d.delivery_date]
            max_delivery_date = max(delivery_date_list) if delivery_date_list else None

            if (max_delivery_date and not self.delivery_date) or (
                max_delivery_date and getdate(self.delivery_date) != getdate(max_delivery_date)
            ):
                self.delivery_date = max_delivery_date

            if self.delivery_date:
                for d in self.get("items"):
                    if not d.delivery_date:
                        d.delivery_date = self.delivery_date
                    if getdate(self.transaction_date) > getdate(d.delivery_date):
                        frappe.msgprint(
                            _("Expected Delivery Date should be after Sales Order Date"),
                            indicator="orange",
                            title=_("Invalid Delivery Date"),
                            raise_exception=True,
                        )

        self.validate_sales_mntc_quotation()