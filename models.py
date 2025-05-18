from flask_sqlalchemy import SQLAlchemy
import datetime
import uuid

db = SQLAlchemy()

class InvoiceClient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(250), nullable=True)

    invoices = db.relationship('InvoiceItem', backref='client', lazy=True)

class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('invoice_client.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)



def generate_uuid():
    return str(uuid.uuid4())

class InvoiceClient(db.Model):
    
    __tablename__ = 'invoice_client'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(255))
    name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    address = db.Column(db.Text)
    logo_path = db.Column(db.String(255))  # store logo file path or URL

class InvoiceItem(db.Model):
    __tablename__ = 'invoice_item'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.String(36), db.ForeignKey('invoice.invoice_uuid'))
    name = db.Column(db.String(255))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)

class Invoice(db.Model):
    __tablename__ = 'invoice'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    invoice_uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    client_id = db.Column(db.Integer, db.ForeignKey('invoice_client.id'))
    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    payment_terms = db.Column(db.String(100), default="Due on receipt")
    currency = db.Column(db.String(10), default="USD")  # currency code, e.g. USD, EUR

