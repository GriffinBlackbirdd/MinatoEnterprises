from docxtpl import DocxTemplate
import streamlit as st
import datetime
import sqlite3
import num2words

doc = DocxTemplate("templates/invoice_template.docx")

# doc.render({'name': 'Arreyan'})
# doc.save("generated_doc.docx")
st.title("Minato Enterprises")
st.write("Generate your invoice here!")
db = 'inventory.db'
def app():
    date_input = datetime.datetime.now().strftime("%Y-%m-%d")
    with st.form("entry_form", clear_on_submit = True):
        invoice_number = st.text_input("Invoice Number: ", placeholder = "Invoice Number")
        col2, col3, col4 = st.columns(3)
        customer_name = col2.text_input("Customer Name:", placeholder = "Full Name")
        customer_address = col3.text_input("Customer Address: ", placeholder = "Customer's Address")
        number = col4.text_input("Phone Number", placeholder="+91")
        chassis_numbers = get_chassis_numbers()
        selected_chassis_number = st.selectbox('Select Chassis Number', chassis_numbers)
        col6, col7, col8 = st.columns(3)
        # Maybe the unit price will be mentioned in the dataset?
        price = col6.number_input("Price:", placeholder="Price")
        total = col7.number_input("Total:", placeholder="Total")
        sub_total = col8.number_input("Sub Total:", placeholder="Sub Total")
        cgst = (sub_total / 100) * 2.5
        sgst = (sub_total / 100) * 2.5
        final_total = sub_total + cgst + sgst
        in_words = num2words.num2words(int(final_total), lang='en_IN') + " only"
        submitted = st.form_submit_button("Generate Invoice?")
        # submitted = st.form_submit_button("Generate Invoice?")
        if submitted:
            description = fetch_and_delete(selected_chassis_number)
            if description:
                description_str = ', '.join(description)
                doc.render({
                    'date_input': date_input,
                    'invoice_number': invoice_number,
                    'description': description_str,
                    'customer_name': customer_name,
                    'customer_address': customer_address,
                    'customer_mobile': number,
                    'price': price,
                    'total': total,
                    'sub_total': sub_total,
                    'cgst': f"{cgst:,.2f}",
                    'sgst': f"{sgst:,.2f}",
                    'lgst': "0.00",
                    'round_off': "0.00",
                    'FINAL_TOTAL': f"{final_total:,.2f}",
                    'in_words': in_words
                })
                doc.save(f"invoices/#{invoice_number+customer_name}.docx")
                st.success("Invoice saved successfully!")
            else:
                st.error("Failed to fetch the vehicle description. Please check the chassis number and try again.")


def fetch_and_delete(chassis):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
        
    description = None
        
    try:
        cursor.execute("SELECT * FROM inventory WHERE chassis_number = ?", (chassis,))
        row = cursor.fetchone()
            
        if row:
                description = row
                cursor.execute("DELETE FROM inventory WHERE chassis_number = ?", (chassis,))
                conn.commit()
                st.success("Item removed from the inventory!")
        else:
                st.error("Chassis number not found.")
                
    except sqlite3.Error as error:
            st.error(f"Failed to read/delete data from sqlite table, {error}")
    finally:
            if conn:
                conn.close()
    return description

def connect():
    return sqlite3.connect('inventory.db')

def get_chassis_numbers():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT chassis_number FROM inventory')
        return [row[0] for row in cursor.fetchall()]
app()