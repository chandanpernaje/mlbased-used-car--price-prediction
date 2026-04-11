#!/usr/bin/env python3
"""
Database Verification Script
Run this script to check if your MongoDB database is working properly
and to view all stored user data.
"""

import sys
import json
from datetime import datetime
from database import Database
from bson import ObjectId

class DatabaseChecker:
    def __init__(self):
        self.db = Database()
    
    def check_connection(self):
        """Test database connection"""
        try:
            self.db.client.admin.command('ping')
            print("✅ Database connection: SUCCESS")
            return True
        except Exception as e:
            print(f"❌ Database connection: FAILED - {e}")
            return False
    
    def get_database_info(self):
        """Get basic database information"""
        try:
            # Get database stats
            stats = self.db.client[self.db.database_name].command("dbstats")
            
            print(f"\n📊 Database Information:")
            print(f"   Database Name: {self.db.database_name}")
            print(f"   Collections: {stats.get('collections', 'N/A')}")
            print(f"   Data Size: {stats.get('dataSize', 'N/A')} bytes")
            print(f"   Storage Size: {stats.get('storageSize', 'N/A')} bytes")
            print(f"   Indexes: {stats.get('indexes', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Could not get database info: {e}")
    
    def check_users_collection(self):
        """Check users collection and display stats"""
        try:
            collection = self.db.users_collection
            
            # Count documents
            total_users = collection.count_documents({})
            active_users = collection.count_documents({'is_active': True})
            inactive_users = collection.count_documents({'is_active': False})
            
            print(f"\n👥 Users Collection Stats:")
            print(f"   Total Users: {total_users}")
            print(f"   Active Users: {active_users}")
            print(f"   Inactive Users: {inactive_users}")
            
            # Get recent registrations (last 7 days)
            from datetime import timedelta
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_users = collection.count_documents({
                'created_at': {'$gte': week_ago}
            })
            print(f"   Recent Registrations (7 days): {recent_users}")
            
            return total_users > 0
            
        except Exception as e:
            print(f"❌ Could not check users collection: {e}")
            return False
    
    def display_all_users(self):
        """Display all users in the database"""
        try:
            users = list(self.db.users_collection.find())
            
            if not users:
                print("\n📝 No users found in database")
                return
            
            print(f"\n📋 All Users in Database ({len(users)} users):")
            print("-" * 100)
            
            for i, user in enumerate(users, 1):
                print(f"\n{i}. User Details:")
                print(f"   ID: {user['_id']}")
                print(f"   Username: {user['username']}")
                print(f"   Email: {user['email']}")
                print(f"   Status: {'Active' if user.get('is_active', True) else 'Inactive'}")
                print(f"   Created: {user.get('created_at', 'N/A')}")
                print(f"   Last Login: {user.get('last_login', 'Never')}")
                print(f"   Password Hash: {user['password'][:20]}...")
                
        except Exception as e:
            print(f"❌ Could not display users: {e}")
    
    def search_user(self, query):
        """Search for a specific user"""
        try:
            # Search by username or email
            user = self.db.find_user_by_username(query)
            if not user:
                user = self.db.find_user_by_email(query)
            
            if user:
                print(f"\n🔍 User Found:")
                print(f"   ID: {user['_id']}")
                print(f"   Username: {user['username']}")
                print(f"   Email: {user['email']}")
                print(f"   Status: {'Active' if user.get('is_active', True) else 'Inactive'}")
                print(f"   Created: {user.get('created_at', 'N/A')}")
                print(f"   Last Login: {user.get('last_login', 'Never')}")
                return True
            else:
                print(f"\n❌ User not found: {query}")
                return False
                
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return False
    
    def export_users_json(self, filename="users_export.json"):
        """Export all users to JSON file"""
        try:
            users = list(self.db.users_collection.find())
            
            # Convert ObjectId and datetime to string
            for user in users:
                user['_id'] = str(user['_id'])
                if 'created_at' in user and user['created_at']:
                    user['created_at'] = user['created_at'].isoformat()
                if 'last_login' in user and user['last_login']:
                    user['last_login'] = user['last_login'].isoformat()
            
            with open(filename, 'w') as f:
                json.dump(users, f, indent=2)
            
            print(f"\n💾 Users exported to {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False
    
    def run_full_check(self):
        """Run all checks"""
        print("🔍 Starting Database Verification...")
        print("=" * 50)
        
        # Check connection
        if not self.check_connection():
            print("❌ Cannot proceed - Database connection failed")
            return False
        
        # Get database info
        self.get_database_info()
        
        # Check users collection
        has_users = self.check_users_collection()
        
        # Display users if any exist
        if has_users:
            self.display_all_users()
        
        print("\n" + "=" * 50)
        print("✅ Database verification completed!")
        return True

def main():
    checker = DatabaseChecker()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "check":
            checker.run_full_check()
        elif command == "users":
            checker.display_all_users()
        elif command == "search" and len(sys.argv) > 2:
            query = sys.argv[2]
            checker.search_user(query)
        elif command == "export":
            filename = sys.argv[2] if len(sys.argv) > 2 else "users_export.json"
            checker.export_users_json(filename)
        elif command == "stats":
            checker.check_connection()
            checker.get_database_info()
            checker.check_users_collection()
        else:
            print("❌ Invalid command")
            print("\nUsage:")
            print("  python check_database.py check        # Run full check")
            print("  python check_database.py users        # Show all users")
            print("  python check_database.py search <username/email>  # Search user")
            print("  python check_database.py export [filename]        # Export to JSON")
            print("  python check_database.py stats        # Show database stats")
    else:
        # Run full check by default
        checker.run_full_check()

if __name__ == "__main__":
    main()