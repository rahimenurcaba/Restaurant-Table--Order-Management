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
            print("\n--- Current Tables ---")
            for t in table_list:
                status_display = t['status'].ljust(10)
                server_display = t.get('server_name', 'None')
                if server_display is None: server_display = "None"
                
                print(f"Table {str(t['table_number']).ljust(3)} | Status: {status_display} | Server: {server_display}")

        elif choice == "2":
            try:
                t_num = int(input("Table Number: "))
                p_size = int(input("Party Size: "))
                
                assigned_table = tables.assign_table(table_list, t_num, p_size)
                
                if assigned_table:
                    new_order = orders.open_order(t_num)
                    new_order['server_name'] = assigned_table.get('server_name', 'Unknown')
                    order_list.append(new_order)
                    print(f"Table {t_num} seated. Server: {assigned_table['server_name']}")
                else:
                    print("Table cannot be assigned (occupied or too small).")
            except ValueError:
                print("Invalid input. Please enter numbers.")

        elif choice == "3":
            try:
                t_num = int(input("Table Number to Release: "))
                success = tables.release_table(table_list, t_num)
                if success:
                    print(f"Table {t_num} is now free.")
                else:
                    print(f"Table {t_num} could not be found.")
            except ValueError:
                print("Please enter a valid number.")

        elif choice == "4":
            try:
                t_num = int(input("Table Number: "))
                current_order = next((o for o in order_list if o['table_number'] == t_num and o['status'] == 'open'), None)
                
                if not current_order:
                    print("No open order found for this table. Seat the table first.")
                else:
                    print("\n--- Categories ---")
                    for cat in menu_data.keys():
                        print(f"- {cat.title()}")
                    
                    while True:
                        item_name_or_id = input("\nEnter Item ID or Name (or 'done' to finish): ")
                        if item_name_or_id.lower() == 'done':
                            break
                        
                        found_item = None
                        for cat_items in menu_data.values():
                            for item in cat_items:
                                if item['id'] == item_name_or_id or item['name'].lower() == item_name_or_id.lower():
                                    found_item = item
                                    break
                            if found_item: break
                        
                        if found_item:
                            try:
                                qty = int(input(f"Quantity for {found_item['name']}: "))
                                orders.add_item_to_order(current_order, found_item, qty)
                                print(f"Added {qty} x {found_item['name']}")
                            
                            except ValueError:
                                print("Invalid quantity.")
                        else:
                            print("Item not found.")
                      storage.log_kitchen_ticket(current_order, "logs") 
                      print("Kitchen ticket sent.")                         
            except ValueError:
                print("Invalid Table Number.")

        elif choice == "5":
            try:
                t_num = int(input("Table Number to Calculate: "))
                order_to_close = next((o for o in order_list if o['table_number'] == t_num and o['status'] == 'open'), None)
                
                if order_to_close:
                    print("\n--- Bill Calculation ---")
                    print(f"Total Items: {len(order_to_close['items'])}")
                        bill = orders.calculate_bill(order_to_close, tax_rate=0.10, tip_rate=0.10)
                        order_to_close['bill'] = bill
                        print(f"Total Amount: ${bill.get('total', 0):.2f}")
                        confirm = input("Process Payment & Close Order? (y/n): ")
                    if confirm.lower() == 'y':
                        order_to_close['status'] = 'closed'
                        storage.save_receipt(order_to_close)
                        print("Order closed and paid. Receipt saved.")
                        
                        release_choice = input("Release table now? (y/n): ")
                        if release_choice.lower() == 'y':
                            tables.release_table(table_list, t_num)
                            print(f"Table {t_num} is now free.")
                else:
                    print("No open order found for this table.")
            except ValueError:
                print("Invalid input.")

        elif choice == "6":
            closed_orders = [o for o in order_list if o.get('status') == "closed"]
            
            print("\n--- Manager Tools ---")
            print("1. Daily Sales Report")
            print("2. Top Selling Items")
            print("3. Server Performance")
            print("4. Backup All Data")
            
            mgr_choice = input("Select report option: ")
            
            if mgr_choice == "1":
                report_data = reports.daily_sales_report(closed_orders)
                print("\n--- Daily Sales Summary ---")
                for key, value in report_data.items():
                    print(f"{key.replace('_',' ').title()}: {value}")
            
            elif mgr_choice == "2":
                try:
                    limit = int(input("Enter number of top items: "))
                    report_data = reports.top_selling_items(closed_orders, menu_data, limit)
                    print(f"\n--- Top {len(report_data)} Selling Items ---")
                    for item in report_data:
                        print(f"{item['name'].ljust(20)} | Sold: {item['quantity_sold']}")
                except ValueError:
                    print("Invalid number.")
            
            elif mgr_choice == "3":
                report_data = reports.server_performance(closed_orders)
                print("\n--- Server Performance ---")
                if not report_data:
                    print("No performance data available yet.")
                for server_name, data in report_data.items():
                    print(f"Server: {server_name.ljust(10)} | Tables: {data['tables_served']} | Sales: ${data['total_sales']:.2f}")
            
            elif mgr_choice == "4":
                backup_path = storage.backup_day(DATA_DIR, BACKUP_DIR)
                print(f"Backup created at: {backup_path}")

        elif choice == "7":
            storage.save_state(DATA_DIR, table_list, menu_data, order_list)
            print("Data saved. Exiting...")
            break

        elif choice == "8":
            print("\n--- Menu Management ---")
            for category, items in menu_data.items():
                print(f"--- {category.upper()} ---")
                for item in items:
                    print(f"ID: {item['id']} | {item['name']} | ${item['price']}")
            
            print("\nOptions: (A)dd Item | (R)emove Item | (B)ack")
            menu_choice = input("Select: ").lower()
            
            if menu_choice == 'a':
                cat = input("Category: ").lower()
                name = input("Name: ")
                item_id = input("Unique ID: ")
                try:
                    price = float(input("Price: "))
                    
                    new_item = {
                        "id": item_id,
                        "name": name,
                        "price": price,
                        "available": True,
                        "category": cat
                    }
                    menu.add_menu_item(menu_data, new_item)
                    print("Item added.")
                except ValueError:
                    print("Invalid price.")
                    
            elif menu_choice == 'r':
                rem_id = input("Enter Item ID to remove: ")
                if menu.remove_menu_item(menu_data, rem_id):
                    print("Item removed.")
                else:
                    print("Item ID not found.")

if __name__ == "__main__":
    main()
