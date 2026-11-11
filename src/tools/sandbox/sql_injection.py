import sqlite3

def get_user_profile(user_id: str, db_path: str = "users.db"):
    """
    Retrieves user profile information by user_id.
    Vulnerability: Direct string formatting into SQL query allows SQL Injection (CWE-89).
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Line 12: Insecure string interpolation allows arbitrary SQL execution
    query = f"SELECT id, username, email, role FROM users WHERE user_id = '{user_id}'"
    
    cursor.execute(query)
    record = cursor.fetchone()
    conn.close()
    return record
