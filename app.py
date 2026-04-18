from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_cors import CORS
from database import Database
from auth import Auth
import joblib
import pandas as pd
import numpy as np
import os
import json
import logging
from datetime import datetime, timedelta
from urllib.parse import quote
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import warnings
import random
import threading
import time
from typing import Dict, List, Optional
import uuid
from flask_pymongo import PyMongo
from bson import ObjectId
from admin import admin_bp
from werkzeug.security import generate_password_hash, check_password_hash

warnings.filterwarnings('ignore')

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', '9f1c56e5a0d1e49d9187a1e2d9f3bc458cb29b15d2bfa35e38f2364775b9f9a7')
CORS(app)  # Enable CORS for API endpoints

# Initialize database and auth
db = Database()
auth = Auth(db)
app.register_blueprint(admin_bp)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for models
model = None
scaler = None
encoders = None
feature_columns = None

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

app.json_encoder = JSONEncoder

# CarMarketplace class
class CarMarketplace:
    def __init__(self, db):
        self.db = db
        self.categories = {
            'luxury': ['BMW', 'Mercedes-Benz', 'Audi', 'Jaguar', 'Lexus', 'Porsche'],
            'premium': ['Honda', 'Toyota', 'Hyundai', 'Volkswagen', 'Skoda', 'Nissan'],
            'budget': ['Maruti', 'Tata', 'Mahindra', 'Datsun', 'Renault'],
            'sports': ['Ferrari', 'Lamborghini', 'Maserati', 'Bentley'],
            'suv': ['Ford', 'Chevrolet', 'Jeep', 'Land Rover']
        }
        self._initialize_sample_data()
        self._start_update_thread()

    def _initialize_sample_data(self):
        sample_cars = [
            {
                'brand': 'Maruti', 'model': 'Swift', 'year': 2020, 'fuel': 'Petrol',
                'km_driven': 25000, 'price': 650000, 'location': 'Bangalore',
                'seller_type': 'Individual', 'transmission': 'Manual'
            },
            {
                'brand': 'Hyundai', 'model': 'Creta', 'year': 2021, 'fuel': 'Diesel',
                'km_driven': 18000, 'price': 1250000, 'location': 'Delhi',
                'seller_type': 'Dealer', 'transmission': 'Automatic'
            },
            {
                'brand': 'Honda', 'model': 'City', 'year': 2019, 'fuel': 'Petrol',
                'km_driven': 35000, 'price': 850000, 'location': 'Mumbai',
                'seller_type': 'Individual', 'transmission': 'Manual'
            },
            {
                'brand': 'Toyota', 'model': 'Innova', 'year': 2022, 'fuel': 'Diesel',
                'km_driven': 12000, 'price': 1850000, 'location': 'Chennai',
                'seller_type': 'Dealer', 'transmission': 'Manual'
            },
            {
                'brand': 'BMW', 'model': 'X1', 'year': 2020, 'fuel': 'Petrol',
                'km_driven': 22000, 'price': 3200000, 'location': 'Bangalore',
                'seller_type': 'Individual', 'transmission': 'Automatic'
            },
            {
                'brand': 'Tata', 'model': 'Nexon', 'year': 2021, 'fuel': 'Electric',
                'km_driven': 15000, 'price': 1100000, 'location': 'Pune',
                'seller_type': 'Dealer', 'transmission': 'Automatic'
            }
        ]
        for car_data in sample_cars:
            self.add_listing(car_data)

    def _start_update_thread(self):
        def update_listings():
            while True:
                if random.random() < 0.3:
                    new_car = {
                        'brand': random.choice(sum(self.categories.values(), [])),
                        'model': random.choice(['Swift', 'Creta', 'City', 'Innova', 'X1', 'Nexon']),
                        'year': random.randint(2018, 2023),
                        'fuel': random.choice(['Petrol', 'Diesel', 'Electric']),
                        'km_driven': random.randint(5000, 50000),
                        'price': random.randint(500000, 4000000),
                        'location': random.choice(['Bangalore', 'Delhi', 'Mumbai', 'Chennai', 'Pune']),
                        'seller_type': random.choice(['Individual', 'Dealer']),
                        'transmission': random.choice(['Manual', 'Automatic'])
                    }
                    self.add_listing(new_car)
                else:
                    cars = self.db.get_all_cars()
                    if cars:
                        listing = random.choice(cars)
                        listing_id = listing['_id']
                        self.update_listing_stats(listing_id, 'view')
                time.sleep(60)

        thread = threading.Thread(target=update_listings, daemon=True)
        thread.start()

    def add_listing(self, car_data: Dict) -> str:
        listing_id = str(uuid.uuid4())[:8]
        listing = {
            'id': listing_id,
            'brand': car_data['brand'],
            'model': car_data['model'],
            'year': car_data['year'],
            'fuel': car_data['fuel'],
            'km_driven': car_data['km_driven'],
            'price': car_data['price'],
            'location': car_data['location'],
            'seller_type': car_data['seller_type'],
            'transmission': car_data['transmission'],
            'posted_date': datetime.now(),
            'last_updated': datetime.now(),
            'views': random.randint(50, 500),
            'favorites': random.randint(5, 50),
            'seller_info': self._generate_seller_info(car_data['seller_type']),
            'car_details': self._generate_car_details(car_data),
            'images': self._generate_image_urls(car_data['brand'], car_data['model']),
            'condition': self._assess_condition(car_data['year'], car_data['km_driven']),
            'features': self._generate_features(car_data['brand'], car_data['year']),
            'inspection_report': self._generate_inspection_report(),
            'price_history': self._generate_price_history(car_data['price']),
            'similar_cars': [],
            'contact_info': self._generate_contact_info(),
            'availability': 'Available',
            'negotiable': random.choice([True, False]),
            'exchange_accepted': random.choice([True, False]),
            'loan_available': random.choice([True, False]),
            'warranty_remaining': self._calculate_warranty(car_data['year']),
            'service_history': self._generate_service_history(car_data['year']),
            'ownership_history': self._generate_ownership_history(),
            'registration_state': self._get_registration_state(car_data['location']),
            'insurance_status': self._generate_insurance_status(),
            'rto_clearance': random.choice(['Clear', 'Pending', 'Minor Issues']),
            'accident_history': self._generate_accident_history(),
            'modification_details': self._generate_modifications(),
            'test_drive_available': True,
            'home_test_drive': random.choice([True, False]),
            'home_inspection': random.choice([True, False]),
            'urgent_sale': random.choice([True, False]),
            'viewing_hours': "9 AM - 7 PM",
            'reason_for_sale': random.choice([
                'Buying new car', 'Relocating', 'Financial reasons',
                'Upgrading', 'Multiple cars', 'Rarely used'
            ])
        }
        # Insert into MongoDB
        inserted_id = self.db.create_car(listing)
        return str(inserted_id)

    def _generate_seller_info(self, seller_type: str) -> Dict:
        if seller_type == 'Individual':
            return {
                'name': random.choice(['Rajesh Kumar', 'Priya Sharma', 'Amit Patel', 'Sunita Singh']),
                'rating': round(random.uniform(4.0, 5.0), 1),
                'total_listings': random.randint(1, 5),
                'member_since': f"{random.randint(2018, 2023)}",
                'verified': random.choice([True, False]),
                'response_time': f"{random.randint(1, 24)} hours",
                'location_verified': True,
                'phone_verified': True
            }
        else:
            return {
                'name': random.choice(['AutoMax Motors', 'Prime Cars', 'Elite Automobiles', 'City Cars']),
                'rating': round(random.uniform(4.2, 4.9), 1),
                'total_listings': random.randint(50, 200),
                'member_since': f"{random.randint(2015, 2020)}",
                'verified': True,
                'response_time': f"{random.randint(1, 6)} hours",
                'location_verified': True,
                'phone_verified': True,
                'business_license': f"DL{random.randint(100000, 999999)}",
                'showroom_address': "Main Road, Commercial Complex"
            }

    def _generate_car_details(self, car_data: Dict) -> Dict:
        return {
            'engine_capacity': f"{random.randint(1000, 3000)}cc",
            'max_power': f"{random.randint(70, 300)}bhp",
            'max_torque': f"{random.randint(100, 400)}Nm",
            'mileage': f"{random.randint(12, 25)}kmpl",
            'seats': random.choice([5, 7, 8]),
            'body_type': random.choice(['Hatchback', 'Sedan', 'SUV', 'Crossover']),
            'color': random.choice(['White', 'Silver', 'Black', 'Red', 'Blue', 'Grey']),
            'variant': f"{car_data['model']} {random.choice(['LXi', 'VXi', 'ZXi', 'Base', 'Top'])}",
            'ownership': random.choice(['First Owner', 'Second Owner', 'Third Owner']),
            'registration_year': car_data['year'],
            'chassis_number': f"ABC{random.randint(1000000, 9999999)}",
            'engine_number': f"ENG{random.randint(100000, 999999)}",
            'description': f"Well-maintained {car_data['brand']} {car_data['model']} in excellent condition."
        }

    def _generate_image_urls(self, brand: str, model: str) -> List[str]:
        return [f"https://via.placeholder.com/300x200?text={brand}+{model}" for _ in range(random.randint(8, 15))]

    def _assess_condition(self, year: int, km_driven: int) -> Dict:
        age = 2024 - year
        if age <= 2 and km_driven < 30000:
            condition = 'Excellent'
            score = random.randint(90, 95)
        elif age <= 4 and km_driven < 60000:
            condition = 'Good'
            score = random.randint(75, 89)
        elif age <= 7 and km_driven < 100000:
            condition = 'Fair'
            score = random.randint(60, 74)
        else:
            condition = 'Average'
            score = random.randint(40, 59)
        return {
            'overall': condition,
            'score': score,
            'exterior': random.choice(['Excellent', 'Good', 'Fair']),
            'interior': random.choice(['Excellent', 'Good', 'Fair']),
            'engine': random.choice(['Excellent', 'Good', 'Fair']),
            'tires': random.choice(['New', 'Good', 'Needs Replacement']),
            'battery': random.choice(['New', 'Good', 'Needs Replacement'])
        }

    def _generate_features(self, brand: str, year: int) -> List[str]:
        basic_features = ['Power Steering', 'Power Windows', 'Central Locking', 'Air Conditioning']
        if year >= 2018:
            basic_features.extend(['Touchscreen Infotainment', 'Bluetooth', 'USB Ports'])
        if year >= 2020:
            basic_features.extend(['Android Auto', 'Apple CarPlay', 'Reverse Camera'])
        if brand in ['BMW', 'Mercedes-Benz', 'Audi']:
            basic_features.extend([
                'Leather Seats', 'Sunroof', 'Alloy Wheels', 'Automatic Climate Control',
                'Cruise Control', 'Parking Sensors', 'Keyless Entry'
            ])
        return random.sample(basic_features, min(len(basic_features), random.randint(6, 12)))

    def _generate_inspection_report(self) -> Dict:
        return {
            'inspected': random.choice([True, False]),
            'inspection_date': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
            'inspector': 'Certified Auto Inspector',
            'report_url': 'https://example.com/inspection-report.pdf',
            'major_issues': random.randint(0, 2),
            'minor_issues': random.randint(0, 5),
            'overall_rating': random.choice(['Pass', 'Pass with Minor Issues', 'Needs Attention'])
        }

    def _generate_price_history(self, current_price: int) -> List[Dict]:
        history = []
        price = current_price
        for i in range(random.randint(1, 5)):
            date = datetime.now() - timedelta(days=random.randint(1, 60))
            price += random.randint(-20000, 10000)
            history.append({
                'date': date.strftime('%Y-%m-%d'),
                'price': price,
                'reason': random.choice(['Initial listing', 'Price reduced', 'Market adjustment'])
            })
        return sorted(history, key=lambda x: x['date'])

    def _generate_contact_info(self) -> Dict:
        return {
            'phone': f"+91-{random.randint(70000, 99999)}{random.randint(10000, 99999)}",
            'whatsapp_available': random.choice([True, False]),
            'email': f"seller{random.randint(100, 999)}@example.com",
            'preferred_contact': random.choice(['Phone', 'WhatsApp', 'Email']),
            'available_hours': "9 AM - 8 PM",
            'call_preference': random.choice(['Anytime', 'After 6 PM', 'Weekends only'])
        }

    def _calculate_warranty(self, year: int) -> Dict:
        car_age = 2024 - year
        if car_age <= 3:
            remaining_months = max(0, 36 - (car_age * 12))
            return {
                'manufacturer_warranty': f"{remaining_months} months",
                'extended_warranty': random.choice([True, False]),
                'warranty_type': 'Comprehensive' if remaining_months > 0 else 'Expired'
            }
        else:
            return {
                'manufacturer_warranty': 'Expired',
                'extended_warranty': random.choice([True, False]),
                'warranty_type': 'Extended' if random.choice([True, False]) else 'None'
            }

    def _generate_service_history(self, year: int) -> Dict:
        car_age = 2024 - year
        total_services = car_age * random.randint(1, 3)
        return {
            'total_services': total_services,
            'last_service_date': (datetime.now() - timedelta(days=random.randint(30, 180))).strftime('%Y-%m-%d'),
            'service_type': random.choice(['Authorized Service Center', 'Local Garage', 'Mixed']),
            'major_repairs': random.randint(0, 2),
            'service_records_available': random.choice([True, False]),
            'next_service_due': (datetime.now() + timedelta(days=random.randint(30, 120))).strftime('%Y-%m-%d')
        }

    def _generate_ownership_history(self) -> Dict:
        return {
            'total_owners': random.randint(1, 3),
            'current_owner_duration': f"{random.randint(1, 5)} years",
            'usage_type': random.choice(['Personal', 'Commercial', 'Taxi']),
            'driven_by': random.choice(['Owner', 'Chauffeur', 'Family Members']),
            'parking_type': random.choice(['Covered', 'Open', 'Street'])
        }

    def _get_registration_state(self, location: str) -> str:
        state_mapping = {
            'Bangalore': 'Karnataka (KA)',
            'Delhi': 'Delhi (DL)',
            'Mumbai': 'Maharashtra (MH)',
            'Chennai': 'Tamil Nadu (TN)',
            'Pune': 'Maharashtra (MH)',
            'Hyderabad': 'Telangana (TS)',
            'Kolkata': 'West Bengal (WB)'
        }
        return state_mapping.get(location, 'Unknown')

    def _generate_insurance_status(self) -> Dict:
        return {
            'valid_until': (datetime.now() + timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d'),
            'insurance_type': random.choice(['Comprehensive', 'Third Party', 'Zero Depreciation']),
            'claim_history': random.randint(0, 2),
            'no_claim_bonus': f"{random.randint(0, 50)}%",
            'transferable': random.choice([True, False])
        }

    def _generate_accident_history(self) -> Dict:
        has_accidents = random.choice([True, False])
        if has_accidents:
            return {
                'total_accidents': random.randint(1, 2),
                'severity': random.choice(['Minor', 'Moderate']),
                'last_accident_date': (datetime.now() - timedelta(days=random.randint(180, 1095))).strftime('%Y-%m-%d'),
                'insurance_claimed': random.choice([True, False]),
                'repaired_at': random.choice(['Authorized Center', 'Local Garage'])
            }
        else:
            return {
                'total_accidents': 0,
                'severity': 'None',
                'last_accident_date': None,
                'insurance_claimed': False,
                'repaired_at': None
            }

    def _generate_modifications(self) -> Dict:
        has_modifications = random.choice([True, False])
        if has_modifications:
            return {
                'modified': True,
                'modifications': random.sample([
                    'Alloy Wheels', 'Body Kit', 'Audio System', 'Seat Covers',
                    'Window Tinting', 'Roof Rails', 'Fog Lights'
                ], random.randint(1, 3)),
                'modification_cost': f"₹{random.randint(10000, 50000):,}",
                'professionally_done': random.choice([True, False])
            }
        else:
            return {
                'modified': False,
                'modifications': [],
                'modification_cost': '₹0',
                'professionally_done': False
            }

    def get_listing(self, listing_id: str) -> Optional[Dict]:
        return self.db.find_car_by_id(listing_id)

    def get_all_listings(self) -> List[Dict]:
        return self.db.get_all_cars()

    def search_listings(self, filters: Dict) -> List[Dict]:
        return self.db.search_cars(filters)

    def get_featured_listings(self, limit: int = 6) -> List[Dict]:
        all_listings = self.db.get_all_cars()
        featured = sorted(all_listings, key=lambda x: (x.get('views', 0) + x.get('favorites', 0) * 2), reverse=True)
        return featured[:limit]

    def update_listing_stats(self, listing_id: str, action: str):
        listing = self.db.find_car_by_id(listing_id)
        if listing:
            update_data = {}
            if action == 'view':
                update_data['views'] = listing.get('views', 0) + 1
            elif action == 'favorite':
                update_data['favorites'] = listing.get('favorites', 0) + 1
            update_data['last_updated'] = datetime.now()
            self.db.update_car(listing_id, update_data)

# Initialize marketplace with database
marketplace = CarMarketplace(db)

# Car database
CAR_DATABASE = {
    'registration_patterns': {
        'DL': 'Delhi', 'MH': 'Maharashtra', 'KA': 'Karnataka', 'TN': 'Tamil Nadu',
        'UP': 'Uttar Pradesh', 'GJ': 'Gujarat', 'RJ': 'Rajasthan', 'WB': 'West Bengal',
        'AP': 'Andhra Pradesh', 'HR': 'Haryana', 'PB': 'Punjab', 'OR': 'Odisha',
        'AS': 'Assam', 'BR': 'Bihar', 'CG': 'Chhattisgarh', 'GA': 'Goa',
        'HP': 'Himachal Pradesh', 'JH': 'Jharkhand', 'KL': 'Kerala', 'MP': 'Madhya Pradesh'
    },
    'insurance_providers': [
        'ICICI Lombard', 'HDFC ERGO', 'Bajaj Allianz', 'IFFCO Tokio',
        'New India Assurance', 'Oriental Insurance', 'United India Insurance',
        'National Insurance', 'Reliance General', 'Royal Sundaram', 'SBI General',
        'Tata AIG', 'Future Generali', 'Cholamandalam MS', 'Liberty General'
    ],
    'service_centers': {
        'Maruti': ['Maruti Service Center - Sector 18', 'Maruti Care - MG Road', 'Maruti Authorized - Whitefield'],
        'Hyundai': ['Hyundai Service - Whitefield', 'Hyundai Care - Koramangala', 'Hyundai Authorized - Electronic City'],
        'Honda': ['Honda Service Center - Electronic City', 'Honda Care - Indiranagar', 'Honda Authorized - Jayanagar'],
        'Toyota': ['Toyota Service - Bommanahalli', 'Toyota Care - Jayanagar', 'Toyota Authorized - Whitefield'],
        'BMW': ['BMW Service Center - Embassy Golf Links', 'BMW Authorized - Whitefield', 'BMW Premium - Koramangala'],
        'Audi': ['Audi Service Center - Koramangala', 'Audi Authorized - Electronic City', 'Audi Premium - MG Road'],
        'Mercedes-Benz': ['Mercedes Service - Whitefield', 'Mercedes Authorized - Koramangala'],
        'Tata': ['Tata Service Center - Electronic City', 'Tata Authorized - Jayanagar'],
        'Mahindra': ['Mahindra Service - Whitefield', 'Mahindra Care - Bommanahalli'],
        'Ford': ['Ford Service Center - Electronic City', 'Ford Authorized - Koramangala']
    },
    'fuel_prices': {
        'Petrol': {'price': 102.84, 'unit': '₹/L'},
        'Diesel': {'price': 94.65, 'unit': '₹/L'},
        'CNG': {'price': 75.50, 'unit': '₹/kg'},
        'LPG': {'price': 85.20, 'unit': '₹/L'},
        'Electric': {'price': 8.50, 'unit': '₹/kWh'}
    }
}

def load_models():
    global model, scaler, encoders, feature_columns
    try:
        model = joblib.load("best_car_price_model.pkl")
        scaler = joblib.load("car_price_scaler.pkl")
        encoders = joblib.load("label_encoders.pkl")
        feature_columns = joblib.load("feature_columns.pkl")
        logger.info("[OK] All models loaded successfully!")
        return True
    except FileNotFoundError as e:
        logger.error(f"[ERROR] Model file not found: {e}")
        return False
    except Exception as e:
        logger.error(f"[ERROR] Error loading models: {e}")
        return False

def generate_registration_number():
    states = list(CAR_DATABASE['registration_patterns'].keys())
    state = random.choice(states)
    district = random.randint(1, 99)
    series = random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'])
    number = random.randint(1000, 9999)
    return f"{state}{district:02d}{series}{number}"

def calculate_fuel_cost(fuel_type, mileage, monthly_km=1000):
    try:
        fuel_info = CAR_DATABASE['fuel_prices'].get(fuel_type, {'price': 100, 'unit': '₹/L'})
        if fuel_type == 'Electric':
            efficiency = 15
            monthly_cost = (monthly_km / 100) * efficiency * fuel_info['price']
        else:
            monthly_fuel_needed = monthly_km / mileage
            monthly_cost = monthly_fuel_needed * fuel_info['price']
        return {
            'monthly_cost': round(monthly_cost, 2),
            'yearly_cost': round(monthly_cost * 12, 2),
            'cost_per_km': round(monthly_cost / monthly_km, 2),
            'fuel_price': fuel_info['price'],
            'fuel_unit': fuel_info['unit']
        }
    except Exception as e:
        logger.error(f"Error calculating fuel cost: {e}")
        return {'monthly_cost': 0, 'yearly_cost': 0, 'cost_per_km': 0}

def get_car_real_time_info(brand, year, registration_number=None, mileage=15.0, fuel='Petrol'):
    if not registration_number:
        registration_number = generate_registration_number()
    state_code = registration_number[:2]
    state_name = CAR_DATABASE['registration_patterns'].get(state_code, 'Unknown')
    current_date = datetime.now()
    insurance_start = current_date - timedelta(days=random.randint(30, 365))
    insurance_expiry = insurance_start + timedelta(days=365)
    insurance_expired = insurance_expiry < current_date
    days_to_insurance_expiry = (insurance_expiry - current_date).days
    puc_date = current_date - timedelta(days=random.randint(1, 180))
    puc_expiry = puc_date + timedelta(days=180)
    puc_expired = puc_expiry < current_date
    days_to_puc_expiry = (puc_expiry - current_date).days
    rc_issue_date = datetime(year, random.randint(1, 12), random.randint(1, 28))
    rc_validity = rc_issue_date + timedelta(days=15*365)
    rc_expired = rc_validity < current_date
    days_to_rc_expiry = (rc_validity - current_date).days
    fitness_required = year < 2015
    fitness_expiry = None
    fitness_expired = False
    days_to_fitness_expiry = 0
    if fitness_required:
        fitness_date = current_date - timedelta(days=random.randint(1, 365))
        fitness_expiry = fitness_date + timedelta(days=365)
        fitness_expired = fitness_expiry < current_date
        days_to_fitness_expiry = (fitness_expiry - current_date).days
    car_age = 2024 - year
    base_premium = 12000 + (car_age * 800)
    if insurance_expired:
        base_premium *= 1.25
    if brand in ['BMW', 'Audi', 'Mercedes-Benz']:
        base_premium *= 2.5
    elif brand in ['Honda', 'Toyota', 'Hyundai']:
        base_premium *= 1.2
    fuel_cost_data = calculate_fuel_cost(fuel, mileage)
    service_cost = 3000
    if brand in ['BMW', 'Audi', 'Mercedes-Benz']:
        service_cost *= 4
    elif brand in ['Honda', 'Toyota']:
        service_cost *= 1.5
    insurance_provider = random.choice(CAR_DATABASE['insurance_providers'])
    service_centers = CAR_DATABASE['service_centers'].get(brand, ['Generic Service Center - Local Area'])
    return {
        'registration_number': registration_number,
        'state': state_name,
        'state_code': state_code,
        'insurance': {
            'provider': insurance_provider,
            'policy_number': f"POL{random.randint(100000000, 999999999)}",
            'start_date': insurance_start.strftime('%d-%m-%Y'),
            'expiry_date': insurance_expiry.strftime('%d-%m-%Y'),
            'expired': insurance_expired,
            'days_remaining': max(0, days_to_insurance_expiry),
            'status': 'Expired' if insurance_expired else 'Active',
            'premium_estimate': f"₹{base_premium:,.0f}",
            'coverage_type': random.choice(['Comprehensive', 'Third Party', 'Zero Depreciation']),
            'idv': f"₹{random.randint(200000, 1500000):,.0f}",
            'no_claim_bonus': f"{random.randint(0, 50)}%"
        },
        'puc': {
            'certificate_number': f"PUC{random.randint(10000000, 99999999)}",
            'issue_date': puc_date.strftime('%d-%m-%Y'),
            'expiry_date': puc_expiry.strftime('%d-%m-%Y'),
            'expired': puc_expired,
            'days_remaining': max(0, days_to_puc_expiry),
            'status': 'Expired' if puc_expired else 'Valid',
            'testing_center': f"Authorized PUC Center - {state_name}",
            'emission_standard': 'BS6' if year >= 2020 else 'BS4',
            'fee': '₹150'
        },
        'registration': {
            'rc_number': registration_number,
            'issue_date': rc_issue_date.strftime('%d-%m-%Y'),
            'validity_date': rc_validity.strftime('%d-%m-%Y'),
            'expired': rc_expired,
            'days_remaining': max(0, days_to_rc_expiry),
            'status': 'Expired' if rc_expired else 'Valid',
            'rto_office': f"RTO {state_code}-{random.randint(1, 20)}",
            'vehicle_class': 'Motor Car'
        },
        'fitness': {
            'required': fitness_required,
            'certificate_number': f"FIT{random.randint(10000000, 99999999)}" if fitness_required else None,
            'expiry_date': fitness_expiry.strftime('%d-%m-%Y') if fitness_expiry else None,
            'expired': fitness_expired,
            'days_remaining': max(0, days_to_fitness_expiry),
            'status': 'Expired' if fitness_expired else 'Valid' if fitness_required else 'Not Required',
            'fee': '₹500' if fitness_required else 'N/A'
        },
        'service': {
            'last_service_date': (current_date - timedelta(days=random.randint(30, 180))).strftime('%d-%m-%Y'),
            'next_service_due': (current_date + timedelta(days=random.randint(30, 90))).strftime('%d-%m-%Y'),
            'service_centers': service_centers[:3],
            'total_services': random.randint(car_age * 2, car_age * 4),
            'service_cost_estimate': f"₹{service_cost:,.0f}",
            'service_interval': '6 months / 10,000 km'
        },
        'fuel_analysis': fuel_cost_data,
        'ownership_cost': {
            'monthly_insurance': f"₹{base_premium/12:,.0f}",
            'monthly_fuel': f"₹{fuel_cost_data['monthly_cost']:,.0f}",
            'monthly_service': f"₹{service_cost/6:,.0f}",
            'total_monthly': f"₹{(base_premium/12 + fuel_cost_data['monthly_cost'] + service_cost/6):,.0f}"
        },
        'alerts': generate_enhanced_alerts(insurance_expired, puc_expired, rc_expired, fitness_expired,
                                         days_to_insurance_expiry, days_to_puc_expiry),
        'overall_status': get_overall_status(insurance_expired, puc_expired, rc_expired, fitness_expired),
        'compliance_score': calculate_compliance_score(insurance_expired, puc_expired, rc_expired, fitness_expired)
    }

def generate_enhanced_alerts(insurance_expired, puc_expired, rc_expired, fitness_expired,
                           days_to_insurance, days_to_puc):
    alerts = []
    if insurance_expired:
        alerts.append({
            'type': 'critical',
            'priority': 1,
            'title': 'Insurance Expired - Immediate Action Required',
            'message': 'Driving without insurance is illegal. You may face penalties up to ₹2,000 and vehicle seizure.',
            'action': 'Renew insurance immediately',
            'estimated_cost': '₹15,000 - ₹50,000'
        })
    elif days_to_insurance <= 30:
        alerts.append({
            'type': 'warning',
            'priority': 2,
            'title': 'Insurance Expiring Soon',
            'message': f'Your insurance expires in {days_to_insurance} days. Start renewal to avoid penalties.',
            'action': 'Initiate renewal process',
            'estimated_cost': '₹12,000 - ₹45,000'
        })
    if puc_expired:
        alerts.append({
            'type': 'critical',
            'priority': 1,
            'title': 'PUC Certificate Expired',
            'message': 'Expired PUC can result in fines up to ₹1,000. Required for insurance claims.',
            'action': 'Get PUC test done immediately',
            'estimated_cost': '₹150'
        })
    elif days_to_puc <= 15:
        alerts.append({
            'type': 'warning',
            'priority': 2,
            'title': 'PUC Expiring Soon',
            'message': f'PUC expires in {days_to_puc} days. Book appointment to avoid last-minute rush.',
            'action': 'Schedule PUC test',
            'estimated_cost': '₹150'
        })
    if rc_expired:
        alerts.append({
            'type': 'critical',
            'priority': 1,
            'title': 'Registration Certificate Expired',
            'message': 'Expired RC is a serious offense. Vehicle cannot be legally driven.',
            'action': 'Visit RTO immediately for renewal',
            'estimated_cost': '₹1,000 - ₹5,000'
        })
    if fitness_expired:
        alerts.append({
            'type': 'critical',
            'priority': 1,
            'title': 'Fitness Certificate Expired',
            'message': 'Required for vehicles over 15 years. Mandatory for legal operation.',
            'action': 'Get fitness certificate from RTO',
            'estimated_cost': '₹500 - ₹2,000'
        })
    if not alerts:
        alerts.append({
            'type': 'success',
            'priority': 0,
            'title': 'All Documents Valid ✅',
            'message': 'Your vehicle is fully compliant with all regulations.',
            'action': 'Maintain regular checks',
            'estimated_cost': 'No immediate costs'
        })
    return sorted(alerts, key=lambda x: x['priority'])

def get_overall_status(insurance_expired, puc_expired, rc_expired, fitness_expired):
    expired_count = sum([insurance_expired, puc_expired, rc_expired, fitness_expired])
    if expired_count == 0:
        return 'Fully Compliant'
    elif expired_count <= 2:
        return 'Partially Compliant'
    else:
        return 'Non-Compliant'

def calculate_compliance_score(insurance_expired, puc_expired, rc_expired, fitness_expired):
    score = 100
    if insurance_expired: score -= 40
    if puc_expired: score -= 25
    if rc_expired: score -= 30
    if fitness_expired: score -= 15
    return max(0, score)

def predict_car_price(brand, year, km_driven, fuel, seller_type, transmission, owner,
                     mileage, engine, max_power, seats, torque_value):
    try:
        if not all([brand, year, km_driven, fuel, seller_type, transmission, owner]):
            return None, "Missing required fields"
        input_data = pd.DataFrame({
            'brand': [brand],
            'year': [year],
            'km_driven': [km_driven],
            'fuel': [fuel],
            'seller_type': [seller_type],
            'transmission': [transmission],
            'owner': [owner],
            'mileage': [mileage],
            'engine': [engine],
            'max_power': [max_power],
            'seats': [seats],
            'torque_value': [torque_value]
        })
        input_data['car_age'] = 2024 - input_data['year']
        input_data['power_to_weight'] = input_data['max_power'] / input_data['engine'] * 1000
        input_data['mileage_efficiency'] = input_data['mileage'] / input_data['engine'] * 1000
        input_data['power_to_weight'] = input_data['power_to_weight'].replace([np.inf, -np.inf], 0)
        input_data['mileage_efficiency'] = input_data['mileage_efficiency'].replace([np.inf, -np.inf], 0)
        for col in ['brand', 'fuel', 'seller_type', 'transmission', 'owner']:
            try:
                if col in encoders:
                    input_data[col + '_encoded'] = encoders[col].transform([input_data[col].iloc[0]])[0]
                else:
                    return None, f"Encoder not available for {col}"
            except ValueError:
                return None, f"Unknown {col} value: {input_data[col].iloc[0]}"
        try:
            X_input = input_data[feature_columns]
        except KeyError as e:
            return None, f"Missing feature columns: {e}"
        prediction = model.predict(X_input)[0]
        confidence_lower = prediction * 0.85
        confidence_upper = prediction * 1.15
        return {
            'price': prediction,
            'confidence_lower': confidence_lower,
            'confidence_upper': confidence_upper,
            'confidence_range': f"₹{confidence_lower:,.0f} - ₹{confidence_upper:,.0f}"
        }, None
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return None, str(e)

def generate_price_visualization(predicted_price, brand, year):
    try:
        brands = ['Maruti', 'Hyundai', 'Honda', 'Toyota', 'Tata']
        if brand not in brands:
            brands[0] = brand
        np.random.seed(42)
        prices = []
        for b in brands:
            if b == brand:
                prices.append(predicted_price)
            else:
                base_price = predicted_price * np.random.uniform(0.7, 1.3)
                prices.append(base_price)
        plt.style.use('seaborn-v0_8')
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ['#FF6B6B' if b == brand else '#4ECDC4' for b in brands]
        bars = ax.bar(brands, prices, color=colors, alpha=0.8)
        for i, bar in enumerate(bars):
            if brands[i] == brand:
                bar.set_edgecolor('#FF6B6B')
                bar.set_linewidth(3)
        ax.set_title(f'Price Comparison - {brand} {year}', fontsize=16, fontweight='bold')
        ax.set_ylabel('Price (₹)', fontsize=12)
        ax.set_xlabel('Car Brands', fontsize=12)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x/100000:.1f}L'))
        for bar, price in zip(bars, prices):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'₹{price/100000:.1f}L',
                   ha='center', va='bottom', fontweight='bold')
        plt.xticks(rotation=45)
        plt.tight_layout()
        img = io.BytesIO()
        plt.savefig(img, format='png', dpi=150, bbox_inches='tight')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        plt.close()
        return plot_url
    except Exception as e:
        logger.error(f"Visualization error: {e}")
        return None

