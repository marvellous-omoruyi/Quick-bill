from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
from io import BytesIO
import base64
from PIL import Image
import uuid
import qrcode
from datetime import datetime
import os

# Register Unicode font
pdfmetrics.registerFont(TTFont('DejaVu', 'fonts/DejaVuSans.ttf'))

def generate_qr_code_image(data, size=100):
    qr = qrcode.QRCode(box_size=2, border=1)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    return img

def create_invoice_pdf_bytes(client_data, items, comp_bytes=None, currency_symbol='$', signature_bytes=None,
                             due_on_receipt=True, due_date=None, logo_path=None):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    left_margin = 1 * inch
    right_margin = width - 1 * inch
    top_margin = height - 1 * inch
    bottom_margin = 1 * inch

    c.setFont("DejaVu", 24)
    c.drawString(left_margin, top_margin, client_data.get('company_name', ''))
    logo_drawn_height = 0
    if comp_bytes:
        try:
            comp_img = Image.open(BytesIO(comp_bytes))
            comp_img_reader = ImageReader(comp_img)
            img_width, img_height = comp_img.size
            max_width = 2 * inch
            max_height = 1 * inch
            if img_width > max_width or img_height > max_height:
                aspect = img_width / img_height
                if (max_width / aspect) <= max_height:
                    new_width = max_width
                    new_height = max_width / aspect
                else:
                    new_height = max_height
                    new_width = max_height * aspect
                comp_img = comp_img.resize((int(new_width), int(new_height)))
                img_width, img_height = comp_img.size
                comp_img_reader = ImageReader(comp_img)
            x = right_margin - img_width
            y = top_margin - img_height + 20
            c.drawImage(comp_img_reader, x, y, width=img_width, height=img_height, mask='auto')
            logo_drawn_height = img_height
        except Exception as e:
            print("Error loading company logo:", e)

    c.setFont("DejaVu", 26)
    c.drawString(left_margin, top_margin - 40, "INVOICE")

    info_y = top_margin - 70
    qr_img = generate_qr_code_image(client_data.get('invoice_number', '') or "INV", size=40)
    qr_img_reader = ImageReader(qr_img)
    c.drawImage(qr_img_reader, left_margin, info_y - 10, width=40, height=40)
    c.setFont("DejaVu", 10)
    c.setFillColorRGB(0.2, 0.2, 0.2)
    invoice_id = client_data.get('invoice_number', '') or str(uuid.uuid4())
    c.drawString(left_margin + 50, info_y + 10, f"Invoice ID: {invoice_id}")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.drawString(left_margin + 50, info_y - 5, f"Date: {now}")
    c.setFillColorRGB(0, 0, 0)

    c.setLineWidth(1)
    c.line(left_margin, top_margin - 95, right_margin, top_margin - 95)

    c.setFont("DejaVu", 12)
    c.drawString(left_margin, top_margin - 110, "Bill To:")
    c.setFont("DejaVu", 11)
    c.drawString(left_margin, top_margin - 125, client_data.get('name', ''))
    c.drawString(left_margin, top_margin - 140, client_data.get('address', ''))
    c.drawString(left_margin, top_margin - 155, client_data.get('email', ''))
    c.drawString(left_margin, top_margin - 170, client_data.get('phone', ''))

    c.setFont("DejaVu", 12)
    c.drawString(right_margin - 180, top_margin - 110, "Payment Details:")
    c.setFont("DejaVu", 11)
    due_text = due_date if due_date else "Due on Receipt"
    c.drawString(right_margin - 180, top_margin - 125, f"Payment Due Date: {due_text}")

    c.setLineWidth(0.5)
    c.line(left_margin, top_margin - 185, right_margin, top_margin - 185)

    c.setFont("DejaVu", 12)
    y = top_margin - 200
    c.drawString(left_margin, y, "Item Description")
    c.drawRightString(left_margin + 3.3 * inch, y, "Quantity")
    c.drawRightString(left_margin + 4.8 * inch, y, "Unit Price")
    c.drawRightString(right_margin, y, "Total")
    c.setLineWidth(0.5)
    c.line(left_margin, y - 5, right_margin, y - 5)
    c.setFont("DejaVu", 11)
    y -= 20
    total_amount = 0
    for item in items:
        total = item['quantity'] * item['price']
        c.drawString(left_margin, y, item['name'])
        c.drawRightString(left_margin + 3.3 * inch, y, str(item['quantity']))
        c.drawRightString(left_margin + 4.8 * inch, y, f"{currency_symbol}{item['price']:.2f}")
        c.drawRightString(right_margin, y, f"{currency_symbol}{total:.2f}")
        y -= 18
        total_amount += total

    y -= 10
    c.setLineWidth(0.8)
    c.line(left_margin + 3.3 * inch, y, right_margin, y)
    y -= 15
    c.setFont("DejaVu", 14)
    c.drawString(left_margin + 3.3 * inch, y, "Total Amount:")
    c.drawRightString(right_margin, y, f"{currency_symbol}{total_amount:.2f}")

    if due_on_receipt and not due_date:
        y -= 30
        c.setFont("DejaVu", 12)
        c.setFillColorRGB(0.5, 0, 0)
        c.drawString(left_margin, y, "Payment Due: Due on Receipt")
        c.setFillColorRGB(0, 0, 0)

    if signature_bytes:
        try:
            signature_img = Image.open(BytesIO(signature_bytes))
            sig_width, sig_height = signature_img.size
            max_width = 2 * inch
            max_height = 1 * inch
            if sig_width > max_width or sig_height > max_height:
                aspect = sig_width / sig_height
                if (max_width / aspect) <= max_height:
                    new_width = max_width
                    new_height = max_width / aspect
                else:
                    new_height = max_height
                    new_width = max_height * aspect
                signature_img = signature_img.resize((int(new_width), int(new_height)))
                sig_width, sig_height = signature_img.size
            signature_img_reader = ImageReader(signature_img)
            sig_y = bottom_margin + 60
            c.drawImage(signature_img_reader, left_margin, sig_y, width=sig_width, height=sig_height, mask='auto')
            c.setFont("DejaVu", 10)
            c.drawString(left_margin, sig_y - 15, "Authorized Signature:")
        except Exception as e:
            pass

    c.setStrokeColorRGB(0.6, 0.6, 0.6)
    c.setLineWidth(0.5)
    c.line(left_margin, bottom_margin + 20, right_margin, bottom_margin + 20)
    c.setFont("DejaVu", 8)
    c.setFillColorRGB(0.3, 0.3, 0.3)
    footer_text = client_data.get('company_name', '') + " - Invoice generated by QuickBill"
    c.drawCentredString(width / 2, bottom_margin + 8, footer_text)
    c.setFillColorRGB(0, 0, 0)

    c.save()
    buffer.seek(0)
    return buffer
