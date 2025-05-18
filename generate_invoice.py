from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import io
import base64
from PIL import Image
import uuid
import qrcode
from datetime import datetime
import os

def generate_qr_code_image(data, size=100):
    qr = qrcode.QRCode(box_size=2, border=1)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    return img

def create_invoice_pdf_bytes(client_data, items, currency_symbol='$', signature_data_url=None,
                             due_on_receipt=True, due_date=None, logo_path=None):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Generate unique invoice ID (UUID4)
    invoice_id = str(uuid.uuid4())

    # Margins
    left_margin = 1 * inch
    right_margin = width - 1 * inch
    top_margin = height - 1 * inch
    bottom_margin = 1 * inch

    # Draw company name - larger and bold, aligned left top
    c.setFont("Helvetica-Bold", 24)
    c.drawString(left_margin, top_margin, client_data.get('company_name', ''))

    # Draw logo if provided and file exists
    if logo_path and os.path.isfile(logo_path):
        try:
            logo_img = Image.open(logo_path)
            max_width = 2 * inch
            max_height = 1 * inch
            logo_width, logo_height = logo_img.size
            aspect = logo_width / logo_height

            # Resize logo maintaining aspect ratio within max dimensions
            if logo_width > max_width or logo_height > max_height:
                if (max_width / aspect) <= max_height:
                    new_width = max_width
                    new_height = max_width / aspect
                else:
                    new_height = max_height
                    new_width = max_height * aspect
                logo_img = logo_img.resize((int(new_width), int(new_height)), Image.Resampling.LANCZOS)
            else:
                new_width, new_height = logo_width, logo_height

            logo_reader = ImageReader(logo_img)
            # Draw logo top-right with 1 inch margin, aligned vertically to company name
            c.drawImage(logo_reader, right_margin - new_width, top_margin - new_height / 2,
                        width=new_width, height=new_height, mask='auto')
        except Exception as e:
            print(f"Error loading logo image: {e}")

    # Draw Invoice title
    c.setFont("Helvetica-Bold", 26)
    c.drawString(left_margin, top_margin - 40, "INVOICE")

    # Invoice ID and Date - right aligned under logo
    c.setFont("Helvetica", 10)
    c.drawRightString(right_margin, top_margin - 15, f"Invoice ID: {invoice_id}")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.drawRightString(right_margin, top_margin - 30, f"Date: {now}")

    # Draw QR code below invoice ID and date
    qr_img = generate_qr_code_image(invoice_id, size=80)
    qr_img_reader = ImageReader(qr_img)
    c.drawImage(qr_img_reader, right_margin - 80, top_margin - 120, width=80, height=80)

    # Draw horizontal line under header
    c.setLineWidth(1)
    c.line(left_margin, top_margin - 130, right_margin, top_margin - 130)

    # Client Information block
    c.setFont("Helvetica-Bold", 14)
    c.drawString(left_margin, top_margin - 150, "Bill To:")
    c.setFont("Helvetica", 12)
    c.drawString(left_margin, top_margin - 170, client_data.get('name', ''))
    c.drawString(left_margin, top_margin - 185, client_data.get('email', ''))
    c.drawString(left_margin, top_margin - 200, client_data.get('address', ''))

    # Payment due info on right side aligned vertically with client info
    c.setFont("Helvetica-Bold", 14)
    c.drawString(right_margin - 200, top_margin - 150, "Payment Details:")
    c.setFont("Helvetica", 12)
    due_text = due_date if due_date else "Due on Receipt"
    c.drawString(right_margin - 200, top_margin - 170, f"Payment Due Date: {due_text}")

    # Draw line separating client/payment details from items table
    c.setLineWidth(0.5)
    c.line(left_margin, top_margin - 215, right_margin, top_margin - 215)

    # Table headers for items
    c.setFont("Helvetica-Bold", 14)
    y = top_margin - 235
    c.drawString(left_margin, y, "Item Description")
    c.drawRightString(left_margin + 3.3 * inch, y, "Quantity")
    c.drawRightString(left_margin + 4.8 * inch, y, "Unit Price")
    c.drawRightString(right_margin, y, "Total")

    # Draw underline for headers
    c.setLineWidth(1)
    c.line(left_margin, y - 5, right_margin, y - 5)

    # Draw items
    c.setFont("Helvetica", 12)
    y -= 20
    total_amount = 0
    for item in items:
        total = item['quantity'] * item['price']
        c.drawString(left_margin, y, item['name'])
        c.drawRightString(left_margin + 3.3 * inch, y, str(item['quantity']))
        # Ensure currency symbol is a string and doesn't cause black fill issues
        c.drawRightString(left_margin + 4.8 * inch, y, f"{currency_symbol}{item['price']:.2f}")
        c.drawRightString(right_margin, y, f"{currency_symbol}{total:.2f}")
        y -= 18
        total_amount += total

    # Draw total amount with emphasis
    y -= 10
    c.setLineWidth(0.8)
    c.line(left_margin + 3.3 * inch, y, right_margin, y)
    y -= 15
    c.setFont("Helvetica-Bold", 16)
    c.drawString(left_margin + 3.3 * inch, y, "Total Amount:")
    c.drawRightString(right_margin, y, f"{currency_symbol}{total_amount:.2f}")

    # Payment due on receipt note
    if due_on_receipt and not due_date:
        y -= 30
        c.setFont("Helvetica-Oblique", 12)
        c.setFillColorRGB(0.5, 0, 0)  # Dark red color for emphasis
        c.drawString(left_margin, y, "Payment Due: Due on Receipt")
        c.setFillColorRGB(0, 0, 0)  # Reset color to black

    # Draw signature block if provided
    if signature_data_url:
        try:
            header, encoded = signature_data_url.split(',', 1)
            signature_bytes = base64.b64decode(encoded)
            image_stream = io.BytesIO(signature_bytes)
            signature_image = Image.open(image_stream).convert("RGBA")

            max_width = 2 * inch
            max_height = 1 * inch
            sig_width, sig_height = signature_image.size
            aspect = sig_width / sig_height

            max_width_px = int(max_width)
            max_height_px = int(max_height)

            if sig_width > max_width_px or sig_height > max_height_px:
                if (max_width_px / aspect) <= max_height_px:
                    sig_width_new = max_width_px
                    sig_height_new = int(max_width_px / aspect)
                else:
                    sig_height_new = max_height_px
                    sig_width_new = int(max_height_px * aspect)
                signature_image = signature_image.resize((sig_width_new, sig_height_new), Image.Resampling.LANCZOS)
                sig_width, sig_height = sig_width_new, sig_height_new

            signature_img_reader = ImageReader(signature_image)
            # Place signature near bottom left above bottom margin
            sig_y = bottom_margin + 40
            c.drawImage(signature_img_reader, left_margin, sig_y, width=sig_width, height=sig_height, mask='auto')

            c.setFont("Helvetica", 10)
            c.drawString(left_margin, sig_y - 15, "Authorized Signature:")

        except Exception as e:
            # skip gracefully if signature decode or render fails
            pass

    # Footer line and page number or company info
    c.setStrokeColorRGB(0.6, 0.6, 0.6)
    c.setLineWidth(0.5)
    c.line(left_margin, bottom_margin + 20, right_margin, bottom_margin + 20)

    c.setFont("Helvetica-Oblique", 8)
    c.setFillColorRGB(0.3, 0.3, 0.3)
    footer_text = client_data.get('company_name', '') + " - Invoice generated by QuickBill"
    c.drawCentredString(width / 2, bottom_margin + 8, footer_text)
    c.setFillColorRGB(0, 0, 0)  # reset to black

    c.save()
    buffer.seek(0)
    return buffer
