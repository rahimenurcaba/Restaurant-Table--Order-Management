import tables
import orders
import menu

def test_bill_calculation():
    print("--- Bill Calculation Testing ---")
    fake_order={
        "items":[
            {"name": "Burger","price":10.00, "quantity":2},
            {"name": "Soda", "price":2.00, "quantity":1}
        ]
    }
    #subtotal is 22.00
    #tax(10%) is 2.20
    #tip(15%) is 3.30
    #total should be 27.50 with this equations.
    bill= orders.calculate_bill(fake_order,0.10,0.15)
    if round(bill['total']) == 27.50:
        print("PASS: The system is working great.")
    else:
        print(f"FAIL: Expected 27.50, got {bill['total']}")
        
def test_table_capacity():
    print("--- Table Capacity Testing ---")
    fake_table=[
        {"table_number":1, "capacity":2,"status":"free", "server_name":"None"}
    ]
    
    #Let's try to seat 4 people at a table with 2 capacity.(It must be fail)
    result=tables.assign_table(fake_table,1,4)
    if result is None:
        print("PASS: Correctly blocked party too large for table.")
    else:
        print("FAIL: Should have blocked the party.")
    
def test_invalid_item_removal():
    print("--- Invalid Item Removal Testing (Requirement 7) ---")
    fake_order = {
        "items": [
             {"name": "Burger", "price": 10.00, "quantity": 1}
        ]
    }
    
    updated_order=orders.remove_item_from_order(fake_order, "Pizza")
    
    if len(updated_order["items"]) == 1:
        print("PASS: System handled invalid item removal gracefully.")
    else:
        print("FAIL: Order list was modified incorrectly.")

if __name__ == "__main__":
    test_bill_calculation()
    test_table_capacity()
    test_invalid_item_removal()