# chatbot_graph.py - Supabase-based persistence

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client (credentials from env)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def load_chat_history():
    """Load chat history from Supabase"""
    try:
        response = (
            supabase.table("chat_history")
            .select("*")
            .order("created_at", desc=False)  # Oldest first
            .execute()
        )
        if response.data:
            # Convert to our message format: [{'role': 'user', 'content': '...'}, ...]
            return [{"role": msg["role"], "content": msg["content"]} for msg in response.data]
        return []
    except Exception as e:
        print(f"Error loading history from Supabase: {e}")
        return []

def save_chat_history(messages):
    """Save entire chat history to Supabase (overwrite by deleting old and inserting new)"""
    try:
        # Clear existing history (simple overwrite for global chat)
        supabase.table("chat_history").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()  # Dummy condition to delete all
        
        # Insert new messages
        for msg in messages:
            supabase.table("chat_history").insert({
                "role": msg["role"],
                "content": msg["content"]
            }).execute()
    except Exception as e:
        print(f"Error saving history to Supabase: {e}")