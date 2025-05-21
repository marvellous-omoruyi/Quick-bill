from flask import Flask, render_template, request, send_file, abort
from werkzeug.utils import secure_filename
from models import db
from generate_invoice import create_invoice_pdf_bytes  # Using bytes version only

import os
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quickbill.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your-secret-key'

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_invoice', methods=['POST'])
def generate_invoice():
    # Extract client info from form data
    client_data = {
        'company_name': request.form.get('company_name', '').strip(),
        
        'name': request.form.get('client_name', '').strip(),
        'address': request.form.get('client_address', '').strip(),
        'email': request.form.get('client_email', '').strip(),
        'phone': request.form.get('client_phone', '').strip(),
        'invoice_number': request.form.get('invoice_number', '').strip(),
        'date': request.form.get('invoice_date', '').strip(),
        'due_date': request.form.get('due_date', '').strip(),
    }

    # Optional signature image as base64 data URL
    signature_data_url = request.form.get('signature_data', None)
    signature_file = request.files.get('signature_image', None)

    signature_bytes = None
    if signature_file and signature_file.filename != '':
        signature_bytes = signature_file.read()
    elif signature_data_url:
        import base64
        header, encoded = signature_data_url.split(',', 1)
        signature_bytes = base64.b64decode(encoded)
    comp_data_url = request.form.get('comp_data', None)
    comp_file = request.files.get('comp_image', None)

    comp_bytes = None
    if comp_file and comp_file.filename != '':
        comp_bytes = comp_file.read()
    elif comp_data_url:
        import base64
        header, encoded = comp_data_url.split(',', 1)
        comp_bytes = base64.b64decode(encoded)

    print("Signature bytes present:", comp_bytes is not None and len(comp_bytes) > 0)

    # Extract invoice items from form data
    item_names = request.form.getlist('item_name')
    item_qtys = request.form.getlist('item_qty')
    item_prices = request.form.getlist('item_price')

    # Filename for the downloaded PDF
    filename = request.form.get('filename', 'invoice.pdf').strip()
    if not filename.lower().endswith('.pdf'):
        filename += '.pdf'

    # Currency symbol defaulting to '$'
    currency_symbol = request.form.get('currency', '$').strip() or '$'

    # Validate and build list of items
    items = []
    for name, qty, price in zip(item_names, item_qtys, item_prices):
        if not (name and qty and price):
            continue
        try:
            items.append({
                'name': name,
                'quantity': int(qty),
                'price': float(price),
            })
        except ValueError:
            continue

    if not items:
        return abort(400, "No valid invoice items provided.")

    # Create invoices directory if it doesn't exist
    os.makedirs('invoices', exist_ok=True)

    # Generate unique invoice ID (UUID4)
    invoice_id = str(uuid.uuid4())

    # Define the path where PDF will be saved
    pdf_path = os.path.join('invoices', f'invoice_{invoice_id}.pdf')

    # Generate the invoice PDF bytes buffer
    pdf_buffer = create_invoice_pdf_bytes(
        
        client_data,
        items,
        comp_bytes=comp_bytes,
        currency_symbol=currency_symbol,
        signature_bytes=signature_bytes,  # <-- update your function to accept this
        due_date=client_data.get('due_date'),
        due_on_receipt=not bool(client_data.get('due_date'))
    )

    # Save the PDF bytes to the file system
    with open(pdf_path, 'wb') as f:
        f.write(pdf_buffer.read())

    # Serve the PDF as a file download with user-specified filename
    return send_file(pdf_path, as_attachment=True, download_name=filename)


import webbrowser
import threading
import base64  # move to global imports

if __name__ == "__main__":
    def open_browser():
        webbrowser.open_new("http://127.0.0.1:5000")

    threading.Timer(1.25, open_browser).start()
    app.run(debug=True)
