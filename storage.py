import json
import os
import shutil
import datetime

def load_state(data_dir: str) -> tuple[list, dict, list]:
    table_file = os.path.join(data_dir, "tables.json")
    menu_file = os.path.join(data_dir, "menu.json")
    orders_file = os.path.join(data_dir, "orders.json")
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    try:
        with open(table_file, 'r') as f:
            data = json.load(f)
            if isinstance(data, dict) and "tables" in data:
                table_list = data["tables"]
            else:
                table_list = data
    except (FileNotFoundError, json.JSONDecodeError):
        table_list = []

    try:
        with open(menu_file, 'r') as f:
            menu_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        menu_data = {}

    try:
        with open(orders_file, 'r') as f:
            orders_list = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        orders_list = []

    return table_list, menu_data, orders_list

def save_receipt(order: dict, folder: str = "receipts") -> str:
    if not os.path.exists(folder):
        os.makedirs(folder)
        
    filename = f"{folder}/receipt_{order['table_number']}_{datetime.datetime.now().strftime('%H%M%S')}.txt"
    
    with open(filename, 'w') as f:
        f.write(f"--- RECEIPT Table {order['table_number']} ---\n")
        f.write(f"Server: {order.get('server_name', 'Unknown')}\n")
        f.write("-" * 30 + "\n")
        
        for item in order['items']:
            f.write(f"{item['quantity']}x {item['name']} ... ${item['price'] * item['quantity']:.2f}\n")
            
        f.write("-" * 30 + "\n")
        if 'bill' in order:
            f.write(f"Subtotal: ${order['bill']['subtotal']:.2f}\n")
            f.write(f"Tax:      ${order['bill']['tax_amount']:.2f}\n")
            f.write(f"Total:    ${order['bill']['total']:.2f}\n")
        else:
            f.write("(Bill not yet calculated)\n")
            
    return filename

def save_state(data_dir: str, tables: list, menu: dict, orders: list) -> None:
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    with open(f"{data_dir}/tables.json", 'w') as f:
        json.dump(tables, f, indent=4)
    
    with open(f"{data_dir}/menu.json", 'w') as f:
        json.dump(menu, f, indent=4)
        
    with open(f"{data_dir}/orders.json", 'w') as f:
        json.dump(orders, f, indent=4)

def backup_day(data_dir: str, archive_dir: str) -> str:
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
        
    timestamp= datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{archive_dir}/backup_{timestamp}"
    shutil.copytree(data_dir, backup_path) 
    
    return backup_path

def log_kitchen_ticket(order: dict, directory: str) -> str:
    if not os.path.exists(directory):
        os.makedirs(directory)
  
    timestamp = datetime.datetime.now().strftime("%H%M%S")
    filename = f"{directory}/ticket_{order['table_number']}_{timestamp}.txt" 
    
    with open(filename, 'w') as f:
        f.write("--- KITCHEN TICKET ---\n") 
        f.write(f"Table: {order['table_number']}\n")
        f.write(f"Time: {datetime.datetime.now().strftime('%H:%M:%S')}\n")
        f.write("-" * 25 + "\n")
        
        for item in order['items']:
            f.write(f"- {item['quantity']}x {item['name']} ({item.get('note', '')})\n")
    return filename
