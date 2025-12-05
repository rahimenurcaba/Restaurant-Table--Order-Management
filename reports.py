import csv
import operator
def daily_sales_report(orders: list) -> dict:
    total_revenue=0.0
    completed_orders=0
    for order in orders:
        if order.get("status")=="closed" and "bill" in order:
            bill =order["bill"]
            final_total=bill.get("final_total",0.0)
            total_revenue += final_total
            completed_orders +=1
    return{
        "total_revenue":round(total_revenue,2),
        "total_orders_counts": completed_orders
    }
          
def top_selling_items(orders: list, menu: dict, limit: int = 5) -> list:...
def server_performance(orders: list) -> dict: ...
def export_report(report: dict, filename: str) -> str: ...
