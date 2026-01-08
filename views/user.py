import streamlit as st
from database import get_employee_by_email, update_password, update_employee
from utils import generate_temp_password, send_email_mock
from components import render_card_preview

def show_user():
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