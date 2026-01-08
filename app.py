import streamlit as st
from database import init_db
from views.admin import show_admin
from views.user import show_user
from views.home import show_home

# 1. SETUP
st.set_page_config(page_title="HR Card System", layout="wide", page_icon="🆔")
init_db()

# 2. ROUTING LOGIC
query_params = st.query_params
role = query_params.get("role", "home") # Default is home

if role == "admin":
    show_admin()
elif role == "user":
    show_user()
else:
    show_home()