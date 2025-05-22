# QuickBill - Invoice Generator

QuickBill is a modern web application for generating professional PDF invoices. Enter your company and client details, add invoice items, select currency, upload your logo, sign digitally, and download a ready-to-send invoice PDF.

You can use QuickBill as a web app, a PWA (installable on your device), or as a standalone Windows executable.

---

## 🚀 Features

- Enter company and client information
- Upload your company logo (appears on the invoice)
- Add, edit, or remove multiple invoice items (name, quantity, price)
- Choose your preferred currency symbol
- Draw or upload a digital signature
- Set a payment due date
- Download the invoice as a PDF
- **PWA:** Install on your device for offline use
- **Windows .exe:** Use as a standalone desktop app

---

## 🛠️ Requirements

- Python 3.8 or higher (for running from source)
- Flask, Flask-SQLAlchemy, Pillow, reportlab, qrcode (see `requirements.txt`)
- Or use the provided `.exe` file (no Python needed)

---

## ⚡ Getting Started

### 1. **Use Online (Recommended)**

Just visit:

👉 [https://quick-bill.onrender.com](https://quick-bill.onrender.com)

- Works on any device with a browser.
- Install as a PWA for offline access (look for "Install App" in your browser).

---

### 2. **Use the Windows Executable**

- Download the `.exe` file from the `dist` folder or from the [Releases](https://github.com/marvellous-omoruyi/Quick-bill/releases) page (if available).
- Double-click to run.  
   No Python or setup required!

---

### 3. **Run Locally from Source**

1. **Clone the repository:**

    ```sh
    git clone https://github.com/marvellous-omoruyi/Quick-bill.git
    cd Quick-bill
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

---

## 🌐 Accessing the App

- **Online:** [https://quick-bill.onrender.com](https://quick-bill.onrender.com)
- **Local:** [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
- **LAN:** Run with `python app.py --host=0.0.0.0` and access from other devices on your network.
- **PWA:** Install from your browser for offline use.
- **Windows:** Use the `.exe` in the `dist` folder.

---

## 📝 Usage Guide

1. Fill in your company and client details.
2. Add invoice items (use the "Add Item" button for more lines).
3. Select your preferred currency.
4. Upload your company logo (optional, but recommended for branding).
5. Draw your signature in the signature box or upload a signature image.
6. Set the payment due date.
7. Click **Generate Invoice PDF** to download your invoice.

---

## 📁 Project Structure

```text
Quick bill/
├── app.py                  # Main Flask application
├── generate_invoice.py     # PDF generation logic
├── models.py               # Database models (if used)
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html          # Main web form
├── static/
│   ├── style.css           # Stylesheet
│   └── ...                 # Other static files (icons, JS, etc.)
├── uploads/                # Uploaded logos
├── invoices/               # Generated PDF invoices
├── dist/                   # Windows executable (.exe)
```

---

## 📌 Notes

- Uploaded logos are stored in the `uploads/` directory.
- Generated invoices are saved in the `invoices/` directory.
- Make sure the `uploads/` and `invoices/` folders are writable if running locally.

---

## 📄 License

MIT License

---

**Enjoy using QuickBill!**
