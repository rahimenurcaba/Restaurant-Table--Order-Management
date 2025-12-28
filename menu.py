import json

def load_menu(path: str) -> dict:
    try:
        with open(path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_menu(path: str, menu: dict) -> None:
    with open(path, 'w') as file:
        json.dump(menu, file, indent=4)

def add_menu_item(menu: dict, item: dict) -> dict:
    category = item.get("category", "extras").lower()
    
    if category not in menu:
        menu[category] = []
        
    menu[category].append(item)
    return menu
    
def remove_menu_item(menu: dict, item_id: str) -> bool:
    for category, items in menu.items():
        for i, item in enumerate(items):
            if item['id'] == item_id:
                del items[i]
                return True
    return False

def update_menu_item(menu: dict, item_id: str, updates: dict) -> dict:
    for category, items_list in menu.items():
        for item in items_list:
            if item['id'] == item_id:
                for key, value in updates.items():
                    item[key] = value
                return menu
    return menu

def filter_menu(menu: dict, category: str, vegetarian: bool | None = None) -> list:
    results = []
    if category in menu:
        for item in menu[category]:
            if vegetarian is None or item.get('vegetarian') == vegetarian:
                results.append(item)
    return results
