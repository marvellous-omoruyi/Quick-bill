# QuickBill - Invoice Generator

QuickBill is a simple web application for generating professional PDF invoices. Users can enter company and client details, add invoice items, select currency, upload a company logo, sign digitally, and download the invoice as a PDF.

## Features

- Add your company and client information
- Upload your company logo (image will appear on the invoice)
- Add multiple invoice items (name, quantity, price)
- Select currency symbol
- Draw and include a digital signature
- Set payment due date
- Download the generated invoice as a PDF

## Requirements

- Python 3.8+
- Flask
- Flask-SQLAlchemy
- Pillow
- reportlab
- qrcode

## Installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/yourusername/quickbill.git
   cd quickbill
   ```

2. **Install dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

3. **Run the application:**

   ```sh
   python app.py
   ```

4. **Open your browser and go to:**

   ```text
   http://127.0.0.1:5000/
   ```

## Usage

1. Fill in your company and client details.
2. Add invoice items (you can add or remove items).
3. Select your preferred currency.
4. Upload your company logo (optional, but recommended for branding).
5. Draw your signature in the signature box.

## Project Structure

```text
Quick bill/
├── app.py
├── generate_invoice.py
├── models.py
├── requirements.txt
├── templates/
│   └── index.html
├── static/
│   └── style.css
├── uploads/
├── invoices/
```text
├── uploads/
├── invoices/
```

- `app.py`: Main Flask application.
- `generate_invoice.py`: PDF generation logic.
- `models.py`: Database models (if used).
- `templates/index.html`: Main web form.
- `static/style.css`: Stylesheet.
- `uploads/`: Uploaded logos.
- `invoices/`: Generated PDF invoices.

## Notes

- Uploaded logos are stored in the `uploads/` directory.
- Generated invoices are saved in the `invoices/` directory.
- Make sure the `uploads/` and `invoices/` folders are writable.

## License

## MIT License

**Enjoy using QuickBill!**

---

**Enjoy using QuickBill!**
