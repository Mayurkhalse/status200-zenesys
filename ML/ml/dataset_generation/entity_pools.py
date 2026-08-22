"""
Entity Pools for synthetic document generation.
Contains realistic companies, counterparties, addresses, products, services, and financial terms.
"""
import random

COMPANIES = [
    "Nova Systems Ltd", "Apex Global Trading", "Zenith Logistics Inc", "Vanguard Healthcare",
    "Nexus Tech Solutions", "Horizon Construction Corp", "Orion Wholesale Supplies",
    "Starlight Retail Group", "Quantum Finance Partners", "EcoEnergy Services",
    "Pinnacle Automotive Ltd", "Aegis Consulting Group", "Summit Education Media",
    "Matrix Manufacturing Co", "Infinitum Software Solutions"
]

COUNTERPARTIES = [
    "ABC Technologies Pvt Ltd", "Global Retail Chains LLC", "Universal Supplies Corp",
    "Acme Enterprises", "Omega Distributors", "Delta Engineering Solutions",
    "Atlas Freight Services", "Beacon Health Systems", "Crestview Media Corp",
    "Synergy Corp International", "Titan Heavy Machinery", "Velocity Software Inc"
]

CITIES = [
    ("Mumbai", "Maharashtra", "India"),
    ("New York", "NY", "United States"),
    ("London", "Greater London", "United Kingdom"),
    ("Berlin", "Berlin State", "Germany"),
    ("Singapore", "Central Region", "Singapore"),
    ("Bengaluru", "Karnataka", "India"),
    ("Chicago", "IL", "United States")
]

PRODUCTS_SERVICES = {
    "IT_SERVICES": [
        ("Cloud Infrastructure Management", 1500.0, "Hours"),
        ("Custom ERP Software Development", 12000.0, "Units"),
        ("Cybersecurity Audit & Compliance", 3500.0, "Services"),
        ("Managed IT Helpdesk Support", 800.0, "Months"),
        ("Database Migration Service", 2500.0, "Projects")
    ],
    "MANUFACTURING": [
        ("Industrial Steel Bolts (M10)", 15.0, "Boxes"),
        ("Precision CNC Machined Valves", 450.0, "Units"),
        ("Heavy Duty Conveyor Belts", 1200.0, "Meters"),
        ("Hydraulic Cylinder Assembly", 850.0, "Units"),
        ("Aluminum Alloy Sheets (4x8ft)", 120.0, "Sheets")
    ],
    "RETAIL": [
        ("Wireless Ergonomic Keyboards", 45.0, "Units"),
        ("4K Ultra HD Monitors 27-inch", 320.0, "Units"),
        ("Smart Office Chairs", 210.0, "Units"),
        ("USB-C Multi-port Hubs", 35.0, "Units"),
        ("Noise Cancelling Headsets", 130.0, "Units")
    ],
    "HEALTHCARE": [
        ("Digital Patient Monitors", 2200.0, "Units"),
        ("Surgical Glove Boxes (Powder-Free)", 25.0, "Boxes"),
        ("Diagnostic Ultrasound Scanners", 18000.0, "Units"),
        ("Infusion Pumps", 1100.0, "Units"),
        ("Medical Face Masks (Pack of 50)", 12.0, "Packs")
    ],
    "CONSTRUCTION": [
        ("Portland Cement (50kg Bags)", 12.0, "Bags"),
        ("Structural Steel I-Beams", 750.0, "Tons"),
        ("Ready-Mix Concrete (M30)", 95.0, "Cubic Meters"),
        ("Safety Helmets & Harnesses", 35.0, "Sets"),
        ("Reinforced Rebar 12mm", 620.0, "Tons")
    ]
}

DEFAULT_PRODUCTS = [
    ("Enterprise Software License", 500.0, "Licenses"),
    ("Technical Support Retainer", 1000.0, "Months"),
    ("Consulting Services", 150.0, "Hours"),
    ("Hardware Maintenance", 300.0, "Services")
]

PAYMENT_TERMS_LIST = [
    "Net 30 Days", "Net 15 Days", "Due on Receipt", "50% Advance, 50% on Delivery", "Net 60 Days"
]

def get_random_company():
    return random.choice(COMPANIES)

def get_random_counterparty():
    return random.choice(COUNTERPARTIES)

def get_random_location():
    city, state, country = random.choice(CITIES)
    street = f"{random.randint(100, 999)} Business Park Road, Suite {random.randint(1, 50)}"
    return {"street": street, "city": city, "state": state, "country": country}

def get_random_items(industry="IT_SERVICES", count=3):
    pool = PRODUCTS_SERVICES.get(industry, DEFAULT_PRODUCTS)
    selected = random.sample(pool, min(count, len(pool)))
    items = []
    for name, base_price, unit in selected:
        qty = random.randint(1, 10)
        price = round(base_price * random.uniform(0.9, 1.1), 2)
        total = round(qty * price, 2)
        items.append({
            "description": name,
            "quantity": qty,
            "unit": unit,
            "unit_price": price,
            "total_price": total
        })
    return items
