import streamlit as st
import pandas as pd
from PIL import Image
from datetime import date
import sqlite3
import io
import os
import base64
import uuid
import qrcode
import barcode
from barcode.writer import ImageWriter
import random
import string

# ==========================================
# 1. SETUP & DATABASE
# ==========================================
st.set_page_config(page_title="HR Card System", layout="wide", page_icon="🆔")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'staff_v5.db') # New Version DB

# --- Admin Configuration ---
ADMIN_PASSWORD = "admin1234"  # <--- กำหนดรหัสผ่านสำหรับเข้าหน้า Admin ที่นี่

def init_db():
    conn = sqlite3.connect(DB_PATH) 
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT,
            emp_id TEXT,
            full_name TEXT,
            position TEXT,
            royal_decoration TEXT,
            department TEXT,
            issue_date TEXT,
            expiry_date TEXT,
            national_id TEXT,
            blood_group TEXT,
            email TEXT UNIQUE,
            password TEXT,
            photo_data BLOB
        )
    ''')
    conn.commit()
    conn.close()

# --- DB Functions ---
def save_new_employee(data_dict, photo_bytes):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO employees (uid, emp_id, full_name, position, royal_decoration, department, issue_date, expiry_date, national_id, blood_group, email, password, photo_data)
            VALUES (:uid, :emp_id, :full_name, :position, :royal_decoration, :department, :issue_date, :expiry_date, :national_id, :blood_group, :email, :password, :photo_data)
        ''', {**data_dict, 'photo_data': photo_bytes})
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def update_employee(uid, data_dict, photo_bytes=None):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        if photo_bytes:
            c.execute('''
                UPDATE employees SET 
                full_name=:full_name, position=:position, royal_decoration=:royal_decoration, 
                department=:department, blood_group=:blood_group, photo_data=:photo_data
                WHERE uid=:uid
            ''', {**data_dict, 'photo_data': photo_bytes, 'uid': uid})
        else:
            c.execute('''
                UPDATE employees SET 
                full_name=:full_name, position=:position, royal_decoration=:royal_decoration, 
                department=:department, blood_group=:blood_group
                WHERE uid=:uid
            ''', {**data_dict, 'uid': uid})
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Update Error: {e}")
        return False

def get_employee_by_email(email):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM employees WHERE email=?", (email,))
    row = c.fetchone()
    conn.close()
    return row

