import tables
import menu
import orders
import storage
import reports
import json
import os
import shutil
import datetime

# --- CONFIGURATION ---
DATA_DIR = "data"
LOGS_DIR = "logs"
BACKUP_DIR = "backups"

# --- MANAGER CREDENTIALS ---
MANAGER_USERNAME = "admin"
MANAGER_PASSWORD = "1234"

def get_int(prompt):
    """
    Helper to get an integer from user.
    Returns None if user types 'b' (back).
    """
    while True:
        user_input = input(prompt).strip()
        
        # Check for Back command
        if user_input.lower() in ['b', 'back', 'q', 'quit']:
            return None
            
        try:
            return int(user_input)
        except ValueError:
            print("Error: Please enter a valid number (or 'b' to go back).")

def autosave(table_list, menu_data, order_list):
    """Saves data immediately to prevent data loss on crash."""
    storage.save_state(DATA_DIR, table_list, menu_data, order_list)

def manager_login():
    """
    Asks for username/password. Returns True if correct, False otherwise.
    """
    print("\n--- SECURITY CHECK (Type 'b' to cancel) ---")
    user = input("Username: ").strip()
    if user.lower() == 'b':
        return False
    
    pwd = input("Password: ").strip()
    
    if user == MANAGER_USERNAME and pwd == MANAGER_PASSWORD:
        print(">> Access Granted.")
        return True
    else:
        print("!! Access Denied: Wrong Credentials !!")
        return False

