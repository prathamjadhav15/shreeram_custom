frappe.ui.form.on('Delivery Note', {
    shipping_address_name: function(frm) {
        if (frm.doc.shipping_address_name && frm.doc.custom_temporary_address) {
            frappe.msgprint({
                title: 'Validation Error',
                message: 'Cannot fill Shipping Address Custom Temporary Address is already filled. Please clear Custom Temporary Address first.',
                indicator: 'red'
            });
            frm.set_value('shipping_address_name', '');
        }
    },

    custom_temporary_address: function(frm) {
        if (frm.doc.custom_temporary_address && frm.doc.shipping_address_name) {
            frappe.msgprint({
                title: 'Validation Error',
                message: 'Cannot fill Temporary Address when Shipping Address is already filled. Please clear Shipping Address first.',
                indicator: 'red'
            });
            frm.set_value('custom_temporary_address', '');
        }
    }
});