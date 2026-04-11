from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson import ObjectId
import os
from datetime import datetime

class Database:
    def __init__(self):
        # MongoDB connection string - update with your MongoDB details
        self.connection_string = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
        self.database_name = 'UsedCar'
        self.client = None
        self.db = None
        self.users_collection = None
        self.cars_collection = None
        self.connect()
    
    def connect(self):
        """Connect to MongoDB database"""
        try:
            self.client = MongoClient(self.connection_string)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            self.users_collection = self.db['users']
            self.cars_collection = self.db['cars']
            print("Connected to MongoDB successfully")
        except ConnectionFailure:
            print("Failed to connect to MongoDB")
            raise
    
    # USER MANAGEMENT METHODS
    def create_user(self, user_data):
        """Insert a new user into the database"""
        try:
            user_data['created_at'] = datetime.now()
            result = self.users_collection.insert_one(user_data)
            return result.inserted_id
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def find_user_by_username(self, username):
        """Find a user by username"""
        try:
            return self.users_collection.find_one({'username': username})
        except Exception as e:
            print(f"Error finding user: {e}")
            return None
    
    def find_user_by_email(self, email):
        """Find a user by email"""
        try:
            return self.users_collection.find_one({'email': email})
        except Exception as e:
            print(f"Error finding user by email: {e}")
            return None
    
    def find_user_by_id(self, user_id):
        """Find a user by ID"""
        try:
            return self.users_collection.find_one({'_id': ObjectId(user_id)})
        except Exception as e:
            print(f"Error finding user by ID: {e}")
            return None
    
    def update_user(self, user_id, update_data):
        """Update user information"""
        try:
            update_data['updated_at'] = datetime.now()
            result = self.users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    def delete_user(self, user_id):
        """Delete a user"""
        try:
            result = self.users_collection.delete_one({'_id': ObjectId(user_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    # CAR MANAGEMENT METHODS
    def create_car(self, car_data):
        """Insert a new car into the database"""
        try:
            car_data['created_at'] = datetime.now()
            car_data['updated_at'] = datetime.now()
            result = self.cars_collection.insert_one(car_data)
            return result.inserted_id
        except Exception as e:
            print(f"Error creating car: {e}")
            return None
    
    def get_all_cars(self, status=None, limit=None):
        """Get all cars or filter by status"""
        try:
            query = {}
            if status:
                query['status'] = status
            
            cursor = self.cars_collection.find(query)
            if limit:
                cursor = cursor.limit(limit)
            
            cars = list(cursor)
            # Convert ObjectId to string for JSON serialization
            for car in cars:
                car['_id'] = str(car['_id'])
            return cars
        except Exception as e:
            print(f"Error getting cars: {e}")
            return []
    
    def find_car_by_id(self, car_id):
        """Find a car by ID"""
        try:
            car = self.cars_collection.find_one({'_id': ObjectId(car_id)})
            if car:
                car['_id'] = str(car['_id'])
            return car
        except Exception as e:
            print(f"Error finding car by ID: {e}")
            return None
    
    def update_car(self, car_id, update_data):
        """Update car information"""
        try:
            update_data['updated_at'] = datetime.now()
            result = self.cars_collection.update_one(
                {'_id': ObjectId(car_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating car: {e}")
            return False
    
    def delete_car(self, car_id):
        """Delete a car"""
        try:
            result = self.cars_collection.delete_one({'_id': ObjectId(car_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting car: {e}")
            return False
    
    def search_cars(self, filters):
        """Search cars with multiple filters"""
        try:
            query = {}
            
            # Brand filter
            if filters.get('brand'):
                query['brand'] = {'$regex': filters['brand'], '$options': 'i'}
            
            # Price range filter
            if filters.get('min_price') or filters.get('max_price'):
                price_query = {}
                if filters.get('min_price'):
                    price_query['$gte'] = filters['min_price']
                if filters.get('max_price'):
                    price_query['$lte'] = filters['max_price']
                query['price'] = price_query
            
            # Fuel type filter
            if filters.get('fuel'):
                query['fuel'] = filters['fuel']
            
            # Year filter
            if filters.get('year'):
                query['year'] = filters['year']
            
            # Location filter
            if filters.get('location'):
                query['location'] = {'$regex': filters['location'], '$options': 'i'}
            
            # Status filter
            if filters.get('status'):
                query['status'] = filters['status']
            
            # Text search in model
            if filters.get('search'):
                query['model'] = {'$regex': filters['search'], '$options': 'i'}
            
            cars = list(self.cars_collection.find(query))
            # Convert ObjectId to string for JSON serialization
            for car in cars:
                car['_id'] = str(car['_id'])
            return cars
        except Exception as e:
            print(f"Error searching cars: {e}")
            return []
    
    def get_cars_by_location(self, location):
        """Get cars by location"""
        try:
            cars = list(self.cars_collection.find({'location': {'$regex': location, '$options': 'i'}}))
            for car in cars:
                car['_id'] = str(car['_id'])
            return cars
        except Exception as e:
            print(f"Error getting cars by location: {e}")
            return []
    
    def get_cars_by_price_range(self, min_price, max_price):
        """Get cars within a price range"""
        try:
            cars = list(self.cars_collection.find({
                'price': {'$gte': min_price, '$lte': max_price}
            }))
            for car in cars:
                car['_id'] = str(car['_id'])
            return cars
        except Exception as e:
            print(f"Error getting cars by price range: {e}")
            return []
    
    def bulk_insert_cars(self, cars_data):
        """Insert multiple cars at once"""
        try:
            for car in cars_data:
                car['created_at'] = datetime.now()
                car['updated_at'] = datetime.now()
            
            result = self.cars_collection.insert_many(cars_data)
            return result.inserted_ids
        except Exception as e:
            print(f"Error bulk inserting cars: {e}")
            return []
    
    def close_connection(self):
        """Close the database connection"""
        if self.client:
            self.client.close()
            print("MongoDB connection closed")
    
    # UTILITY METHODS
    def get_collection_stats(self):
        """Get statistics about the collections"""
        try:
            user_count = self.users_collection.count_documents({})
            car_count = self.cars_collection.count_documents({})
            available_cars = self.cars_collection.count_documents({'status': 'available'})
            sold_cars = self.cars_collection.count_documents({'status': 'sold'})
            pending_cars = self.cars_collection.count_documents({'status': 'pending'})
            
            return {
                'users': user_count,
                'total_cars': car_count,
                'available_cars': available_cars,
                'sold_cars': sold_cars,
                'pending_cars': pending_cars
            }
        except Exception as e:
            print(f"Error getting collection stats: {e}")
            return {}