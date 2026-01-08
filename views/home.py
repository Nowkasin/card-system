import streamlit as st

def show_home():
    st.title("🏫 ระบบบัตรพนักงานมหาวิทยาลัย")
    st.info("กรุณาเลือกระบบที่ต้องการเข้าใช้งาน")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🔒 สำหรับเจ้าหน้าที่ (Admin)")
        st.write("จัดการข้อมูลพนักงาน ออกบัตรใหม่")
        st.markdown(f'<a href="/?role=admin" target="_self"><button style="background-color:#d32f2f;color:white;padding:10px 20px;border:none;border-radius:5px;cursor:pointer;width:100%;">เข้าสู่ระบบ Admin</button></a>', unsafe_allow_html=True)

    with c2:
        st.subheader("👤 สำหรับพนักงาน (User)")
        st.write("แก้ไขข้อมูลส่วนตัว ดูตัวอย่างบัตร")
        st.markdown(f'<a href="/?role=user" target="_self"><button style="background-color:#1976d2;color:white;padding:10px 20px;border:none;border-radius:5px;cursor:pointer;width:100%;">เข้าสู่ระบบพนักงาน</button></a>', unsafe_allow_html=True)