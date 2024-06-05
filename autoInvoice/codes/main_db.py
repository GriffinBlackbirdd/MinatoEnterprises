import sqlite3
from rich.console import Console
import pandas as pd

console = Console()

class InventoryDB:
    def __init__(self, db_path):
        self.db_path = db_path

    def connect(self):
        return sqlite3.connect(self.db_path)

    def show_battery_contents(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM battery')
            for row in cursor.fetchall():
                console.print(row)

    def show_inventory_contents(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM inventory')
            for row in cursor.fetchall():
                console.print(row)



    def make_inventory_db(self):
        console.print("[bold red]Make sure you have the inventory.xlsx file in the data_files folder.[/bold red]")
        with self.connect() as conn:
            excel_data = pd.read_excel('/Users/eagle/Developer/invoiceGen/autoInvoice/data_files/inventory.xlsx', engine='openpyxl')
            excel_data.to_sql('inventory', conn, if_exists='append', index=False)
        console.print("[bold green]Database created successfully![/bold green]")

    def make_battery_db(self):
        console.print("[bold red]Make sure you have the battery.xlsx file in the data_files folder.[/bold red]")
        with self.connect() as conn:
            excel_data = pd.read_excel('/Users/eagle/Developer/invoiceGen/autoInvoice/data_files/battery.xlsx', engine='openpyxl')
            excel_data.to_sql('battery', conn, if_exists='append', index=False)
        console.print("[bold green]Battery database created successfully![/bold green]")

    def modify_inventory_db(self):
        with self.connect() as conn:
            modified_excel_data = pd.read_excel('/Users/eagle/Developer/invoiceGen/autoInvoice/data_files/inventory.xlsx', engine='openpyxl')
            existing_data = pd.read_sql_query("SELECT * FROM inventory", conn)
            new_entries = pd.merge(modified_excel_data, existing_data, how='left', indicator=True).loc[lambda x: x['_merge'] == 'left_only'].drop('_merge', axis=1)
            if not new_entries.empty:
                new_entries.to_sql('inventory', conn, if_exists='append', index=False)
            else:
                console.print("No new entries to add.")

    def modify_battery_db(self):
        with self.connect() as conn:
            modified_excel_data = pd.read_excel('/Users/eagle/Developer/invoiceGen/autoInvoice/data_files/battery.xlsx', engine='openpyxl')
            existing_data = pd.read_sql_query("SELECT * FROM inventory", conn)
            new_entries = pd.merge(modified_excel_data, existing_data, how='left', indicator=True).loc[lambda x: x['_merge'] == 'left_only'].drop('_merge', axis=1)
            if not new_entries.empty:
                new_entries.to_sql('inventory', conn, if_exists='append', index=False)
            else:
                console.print("No new entries to add.")

    def export_inventory_to_excel(self, table_name = "inventory", excel_file_path = "/Users/eagle/Developer/invoiceGen/autoInvoice/codes/exportedFiles/exportedInventory.xlsx"):
        with self.connect() as conn:
            try:
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                df.to_excel(excel_file_path, index=False, engine='openpyxl')
                console.print(f"[bold green]Data exported successfully to {excel_file_path}[/bold green]")
            except Exception as e:
                console.print(f"An error occurred: {e}")

    def export_battery_to_excel(self, table_name = "battery", excel_file_path = "/Users/eagle/Developer/invoiceGen/autoInvoice/codes/exportedFiles/exportedBattery.xlsx"):
        with self.connect() as conn:
            try:
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                df.to_excel(excel_file_path, index=False, engine='openpyxl')
                console.print(f"[bold green]Data exported successfully to {excel_file_path}[/bold green]")
            except Exception as e:
                console.print(f"An error occurred: {e}")



    def get_chassis_numbers(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT chassis_number FROM inventory')
            return [row[0] for row in cursor.fetchall()]
        
    def get_battery_numbers(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT battery_serial_no FROM battery')
            return [row[0] for row in cursor.fetchall()]

    def get_make_and_model_and_controller(self, chassis_number):
        with self.connect() as conn:
            cursor = conn.cursor()
            query = 'SELECT make, model, controller FROM inventory WHERE chassis_number = ?'
            cursor.execute(query, (chassis_number,))
            result = cursor.fetchone()
            if result:
                return result[0], result[1], result[2]
            else:
                return None, None, None
            
    def get_chassis_warranty(self, chassis_number):
        with self.connect() as conn:
            cursor = conn.cursor()
            query = 'SELECT motor_warranty, chassis_warranty, controller_warranty  FROM inventory WHERE chassis_number = ?'
            cursor.execute(query, (chassis_number,))
            result = cursor.fetchone()
            if result:
                return result[0], result[1], result[2]
            else:
                return None, None, None
    
    def get_battery_warranty(self, battery_serial_no):
        with self.connect() as conn:
            cursor = conn.cursor()
            query = 'SELECT warranty_in_months FROM battery WHERE battery_serial_no = ?'
            cursor.execute(query, (battery_serial_no,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None



def main():
    db = InventoryDB('inventory.db')
    while True:
        console.print("[bold magenta]Inventory Management System[/bold magenta]")
        console.print("1. Make the Inventory table?")
        console.print("2. Make the Battery table?")
        console.print("3. See the Inventory table?")
        console.print("4. See the Battery table?")
        console.print("5. Modify the Inventory table?")
        console.print("6. Modify the battery table")
        console.print("7. Export the inventory table to an Excel file?")
        console.print("8. Export the battery table to an Excel file?")

        console.print("9. Exit")

        choice = console.input("Enter your choice: ")
        if choice == '1':
            db.make_inventory_db()

        elif choice == '2':
            db.make_battery_db()

        elif choice == '3':
            db.show_inventory_contents()

        elif choice == '4':
            db.show_battery_contents()

        elif choice == '5':
            db.modify_inventory_db()

        elif choice == '6':
            db.modify_battery_db()
        
        elif choice == '7':
            db.export_inventory_to_excel()

        elif choice == '8':
            db.export_battery_to_excel()

        elif choice == '9':
            console.print("[bold yellow]Exiting the program. Goodbye![/bold yellow]")
            break
        
        else:
            console.print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()