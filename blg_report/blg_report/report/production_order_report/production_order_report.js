// production_order_report.js
// Place in: your_app/your_app/report/production_order_report/production_order_report.js
// Report name must exactly match "Production Order Report"

frappe.query_reports["Production Order Report"] = {
    "filters": [
        {
            "fieldname": "item_code",
            "label": __("Item Code"),
            "fieldtype": "Link",
            "options": "Item",
        },
    ]
};