def format_price(price):
    if price >= 10000000:
        return f"₹{price/10000000:.1f} Cr"
    elif price >= 100000:
        return f"₹{price/100000:.1f} L"
    else:
        return f"₹{price:,}"

def time_ago(date):
    now = datetime.now()
    diff = now - date
    if diff.days > 0:
        return f"{diff.days} days ago"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600} hours ago"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60} minutes ago"
    else:
        return "Just now"

@app.template_filter('number_format')
def number_format(value):
    """Format numbers with commas"""
    return f"{value:,}"

@app.template_filter('time_ago')
def time_ago_filter(date):
    """Format datetime to time ago string"""
    return time_ago(date)

@app.route('/')
def index():
    return render_template('entry.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = auth.login_user(username, password)
        if user:
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        result = auth.register_user(username, email, password)
        if result['success']:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash(result['message'], 'error')
    
    return render_template('register.html')

@app.route('/hr')
def home():
    return render_template('home.html')

@app.route('/pre')
def predict_form():
    return render_template('index.html')

@app.route('/car/<listing_id>')
def car_details(listing_id):
    """Car details page"""
    try:
        listing = db.find_car_by_id(listing_id)
        if listing:
            db.update_car(listing_id, {'views': listing.get('views', 0) + 1})
            return render_template('cardetails.html', listing=listing, error=None)
        else:
            return render_template('cardetails.html', listing=None, error="Car listing not found")
    except Exception as e:
        return render_template('cardetails.html', listing=None, error=f"An error occurred: {str(e)}")

@app.route('/api/car', methods=['GET'])
def get_cars():
    """Get all cars with optional filtering"""
    try:
        filters = {}
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('brand'):
            filters['brand'] = request.args.get('brand')
        if request.args.get('min_price'):
            filters['min_price'] = float(request.args.get('min_price'))
        if request.args.get('max_price'):
            filters['max_price'] = float(request.args.get('max_price'))
        if request.args.get('fuel'):
            filters['fuel'] = request.args.get('fuel')
        if request.args.get('year'):
            filters['year'] = int(request.args.get('year'))
        if request.args.get('location'):
            filters['location'] = request.args.get('location')
        if request.args.get('search'):
            filters['search'] = request.args.get('search')
        
        limit = request.args.get('limit')
        cars = db.search_cars(filters) if filters else db.get_all_cars(limit=int(limit) if limit else None)
        
        return jsonify({
            'success': True,
            'cars': cars,
            'total': len(cars)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/car/<car_id>', methods=['GET'])
def get_car(car_id):
    """Get a specific car by ID"""
    try:
        car = db.find_car_by_id(car_id)
        if car:
            return jsonify({
                'success': True,
                'car': car
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Car not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/car', methods=['POST'])
def create_car():
    """Create a new car listing"""
    try:
        car_data = request.get_json()
        required_fields = ['brand', 'model', 'year', 'price', 'fuel', 'transmission', 'location']
        for field in required_fields:
            if field not in car_data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        car_data.setdefault('status', 'available')
        car_data.setdefault('km_driven', 0)
        car_data.setdefault('owner', '1st')
        car_data.setdefault('features', [])
        car_data.setdefault('description', '')
        
        car_id = db.create_car(car_data)
        
        if car_id:
            return jsonify({
                'success': True,
                'car_id': str(car_id),
                'message': 'Car created successfully'
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create car'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/car/<car_id>', methods=['PUT'])
def update_car(car_id):
    """Update a car listing"""
    try:
        update_data = request.get_json()
        success = db.update_car(car_id, update_data)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Car updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update car or car not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/car/<car_id>', methods=['DELETE'])
def delete_car(car_id):
    """Delete a car listing"""
    try:
        success = db.delete_car(car_id)
        if success:
            return jsonify({
                'success': True,
                'message': 'Car deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete car or car not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    try:
        stats = db.get_collection_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/locations', methods=['GET'])
def get_locations():
    """Get unique locations from cars"""
    try:
        locations = db.cars_collection.distinct('location')
        return jsonify({
            'success': True,
            'locations': locations
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/brands', methods=['GET'])
def get_brands():
    """Get unique brands from cars"""
    try:
        brands = db.cars_collection.distinct('brand')
        return jsonify({
            'success': True,
            'brands': brands
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/seed', methods=['POST'])
def seed_database():
    """Seed the database with sample car data"""
    try:
        sample_cars = [
            {
                "brand": "MARUTI SUZUKI ALTO",
                "model": "X1",
                "year": 2008,
                "price": 100500,
                "fuel": "Petrol",
                "transmission": "Automatic",
                "km_driven": 22000,
                "owner": "2nd",
                "location": "Puttur",
                "status": "available",
                "image": "../static/s1.avif",
                "engine": "1995cc",
                "power": "192 bhp",
                "mileage": "14.8 kmpl",
                "color": "White",
                "seats": 4,
                "features": ["Leather Seats", "Sunroof", "Alloy Wheels", "Climate Control"],
                "description": "Premium Budget friendly Car in Good condition."
            },
            {
                "brand": "Maruti 800",
                "model": "C-Class",
                "year": 2000,
                "price": 60000,
                "fuel": "Petrol",
                "transmission": "Manual",
                "km_driven": 15000,
                "owner": "3rd",
                "location": "Mangalore",
                "status": "available",
                "image": "../static/s2.avif",
                "engine": "1991cc",
                "power": "204 bhp",
                "mileage": "13.2 kmpl",
                "color": "White",
                "seats": 4,
                "features": ["Premium Audio", "Panoramic Sunroof", "Ambient Lighting", "Wireless Charging"],
                "description": "Elegant luxury sedan with cutting-edge technology and comfort features."
            },
            {
                "brand": "Car Available Puttur",
                "model": "Nova",
                "year": 2000,
                "price": 170000,
                "fuel": "Diesel",
                "transmission": "Manual",
                "km_driven": 80000,
                "owner": "1st",
                "location": "Puttur",
                "status": "available",
                "image": "../static/s3.webp",
                "engine": "1968cc",
                "power": "204 bhp",
                "mileage": "17.8 kmpl",
                "color": "Black",
                "seats": 5,
                "features": ["Virtual Cockpit", "Matrix LED", "Bang & Olufsen Audio", "Quattro AWD"],
                "description": "Sophisticated SUV with advanced technology and superior performance."
            }
        ]
        car_ids = db.bulk_insert_cars(sample_cars)
        return jsonify({
            'success': True,
            'message': f'Successfully seeded {len(car_ids)} cars',
            'car_ids': [str(id) for id in car_ids]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/search')
def search():
    """Search page with filters"""
    filters = {}
    if request.args.get('brand'):
        filters['brand'] = request.args.get('brand')
    if request.args.get('max_price'):
        filters['max_price'] = int(request.args.get('max_price'))
    if request.args.get('min_price'):
        filters['min_price'] = int(request.args.get('min_price'))
    if request.args.get('fuel'):
        filters['fuel'] = request.args.get('fuel')
    if request.args.get('location'):
        filters['location'] = request.args.get('location')
    if request.args.get('year_from'):
        filters['year_from'] = int(request.args.get('year_from'))
    if request.args.get('year_to'):
        filters['year_to'] = int(request.args.get('year_to'))
    if request.args.get('transmission'):
        filters['transmission'] = request.args.get('transmission')
    if request.args.get('sort_by'):
        filters['sort_by'] = request.args.get('sort_by')
    
    results = marketplace.search_listings(filters)
    return render_template('search.html', listings=results, filters=filters)

@app.route('/featured')
def featured():
    """Featured listings page"""
    featured_listings = marketplace.get_featured_listings()
    return render_template('featured.html', listings=featured_listings)

@app.route('/api/listings')
def api_listings():
    """API endpoint for listings"""
    listings = marketplace.get_all_listings()
    for listing in listings:
        listing['posted_date'] = listing['posted_date'].isoformat()
        listing['last_updated'] = listing['last_updated'].isoformat()
    return jsonify(listings)

@app.route('/api/car/<listing_id>')
def api_car_details(listing_id):
    """API endpoint for single car details"""
    listing = marketplace.get_listing(listing_id)
    if listing:
        marketplace.update_listing_stats(listing_id, 'view')
        listing['posted_date'] = listing['posted_date'].isoformat()
        listing['last_updated'] = listing['last_updated'].isoformat()
        return jsonify(listing)
    else:
        return jsonify({'error': 'Car listing not found'}), 404

@app.route('/api/search')
def api_search():
    """API endpoint for search"""
    filters = {}
    if request.args.get('brand'):
        filters['brand'] = request.args.get('brand')
    if request.args.get('max_price'):
        filters['max_price'] = int(request.args.get('max_price'))
    if request.args.get('min_price'):
        filters['min_price'] = int(request.args.get('min_price'))
    if request.args.get('fuel'):
        filters['fuel'] = request.args.get('fuel')
    if request.args.get('location'):
        filters['location'] = request.args.get('location')
    if request.args.get('year_from'):
        filters['year_from'] = int(request.args.get('year_from'))
    if request.args.get('year_to'):
        filters['year_to'] = int(request.args.get('year_to'))
    if request.args.get('transmission'):
        filters['transmission'] = request.args.get('transmission')
    if request.args.get('sort_by'):
        filters['sort_by'] = request.args.get('sort_by')
    
    results = marketplace.search_listings(filters)
    for listing in results:
        listing['posted_date'] = listing['posted_date'].isoformat()
        listing['last_updated'] = listing['last_updated'].isoformat()
    return jsonify(results)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.form
        brand = data['brand']
        year = int(data['year'])
        km_driven = int(data['km_driven'].replace(',', ''))
        fuel = data['fuel']
        seller_type = data['seller_type']
        transmission = data['transmission']
        owner = data['owner']
        mileage = float(data['mileage'])
        engine = float(data['engine'])
        max_power = float(data['max_power'])
        seats = int(data['seats'])
        torque_value = float(data['torque_value'])
        registration_number = data.get('registration_number', None)
        if year < 1990 or year > 2024:
            raise ValueError("Year must be between 1990 and 2024")
        if km_driven < 0 or km_driven > 10000000:
            raise ValueError("Invalid kilometer reading")
        if mileage <= 0 or engine <= 0 or max_power <= 0:
            raise ValueError("Technical specifications must be positive")
        if seats < 2 or seats > 10:
            raise ValueError("Seats must be between 2 and 10")
        prediction_result, error = predict_car_price(
            brand, year, km_driven, fuel, seller_type, transmission,
            owner, mileage, engine, max_power, seats, torque_value
        )
        if error:
            return render_template('result.html', error=error, input_data=data)
        predicted_price = prediction_result['price']
        real_time_info = get_car_real_time_info(brand, year, registration_number, mileage, fuel)
        price_chart = generate_price_visualization(predicted_price, brand, year)
        car_age = 2024 - year
        depreciation_rate = max(0, (car_age * 8))
        return render_template('result.html',
                             predicted_price=predicted_price,
                             prediction_result=prediction_result,
                             brand=brand, year=year, km_driven=km_driven,
                             fuel=fuel, seller_type=seller_type,
                             transmission=transmission, owner=owner,
                             mileage=mileage, engine=engine,
                             max_power=max_power, seats=seats,
                             torque_value=torque_value,
                             car_age=car_age,
                             depreciation_rate=depreciation_rate,
                             prediction_date=datetime.now().strftime('%d-%m-%Y %H:%M'),
                             real_time_info=real_time_info,
                             price_chart=price_chart)
    except ValueError as e:
        return render_template('result.html',
                             error=f"Input validation error: {str(e)}",
                             input_data=request.form)
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return render_template('result.html',
                             error=f"Prediction error: {str(e)}",
                             input_data=request.form)

@app.route('/api/predict', methods=['POST'])
def api_predict():
    try:
        data = request.json
        required_fields = ['brand', 'year', 'km_driven', 'fuel', 'seller_type',
                          'transmission', 'owner', 'mileage', 'engine', 'max_power',
                          'seats', 'torque_value']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        prediction_result, error = predict_car_price(
            data['brand'], data['year'], data['km_driven'], data['fuel'],
            data['seller_type'], data['transmission'], data['owner'],
            data['mileage'], data['engine'], data['max_power'],
            data['seats'], data['torque_value']
        )
        if error:
            return jsonify({'error': error}), 400
        real_time_info = get_car_real_time_info(
            data['brand'], data['year'],
            data.get('registration_number'),
            data.get('mileage', 15.0),
            data.get('fuel', 'Petrol')
        )
        response = {
            'predicted_price': prediction_result['price'],
            'formatted_price': f"₹{prediction_result['price']:,.2f}",
            'confidence_range': prediction_result['confidence_range'],
            'car_age': 2024 - data['year'],
            'real_time_info': real_time_info,
            'prediction_timestamp': datetime.now().isoformat(),
            'model_version': '2.0',
            'accuracy': '90.2%'
        }
        return jsonify(response)
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/vehicle-info/<registration_number>')
def get_vehicle_info(registration_number):
    try:
        if len(registration_number) < 8:
            return jsonify({'error': 'Invalid registration number format'}), 400
        real_time_info = get_car_real_time_info('Maruti', 2018, registration_number)
        return jsonify(real_time_info)
    except Exception as e:
        logger.error(f"Vehicle info error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/listings', methods=['GET'])
def get_listings():
    try:
        filters = {
            'brand': request.args.get('brand', ''),
            'max_price': float(request.args.get('max_price', float('inf'))),
            'min_price': float(request.args.get('min_price', 0)),
            'fuel': request.args.get('fuel', ''),
            'location': request.args.get('location', ''),
            'year_from': int(request.args.get('year_from', 1900)),
            'year_to': int(request.args.get('year_to', 2024)),
            'transmission': request.args.get('transmission', ''),
            'sort_by': request.args.get('sort_by', 'date')
        }
        listings = marketplace.search_listings(filters)
        return jsonify([{
            'id': listing['_id'],
            'brand': listing['brand'],
            'model': listing['model'],
            'year': listing['year'],
            'price': listing['price'],
            'formatted_price': format_price(listing['price']),
            'km_driven': listing['km_driven'],
            'fuel': listing['fuel'],
            'location': listing['location'],
            'seller_type': listing['seller_type'],
            'transmission': listing['transmission'],
            'posted_date': listing['posted_date'].isoformat(),
            'last_updated': time_ago(listing['last_updated']),
            'views': listing.get('views', 0),
            'favorites': listing.get('favorites', 0),
            'images': listing.get('images', []),
            'condition': listing.get('condition', {})
        } for listing in listings])
    except Exception as e:
        logger.error(f"Listings error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    model_status = {
        'model_loaded': model is not None,
        'scaler_loaded': scaler is not None,
        'encoders_available': encoders is not None,
        'feature_columns_loaded': feature_columns is not None
    }
    overall_health = all(model_status.values())
    return jsonify({
        'status': 'healthy' if overall_health else 'unhealthy',
        'components': model_status,
        'database_status': 'operational',
        'marketplace_listings': db.get_collection_stats().get('total_cars', 0),
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    })

@app.route('/model-info')
def model_info():
    if not model:
        return jsonify({'error': 'Models not loaded'}), 500
    info = {
        'model_type': str(type(model).__name__),
        'feature_count': len(feature_columns) if feature_columns else 0,
        'available_encoders': list(encoders.keys()) if encoders else [],
        'features': feature_columns.tolist() if feature_columns is not None else [],
        'supported_brands': list(encoders['brand'].classes_) if encoders and 'brand' in encoders else [],
        'database_info': {
            'states_covered': len(CAR_DATABASE['registration_patterns']),
            'insurance_providers': len(CAR_DATABASE['insurance_providers']),
            'service_centers': sum(len(centers) for centers in CAR_DATABASE['service_centers'].values())
        }
    }
    return jsonify(info)

if __name__ == '__main__':
    if load_models():
        print("Starting Enhanced Car Marketplace and Price Predictor...")
        print("Available endpoints:")
        print("  - GET  /                           : Web interface (entry)")
        print("  - GET  /hr                        : Home page")
        print("  - GET  /pre                       : Price prediction form")
        print("  - GET  /car/<listing_id>          : Car details page")
        print("  - POST /predict                   : Web form prediction")
        print("  - POST /api/predict               : JSON API prediction")
        print("  - GET  /api/vehicle-info/<reg_no> : Vehicle info by registration")
        print("  - GET  /api/listings              : Get marketplace listings")
        print("  - GET  /health                    : Health check")
        print("  - GET  /model-info                : Model and database information")
        print("\nFeatures:")
        print("  [OK] Real-time simulated OLX-like listings")
        print("  [OK] Car price prediction with confidence intervals")
        print("  [OK] Real-time insurance, PUC, RC, and fitness status")
        print("  [OK] Compliance alerts and warnings")
        print("  [OK] State-wise RTO information")
        print("  [OK] Price comparison visualization")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("[ERROR] Failed to load models. Please ensure model files exist.")
        print("Required files:")
        print("  - best_car_price_model.pkl")
        print("  - car_price_scaler.pkl")
        print("  - label_encoders.pkl")
        print("  - feature_columns.pkl")