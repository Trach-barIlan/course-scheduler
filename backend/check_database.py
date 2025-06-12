import sqlite3
import os
from datetime import datetime

def check_database():
    db_path = "users.db"
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return
    
    print("✅ Database file exists!")
    print(f"📍 Location: {os.path.abspath(db_path)}")
    print(f"📊 Size: {os.path.getsize(db_path)} bytes")
    print("-" * 50)
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"📋 Tables found: {[table[0] for table in tables]}")
            print("-" * 50)
            
            # Check users table structure
            cursor.execute("PRAGMA table_info(users);")
            columns = cursor.fetchall()
            print("👥 Users table structure:")
            for col in columns:
                print(f"   {col[1]} ({col[2]})")
            print("-" * 50)
            
            # Count users
            cursor.execute("SELECT COUNT(*) FROM users;")
            user_count = cursor.fetchone()[0]
            print(f"👤 Total users: {user_count}")
            
            if user_count > 0:
                # Show recent users (without passwords)
                cursor.execute("""
                    SELECT id, username, email, first_name, last_name, created_at, last_login 
                    FROM users 
                    ORDER BY created_at DESC 
                    LIMIT 5
                """)
                users = cursor.fetchall()
                print("\n🔍 Recent users:")
                for user in users:
                    print(f"   ID: {user[0]}")
                    print(f"   Username: {user[1]}")
                    print(f"   Email: {user[2]}")
                    print(f"   Name: {user[3]} {user[4]}")
                    print(f"   Created: {user[5]}")
                    print(f"   Last Login: {user[6] or 'Never'}")
                    print("   " + "-" * 30)
            
    except Exception as e:
        print(f"❌ Error accessing database: {e}")

if __name__ == "__main__":
    check_database()