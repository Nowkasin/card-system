import streamlit as st
import uuid
from datetime import date
from database import save_new_employee, get_all_data

ADMIN_PASSWORD = "admin1234"

def show_admin():
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