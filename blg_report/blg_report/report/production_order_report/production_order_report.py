import frappe
from frappe.utils import flt

def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 160},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 250},
        {"label": "Total Ordered Qty", "fieldname": "ordered_qty", "fieldtype": "Float", "width": 150},
        {"label": "Total Delivered Qty", "fieldname": "delivered_qty", "fieldtype": "Float", "width": 150},
        {"label": "Total Pending Qty", "fieldname": "pending_qty", "fieldtype": "Float", "width": 150},
    ]


def get_data(filters):
    # base condition: only submitted Sales Orders
    conditions = ["so.docstatus = 1"]
    values = {}

    # optional item filter
    if filters.get("item_code"):
        conditions.append("soi.item_code = %(item_code)s")
        values["item_code"] = filters.get("item_code")

    condition_str = " AND ".join(conditions) if conditions else "1=1"

    # aggregate by item_code
    query = f"""
        SELECT
            soi.item_code AS item_code,
            MAX(soi.item_name) AS item_name,
            SUM(soi.qty) AS total_ordered_qty,
            SUM(COALESCE(soi.delivered_qty, 0)) AS total_delivered_qty,
            (SUM(soi.qty) - SUM(COALESCE(soi.delivered_qty, 0))) AS total_pending_qty
        FROM `tabSales Order` so
        JOIN `tabSales Order Item` soi ON soi.parent = so.name
        WHERE {condition_str}
        GROUP BY soi.item_code
        HAVING (SUM(soi.qty) - SUM(COALESCE(soi.delivered_qty, 0))) > 0
        ORDER BY total_pending_qty DESC
    """

    rows = frappe.db.sql(query, values, as_dict=True)

    # normalize numeric types
    result = []
    for r in rows:
        ordered = flt(r.get("total_ordered_qty", 0), 6)
        delivered = flt(r.get("total_delivered_qty", 0), 6)
        pending = flt(r.get("total_pending_qty", 0), 6)
        if pending > 0:
            result.append({
                "item_code": r.get("item_code"),
                "item_name": r.get("item_name"),
                "ordered_qty": ordered,
                "delivered_qty": delivered,
                "pending_qty": pending
            })

    return result
