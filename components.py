import streamlit as st
import base64
import os
from utils import get_qr_base64, get_barcode_base64, load_font_as_base64

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

    # โหลดฟอนต์
    base_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(base_dir, 'assets', 'THSarabunNew.ttf') # เช็ค Path ให้ถูก
    font_b64 = load_font_as_base64(font_path)

    # สร้าง CSS Font Face
    font_face_css = ""
    font_family_name = "sans-serif" # ค่า Default

    if font_b64:
        font_family_name = "THSarabunNew"
        font_face_css = f"""
        @font-face {{
            font-family: 'THSarabunNew';
            src: url(data:font/ttf;base64,{font_b64}) format('truetype');
        }}
        """

    # แทรก CSS
    st.markdown(f"""
    <style>
        {font_face_css} /* แทรก @font-face ตรงนี้ */

        .card-box {{
            width: 300px; height: 480px; background: white; border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.15); border: 1px solid #e0e0e0;
            overflow: hidden; 
            font-family: '{font_family_name}', sans-serif; /* เรียกใช้ฟอนต์ที่นี่ */
            position: relative; display: flex; flex-direction: column;
        }}
        
        /* ... (CSS Class อื่นๆ เหมือนเดิม) ... */
        .c-header {{ height: 50px; background: #d32f2f; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 20px; }} /* ปรับ font-size ขึ้นหน่อยเพราะสารบัญตัวเล็ก */
        .c-footer {{ height: 20px; background: #d32f2f; margin-top: auto; }}
        .c-logo {{ text-align: center; margin-top: -25px; margin-bottom: 5px; z-index: 2; }}
        .c-logo img {{ width: 60px; height: 60px; background: white; border-radius: 50%; padding: 3px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .c-photo {{ width: 120px; height: 150px; background: #f5f5f5; margin: 5px auto; border: 2px solid #d32f2f; border-radius: 4px; overflow: hidden; display: flex; justify-content: center; }}
        .c-photo img {{ width: 100%; height: 100%; object-fit: cover; }}
        .c-body {{ text-align: center; padding: 5px; color: #333; }}
        
        /* ปรับขนาด Font ให้เหมาะสมกับ TH Sarabun */
        .c-name {{ font-size: 24px; font-weight: bold; color: #d32f2f; line-height: 1.1; }}
        .c-pos {{ font-size: 20px; font-weight: bold; margin-bottom: 5px; }}
        .c-royal {{ color: #b8860b; font-size: 18px; font-weight: bold; margin-bottom: 5px; }}
        .c-meta {{ font-size: 16px; color: #666; }}
        
        .c-qr {{ position: absolute; bottom: 30px; right: 10px; width: 45px; height: 45px; background: white; padding: 2px; }}
        .c-qr img {{ width: 100%; }}
        .c-back-content {{ padding: 20px; text-align: left; font-size: 16px; }}
        .c-row {{ display: flex; justify-content: space-between; border-bottom: 1px dashed #eee; padding: 6px 0; }}
        .lbl {{ font-weight: bold; color: #d32f2f; }}
        .c-bc {{ text-align: center; margin-top: 20px; }}
        .c-bc img {{ height: 40px; max-width: 90%; }}
    </style>
    """, unsafe_allow_html=True)

    # ส่วน render HTML c1, c2
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
            <div class="card-box">
            <div class="c-header">มหาวิทยาลัยศรีนครินทรวิโรฒ</div> <div class="c-logo"><img src="https://upload.wikimedia.org/wikipedia/commons/2/2c/Logo_of_Srinakharinwirot_University-EN.svg"></div>
            <div class="c-photo">{photo_html}</div>
            <div class="c-body">
            <div class="c-name">{data['full_name']}</div>
            <div class="c-pos">{data['position']}</div>
            {royal_html}
            <div class="c-meta">รหัส: {data['emp_id']}</div>
            <div class="c-meta">{data['department']}</div>
            </div>
            <div class="c-qr">{qr_html}</div>
            <div class="c-footer"></div>
            </div>
                    """, unsafe_allow_html=True)
    
    with c2:
        st.markdown(f"""
            <div class="card-box">
            <div class="c-header">เอกสารราชการ</div>
            <div class="c-back-content">
            <div class="c-row"><span class="lbl">UID:</span> <span>{data['uid'][:8]}...</span></div>
            <div class="c-row"><span class="lbl">เลข ปชช.:</span> <span>{data['national_id']}</span></div>
            <div class="c-row"><span class="lbl">กรุ๊ปเลือด:</span> <span>{data['blood_group']}</span></div>
            <div class="c-row"><span class="lbl">วันออกบัตร:</span> <span>{data['issue_date']}</span></div>
            <div class="c-row"><span class="lbl">วันหมดอายุ:</span> <span>{data['expiry_date']}</span></div>
            <div class="c-bc">{bc_html}</div>
            </div>
            <div class="c-footer"></div>
            </div>
                    """, unsafe_allow_html=True)