def main():
    # 1. Setup Directories & Load Data
    if not os.path.exists(LOGS_DIR): os.makedirs(LOGS_DIR)
    if not os.path.exists(BACKUP_DIR): os.makedirs(BACKUP_DIR)
    
    # Load all data from the other files
    table_list, menu_data, order_list = storage.load_state(DATA_DIR)

    while True:
        print("\n--- RESTAURANT MANAGER ---")
        print("1. View Tables")
        print("2. Seat Table")
        print("3. Release Table")
        print("4. Place Order")
        print("5. Calculate & Split Bill") 
        print("6. Manager Tools (LOCKED)")
        print("7. Manual Save & Exit")
        print("8. Menu Management (LOCKED)")
        
        choice = input("Select option: ").strip()

        # --- OPTION 1: VIEW TABLES ---
        if choice == "1":
            print("\n--- Current Tables ---")
            for t in table_list:
                status = t['status'].upper()
                srv = t.get('server_name') or "None"
                print(f"Table {t['table_number']} | Size: {t['capacity']} | {status} | Server: {srv}")

        # --- OPTION 2: SEAT TABLE ---
        elif choice == "2":
            print("\n--- Seat Table (Type 'b' to go back) ---")
            
            t_num = get_int("Table Number: ")
            if t_num is None: continue
            
            p_size = get_int("Party Size: ")
            if p_size is None: continue
            
            srv_name = input("Server Name: ").strip()
            if srv_name.lower() in ['b', 'back']: continue

            try:
                table = tables.assign_table(table_list, t_num, p_size)
                if table:
                    tables.update_server(table_list, t_num, srv_name)
                    
                    # Create the open order
                    new_order = orders.open_order(t_num)
                    new_order['server_name'] = srv_name
                    order_list.append(new_order)
                    
                    print(f"Table {t_num} seated. Server: {srv_name}")
                    autosave(table_list, menu_data, order_list)
                else:
                    print("Table not available or capacity too small.")
            except Exception as e:
                print(f"Error: {e}")

        # --- OPTION 3: RELEASE TABLE ---
        elif choice == "3":
            t_num = get_int("Table Number to Release: ")
            if t_num is None: continue

            # Zombie Check: Is there an unpaid open order?
            open_order = next((o for o in order_list if o['table_number'] == t_num and o['status'] == 'open'), None)
            
            if open_order:
                print(f"\n!!! WARNING: Table {t_num} has an UNPAID BILL !!!")
                confirm = input("Are you sure you want to release it? (y/n): ").lower()
                if confirm != 'y':
                    print("Cancelled. Go to Option 5 to pay first.")
                    continue

            if tables.release_table(table_list, t_num):
                print(f"Table {t_num} released.")
                autosave(table_list, menu_data, order_list)
            else:
                print("Table not found.")

        # --- OPTION 4: PLACE ORDER ---
        elif choice == "4":
            t_num = get_int("Table Number: ")
            if t_num is None: continue

            # Find active order
            current_order = next((o for o in order_list if o['table_number'] == t_num and o['status'] == 'open'), None)

            if not current_order:
                print("No open order for this table. Seat it first (Option 2).")
            else:
                # 1. SHOW THE MENU
                print("\n" + "="*30)
                print("         CURRENT MENU")
                print("="*30)
                for cat, items in menu_data.items():
                    print(f"\n--- {cat.upper()} ---")
                    for item in items:
                        if item.get('available', True):
                            print(f"[{item['id']}] {item['name']} - ${item['price']}")
                print("="*30)

                # 2. Add Items Loop
                while True:
                    user_in = input("\nEnter Item ID or Name (or 'done' to finish): ").strip()
                    
                    if user_in.lower() in ['done', 'b', 'back']:
                        break
                    
                    # Logic to find item by ID OR Name (Case Insensitive)
                    found_item = None
                    for cat_items in menu_data.values():
                        for item in cat_items:
                            if (item['id'].lower() == user_in.lower() or 
                                item['name'].lower() == user_in.lower()):
                                found_item = item
                                break
                        if found_item: break
                    
                    if found_item:
                        qty = get_int(f"Quantity for {found_item['name']}: ")
                        if qty is None: continue
                        
                        orders.add_item_to_order(current_order, found_item, qty)
                        print(f"--> Added {qty} x {found_item['name']}")
                    else:
                        print("Item not found. Try again.")

                storage.log_kitchen_ticket(current_order, LOGS_DIR) 
                print("Kitchen ticket sent.")
                autosave(table_list, menu_data, order_list)

        # --- OPTION 5: CALCULATE & SPLIT ---
        elif choice == "5":
            t_num = get_int("Table Number: ")
            if t_num is None: continue

            order_to_close = next((o for o in order_list if o['table_number'] == t_num and o['status'] == 'open'), None)
            
            if order_to_close:
                print(f"\n--- BILLING FOR TABLE {t_num} ---")
                print(f"Total Items: {len(order_to_close['items'])}")
                
                print("\nPayment Method:")
                print("1. Single Bill (Full Payment)")
                print("2. Split Equally")
                print("3. Split by Item (Itemized)")
                
                pay_method = input("Select method: ").strip()
                
                # A. SPLIT EQUALLY
                if pay_method == "2":
                    num_people = get_int("How many people? ")
                    if num_people:
                        splits = orders.calculate_split_bill(order_to_close, "equal", 0.10, 0.10, parties=num_people)
                        print("\n--- EQUAL SPLIT BREAKDOWN ---")
                        for p in splits:
                            print(f"Person {p['party_id']}: ${p['total_bill']:.2f}")

                # B. SPLIT BY ITEM
                elif pay_method == "3":
                    num_people = get_int("How many people? ")
                    if num_people:
                        print("\n--- Order Items ---")
                        for item in order_to_close['items']:
                            print(f"- {item['name']} (${item['price']})")
                        
                        party_selections = []
                        print("\n(Type exact item names, comma separated. Example: Soup, Cola)")
                        
                        for i in range(1, num_people + 1):
                            raw_input = input(f"Items for Person {i}: ")
                            person_items = [x.strip() for x in raw_input.split(',')]
                            party_selections.append(person_items)
                        
                        try:
                            splits = orders.calculate_split_bill(order_to_close, "itemized", 0.10, 0.10, parties=party_selections)
                            print("\n--- ITEMIZED SPLIT BREAKDOWN ---")
                            for p in splits:
                                print(f"Person {p['party_id']}: ${p['total_bill']:.2f}")
                        except Exception as e:
                            print(f"Error calculating split: {e}")

                # C. FINAL PAYMENT
                master_bill = orders.calculate_bill(order_to_close, tax_rate=0.10, tip_rate=0.10)
                print(f"\n>> GRAND TOTAL TO PAY: ${master_bill['total']:.2f}")
                
                confirm = input("Mark Order as PAID and Close? (y/n): ").lower()
                if confirm == 'y':
                    order_to_close['bill'] = master_bill 
                    order_to_close['status'] = 'closed'
                    
                    storage.save_receipt(order_to_close)
                    print("Receipt saved.")
                    
                    rel = input("Release table now? (y/n): ").lower()
                    if rel == 'y':
                        tables.release_table(table_list, t_num)
                        print("Table released.")
                    
                    autosave(table_list, menu_data, order_list)
            else:
                print("No open order found.")

        # --- OPTION 6: REPORTS (PROTECTED) ---
        elif choice == "6":
            if not manager_login():
                continue # Skip the rest of this block if login fails

            print("\n--- Manager Tools ---")
            print("1. Daily Sales")
            print("2. Top Items")
            print("3. Server Stats")
            print("4. Backup Data")
            
            sub = input("Select: ").strip()
            closed_orders = [o for o in order_list if o.get('status') == "closed"]

            if sub == "1":
                rep = reports.daily_sales_report(closed_orders)
                print(f"Revenue: ${rep['total_revenue']} | Orders: {rep['total_orders_counts']}")
            
            elif sub == "2":
                limit = get_int("How many top items? ") or 5
                top = reports.top_selling_items(closed_orders, menu_data, limit)
                for x in top:
                    print(f"{x['name']}: {x['quantity_sold']}")
            
            elif sub == "3":
                perf = reports.server_performance(closed_orders)
                for srv, dat in perf.items():
                    print(f"{srv}: ${dat['total_sales']} ({dat['tables_served']} tables)")
            
            elif sub == "4":
                path = storage.backup_day(DATA_DIR, BACKUP_DIR)
                print(f"Backup saved to: {path}")

        # --- OPTION 7: EXIT ---
        elif choice == "7":
            storage.save_state(DATA_DIR, table_list, menu_data, order_list)
            print("Data saved. Goodbye!")
            break

        # --- OPTION 8: MENU MANAGER (PROTECTED) ---
        elif choice == "8":
            if not manager_login():
                continue # Skip if login fails

            print("\n--- Menu Management ---")
            for cat, items in menu_data.items():
                print(f"--- {cat.upper()} ---")
                for item in items:
                    print(f"ID: {item['id']} | {item['name']} | ${item['price']}")
            
            action = input("\n(A)dd Item | (R)emove | (B)ack: ").lower().strip()
            
            if action == 'a':
                cat = input("Category: ").lower()
                name = input("Name: ")
                item_id = input("ID: ").strip()
                try:
                    price = float(input("Price: "))
                    new_item = {"id": item_id, "name": name, "price": price, "available": True, "category": cat}
                    menu.add_menu_item(menu_data, new_item)
                    print("Item added.")
                    autosave(table_list, menu_data, order_list)
                except ValueError:
                    print("Invalid price.")
            
            elif action == 'r':
                rem_id = input("Item ID to remove: ").strip()
                if menu.remove_menu_item(menu_data, rem_id):
                    print("Removed.")
                    autosave(table_list, menu_data, order_list)
                else:
                    print("ID not found.")

if __name__ == "__main__":
    main()
