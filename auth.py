import bcrypt
from utils.db import get_connection

def authenticate_user(student_id, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT full_name, department, password, role FROM students WHERE student_id=:id", id=student_id)
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        full_name, department, stored_hash, role = row
        if bcrypt.checkpw(password.encode(), stored_hash.encode()):
            return {"name": full_name, "department": department, "role": role}
    return None