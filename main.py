import tables
import menu
import orders
import storage

DATA_DIR = "data"

def main():
    table_list, menu_data, order_list = storage.load_state(DATA_DIR)

    while True:
        print("\n--- RESTAURANT MANAGER ---")
        print("1. View Tables")
        print("2. Seat Table")
        print("3. Release Table")
        print("4. Place Order")
        print("5. Calculate Bill")
        print("6. Save & Exit")
        
        choice = input("Select option: ")

        if choice == "1":
            for t in table_list:
                print(f"Table {t['table_number']}: {t['status']} (Server: {t.get('server_name', 'None')})")

        elif choice == "2":
            t_num = int(input("Table Number: "))
            p_size = int(input("Party Size: "))
            result = tables.assign_table(table_list, t_num, p_size)
            if result:
                server = input("Assign Server: ")
                tables.update_server(table_list, t_num, server)
                orders.open_order(t_num) 
                print("Table Seated.")
            else:
                print("Cannot seat table.")

        elif choice == "3":
            t_num = int(input("Table Number: "))
            if tables.release_table(table_list, t_num):
                print("Table Released.")
            else:
                print("Table not found.")

        elif choice == "4":
            t_num = int(input("Table Number for Order: "))
            current_order = None
            for i in order_list:
                if i['table_number'] == t_num and i['status'] == 'open':
                    current_order = i
                    break
            
            if not current_order:
                current_order = orders.open_order(t_num)
                order_list.append(current_order)

            item_name = input("Enter Menu Item Name: ")
            qty = int(input("Quantity: "))
            price = float(input("Price (Temporary): ")) 
            
            temp_item = {"name": item_name, "price": price}
            orders.add_item_to_order(current_order, temp_item, qty)
            print("Item added.")

        elif choice == "5":
            t_num = int(input("Table Number to Bill: "))
            found = False
            for i in order_list:
                if i['table_number'] == t_num and i['status'] == 'open':
                    bill = orders.calculate_bill(i, 0.10, 0.15)
                    print(f"Subtotal: ${bill['subtotal']}")
                    print(f"Tax: ${bill['tax']}")
                    print(f"Tip: ${bill['tip']}")
                    print(f"TOTAL: ${bill['total']}")
                    found = True
                    break
            if not found:
                print("No open order for this table.")

        elif choice == "6":
            storage.save_state(DATA_DIR, table_list, menu_data, order_list)
            print("Data saved. Goodbye.")
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