def update_password(email, new_password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE employees SET password=? WHERE email=?", (new_password, email))
    conn.commit()
    conn.close()

def get_all_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT id, emp_id, full_name, email, department, position FROM employees", conn)
    conn.close()
    return df

# ==========================================
# 2. UTILS
# ==========================================
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

# ==========================================
# 3. CARD RENDERER
# ==========================================
def render_card_preview(data, photo_bytes):
    b64_photo = None
    if photo_bytes:
        b64_photo = base64.b64encode(photo_bytes).decode()
    
    qr_url = f"https://univ-verify.com/check?uid={data['uid']}"
    b64_qr = get_qr_base64(qr_url)
    b64_bc = get_barcode_base64(data['national_id'])
    
    photo_html = f'<img src="data:image/png;base64,{b64_photo}">' if b64_photo else '<div style="padding-top:50px;color:#ccc;">NO PHOTO</div>'
    qr_html = f'<img src="data:image/png;base64,{b64_qr}">' if b64_qr else ""
    bc_html = f'<img src="data:image/png;base64,{b64_bc}">' if b64_bc else ""
    royal_html = f'<div class="c-royal">🎖️ {data["royal_decoration"]}</div>' if data['royal_decoration'] != "-" else ""

    st.markdown("""
    <style>
        .card-box {
            width: 300px; height: 480px; background: white; border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.15); border: 1px solid #e0e0e0;
            overflow: hidden; font-family: sans-serif; position: relative; display: flex; flex-direction: column;
        }
        .c-header { height: 50px; background: #d32f2f; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 16px; }
        .c-footer { height: 20px; background: #d32f2f; margin-top: auto; }
        .c-logo { text-align: center; margin-top: -25px; margin-bottom: 5px; z-index: 2; }
        .c-logo img { width: 60px; height: 60px; background: white; border-radius: 50%; padding: 3px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .c-photo { width: 120px; height: 150px; background: #f5f5f5; margin: 5px auto; border: 2px solid #d32f2f; border-radius: 4px; overflow: hidden; display: flex; justify-content: center; }
        .c-photo img { width: 100%; height: 100%; object-fit: cover; }
        .c-body { text-align: center; padding: 5px; color: #333; }
        .c-name { font-size: 18px; font-weight: bold; color: #d32f2f; }
        .c-pos { font-size: 15px; font-weight: bold; margin-bottom: 5px; }
        .c-royal { color: #b8860b; font-size: 13px; font-weight: bold; margin-bottom: 5px; }
        .c-meta { font-size: 13px; color: #666; }
        .c-qr { position: absolute; bottom: 30px; right: 10px; width: 45px; height: 45px; background: white; padding: 2px; }
        .c-qr img { width: 100%; }
        .c-back-content { padding: 20px; text-align: left; font-size: 13px; }
        .c-row { display: flex; justify-content: space-between; border-bottom: 1px dashed #eee; padding: 6px 0; }
        .lbl { font-weight: bold; color: #d32f2f; }
        .c-bc { text-align: center; margin-top: 20px; }
        .c-bc img { height: 40px; max-width: 90%; }
    </style>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
<div class="card-box">
<div class="c-header">UNIVERSITY STAFF</div>
<div class="c-logo"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Srinakharinwirot_University_Logo.svg/1200px-Srinakharinwirot_University_Logo.svg.png"></div>
<div class="c-photo">{photo_html}</div>
<div class="c-body">
<div class="c-name">{data['full_name']}</div>
<div class="c-pos">{data['position']}</div>
{royal_html}
<div class="c-meta">ID: {data['emp_id']}</div>
<div class="c-meta">{data['department']}</div>
</div>
<div class="c-qr">{qr_html}</div>
<div class="c-footer"></div>
</div>
        """, unsafe_allow_html=True)
    
    with c2:
        st.markdown(f"""
<div class="card-box">
<div class="c-header">OFFICIAL DOCUMENT</div>
<div class="c-back-content">
<div class="c-row"><span class="lbl">UID:</span> <span>{data['uid'][:8]}...</span></div>
<div class="c-row"><span class="lbl">ID Card:</span> <span>{data['national_id']}</span></div>
<div class="c-row"><span class="lbl">Blood:</span> <span>{data['blood_group']}</span></div>
<div class="c-row"><span class="lbl">Issue:</span> <span>{data['issue_date']}</span></div>
<div class="c-row"><span class="lbl">Expiry:</span> <span>{data['expiry_date']}</span></div>
<div class="c-bc">{bc_html}</div>
</div>
<div class="c-footer"></div>
</div>
        """, unsafe_allow_html=True)

# ==========================================
# 4. PAGE ROUTING LOGIC
# ==========================================
init_db()

# อ่านค่า Parameter จาก URL (เช่น /?role=admin หรือ /?role=user)
query_params = st.query_params
role = query_params.get("role", "home") # Default is home

# --- หน้า ADMIN ---
if role == "admin":
    st.title("🔒 Admin Panel (เจ้าหน้าที่ฝ่ายบุคคล)")
    
    if "admin_authed" not in st.session_state:
        st.session_state.admin_authed = False

    if not st.session_state.admin_authed:
        pwd = st.text_input("กรุณาใส่รหัสผ่าน Admin", type="password")
        if st.button("เข้าสู่ระบบ Admin"):
            if pwd == ADMIN_PASSWORD:
                st.session_state.admin_authed = True
                st.rerun()
            else:
                st.error("รหัสผ่านไม่ถูกต้อง")
    else:
        # Admin Dashboard Content
        if st.button("ออกจากระบบ (Logout)"):
            st.session_state.admin_authed = False
            st.rerun()
            
        st.header("📝 ลงทะเบียนพนักงานใหม่")
        with st.form("admin_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                uid = str(uuid.uuid4())
                emp_id = st.text_input("รหัสพนักงาน", "67001")
                title = st.selectbox("คำนำหน้า", ["นาย", "นาง", "นางสาว", "ดร.", "ผศ."])
                fname = st.text_input("ชื่อ", "รักเรียน")
                lname = st.text_input("นามสกุล", "เพียรศึกษา")
                position = st.text_input("ตำแหน่ง", "เจ้าหน้าที่")
                email = st.text_input("อีเมล (สำหรับ Login)", "staff@univ.ac.th")
            
            with col_b:
                dept = st.text_input("สังกัด/คณะ", "คณะวิศวกรรมศาสตร์")
                nid = st.text_input("เลขบัตรประชาชน", "1234567890123")
                blood = st.selectbox("กลุ่มเลือด", ["A", "B", "AB", "O"])
                royal = st.selectbox("เครื่องราชฯ", ["-", "บ.ม.", "บ.ช.", "จ.ม.", "จ.ช."])
                issued = st.date_input("วันออกบัตร", date.today())
                expired = st.date_input("วันหมดอายุ", date(date.today().year+5, date.today().month, date.today().day))
                photo_file = st.file_uploader("รูปถ่ายพนักงาน", type=['jpg', 'png'])

            submit_new = st.form_submit_button("บันทึกข้อมูลพนักงาน")
        
        if submit_new:
            if not email:
                st.error("กรุณาระบุอีเมล")
            else:
                p_blob = photo_file.getvalue() if photo_file else None
                full_n = f"{title}{fname} {lname}"
                data = {
                    'uid': uid, 'emp_id': emp_id, 'full_name': full_n, 'position': position,
                    'royal_decoration': royal, 'department': dept, 
                    'issue_date': str(issued), 'expiry_date': str(expired),
                    'national_id': nid, 'blood_group': blood, 'email': email, 'password': None 
                }
                if save_new_employee(data, p_blob):
                    st.success(f"✅ บันทึกข้อมูล {full_n} เรียบร้อย!")

        st.divider()
        st.write("📂 รายชื่อพนักงานทั้งหมด")
        st.dataframe(get_all_data(), use_container_width=True)

# --- หน้า USER (Employee) ---
elif role == "user":
    st.title("👤 Employee Portal (พนักงาน)")
    
    if 'user_session' not in st.session_state:
        st.session_state.user_session = None

    # Login Flow
    if st.session_state.user_session is None:
        tab_login, tab_forgot = st.tabs(["เข้าสู่ระบบ", "ลืมรหัสผ่าน / ขอรหัสผ่าน"])
        
        with tab_login:
            l_email = st.text_input("อีเมล")
            l_pwd = st.text_input("รหัสผ่าน", type="password")
            if st.button("Login"):
                user = get_employee_by_email(l_email)
                if user and user['password'] == l_pwd:
                    st.session_state.user_session = dict(user)
                    st.success("Login สำเร็จ!")
                    st.rerun()
                else:
                    st.error("อีเมลหรือรหัสผ่านไม่ถูกต้อง")
        
        with tab_forgot:
            req_email = st.text_input("กรอกอีเมลเพื่อรับรหัสผ่าน")
            if st.button("ส่งรหัสผ่าน"):
                user = get_employee_by_email(req_email)
                if user:
                    new_pwd = generate_temp_password()
                    update_password(req_email, new_pwd)
                    send_email_mock(req_email, new_pwd)
                else:
                    st.error("ไม่พบอีเมลในระบบ")

    # Employee Dashboard
    else:
        user = st.session_state.user_session
        st.success(f"สวัสดี, {user['full_name']}")
        
        col_edit, col_preview = st.columns([1, 1.5])
        
        with col_edit:
            st.subheader("✏️ แก้ไขข้อมูล")
            with st.form("edit_form"):
                e_name = st.text_input("ชื่อ-สกุล", user['full_name'])
                e_pos = st.text_input("ตำแหน่ง", user['position'])
                e_dept = st.text_input("สังกัด", user['department'])
                e_royal = st.selectbox("เครื่องราชฯ", ["-", "บ.ม.", "บ.ช.", "จ.ม.", "จ.ช."], index=0)
                
                bg_options = ["A", "B", "AB", "O"]
                try: bg_index = bg_options.index(user['blood_group'])
                except: bg_index = 0
                e_blood = st.selectbox("กลุ่มเลือด", bg_options, index=bg_index)
                
                new_photo = st.file_uploader("เปลี่ยนรูปถ่าย", type=['jpg', 'png'])
                
                btn_preview = st.form_submit_button("👁️ พรีวิวบัตร")
                btn_save = st.form_submit_button("💾 บันทึก")

            if st.button("Logout"):
                st.session_state.user_session = None
                st.rerun()

        # Logic
        current_photo_bytes = user['photo_data']
        if new_photo: current_photo_bytes = new_photo.getvalue()
        
        updated_data = {
            'uid': user['uid'], 'full_name': e_name, 'position': e_pos, 'royal_decoration': e_royal,
            'department': e_dept, 'blood_group': e_blood, 'emp_id': user['emp_id'],
            'national_id': user['national_id'], 'issue_date': user['issue_date'], 'expiry_date': user['expiry_date']
        }

        with col_preview:
            st.subheader("บัตรประจำตัว")
            render_card_preview(updated_data, current_photo_bytes)
            
            if btn_save:
                p_blob = new_photo.getvalue() if new_photo else None
                if update_employee(user['uid'], updated_data, p_blob):
                    st.toast("✅ บันทึกเรียบร้อย")
                    new_user_data = get_employee_by_email(user['email'])
                    st.session_state.user_session = dict(new_user_data)
                    st.rerun()

# --- หน้า HOME (Landing Page) ---
else:
    st.title("🏫 ระบบบัตรพนักงานมหาวิทยาลัย")
    st.info("กรุณาเลือกระบบที่ต้องการเข้าใช้งาน")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🔒 สำหรับเจ้าหน้าที่ (Admin)")
        st.write("จัดการข้อมูลพนักงาน ออกบัตรใหม่")
        # ใช้ markdown link เพื่อเปลี่ยน URL query param
        st.markdown(f'<a href="/?role=admin" target="_self"><button style="background-color:#d32f2f;color:white;padding:10px 20px;border:none;border-radius:5px;cursor:pointer;width:100%;">เข้าสู่ระบบ Admin</button></a>', unsafe_allow_html=True)

    with c2:
        st.subheader("👤 สำหรับพนักงาน (User)")
        st.write("แก้ไขข้อมูลส่วนตัว ดูตัวอย่างบัตร")
        st.markdown(f'<a href="/?role=user" target="_self"><button style="background-color:#1976d2;color:white;padding:10px 20px;border:none;border-radius:5px;cursor:pointer;width:100%;">เข้าสู่ระบบพนักงาน</button></a>', unsafe_allow_html=True)