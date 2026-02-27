import streamlit as st
import oracledb
import bcrypt
import os
from dotenv import load_dotenv
from datetime import datetime
from collections import defaultdict

# Load environment variables (for local testing)
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")

# -----------------------------
# Database Connection
# -----------------------------
def get_connection():
    return oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)

# -----------------------------
# Authentication
# -----------------------------
def create_default_admin():
    """Creates a default admin if not exists"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id='admin01'")
    if not cursor.fetchone():
        # hash password
        hashed = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
        cursor.execute("""
            INSERT INTO students (student_id, password, full_name, department, role)
            VALUES (:id, :pwd, :name, :dept, :role)
        """, id="admin01", pwd=hashed, name="ATSS Admin", dept="All", role="admin")
        conn.commit()
    cursor.close()
    conn.close()

def authenticate_user(student_id, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT full_name, department, password, role 
        FROM students WHERE student_id=:id
    """, id=student_id)
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        full_name, department, stored_hash, role = row
        if bcrypt.checkpw(password.encode(), stored_hash.encode()):
            return {"name": full_name, "department": department, "role": role}
    return None

# -----------------------------
# Chat Functions
# -----------------------------
def save_chat(student_id, message, sender):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chats (student_id, message, sender) 
        VALUES (:id, :msg, :sender)
    """, id=student_id, msg=message, sender=sender)
    conn.commit()
    cursor.close()
    conn.close()

def get_all_chats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT student_id, message, sender, timestamp FROM chats ORDER BY student_id, timestamp")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_chats_by_student(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT message, sender, timestamp FROM chats 
        WHERE student_id=:id ORDER BY timestamp
    """, id=student_id)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="ATSS COLLEGE Chatbot", layout="wide")
st.title("🎓 ATSS COLLEGE Chatbot")

# Initialize default admin on first run
create_default_admin()

# Session state for login
if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.user = None

# -----------------------------
# Login Page
# -----------------------------
if not st.session_state.login:
    st.subheader("Login")
    student_id = st.text_input("Student ID")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = authenticate_user(student_id, password)
        if user:
            st.session_state.login = True
            st.session_state.user = user
        else:
            st.error("Invalid credentials")
else:
    user = st.session_state.user
    st.success(f"Welcome {user['name']}! Role: {user['role']}")

    if user['role'] == "student":
        st.subheader("💬 Chat with the bot")
        chats = get_chats_by_student(user['name'])
        for msg, sender, ts in chats:
            if sender == "student":
                st.markdown(f"**You:** {msg}  _(at {ts})_")
            else:
                st.markdown(f"**Bot:** {msg}  _(at {ts})_")
        message = st.text_input("Type your message here")
        if st.button("Send"):
            if message.strip() != "":
                save_chat(user['name'], message, "student")
                # simple bot response
                bot_reply = f"Hello {user['name']}, you said: {message}"
                save_chat(user['name'], bot_reply, "bot")
                st.experimental_rerun()

    elif user['role'] == "admin":
        st.subheader("🛠 Admin Panel")
        all_chats = get_all_chats()
        chats_by_student = defaultdict(list)
        for sid, msg, sender, ts in all_chats:
            chats_by_student[sid].append((sender, msg, ts))
        for sid, messages in chats_by_student.items():
            with st.expander(f"Student ID: {sid}"):
                for sender, msg, ts in messages:
                    st.markdown(f"**{sender.capitalize()}:** {msg} _(at {ts})_")

        st.subheader("Add New Student")
        new_id = st.text_input("Student ID", key="newid")
        new_name = st.text_input("Full Name", key="newname")
        new_pass = st.text_input("Password", type="password", key="newpass")
        new_dept = st.text_input("Department", key="newdept")
        if st.button("Create Student"):
            if new_id and new_name and new_pass:
                hashed = bcrypt.hashpw(new_pass.encode(), bcrypt.gensalt()).decode()
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO students (student_id, password, full_name, department, role)
                    VALUES (:id, :pwd, :name, :dept, :role)
                """, id=new_id, pwd=hashed, name=new_name, dept=new_dept, role="student")
                conn.commit()
                cursor.close()
                conn.close()
                st.success(f"Student {new_name} created successfully")