from utils.db import get_connection

def save_chat(student_id, message, sender):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chats (student_id, message, sender) VALUES (:id, :msg, :sender)",
        id=student_id, msg=message, sender=sender
    )
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