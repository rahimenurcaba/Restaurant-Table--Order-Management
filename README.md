# Restaurant Table & Order Manager 

## Project Overview
This project is a terminal-based Point of Sale (POS) system designed to help restaurant staff manage dining room operations. It handles table assignments, order tracking, bill calculation (including complex splitting), menu management, and sales reporting. The system ensures data persistence using JSON files and includes security features for manager tasks.

## New Features
* **Manager Security:** Restricted access to "Manager Tools" and "Menu Management" via username/password login.
* **Smart Bill Splitting:**
    * **Equal Split:** Divide the total evenly among a specific number of people.
    * **Itemized Split:** Calculate individual bills based on who ordered exactly what items.
* **Auto-Save Protection:** Data is automatically saved after every order, seating, or payment to prevent data loss during crashes.
* **"Zombie Order" Prevention:** The system warns you if you try to release a table that has an unpaid open bill.
* **Improved UX:**
    * **"Back" Button:** Type `b` in almost any menu to go back.
    * **Smart Search:** Order items by ID (e.g., `DR1`) or Name (e.g., `Coke`), case-insensitive.
    * **Visual Menus:** The menu is displayed automatically before you place an order.

## Project Structure
* `main.py`: The entry point. Handles the main menu loop, user input, and security.
* `tables.py`: Logic for seating tables, checking capacity, and updating server assignments.
* `orders.py`: Functions for managing order items, calculating totals, and splitting bills.
* `menu.py`: CRUD operations for the menu (add, update, filter items).
* `reports.py`: Generates analytics for sales and performance.
* `storage.py`: Handles loading/saving JSON data and creating backups.
* `tests.py`: Automated tests for critical business logic.

## Installation & Setup (Critical)
1.  **Prerequisites:** Ensure you have Python 3.x installed.
2.  **Folder Structure:** You **MUST** create a folder named `data` in the same directory as the python files.
3.  **Move Files:** Move `tables.json`, `menu.json`, and `orders.json` **inside** the `data/` folder.
    * *Structure should look like this:*
      ```text
      /project_folder
         ├── main.py
         ├── ... (other .py files)
         └── data/
              ├── tables.json
              ├── menu.json
              └── orders.json
      ```
4.  **Run the Application:**
    ```bash
    python main.py
    ```

## User Guide & Workflows

### 1. The "Seating to Billing" Workflow
This is the standard flow for a customer visit:

1.  **View Tables (Option 1):** Check which tables are "free".
2.  **Seat Table (Option 2):**
    * Enter Table Number & Party Size.
    * Assign a Server.
3.  **Place Order (Option 4):**
    * The menu is displayed on screen.
    * Type the **Item Name** (e.g., "Lentil Soup") or **ID** (e.g., "SO1").
    * The system logs a timestamped kitchen ticket in the `logs/` folder.
4.  **Calculate & Split Bill (Option 5):**
    * Choose your payment method (Single Bill, Equal Split, or Itemized Split).
    * Confirming payment closes the order and saves the receipt.
    * *Note:* You can release the table automatically here.

### 2. Manual Table Release (Option 3)
* **Usage:** Use this to manually free up a table (e.g., if a mistake was made or guests left without ordering).
* **Safety Warning:** If you try to release a table that has an **unpaid open order**, the system will warn you ("Zombie Order Detected"). You must confirm that you really want to abandon the bill.

### 3. Manager Tools (Option 6 & 8)
**Security Alert:** These options are locked.
* **Default Username:** `admin`
* **Default Password:** `1234`
*(These can be changed at the top of `main.py`)*

* **Manager Tools (Option 6):**
    * **Daily Sales Report:** Revenue and order counts.
    * **Top Selling Items:** Bestsellers list.
    * **Server Performance:** Sales tracked by server name.
    * **Backup:** Creates a copy of data in `backups/`.
* **Menu Management (Option 8):**
    * Add new items or remove old ones from the database.

## Testing
This project includes automated tests to validate business logic.
**To run the tests:**
```bash
python tests.py
