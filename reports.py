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
          
def top_selling_items(orders: list, menu: dict, limit: int = 5) -> list:
    item_counts = {}
    for order in orders:
        if order.get("status") == "closed":
            for item in order.get("items", []):
                item_id = item.get("id")
                quantity = item.get("quantity", 1)
                if item_id in item_counts:
                    item_counts[item_id] += quantity
                else:
                    item_counts[item_id] = quantity
    
    item_list_for_sorting = []
    for item_id, count in item_counts.items():
        item_list_for_sorting.append((item_id, count))
    sorted_items = sorted(item_list_for_sorting, key=operator.itemgetter(1), reverse=True)
    top_items = []
    items_to_process = min(limit, len(sorted_items))
    
    for i in range(items_to_process):
        item_id, count = sorted_items[i]
        item_name = "Unknown item"
        for category_name in menu:
            for item_data in menu[category_name]:
                if item_data.get("id") == item_id:
                    item_name = item_data.get("name")
                    break
        top_items.append({"name": item_name, "quantity_sold": count})
    return top_items

            
def server_performance(orders: list) -> dict:
    performance={}
    
    for order in orders:
        if order.get("status")=="closed":
            server_name=order.get("server_name") 
            if not server_name:
                continue
            if server not in performance:
                performance[server_name]= {"tables_served":0, "total_sales":0.0}
            bill = order.get("bill",{})
            total = bill.get("final_total", 0.0)
            performance[server_name]["tables_served"] +=1
            performance[server_name]["total sales"] += total
            
    for server_name,data in performance.items():
            data["total_sales"]=round(data["total_sales"],2)
            
    return performance
    
def export_report(report: dict, filename: str) -> str:
    try:
       with open(filename,mode='w', newline='') as csvfile:
           writer= csv.writer(csvfile)
           writer.writerow(["Metric","Value"])
           for key,value in report.items():
               writer.writerow([key,value])
       return f"Report succesfully exported to {filename}"
        
    except IOError as e:
        return f"Error exporting report: {e}"
      
    