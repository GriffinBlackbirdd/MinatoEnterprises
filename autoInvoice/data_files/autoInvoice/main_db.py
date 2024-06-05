import sqlite3
from rich.console import Console
import pandas as pd

console = Console()

class InventoryDB:
    def __init__(self, db_path):
        self.db_path = db_path

    def connect(self):
        return sqlite3.connect(self.db_path)

    def show_contents(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM inventory')
            for row in cursor.fetchall():
                console.print(row)

    def get_chassis_numbers(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT chassis_number FROM inventory')
            return [row[0] for row in cursor.fetchall()]

    def make_db(self):
        console.print("[bold red]Make sure you have the inventory.xlsx file in the data_files folder.[/bold red]")
        with self.connect() as conn:
            excel_data = pd.read_excel('data_files/inventory.xlsx', engine='openpyxl')
            excel_data.to_sql('inventory', conn, if_exists='append', index=False)
        console.print("[bold green]Database created successfully![/bold green]")

    def modify_db(self):
        with self.connect() as conn:
            modified_excel_data = pd.read_excel('data_files/inventory.xlsx', engine='openpyxl')
            existing_data = pd.read_sql_query("SELECT * FROM inventory", conn)
            new_entries = pd.merge(modified_excel_data, existing_data, how='left', indicator=True).loc[lambda x: x['_merge'] == 'left_only'].drop('_merge', axis=1)
            if not new_entries.empty:
                new_entries.to_sql('inventory', conn, if_exists='append', index=False)
            else:
                console.print("No new entries to add.")

    def export_db_to_excel(self, table_name, excel_file_path):
        with self.connect() as conn:
            try:
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                df.to_excel(excel_file_path, index=False, engine='openpyxl')
                console.print(f"[bold green]Data exported successfully to {excel_file_path}[/bold green]")
            except Exception as e:
                console.print(f"An error occurred: {e}")

def main():
    db = InventoryDB('inventory.db')
    while True:
        console.print("[bold magenta]Inventory Management System[/bold magenta]")
        console.print("1. Make the database?")
        console.print("2. See the table?")
        console.print("3. Modify the database?")
        console.print("4. Export the database to an Excel file?")
        console.print("5. Chassis numbers?[Debug]")
        console.print("6. Exit")

        choice = console.input("Enter your choice: ")
        if choice == '1':
            db.make_db()

        elif choice == '2':
            db.show_contents()

        elif choice == '3':
            db.modify_db()

        elif choice == '4':
            db.export_db_to_excel('inventory', 'exported_inventory.xlsx')

        elif choice == '5':
            chassis_numbers = db.get_chassis_numbers()
            console.print(chassis_numbers)

        elif choice == '6':
            console.print("[bold yellow]Exiting the program. Goodbye![/bold yellow]")
            break

        else:
            console.print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()