import tables
import menu
import orders
import storage
import reports
import json
import os
import shutil
import datetime

DATA_DIR = "data"
LOGS_DIR = "logs"
BACKUP_DIR = "backups"

def main():
    table_list, menu_data, order_list = storage.load_state(DATA_DIR)
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR) 
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    while True:
        print("\n--- RESTAURANT MANAGER ---")
        print("1. View Tables")
        print("2. Seat Table")
        print("3. Release Table")
        print("4. Place Order")
        print("5. Calculate Bill")
        print("6. Manager Tools (Reports & Backup)")
        print("7. Save & Exit")
        print("8. Menu Management")
        
        choice = input("Select option: ")

        if choice == "1":
            print("\n---Current Tables---")
            for t in table_list:
                status_display = t['status'].ljust(15)
                server_display = t.get('server_name','None').ljust(10)
                print(f"Table {str(t['table_number']).ljust(3)} | Status:{status_display} | Server:{server_display}")

        elif choice == "2":
            t_num = int(input("Table Number: "))
            p_size = int(input("Party Size: "))
            result = tables.assign_table(table_list, t_num, p_size)
            if result:
                server_name = input("Assign Server: ")
                tables.update_server(table_list, t_num, server_name)
                server_name= 'Unassingned'
                for t in table_list:
                    if t['table_number'] == t_num:
                        server_name=t['server_name']
                        break
                new_order = orders.open_order(t_num, server_name)
                order_list.append(new_order)
                print(f" Table {t_num} seated and order opened.")
            else:
                print("Cannot seat table.")

        elif choice == "3":
            t_num = int(input("Table number to release: "))
            confirm=input("Confirm releasing table {t_num}? This should only be used if the table is paid. (y/n):").lower()
            if confirm == 'y':
                if tables.release_table(table_list, t_num):
                    print("Table {t_num} released.")
            else:
                print("Table not found or already released.")

        elif choice == "4":
            t_num = int(input("Table Number for Order: "))
            current_order = None
            for i in order_list:
                if i['table_number'] == t_num and i['status'] == 'open':
                    current_order = i
                    break
    
            if not current_order:
                print(f"Error: No open error found for table {t_num}. Seat the table first (Option 2).")
                continue

            item_name = input("Enter Menu Item Name: ")
            qty = int(input("Quantity: "))
            price = float(input("Price (Temporary): ")) 
            temp_item = {"id": item_name[:3].upper(), "name": item_name, "price": price}
            orders.add_item_to_order(current_order, temp_item, qty)
            print(f"Item added to table {t_num}.")
            result= storage.log_kitchen_ticket(current_order, LOGS_DIR)
            print(f"Kitchen order ticket generated. ({result})")

        elif choice == "5":
            t_num = int(input("Table Number to Bill: "))
            current_order= None
            for i in order_list:
                if i['table_number'] == t_num and i['status'] == 'open':
                    current_order=i
                    break
                if not current_order:
                    print("No open order for this table.")
                    continue
                    
                bill = orders.calculate_bill(i, 0.10, 0.15)
                print(f"Subtotal: ${bill['subtotal']:.2f}")
                print(f"Tax: ${bill['tax']:.2f}")
                print(f"Tip: ${bill['tip']:.2f}")
                print(f"TOTAL: ${bill['total']:.2f}")
                
                confirm_close=input("\nConfirm payment reveived and close order? (y/n):").lower()
                if confirm_close == 'y':
                    current_order['status'] = 'closed'
                    current_order['bill'] = bill
                    tables.release_table(table_list, t_num)
                    print(f"Order for table {t_num} closed and table released.")
                
                else:
                    print("Order remains open , avaiting payment.")
                    
        elif choice == "6":
            manager_tools(order_list,menu_data)
            
        elif choice == "7":
            storage.save_state(DATA_DIR, table_list, menu_data, order_list)
            print("Data saved. Goodbye.")
            break
            
        elif choice == "8":
            print("\n--- Menu Management ---")
            print("1. Add item")
            print("2. Update item")
            m_choice= input("Select: ")
            if m_choice=="1":
                name=input("İrem Name:")
                price=float(input("Price:"))
                cat=input("Category")
                new_item={
                    "category":cat,
                    "name":name,
                    "price":price,
                    "available": "true"}
                menu.add_menu_item(menu_data,new_item)
                print("Item added.")
                
        else:
            print("Invalid option.")
            
def manager_tools(order_list,menu_data):
    closed_orders=[]
    for i in order_list:
        if i.get('status') == "closed":
            closed_orders.append(i)
    print("\n--- Manager Tools ---")
    print("1. Daily Sales Report")
    print("2. Top Selling Items")
    print("3. Server Performance")
    print("4. Backup All Data")
    
    mgr_choice = input("Select report option:")
    
    if mgr_choice == "1":
        report_data = reports.daily_sales_report(closed_orders)
        print("\n---Daily Sales Summary ---")
        for key, value in report_data.items():
            print(f"{key.replace('_','').title()}:{value}")
    
    if mgr_choice=="2":
        limit = int(input("Enter number of top items:"))
        report_data=reports.top_selling_items(closed_orders,menu_data,limit)
        print(f"\n--- Top {len(report_data)} Selling Items---")
        for item in report_data:
            print(f"{item['name'].ljust(20)}| Sold: {item['quantity_sold']}")
    
    if mgr_choice == "3":
        report_data = reports.server_performance(closed_orders)
        print("\n--- Server Performance ---")
        for server_name, data in report_data.items():
            print(f"Server{server_name.ljust(10)} | Served:{data['tables_served']} | Total Sales:${data['total_sales']:.2f}")
        
    if mgr_choice == "4":
        result=storage.backup.day(DATA_DIR, BACKUP_DIR)
        print(result)
        
    else:
        print("Invalid manager option.")
        
if __name__ == "__main__":
    main( )