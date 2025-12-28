import json

def initialize_tables(path: str) -> list:
    try:
        with open(path, 'r') as file:
            table_data = json.load(file)
            if isinstance(table_data, dict) and "tables" in table_data:
                return table_data["tables"]
            return table_data
    except FileNotFoundError:
        return []


def add_table(tables: list, table_data: dict) -> list:
    tables.append(table_data)
    return tables

def assign_table(tables: list, table_number: int, party_size: int) -> dict | None:
    for table in tables:
        if table['table_number'] == table_number:
            if table['status'] == 'free' and table['capacity'] >= party_size:
                table['status'] = 'occupied'
                table['party_size'] = party_size
                return table
    return None

def release_table(tables: list, table_number: int) -> bool:
    for table in tables:
        if table['table_number'] == table_number:
            table['status'] = 'free'
            table['party_size'] = 0
            table['server_name'] = ""
            return True
    return False

def update_server(tables: list, table_number: int, server_name: str) -> dict:
    for table in tables:
        if table['table_number'] == table_number:
            table['server_name'] = server_name
            return table
    return {}
