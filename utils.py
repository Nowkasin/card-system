import string
import random
import io
import base64
import qrcode
import barcode
from barcode.writer import ImageWriter
import streamlit as st

def generate_temp_password(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for i in range(length))

def send_email_mock(to_email, password):
    st.toast(f"📨 Email Sent to {to_email}", icon="📧")
    st.info(f"🔑 [จำลองระบบอีเมล] รหัสผ่านของคุณคือ: **{password}**")

def get_qr_base64(data):
    qr = qrcode.QRCode(version=1, box_size=5, border=1)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def get_barcode_base64(value):
    if not value: return None
    try:
        code128 = barcode.get_barcode_class('code128')
        rv = io.BytesIO()
        writer = ImageWriter()
        code128(value, writer=writer).write(rv, options={"write_text": True, "module_height": 8.0, "font_size": 6, "quiet_zone": 1.0})
        rv.seek(0)
        return base64.b64encode(rv.getvalue()).decode()
    except: return None

def load_font_as_base64(font_path):
    """อ่านไฟล์ Font และแปลงเป็น Base64 string"""
    try:
        with open(font_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None