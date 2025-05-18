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
    logo_file = request.files.get('logo')
    logo_path = None
    if logo_file and logo_file.filename != '':
        filename = secure_filename(logo_file.filename)
        os.makedirs('uploads', exist_ok=True)
        logo_path = os.path.abspath(os.path.join('uploads', filename))
        logo_file.save(logo_path)
    client_data = {
        'company_name': request.form.get('company_name', '').strip(),
        'name': request.form.get('client_name', '').strip(),
        'address': request.form.get('client_address', '').strip(),
        'email': request.form.get('client_email', '').strip(),
        'phone': request.form.get('client_phone', '').strip(),
        'invoice_number': request.form.get('invoice_number', '').strip(),
        'date': request.form.get('invoice_date', '').strip(),
        'due_date': request.form.get('due_date', '').strip(),
        'logo_path': logo_path
    }

    # Optional signature image as base64 data URL
    signature_data_url = request.form.get('signature_data', None)

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
        currency_symbol=currency_symbol,
        signature_data_url=signature_data_url,
        due_date=client_data.get('due_date'),
        due_on_receipt=not bool(client_data.get('due_date'))
    )

    # Save the PDF bytes to the file system
    with open(pdf_path, 'wb') as f:
        f.write(pdf_buffer.read())

    # Serve the PDF as a file download with user-specified filename
    return send_file(pdf_path, as_attachment=True, download_name=filename)


if __name__ == "__main__":
    app.run(debug=True)
