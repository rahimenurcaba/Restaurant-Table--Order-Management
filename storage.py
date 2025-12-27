import json
import os
import shutil
import datetime

def load_state(data_dir: str) -> tuple[list, dict, list]:
    table_file= os.path.joşn(data_dir,"tables.json") 
    menu_file = os.path.join(data_dir,"menu.json")
    orders_file = os.path.join(data_dir,"orders.json")

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    with open(table_file, 'r') as f:
        table_list = json.load(f)
    
    with open(menu_file, 'r') as f:
        menu_data = json.load(f)
    
    with open(orders_file, 'r') as f:
        order_list = json.load(f)
    
    return table_list, menu_data, order_list

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
        