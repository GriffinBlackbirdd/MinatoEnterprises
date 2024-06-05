from docxtpl import DocxTemplate
import streamlit as st
import datetime
import sqlite3
import num2words, re

from main_db import InventoryDB
inventory = InventoryDB(db_path="/Users/eagle/Developer/invoiceGen/autoInvoice/codes/inventory.db")

st.title("Minato Enterprises")
st.write("Generate your invoice here!")
db = 'inventory.db'

def generate_document(template_path, context, output_path):
    doc = DocxTemplate(template_path)
    doc.render(context)
    doc.save(output_path)
    st.success(f"{output_path} saved successfully!")

def app():
    date_input = datetime.datetime.now().strftime("%Y-%m-%d")
    with st.form("entry_form", clear_on_submit=True):
        invoice = st.text_input("Invoice Number: ", placeholder="Invoice Number")
        invoice_number = f'ME-23-24-{invoice}'
        col2, col3, col4, col5 = st.columns(4)
        aadhar_number = col2.text_input("Aadhar Number:", placeholder="Aadhar Number")
        aadhar_number_str = " ".join(re.findall('.{1,4}', aadhar_number))
        customer_name = col3.text_input("Customer Name:", placeholder="Full Name")
        customer_address = col4.text_input("Customer Address: ", placeholder="Customer's Address")
        number = col5.text_input("Phone Number", placeholder="+91")
        chassis_numbers = inventory.get_chassis_numbers()
        selected_chassis_number = st.selectbox('Select Chassis Number', chassis_numbers)
        make, model, controller = inventory.get_make_and_model_and_controller(selected_chassis_number)
        motor_warranty, chassis_warranty, controller_warranty = inventory.get_chassis_warranty(selected_chassis_number)
        col6, col7 = st.columns(2)
        quantity = col6.number_input("Quantity:", value=1)  
        price = col7.number_input("Final Price:", value=0)
        if quantity > 1:
            total = quantity * price
        else:
            total = price

        sub_total = total
        tax = st.radio(
            "***Do you want to apply IGST?***",
                [":rainbow[Yes]", "No"],
        )
        if tax == ":rainbow[Yes]":
                igst = (sub_total / 100) * 5
                final_total = sub_total + igst

        else:
             cgst = (sub_total / 100) * 2.5
             sgst = (sub_total / 100) * 2.5
             final_total = sub_total + cgst + sgst 


        in_word = num2words.num2words(int(final_total), lang='en_IN') + " only"
        in_words = in_word.capitalize()

        with st.expander("Battery Details: "):
            battery_numbers = inventory.get_battery_numbers()
            battery1 = st.selectbox('Select First Battery', battery_numbers)
            battery2 = st.selectbox('Select Second Battery', battery_numbers)
            battery3 = st.selectbox('Select Third Battery', battery_numbers)
            battery4 = st.selectbox('Select Fourth Battery', battery_numbers)

                    
        battery_warranty = inventory.get_battery_warranty(battery1)
        tool_options = ["Provided", "Not Applicable", "Post-payment"]
        with st.expander("Tool Options:"):
            tool1_status = st.selectbox('Wheel Wrench Status:', tool_options, key='tool1')
            tool2_status = st.selectbox('E-Rickshaw Jack Status:', tool_options, key='tool2')
            tool3_status = st.selectbox('Charger Status:', tool_options, key='tool3')
            tool4_status = st.selectbox('Jack Wrench Status:', tool_options, key='tool4')
            tool5_status = st.selectbox('Form 22 Status:', tool_options, key='tool5')

        submitted = st.form_submit_button("Generate Invoice?")
        if submitted:
                description_str = f"{make} {model} with {controller} Controller Only"


                shared_context = {
                    'date_input': date_input,
                    'customer_name': customer_name,
                    'customer_address': customer_address,
                    'customer_mobile': number,
                    'customer_aadhar': aadhar_number_str,
                }

                invoice_context = {**shared_context, 'description': description_str, 'battery1': battery1, 'battery2': battery2, 'battery3': battery3, 'battery4': battery4, 'quantity': quantity, 'price': f"{price:,.2f}", 'total': f"{total:,.2f}", 'sub_total': f"{sub_total:,.2f}", 'cgst': f"{cgst:,.2f}", 'sgst': f"{sgst:,.2f}", 'igst': f"{igst:,.2f}", 'final_total': f"{final_total:,.2f}", 'in_words': in_words}                
                tools_context = {**shared_context, 'make': make, 'model': model, 'provided_status1': tool1_status, 'provided_status2': tool2_status, 'provided_status3': tool3_status, 'provided_status4': tool4_status, 'provided_status5': tool5_status}
                warranty_context = {**shared_context, 'motor_warranty': motor_warranty, 'chassis_warranty': chassis_warranty, 'controller_warranty': controller_warranty, 'make': make, 'model': model, 'battery_warranty': battery_warranty}
                # invoice_doc = DocxTemplate("/Users/eagle/Developer/invoiceGen/autoInvoice/templates/invoice_template.docx")
                # invoice_doc.render(invoice_context)
                # invoice_doc.save(f"/Users/eagle/Developer/invoiceGen/autoInvoice/Bills/invoices/{invoice_number}_{customer_name}_Invoice.docx")
                generate_document("/Users/eagle/Developer/invoiceGen/autoInvoice/templates/invoice_template.docx", invoice_context, f"/Users/eagle/Developer/invoiceGen/autoInvoice/Bills/invoices/Buyers#{invoice_number}_{customer_name}_Invoice.docx")
                generate_document("/Users/eagle/Developer/invoiceGen/autoInvoice/templates/invoice_template.docx", invoice_context, f"/Users/eagle/Developer/invoiceGen/autoInvoice/Bills/invoices/Sellers#{invoice_number}_{customer_name}_Invoice.docx")

                generate_document("/Users/eagle/Developer/invoiceGen/autoInvoice/templates/warranty.docx", warranty_context, f"/Users/eagle/Developer/invoiceGen/autoInvoice/Bills/warranty/#{invoice_number}_{customer_name}_Warranty.docx")
                generate_document("/Users/eagle/Developer/invoiceGen/autoInvoice/templates/tools.docx", tools_context, f"/Users/eagle/Developer/invoiceGen/autoInvoice/Bills/tools/#{invoice_number}_{customer_name}_Tools.docx")
                row_delete(selected_chassis_number, battery1, battery2, battery3, battery4)


def row_delete(chassis, battery1, battery2, battery3, battery4):
    try:
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()

        # Delete from inventory table
        cursor.execute("DELETE FROM inventory WHERE chassis_number = ?", (chassis,))
        conn.commit()

        # Delete from battery table
        for battery in [battery1, battery2, battery3, battery4]:
            cursor.execute("DELETE FROM battery WHERE battery_serial_no = ?", (battery,))
            conn.commit()

        st.success("Item removed from the inventory!")
    except sqlite3.Error as e:
        st.error(f"An error occurred: {e.args[0]}")
    finally:
        if conn:
            conn.close()

app()