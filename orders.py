import datetime
def open_order(table_number: int) -> dict:
    return {
        "table_number": table_number,
        "items": [],
        "status": "open",
        "total": 0.0
        "date": datetime.date.today().isoformat()
    }

def add_item_to_order(order: dict, menu_item: dict, quantity: int, note: str = "") -> dict:
    item_entry = {
        "id": menu_item.get("id", "unknown"),
        "name": menu_item["name"],
        "price": menu_item["price"],
        "quantity": quantity,
        "note": note,
        "status": "ordered"
    }
    order["items"].append(item_entry)
    return order

def remove_item_from_order(order: dict, item_name: str) -> dict:
    for i, item in enumerate(order["items"]):
        if item["name"] == item_name:
            del order["items"][i]
            break
    return order

def update_item_status(order: dict, item_name: str, status: str) -> dict:
    for item in order["items"]:
        if item["name"] == item_name:
            item["status"] = status
    return order

def calculate_bill(order: dict, tax_rate: float, tip_rate: float) -> dict:
    subtotal = 0.0
    for item in order["items"]:
        subtotal += item["price"] * item["quantity"]
    
    tax_amount = subtotal * tax_rate
    tip_amount = subtotal * tip_rate
    total = subtotal + tax_amount + tip_amount
    
    return {
        "subtotal": round(subtotal, 2),
        "tax": round(tax_amount, 2),
        "tip": round(tip_amount, 2),
        "total": round(total, 2)
    }

def split_bill(order: dict, method: str, parties: int | list) -> list:

    if "bill" not in order:
        print("Error: Calculate bill first.")
        return []

    tax_rate = order["bill"]["tax_rate"]
    tip_rate = order["bill"]["tip_rate"]
    total_bill = order["bill"]["total"] 

    # Simple split (Evenly)
    if method == "even":
        if isinstance(parties, int) and parties > 0:
            amount_per_person = total_bill / parties
            split_bills = []
            for i in range(parties):
                split_bills.append({
                    "party_id": i + 1,
                    "amount_due": round(amount_per_person, 2)
                })
            return split_bills
    
    # Itemized Split (Paying for your own food)
    elif method == "itemized":
        if isinstance(parties, list):
            split_bills = []
            for i, party_items_ids in enumerate(parties):
                party_subtotal = 0.0
                for item in order["items"]:                
                    if item.get("id") in party_items_ids or item.get("name") in party_items_ids:
                        party_subtotal += item["price"] * item["quantity"]
                
                party_tax = party_subtotal * tax_rate
                party_total = party_subtotal + party_tax
                party_tip = party_total * tip_rate
                
                split_bills.append({
                    "party_id": i + 1,
                    "subtotal": round(party_subtotal, 2),
                    "tax_amount": round(party_tax, 2),
                    "tip_amount": round(party_tip, 2),
                    "total_bill": round(party_total + party_tip, 2)
                })
            return split_bills
            
    print("Invalid split method.")
    return []
