import streamlit as st
from st_supabase_connection import SupabaseConnection
from datetime import datetime
import time
import re

import sqlite3

try:
    # Connect to SQLite Database and create a cursor
    sqliteConnection = sqlite3.connect('sql.db')
    cursor = sqliteConnection.cursor()
    print('DB Init')

    # Execute a query to get the SQLite version
    query = 'SELECT sqlite_version();'
    cursor.execute(query)

    # Fetch and print the result
    result = cursor.fetchall()
    print('SQLite Version is {}'.format(result[0][0]))

    # Close the cursor after use
    cursor.close()

except sqlite3.Error as error:
    print('Error occurred -', error)

finally:
    # Ensure the database connection is closed
    if sqliteConnection:
        sqliteConnection.close()
        print('SQLite Connection closed')


class AuthService:
    def __init__(self):
        
        try:
            # Custom connection parameters
            self.supabase = st.connection(
                "supabase",
                type=SupabaseConnection,
                ttl=None,
                url='https://pckcnvmpqcizemkmknji.supabase.co',#st.secrets["SUPABASE_URL"],
                key='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBja2Nudm1wcWNpemVta21rbmppIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE3ODIzODUsImV4cCI6MjA2NzM1ODM4NX0.P8JLk_a7Unp1rVjM3SZz5Pn3-bOI3DDexZKSc_JQK44', #st.secrets["SUPABASE_KEY"],
                client_options={    
                    "timeout": 30,  # 30 seconds timeout
                    "retries": 3,   # 3 retries
                }
            )
        except Exception as e:
            st.error(f"Failed to initialize services: {str(e)}")
            raise e
        
        # Validate session on initialization
        if 'auth_token' in st.session_state:
            if not self.validate_session_token():
                self.sign_out()

    def validate_email(self, email):
        """Validate email format."""
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(pattern, email))

    def check_existing_user(self, email):
        """Check if user already exists."""
        try:
            result = self.supabase.table('users')\
                .select('id')\
                .eq('email', email)\
                .execute()
            print(result.data)
            return len(result.data) > 0
        except Exception:
            return False

    def sign_up(self, email, password, name):
        try:
            auth_response = self.supabase.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "name": name
                    }
                }
            })
            print(f'auth_response - {auth_response}')
            if not auth_response.user:
                return False, "Failed to create user account"
            import random
            user_data = {
                'id': random.randint(10000,1000000),
                'email': email,
                'name': name,
                'created_at': datetime.now().isoformat()
            }
            
            # Insert user data into users table, make sure supabase RLS disabled and schema created
            self.supabase.table('users').insert(user_data).execute()
            print(f'user_data - {user_data}')
            return True, user_data
                
        except Exception as e:
            error_msg = str(e).lower()
            if "duplicate" in error_msg or "already registered" in error_msg:
                return False, "Email already registered"
            return False, f"Sign up failed: {str(e)}"

    def sign_in(self, email, password):
        try:
            # Clear any existing session data first
            self.sign_out()
            print('signinig in with email and password')
            auth_response = self.supabase.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response and auth_response.user:
                # Get user data
                user_data = self.get_user_data(auth_response.user.email)
                if not user_data:
                    return False, "User data not found"
                    
                # Store session info
                st.session_state.auth_token = auth_response.session.access_token
                st.session_state.user = user_data
                return True, user_data
                
            return False, "Invalid login response"
        except Exception as e:
            return False, str(e)
    
    def sign_out(self):
        """Sign out and clear all session data."""
        try:
            self.supabase.client.auth.sign_out()
            from auth.session_manager import SessionManager
            SessionManager.clear_session_state()
            return True, None
        except Exception as e:
            return False, str(e)
    
    def get_user(self):
        try:
            return self.supabase.client.auth.get_user()
        except Exception:
            return None

    def create_session(self, user_id, title=None):
        try:
            current_time = datetime.now()
            default_title = f"{current_time.strftime('%d-%m-%Y')} | {current_time.strftime('%H:%M:%S')}"
            
            session_data = {
                'user_id': user_id,
                'title': title or default_title,
                'created_at': current_time.isoformat()
            }
            result = self.supabase.table('chat_sessions').insert(session_data).execute()
            return True, result.data[0] if result.data else None
        except Exception as e:
            return False, str(e)

    def get_user_sessions(self, user_id):
        try:
            result = self.supabase.table('chat_sessions')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('created_at', desc=True)\
                .execute()
            return True, result.data
        except Exception as e:
            st.error(f"Error fetching sessions: {str(e)}")
            return False, []

    def save_chat_message(self, session_id, content, role='user'):
        try:
            message_data = {
                'session_id': session_id,
                'content': content,
                'role': role,
                'created_at': datetime.now().isoformat()
            }
            result = self.supabase.table('chat_messages').insert(message_data).execute()
            return True, result.data[0] if result.data else None
        except Exception as e:
            return False, str(e)

    def get_session_messages(self, session_id):
        try:
            result = self.supabase.table('chat_messages')\
                .select('*')\
                .eq('session_id', session_id)\
                .order('created_at')\
                .execute()
            return True, result.data
        except Exception as e:
            return False, str(e)

    def delete_session(self, session_id):
        try:
            messages_delete = self.supabase.table('chat_messages')\
                .delete()\
                .eq('session_id', session_id)\
                .execute()

            session_delete = self.supabase.table('chat_sessions')\
                .delete()\
                .eq('id', session_id)\
                .execute()

            return True, None
        except Exception as e:
            st.error(f"Failed to delete session: {str(e)}")
            return False, str(e)
    
    def validate_session_token(self):
        """Validate existing session token on startup."""
        try:
            session = self.supabase.client.auth.get_session()
            if not session or not session.access_token:
                return None
                
            # Verify token matches stored token
            if session.access_token != st.session_state.get('auth_token'):
                return None
                
            user = self.supabase.client.auth.get_user()
            if not user or not user.user:
                return None
                
            return self.get_user_data(user.user.email)
        except Exception:
            return None
    
    def get_user_data(self, email_id):
        """Get user data from database."""
        try:
            print(f'getting user id - {email_id}')
            response = self.supabase.table('users')\
                .select('*')\
                .eq('email', email_id)\
                .single()\
                .execute()
            return response.data if response else None
        except Exception:
            return None