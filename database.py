import sqlite3
import pandas as pd
import os
import streamlit as st

# กำหนด Path ให้อยู่ที่ Root เสมอ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'staff_v5.db')

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