
# Restaurant Table & Order Manager

## Project Overview
This project is a terminal-based Point of Sale (POS) system designed to help restaurant staff manage dining room operations. It handles table assignments, order tracking, bill calculation (including splitting), menu management, and sales reporting. The system ensures data persistence using JSON files.

## Features
* **Table Management:** View status, assign tables to parties (checking capacity), and release tables upon payment.
* **Order Processing:** Create orders, add items, and generate kitchen tickets.
* **Billing System:**
    * Automatic tax and tip calculation.
    * **Bill Splitting:** Support for splitting bills evenly or by item.
* **Menu Management:** Add or update menu items via the CLI.
* **Admin Tools:**
    * Generate Daily Sales Reports.
    * Track Server Performance.
    * Identify Top Selling Items.
    * Data Backup utilities.
* **Data Persistence:** All data is saved automatically to `data/` (tables, menu, orders).

## Project Structure
* `main.py`: The entry point. Handles the main menu loop and user input.
* `tables.py`: Logic for seating tables, checking capacity, and updating server assignments.
* `orders.py`: Functions for managing order items, calculating totals, and splitting bills.
* `menu.py`: CRUD operations for the menu (add, update, filter items).
* `reports.py`: Generates analytics for sales and performance.
* `storage.py`: Handles loading/saving JSON data and creating backups.
* `tests.py`: Automated tests for critical business logic.

## Installation & Setup
1.  **Prerequisites:** Ensure you have Python 3.x installed.
2.  **File Setup:** Ensure the `data/` directory exists with `tables.json`, `menu.json`, and `orders.json`.
3.  **Run the Application:**
    ```bash
    python main.py
    ```

## User Guide & Workflows

### 1. The "Seating to Billing" Workflow
This is the standard flow for a customer visit:

1.  **View Tables (Option 1):** Check which tables are "free".
2.  **Seat Table (Option 2):**
    * Enter the Table Number 
    * Enter Party Size (System checks if table capacity is sufficient).
    * Assign a Server.
3.  **Place Order (Option 4):**
    * Enter Table Number.
    * Add items by name (e.g., "Lentil Soup").
    * The system logs a timestamped kitchen ticket in the `logs/` folder.
4.  **Calculate Bill (Option 5):**
    * The system displays the Subtotal, Tax, and Tip.
    * **Splitting:** You will be asked if you want to split the bill (`even` / `itemized` / `no`).
    * **Closing:** Confirm payment to release the table and archive the order.

### 2. Menu Management (Option 8)
* Select **Option 8** from the main menu.
* Choose "Add Item" to introduce new dishes or drinks to the system.
* These changes are saved immediately to `menu.json`.

### 3. Manager Tools (Option 6)
* **Daily Sales Report:** Shows total revenue and order counts.
* **Top Selling Items:** Lists the most popular dishes.
* **Server Performance:** Shows total sales per server.
* **Backup:** Creates a timestamped copy of all data in the `backups/` folder.

## Testing
This project includes automated tests to validate business logic.

**To run the tests:**
```bash
python tests.py
