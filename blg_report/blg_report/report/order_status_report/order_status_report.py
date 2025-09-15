import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": "Sales Order No", "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 150},
        {"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Data", "width": 200},
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 200},
        {"label": "Order Quantity", "fieldname": "ordered_qty", "fieldtype": "Float", "width": 120},
        {"label": "Delivered Quantity", "fieldname": "delivered_qty", "fieldtype": "Float", "width": 120},
        {"label": "Pending Quantity", "fieldname": "pending_qty", "fieldtype": "Float", "width": 120},
    ]


def get_data(filters):
    conditions = []
    values = {}

    if filters.get("sales_order"):
        conditions.append("so.name = %(sales_order)s")
        values["sales_order"] = filters.get("sales_order")

    if filters.get("customer"):
        conditions.append("so.customer = %(customer)s")
        values["customer"] = filters.get("customer")

    if filters.get("item_code"):
        conditions.append("soi.item_code = %(item_code)s")
        values["item_code"] = filters.get("item_code")

    if filters.get("from_date"):
        conditions.append("so.transaction_date >= %(from_date)s")
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions.append("so.transaction_date <= %(to_date)s")
        values["to_date"] = filters.get("to_date")

    condition_str = " AND ".join(conditions)
    if condition_str:
        condition_str = " AND " + condition_str

    query = f"""
        SELECT 
            so.name as sales_order,
            so.customer_name,
            soi.item_code,
            soi.item_name,
            soi.qty as ordered_qty,
            soi.delivered_qty,
            (soi.qty - soi.delivered_qty) as pending_qty
        FROM `tabSales Order` so
        JOIN `tabSales Order Item` soi ON soi.parent = so.name
        WHERE so.docstatus = 1
          AND (soi.qty - soi.delivered_qty) > 0
          {condition_str}
        ORDER BY so.transaction_date DESC
    """

    return frappe.db.sql(query, values, as_dict=True)
