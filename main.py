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
            try:
                t_num = int(input("Table Number: "))
                p_size = int(input("Party Size: "))
                assigned_table = tables.assign_table(table_list, t_num, p_size)
                
                if assigned_table:
                    print(f"Success: Table {t_num} is now occupied by {p_size} people.")
                    server_name=input("Assign Server: ")
                    tables.update_server(table_list,t_num,server_name)
                    storage.save_state(DATA_DIR, table_list, menu_data, order_list)
                else:
                    print("Error: Could not seat table. Check if occupied, too small, or invalid number.")
            except ValueError:
                print("Error: Please enter valid numbers.")

        elif choice == "3":
            try:
                t_num = int(input("Table number to release: "))
                order_to_close=None
                for order in order_list:
                    if order['table_number'] == t_num and order['status'] == 'open':
                        order_to_close = order
                        break
                if order_to_close and 'bill' not in order_to_close:
                    confirm=input(f"Confirm releasing table {t_num}? This should only be used if the table is paid. (y/n):").lower()
                if confirm.lower() == 'y':
                    if tables.release_table(table_list, t_num):
                        print(f"Table {t_num} released.")
                        storage.save_state(DATA_DIR, table_list, menu_data, order_list)
                elif confirm.lower() != 'y':
                    continue
                else:
                    print("Table not found or already released.")
            except ValueError:
                print("Error: Please enter valid numbers.")
                
        elif choice == "4":
            try:
                t_num = int(input("Table Number for Order: "))
            except ValueError:
                print("Invalid number.")
                continue

            current_order = None
            for i in order_list:
                if i['table_number'] == t_num and i['status'] == 'open':
                    current_order = i
                    break
    
            if not current_order:
                is_occupied = False
                server_name = "Unknown"
                
                for t in table_list:
                    if t['table_number'] == t_num:
                        if t['status'] == 'occupied':
                            is_occupied = True
                            server_name = t.get('server_name', 'Unknown')
                        break
                
                if is_occupied:
                    new_order = orders.open_order(t_num)
                    new_order['server_name'] = server_name 
                    order_list.append(new_order)
                    current_order = new_order
                    print(f"New order created for Table {t_num} (Server: {server_name}).")
                else:
                    print(f"Error: Table {t_num} is not seated. Please use Option 2 first.")
                    continue
            while True:
                print(f"\n--- Order Management (Table {t_num}) ---")
                print("1. Add Item")
                print("2. Void/Remove Item")
                print("3. Done (Return to Main Menu)")
                sub_choice = input("Select: ")

                if sub_choice == "1":
                    print("\nAvailable Categories:", ", ".join(menu_data.keys()))
                    category = input("Enter Category: ").strip().lower()

                    if category in menu_data:
                        print(f"\n--- {category.capitalize()} ---")
                        for item in menu_data[category]:
                            status = "" if item.get("available", True) else "(SOLD OUT)"
                            print(f"{item['id']}: {item['name']} (${item['price']}) {status}")
                        
                        item_id = input("Enter Item ID: ")
                        selected_item = None
                        for item in menu_data[category]:
                            if item['id'] == item_id:
                                selected_item = item
                                break
                        
                        if selected_item:
                            try:
                                if not selected_item.get("available", True):
                                    print("Sorry, this item is currently unavailable.")
                                else:
                                    qty = int(input("Quantity: "))
                                    orders.add_item_to_order(current_order, selected_item, qty)
                                    print(f"{qty}x {selected_item['name']} added.")
                                    result = storage.log_kitchen_ticket(current_order, LOGS_DIR)
                                    print(f"Ticket updated: {result}")
                                    storage.save_state(DATA_DIR, table_list, menu_data, order_list)
                            except ValueError:
                                print("Invalid quantity.")
                        else:
                            print("Error: Item ID not found.")
                    else:
                        print("Error: Invalid category.")

                elif sub_choice == "2":
                    print("\nCurrent Items:")
                    for item in current_order['items']:
                        print(f"- {item['name']} (Qty: {item['quantity']})")
                    
                    rem_name = input("Enter exact name of item to remove: ")
                    orders.remove_item_from_order(current_order, rem_name)
                    print("Item removed (if it existed).")
                    storage.save_state(DATA_DIR, table_list, menu_data, order_list)

                elif sub_choice == "3":
                    break

        elif choice == "5":
            try:
                t_num = int(input("Table Number: "))
                current_order = None
                for order in order_list:
                    if order['table_number'] == t_num and order['status'] == 'open':
                        current_order = order
                        break
                
                if current_order:
                    print(f"\n--- Bill Options for Table {t_num} ---")
                    print("1. Standard Bill (Single Receipt)")
                    print("2. Split Bill (Split Evenly)")
                    bill_choice = input("Select Bill Type: ")

                    tax_rate = 0.10
                    tip_rate = 0.15

                    if bill_choice == "1":
                        bill = orders.calculate_bill(current_order, tax_rate, tip_rate)
                        current_order['bill'] = bill
                        
                        print("\n" + "-"*30)
                        print(f"Subtotal: ${bill['subtotal']:.2f}")
                        print(f"Tax:      ${bill['tax_amount']:.2f}")
                        print(f"Tip:      ${bill['tip_amount']:.2f}")
                        print(f"TOTAL:    ${bill['total']:.2f}")
                        print("-" * 30)
                        
                        receipt_file = storage.save_receipt(current_order)
                        print(f"Receipt saved to: {receipt_file}")
                        storage.save_state(DATA_DIR, table_list, menu_data, order_list)

                    elif bill_choice == "2":
                        try:
                            splits = int(input("How many ways to split? "))
                            split_data = orders.split_bill(current_order, "even", splits, tax_rate, tip_rate)
                            print(f"\n--- Split Breakdown ({splits} ways) ---")
                            for p in split_data:
                                print(f"Person {p['party_id']}: ${p['amount_due']:.2f}")
                            full_bill = orders.calculate_bill(current_order, tax_rate, tip_rate)
                            current_order['bill'] = full_bill
                            receipt_file = storage.save_receipt(current_order) 
                            print(f"Master Receipt saved to: {receipt_file}")
                            storage.save_state(DATA_DIR, table_list, menu_data, order_list)
                            
                        except ValueError:
                            print("Error: Invalid number for split.")

                else:
                    print("Error: No open order found for this table.")
            
            except ValueError:
                print("Error: Invalid table number.")


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
            print("3. Remove item")
            m_choice= input("Select: ")
            if m_choice=="1":
                item_id=input("Id (e.g., M1) : ")
                exists=False
                for cat_items in menu_data.values():
                    for item in cat_items:
                        if item['id'] == item_id:
                            exists = True
                            break
                if exists:
                    print("Error: Item ID already exists! Try again.")
                    continue
                name=input("Item Name:")
                price=float(input("Price:"))
                cat=input("Category:")
                new_item={
                    "id" : item_id,
                    "category":cat,
                    "name":name,
                    "price":price,
                    "available": True}
                menu.add_menu_item(menu_data,new_item)
                print(f"Item '{name}' added with ID '{item_id}' to category '{cat}'.")
                storage.save_state(DATA_DIR, table_list, menu_data, order_list)
            
            elif m_choice == "2":
                item_id = input("Enter ID of item to update: ")
                print("Leave field blank to keep current value.")
                new_price = input("New Price: ")
                new_avail = input("Is Available (true/false): ")

                updates = {}
                if new_price: 
                    updates["price"] = float(new_price)
                if new_avail: 
                    updates["available"] = new_avail.lower() == 'true'

                if updates:
                    menu.update_menu_item(menu_data, item_id, updates)
                    print("Item updated.")
                    storage.save_state(DATA_DIR, table_list, menu_data, order_list)
            
            elif m_choice == "3":
                del_id=input("Enter ID of item to remove:")
                if menu.remove_menu_item(menu_data,del_id):
                    print("Item removed.")
                    storage.save_state(DATA_DIR, table_list, menu_data, order_list)
                else:
                    print("Item ID not found.")

                
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
        result=storage.backup_day(DATA_DIR, BACKUP_DIR)
        print(result)
        
    else:
        print("Invalid manager option.")
        
if __name__ == "__main__":
    main( )