import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid

class CarMarketplace:
    def __init__(self):
        self.listings = {}
        self.categories = {
            'luxury': ['BMW', 'Mercedes-Benz', 'Audi', 'Jaguar', 'Lexus', 'Porsche'],
            'premium': ['Honda', 'Toyota', 'Hyundai', 'Volkswagen', 'Skoda', 'Nissan'],
            'budget': ['Maruti', 'Tata', 'Mahindra', 'Datsun', 'Renault'],
            'sports': ['Ferrari', 'Lamborghini', 'Maserati', 'Bentley'],
            'suv': ['Ford', 'Chevrolet', 'Jeep', 'Land Rover']
        }
        
        # Initialize with sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize marketplace with sample car listings"""
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
    
    def add_listing(self, car_data: Dict) -> str:
        """Add a new car listing to the marketplace"""
        listing_id = str(uuid.uuid4())[:8]
        
        # Generate additional details
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
            
            # Additional marketplace details
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
            'home_inspection': random.choice([True, False]),
            'urgent_sale': random.choice([True, False]),
            'reason_for_sale': random.choice([
                'Buying new car', 'Relocating', 'Financial reasons',
                'Upgrading', 'Multiple cars', 'Rarely used'
            ])
        }
        
        self.listings[listing_id] = listing
        return listing_id
    
    def _generate_seller_info(self, seller_type: str) -> Dict:
        """Generate seller information"""
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
        """Generate detailed car specifications"""
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
            'engine_number': f"ENG{random.randint(100000, 999999)}"
        }
    
    def _generate_image_urls(self, brand: str, model: str) -> List[str]:
        """Generate sample image URLs for the car"""
        base_url = "https://example.com/car-images/"
        images = []
        for i in range(random.randint(8, 15)):
            images.append(f"{base_url}{brand.lower()}-{model.lower()}-{i+1}.jpg")
        return images
    
    def _assess_condition(self, year: int, km_driven: int) -> Dict:
        """Assess car condition based on year and mileage"""
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
        """Generate car features based on brand and year"""
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
        """Generate inspection report"""
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
        """Generate price history for the listing"""
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
        """Generate contact information"""
        return {
            'phone': f"+91-{random.randint(70000, 99999)}{random.randint(10000, 99999)}",
            'whatsapp_available': random.choice([True, False]),
            'email': f"seller{random.randint(100, 999)}@example.com",
            'preferred_contact': random.choice(['Phone', 'WhatsApp', 'Email']),
            'available_hours': "9 AM - 8 PM",
            'call_preference': random.choice(['Anytime', 'After 6 PM', 'Weekends only'])
        }
    
    def _calculate_warranty(self, year: int) -> Dict:
        """Calculate remaining warranty"""
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
        """Generate service history"""
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
        """Generate ownership history"""
        return {
            'total_owners': random.randint(1, 3),
            'current_owner_duration': f"{random.randint(1, 5)} years",
            'usage_type': random.choice(['Personal', 'Commercial', 'Taxi']),
            'driven_by': random.choice(['Owner', 'Chauffeur', 'Family Members']),
            'parking_type': random.choice(['Covered', 'Open', 'Street'])
        }
    
    def _get_registration_state(self, location: str) -> str:
        """Get registration state based on location"""
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
        """Generate insurance status"""
        return {
            'valid_until': (datetime.now() + timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d'),
            'insurance_type': random.choice(['Comprehensive', 'Third Party', 'Zero Depreciation']),
            'claim_history': random.randint(0, 2),
            'no_claim_bonus': f"{random.randint(0, 50)}%",
            'transferable': random.choice([True, False])
        }
    
    def _generate_accident_history(self) -> Dict:
        """Generate accident history"""
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
        """Generate modification details"""
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
        """Get a specific listing by ID"""
        return self.listings.get(listing_id)
    
    def get_all_listings(self) -> List[Dict]:
        """Get all listings"""
        return list(self.listings.values())
    
    def search_listings(self, filters: Dict) -> List[Dict]:
        """Search listings based on filters"""
        results = []
        
        for listing in self.listings.values():
            match = True
            
            # Apply filters
            if 'brand' in filters and listing['brand'].lower() != filters['brand'].lower():
                match = False
            if 'max_price' in filters and listing['price'] > filters['max_price']:
                match = False
            if 'min_price' in filters and listing['price'] < filters['min_price']:
                match = False
            if 'fuel' in filters and listing['fuel'].lower() != filters['fuel'].lower():
                match = False
            if 'location' in filters and filters['location'].lower() not in listing['location'].lower():
                match = False
            if 'year_from' in filters and listing['year'] < filters['year_from']:
                match = False
            if 'year_to' in filters and listing['year'] > filters['year_to']:
                match = False
            if 'transmission' in filters and listing['transmission'].lower() != filters['transmission'].lower():
                match = False
            
            if match:
                results.append(listing)
        
        # Sort by relevance (price, date, etc.)
        if 'sort_by' in filters:
            if filters['sort_by'] == 'price_low':
                results.sort(key=lambda x: x['price'])
            elif filters['sort_by'] == 'price_high':
                results.sort(key=lambda x: x['price'], reverse=True)
            elif filters['sort_by'] == 'date':
                results.sort(key=lambda x: x['posted_date'], reverse=True)
            elif filters['sort_by'] == 'km_low':
                results.sort(key=lambda x: x['km_driven'])
        
        return results
    
    def get_featured_listings(self, limit: int = 6) -> List[Dict]:
        """Get featured listings"""
        all_listings = list(self.listings.values())
        
        # Sort by a combination of factors (views, favorites, recency)
        featured = sorted(all_listings, 
                         key=lambda x: (x['views'] + x['favorites'] * 2), 
                         reverse=True)
        
        return featured[:limit]
    
    def get_similar_cars(self, listing_id: str, limit: int = 4) -> List[Dict]:
        """Get similar cars for a given listing"""
        if listing_id not in self.listings:
            return []
        
        target_listing = self.listings[listing_id]
        similar = []
        
        for lid, listing in self.listings.items():
            if lid == listing_id:
                continue
            
            # Calculate similarity score
            score = 0
            
            # Same brand
            if listing['brand'] == target_listing['brand']:
                score += 3
            
            # Similar price range (±30%)
            price_diff = abs(listing['price'] - target_listing['price']) / target_listing['price']
            if price_diff <= 0.3:
                score += 2
            
            # Similar year (±3 years)
            year_diff = abs(listing['year'] - target_listing['year'])
            if year_diff <= 3:
                score += 1
            
            # Same fuel type
            if listing['fuel'] == target_listing['fuel']:
                score += 1
            
            # Same location
            if listing['location'] == target_listing['location']:
                score += 1
            
            if score > 0:
                listing['similarity_score'] = score
                similar.append(listing)
        
        # Sort by similarity score
        similar.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return similar[:limit]
    
    def update_listing_stats(self, listing_id: str, action: str):
        """Update listing statistics"""
        if listing_id in self.listings:
            if action == 'view':
                self.listings[listing_id]['views'] += 1
            elif action == 'favorite':
                self.listings[listing_id]['favorites'] += 1
            
            self.listings[listing_id]['last_updated'] = datetime.now()
    
    def get_marketplace_stats(self) -> Dict:
        """Get marketplace statistics"""
        total_listings = len(self.listings)
        total_value = sum(listing['price'] for listing in self.listings.values())
        
        brands = {}
        fuel_types = {}
        locations = {}
        
        for listing in self.listings.values():
            # Count brands
            brands[listing['brand']] = brands.get(listing['brand'], 0) + 1
            
            # Count fuel types
            fuel_types[listing['fuel']] = fuel_types.get(listing['fuel'], 0) + 1
            
            # Count locations
            locations[listing['location']] = locations.get(listing['location'], 0) + 1
        
        return {
            'total_listings': total_listings,
            'total_value': total_value,
            'average_price': total_value // total_listings if total_listings > 0 else 0,
            'brands_distribution': brands,
            'fuel_types_distribution': fuel_types,
            'locations_distribution': locations,
            'latest_listings': sorted(self.listings.values(), 
                                    key=lambda x: x['posted_date'], 
                                    reverse=True)[:5]
        }

# Initialize global marketplace instance
marketplace = CarMarketplace()

# Utility functions for Flask integration
def get_marketplace_instance():
    """Get the global marketplace instance"""
    return marketplace

def format_price(price):
    """Format price in Indian currency format"""
    if price >= 10000000:  # 1 crore
        return f"₹{price/10000000:.1f} Cr"
    elif price >= 100000:  # 1 lakh
        return f"₹{price/100000:.1f} L"
    else:
        return f"₹{price:,}"

def time_ago(date):
    """Calculate time ago from given date"""
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