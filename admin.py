from flask import Blueprint, render_template, jsonify, request
from database import Database
from datetime import datetime
import json
from bson import ObjectId

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
db = Database()

class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle MongoDB ObjectId and datetime objects"""
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

@admin_bp.route('/users')
def view_users():
    """View all users in the database"""
    try:
        users = list(db.users_collection.find())
        # Convert to JSON-serializable format
        users_json = json.loads(json.dumps(users, cls=CustomJSONEncoder))
        return render_template('admin_users.html', users=users_json)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/json')
def users_json():
    """Get all users as JSON"""
    try:
        users = list(db.users_collection.find())
        return jsonify(json.loads(json.dumps(users, cls=CustomJSONEncoder)))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/user/<user_id>')
def view_user(user_id):
    """View specific user details"""
    try:
        user = db.find_user_by_id(user_id)
        if user:
            user_json = json.loads(json.dumps(user, cls=CustomJSONEncoder))
            return jsonify(user_json)
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/user/<user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """Delete a user and archive the deletion"""
    try:
        # Find the user first
        user = db.find_user_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Create deletion record
        deletion_record = {
            'deleted_user_id': user['_id'],
            'username': user['username'],
            'email': user['email'],
            'original_created_at': user.get('created_at'),
            'deleted_at': datetime.utcnow(),
            'deleted_by': 'admin',  # You can make this dynamic based on logged-in admin
            'reason': request.json.get('reason', 'Admin deletion') if request.is_json else 'Admin deletion',
            'user_data': user  # Store complete user data for reference
        }
        
        # Insert into deleted_users collection
        # Fix: Use client to get database, then collection
        deleted_users_collection = db.client[db.database_name]['deleted_users']
        deleted_users_collection.insert_one(deletion_record)
        
        # Delete from users collection
        result = db.users_collection.delete_one({'_id': ObjectId(user_id)})
        
        if result.deleted_count > 0:
            return jsonify({
                'success': True,
                'message': f'User {user["username"]} deleted successfully',
                'deleted_at': deletion_record['deleted_at'].isoformat()
            })
        else:
            return jsonify({'error': 'Failed to delete user'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/deleted-users')
def view_deleted_users():
    """View all deleted users"""
    try:
        deleted_users_collection = db.client[db.database_name]['deleted_users']
        deleted_users = list(deleted_users_collection.find().sort('deleted_at', -1))
        deleted_users_json = json.loads(json.dumps(deleted_users, cls=CustomJSONEncoder))
        return render_template('admin_deleted.html', deleted_users=deleted_users_json)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/deleted-users/json')
def deleted_users_json():
    """Get all deleted users as JSON"""
    try:
        deleted_users_collection = db.client[db.database_name]['deleted_users']
        deleted_users = list(deleted_users_collection.find().sort('deleted_at', -1))
        return jsonify(json.loads(json.dumps(deleted_users, cls=CustomJSONEncoder)))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/user/<user_id>/restore', methods=['POST'])
def restore_user(user_id):
    """Restore a deleted user"""
    try:
        deleted_users_collection = db.client[db.database_name]['deleted_users']
        
        # Find the deletion record
        deletion_record = deleted_users_collection.find_one({'deleted_user_id': ObjectId(user_id)})
        if not deletion_record:
            return jsonify({'error': 'Deleted user record not found'}), 404
        
        # Restore the user data
        user_data = deletion_record['user_data']
        user_data['restored_at'] = datetime.utcnow()
        user_data['restored_by'] = 'admin'
        
        # Insert back into users collection
        db.users_collection.insert_one(user_data)
        
        # Remove from deleted_users collection
        deleted_users_collection.delete_one({'_id': deletion_record['_id']})
        
        return jsonify({
            'success': True,
            'message': f'User {user_data["username"]} restored successfully',
            'restored_at': user_data['restored_at'].isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/stats')
def database_stats():
    """Get database statistics"""
    try:
        total_users = db.users_collection.count_documents({})
        active_users = db.users_collection.count_documents({'is_active': True})
        inactive_users = db.users_collection.count_documents({'is_active': False})
        
        # Get deleted users count
        deleted_users_collection = db.client[db.database_name]['deleted_users']
        deleted_users_count = deleted_users_collection.count_documents({})
        
        # Get recent registrations (last 7 days)
        from datetime import datetime, timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_users = db.users_collection.count_documents({
            'created_at': {'$gte': week_ago}
        })
        
        # Get recent deletions (last 7 days)
        recent_deletions = deleted_users_collection.count_documents({
            'deleted_at': {'$gte': week_ago}
        })
        
        stats = {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': inactive_users,
            'deleted_users': deleted_users_count,
            'recent_registrations': recent_users,
            'recent_deletions': recent_deletions,
            'database_name': db.database_name,
            'collection_name': 'users'
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/test-connection')
def test_connection():
    """Test database connection"""
    try:
        # Test ping to MongoDB
        db.client.admin.command('ping')
        return jsonify({
            'status': 'success',
            'message': 'Database connection is working',
            'database': db.database_name,
            'connection_string': db.connection_string.split('@')[0] + '@***' if '@' in db.connection_string else db.connection_string
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@admin_bp.route('/search-user')
def search_user():
    """Search for users by username or email"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Search query required'}), 400
    
    try:
        # Search by username or email
        users = list(db.users_collection.find({
            '$or': [
                {'username': {'$regex': query, '$options': 'i'}},
                {'email': {'$regex': query, '$options': 'i'}}
            ]
        }))
        
        users_json = json.loads(json.dumps(users, cls=CustomJSONEncoder))
        return jsonify(users_json)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/search-deleted-user')
def search_deleted_user():
    """Search for deleted users by username or email"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Search query required'}), 400
    
    try:
        deleted_users_collection = db.client[db.database_name]['deleted_users']
        
        # Search by username or email in deleted users
        deleted_users = list(deleted_users_collection.find({
            '$or': [
                {'username': {'$regex': query, '$options': 'i'}},
                {'email': {'$regex': query, '$options': 'i'}}
            ]
        }).sort('deleted_at', -1))
        
        deleted_users_json = json.loads(json.dumps(deleted_users, cls=CustomJSONEncoder))
        return jsonify(deleted_users_json)
    except Exception as e:
        return jsonify({'error': str(e)}), 500