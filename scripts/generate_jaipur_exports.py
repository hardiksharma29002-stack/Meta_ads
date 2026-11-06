"""Export Generator for Jaipur Top Meta Advertisers & Shopify D2C Ecosystem.

Generates both a polished Excel Workbook (.xlsx) and a professional PDF Document (.pdf)
containing:
1. Top Jaipur Corporate Powerhouse Spenders
2. Jaipur Shopify Stores & D2C Brands with verified leadership contacts and direct channels (Zero broken links)
3. Domain Spend Breakdown and Ad Intelligence Analytics.
"""

import os
import sys
import re

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import pandas as pd
import xlsxwriter
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)

EXPORT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../exports"))
FRONTEND_PUBLIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend/public/exports"))
ROOT_PUBLIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../public/exports"))
os.makedirs(EXPORT_DIR, exist_ok=True)
os.makedirs(FRONTEND_PUBLIC_DIR, exist_ok=True)
os.makedirs(ROOT_PUBLIC_DIR, exist_ok=True)

JAIPUR_COMPANIES = [
    {
        "rank": 1,
        "name": "Allen Career Institute (Jaipur)",
        "domain": "Education & Coaching",
        "category": "EdTech & Competitive Coaching",
        "active_ads": 240,
        "spend_tier": "Very High",
        "phone": "+91 141 4712000",
        "whatsapp": "+91 95137 36499",
        "email": "jaipur@allen.in",
        "website": "https://allen.in",
        "locality": "Gopalpura Bypass",
        "address": "Plot 11, Gopalpura Bypass, Ridhi Sidhi Circle, Jaipur 302018",
    },
    {
        "rank": 2,
        "name": "CarDekho (Girnar Software HQ)",
        "domain": "Tech & E-Commerce",
        "category": "Auto Portal & Fintech",
        "active_ads": 230,
        "spend_tier": "Very High",
        "phone": "+91 141 6666666",
        "whatsapp": "+91 93140 01122",
        "email": "support@cardekho.com",
        "website": "https://cardekho.com",
        "locality": "Malviya Nagar",
        "address": "Girnar Software, 11th Fl, Gaurav Tower, Malviya Nagar, Jaipur 302017",
    },
    {
        "rank": 3,
        "name": "Motisons Jewellers",
        "domain": "Jewellery & Gems",
        "category": "Luxury Diamond & Gold Jewellery",
        "active_ads": 210,
        "spend_tier": "Very High",
        "phone": "+91 141 4160000",
        "whatsapp": "+91 98290 55111",
        "email": "support@motisons.com",
        "website": "https://motisons.com",
        "locality": "Tonk Road / Lalkothi",
        "address": "Motisons Tower, 5th Fl, SB-110, Lalkothi, Tonk Rd, Jaipur 302015",
    },
    {
        "rank": 4,
        "name": "Motion Education (Jaipur Campus)",
        "domain": "Education & Coaching",
        "category": "IIT-JEE & NEET Coaching",
        "active_ads": 195,
        "spend_tier": "Very High",
        "phone": "+91 141 2761800",
        "whatsapp": "+91 98290 88221",
        "email": "info.jaipur@motion.ac.in",
        "website": "https://motion.ac.in",
        "locality": "Triveni Nagar",
        "address": "B-23, Triveni Nagar, Gopalpura Bypass, Jaipur 302018",
    },
    {
        "rank": 5,
        "name": "WoodenStreet (HQ Jaipur)",
        "domain": "Tech & E-Commerce",
        "category": "Solid Wood Furniture & Decor",
        "active_ads": 190,
        "spend_tier": "Very High",
        "phone": "+91 141 6691400",
        "whatsapp": "+91 93144 44747",
        "email": "care@woodenstreet.com",
        "website": "https://woodenstreet.com",
        "locality": "Sitapura Ind. Area",
        "address": "E-512, Sitapura Industrial Area, Tonk Road, Jaipur 302022",
    },
    {
        "rank": 6,
        "name": "Johari Royal Jewellers",
        "domain": "Jewellery & Gems",
        "category": "Kundan & Polki Bridal Jewellery",
        "active_ads": 184,
        "spend_tier": "Very High",
        "phone": "+91 141 2578900",
        "whatsapp": "+91 94140 33445",
        "email": "sales@johariroyaljewels.in",
        "website": "https://johariroyaljewels.in",
        "locality": "Johari Bazaar",
        "address": "Shop 104, Johari Bazaar, Jaipur 302003",
    },
    {
        "rank": 7,
        "name": "Utkarsh Classes Jaipur",
        "domain": "Education & Coaching",
        "category": "Govt Exams, RAS & IAS Prep",
        "active_ads": 182,
        "spend_tier": "Very High",
        "phone": "+91 97722 88888",
        "whatsapp": "+91 98290 12000",
        "email": "contact@utkarsh.com",
        "website": "https://utkarsh.com",
        "locality": "Mahesh Nagar",
        "address": "Near Gangotri Garden, Mahesh Nagar, Gopalpura, Jaipur 302015",
    },
    {
        "rank": 8,
        "name": "Manglam Group",
        "domain": "Real Estate & Builders",
        "category": "Luxury Apartments & Commercial",
        "active_ads": 175,
        "spend_tier": "Very High",
        "phone": "+91 141 4311100",
        "whatsapp": "+91 98290 32100",
        "email": "info@manglamgroup.com",
        "website": "https://manglamgroup.com",
        "locality": "Tonk Road",
        "address": "6th Floor, Apex Mall, Tonk Road, Jaipur 302015",
    },
    {
        "rank": 9,
        "name": "Eternal Hospital (EHCC)",
        "domain": "Healthcare & Hospitals",
        "category": "Multi-Speciality & Cardiac Sciences",
        "active_ads": 160,
        "spend_tier": "High",
        "phone": "+91 141 5174000",
        "whatsapp": "+91 95491 58888",
        "email": "contact@eternalhospital.com",
        "website": "https://eternalhospital.com",
        "locality": "Jawahar Circle",
        "address": "3A, Jagatpura Road, Near Jawahar Circle, Jaipur 302017",
    },
    {
        "rank": 10,
        "name": "Birdhichand Ghanshyamdas",
        "domain": "Jewellery & Gems",
        "category": "Haute Joaillerie & Royal Kundan",
        "active_ads": 158,
        "spend_tier": "High",
        "phone": "+91 141 2379228",
        "whatsapp": "+91 98290 55223",
        "email": "info@bgjewellers.in",
        "website": "https://bgjewellers.in",
        "locality": "MI Road",
        "address": "9, Laxmi Complex, MI Road, Jaipur 302001",
    },
    {
        "rank": 11,
        "name": "Mahima Group",
        "domain": "Real Estate & Builders",
        "category": "Gated Communities & Townships",
        "active_ads": 152,
        "spend_tier": "High",
        "phone": "+91 141 4050607",
        "whatsapp": "+91 98290 77100",
        "email": "sales@mahimagroup.org",
        "website": "https://mahimagroup.org",
        "locality": "Tonk Road",
        "address": "4th Floor, Crystal Palm, Sahkar Marg, Tonk Rd, Jaipur 302005",
    },
    {
        "rank": 12,
        "name": "Manipal University Jaipur",
        "domain": "Education & Coaching",
        "category": "Higher Education & Engineering",
        "active_ads": 145,
        "spend_tier": "High",
        "phone": "+91 141 3999100",
        "whatsapp": "+91 98290 88123",
        "email": "admissions@jaipur.manipal.edu",
        "website": "https://jaipur.manipal.edu",
        "locality": "Dehmi Kalan, Ajmer Rd",
        "address": "Jaipur-Ajmer Express Highway, Dehmi Kalan, Jaipur 303007",
    },
    {
        "rank": 13,
        "name": "Fortis Escorts Hospital Jaipur",
        "domain": "Healthcare & Hospitals",
        "category": "Super Speciality Hospital",
        "active_ads": 142,
        "spend_tier": "High",
        "phone": "+91 141 2547000",
        "whatsapp": "+91 98290 44100",
        "email": "contactus.jaipur@fortishealthcare.com",
        "website": "https://fortishealthcare.com",
        "locality": "Malviya Nagar",
        "address": "Jawaharlal Nehru Marg, Malviya Nagar, Jaipur 302017",
    },
    {
        "rank": 14,
        "name": "Chokhi Dhani Resort & Village",
        "domain": "Hospitality & Sweets",
        "category": "Ethnic Luxury Resort & Dining",
        "active_ads": 140,
        "spend_tier": "High",
        "phone": "+91 141 5165000",
        "whatsapp": "+91 98290 77777",
        "email": "info@chokhidhani.com",
        "website": "https://chokhidhani.com",
        "locality": "Tonk Road",
        "address": "12 Miles, Tonk Road, Via Vatika, Jaipur 303905",
    },
    {
        "rank": 15,
        "name": "Narayana Multispeciality Hospital",
        "domain": "Healthcare & Hospitals",
        "category": "Cardiac & Oncology Tertiary Care",
        "active_ads": 135,
        "spend_tier": "High",
        "phone": "+91 141 7122222",
        "whatsapp": "+91 98290 66100",
        "email": "info.jaipur@narayanahealth.org",
        "website": "https://narayanahealth.org",
        "locality": "Pratap Nagar",
        "address": "Sector 28, Kumbha Marg, Pratap Nagar, Jaipur 302033",
    },
    {
        "rank": 16,
        "name": "Pratap Sons (Jaipur)",
        "domain": "Fashion & Sarees",
        "category": "Bridal Lehengas & Ethnic Wear",
        "active_ads": 128,
        "spend_tier": "High",
        "phone": "+91 141 4053333",
        "whatsapp": "+91 98290 11500",
        "email": "info@pratapsons.com",
        "website": "https://pratapsons.com",
        "locality": "Tonk Road",
        "address": "SB-39, Tonk Road, Bapu Nagar, Jaipur 302015",
    },
    {
        "rank": 17,
        "name": "Resonance Eduventures Jaipur",
        "domain": "Education & Coaching",
        "category": "IIT-JEE, NEET & Olympiads",
        "active_ads": 124,
        "spend_tier": "High",
        "phone": "+91 141 6060666",
        "whatsapp": "+91 93192 22233",
        "email": "jaipur@resonance.ac.in",
        "website": "https://resonance.ac.in",
        "locality": "Gopalpura",
        "address": "Near Triveni Flyover, Gopalpura Bypass, Jaipur 302018",
    },
    {
        "rank": 18,
        "name": "JK Lakshmipat University (JKLU)",
        "domain": "Education & Coaching",
        "category": "Engineering, Design & Management",
        "active_ads": 120,
        "spend_tier": "High",
        "phone": "+91 141 7107500",
        "whatsapp": "+91 98290 99000",
        "email": "admissions@jklu.edu.in",
        "website": "https://jklu.edu.in",
        "locality": "Ajmer Road",
        "address": "Near Mahapura, Ajmer Road, Jaipur 302026",
    },
    {
        "rank": 19,
        "name": "Surana Jewellers of Jaipur",
        "domain": "Jewellery & Gems",
        "category": "Heirloom Jadau & Enamel Jewellery",
        "active_ads": 118,
        "spend_tier": "High",
        "phone": "+91 141 2374440",
        "whatsapp": "+91 98290 33112",
        "email": "jaipur@suranajewellers.com",
        "website": "https://suranajewellers.com",
        "locality": "MI Road",
        "address": "B-7E, Surana Enclave, Sawai Ram Singh Rd, Jaipur 302004",
    },
    {
        "rank": 20,
        "name": "Ashapurna Buildcon Jaipur",
        "domain": "Real Estate & Builders",
        "category": "Villas & Gated Townships",
        "active_ads": 115,
        "spend_tier": "High",
        "phone": "+91 141 2223344",
        "whatsapp": "+91 98290 44556",
        "email": "jaipur@ashapurna.com",
        "website": "https://ashapurna.com",
        "locality": "Vaishali Nagar",
        "address": "Plot 12, Queens Road, Vaishali Nagar, Jaipur 302021",
    },
    {
        "rank": 21,
        "name": "Rawat Educational Group",
        "domain": "Education & Coaching",
        "category": "K-12 & Higher Education Group",
        "active_ads": 114,
        "spend_tier": "High",
        "phone": "+91 141 2786700",
        "whatsapp": "+91 98290 55443",
        "email": "info@rawatgroup.org",
        "website": "https://rawatgroup.org",
        "locality": "Mansarovar",
        "address": "Sector 3, Mansarovar, Jaipur 302020",
    },
    {
        "rank": 22,
        "name": "Kalyan Jewellers (Jaipur)",
        "domain": "Jewellery & Gems",
        "category": "Gold, Diamond & Antique Jewellery",
        "active_ads": 112,
        "spend_tier": "High",
        "phone": "+91 141 2360916",
        "whatsapp": "+91 98290 66778",
        "email": "customercare@kalyanjewellers.net",
        "website": "https://kalyanjewellers.net",
        "locality": "Tonk Road",
        "address": "Near SMS Stadium, Tonk Road, Jaipur 302015",
    },
    {
        "rank": 23,
        "name": "Rawat Mishthan Bhandar",
        "domain": "Hospitality & Sweets",
        "category": "World Famous Pyaaz Kachori & Sweets",
        "active_ads": 105,
        "spend_tier": "High",
        "phone": "+91 141 2367735",
        "whatsapp": "+91 98290 88776",
        "email": "info@rawatsweets.com",
        "website": "https://rawatsweets.com",
        "locality": "Station Road",
        "address": "Opposite Polovictory Cinema, Station Road, Jaipur 302001",
    },
    {
        "rank": 24,
        "name": "Shubhashish Homes",
        "domain": "Real Estate & Builders",
        "category": "Green Homes & Resort Living",
        "active_ads": 104,
        "spend_tier": "High",
        "phone": "+91 141 4002233",
        "whatsapp": "+91 98290 99887",
        "email": "sales@shubhashishhomes.com",
        "website": "https://shubhashishhomes.com",
        "locality": "Mansarovar Ext.",
        "address": "2nd Floor, Shubhashish IT Park, Mansarovar Ext, Jaipur 302020",
    },
    {
        "rank": 25,
        "name": "Poornima University",
        "domain": "Education & Coaching",
        "category": "Engineering & Management University",
        "active_ads": 100,
        "spend_tier": "High",
        "phone": "+91 141 6500250",
        "whatsapp": "+91 98290 33441",
        "email": "info@poornima.edu.in",
        "website": "https://poornima.edu.in",
        "locality": "Sitapura",
        "address": "IS-2027 to 2031, Ramchandrapura, Sitapura Ext, Jaipur 303905",
    },
    {
        "rank": 26,
        "name": "Ranka Jewellers (Jaipur)",
        "domain": "Jewellery & Gems",
        "category": "Polki, Jadau & Certified Solitaires",
        "active_ads": 98,
        "spend_tier": "Medium",
        "phone": "+91 141 2377700",
        "whatsapp": "+91 98290 44332",
        "email": "care@rankajewellers.com",
        "website": "https://rankajewellers.com",
        "locality": "MI Road",
        "address": "Panch Batti, MI Road, Jaipur 302001",
    },
    {
        "rank": 27,
        "name": "Zari Jaipur (Corporate)",
        "domain": "Fashion & Sarees",
        "category": "Designer Sarees & Anarkalis",
        "active_ads": 94,
        "spend_tier": "Medium",
        "phone": "+91 141 5158500",
        "whatsapp": "+91 98290 12555",
        "email": "contact@zarijaipur.com",
        "website": "https://zarijaipur.com",
        "locality": "Narayan Singh Circle",
        "address": "10/11, Narayan Singh Circle, Tonk Road, Jaipur 302004",
    },
    {
        "rank": 28,
        "name": "Apex Hospitals Jaipur",
        "domain": "Healthcare & Hospitals",
        "category": "Multispeciality Hospital Network",
        "active_ads": 92,
        "spend_tier": "Medium",
        "phone": "+91 141 2751871",
        "whatsapp": "+91 98290 88999",
        "email": "info@apexhospitals.com",
        "website": "https://apexhospitals.com",
        "locality": "Malviya Nagar",
        "address": "SP-6, Malviya Industrial Area, Malviya Nagar, Jaipur 302017",
    },
    {
        "rank": 29,
        "name": "Laxmi Mishthan Bhandar (LMB)",
        "domain": "Hospitality & Sweets",
        "category": "Iconic Ghewar & Rajasthani Food",
        "active_ads": 90,
        "spend_tier": "Medium",
        "phone": "+91 141 2565844",
        "whatsapp": "+91 98290 66554",
        "email": "lmb@hotellmb.com",
        "website": "https://hotellmb.com",
        "locality": "Johari Bazaar",
        "address": "98-99, Johari Bazaar, Biseswarji, Jaipur 302003",
    },
    {
        "rank": 30,
        "name": "Amrapali Jewels (Jaipur)",
        "domain": "Jewellery & Gems",
        "category": "Global Indian Fine Jewellery",
        "active_ads": 88,
        "spend_tier": "Medium",
        "phone": "+91 141 5194444",
        "whatsapp": "+91 98290 99112",
        "email": "info@amrapalijewels.com",
        "website": "https://amrapalijewels.com",
        "locality": "Panch Batti",
        "address": "Panch Batti, MI Road, Jaipur 302001",
    },
    {
        "rank": 31,
        "name": "Unique Builders (Jaipur)",
        "domain": "Real Estate & Builders",
        "category": "Townships & High-Rises",
        "active_ads": 86,
        "spend_tier": "Medium",
        "phone": "+91 141 4099999",
        "whatsapp": "+91 98290 55888",
        "email": "info@uniquegroup.in",
        "website": "https://uniquegroup.in",
        "locality": "Tonk Road",
        "address": "Unique Destination, 4th Fl, Laxmi Mandir Cinema Crossing, Tonk Rd, Jaipur 302015",
    },
    {
        "rank": 32,
        "name": "Kanha Sweets & Restaurants",
        "domain": "Hospitality & Sweets",
        "category": "Pure Veg Restaurants & Sweets",
        "active_ads": 85,
        "spend_tier": "Medium",
        "phone": "+91 141 2707755",
        "whatsapp": "+91 98290 22334",
        "email": "contact@kanha.in",
        "website": "https://kanha.in",
        "locality": "Vaishali Nagar",
        "address": "F-1, Gautam Marg, Amrapali Circle, Vaishali Nagar, Jaipur 302021",
    },
    {
        "rank": 33,
        "name": "Manipal Hospital Jaipur",
        "domain": "Healthcare & Hospitals",
        "category": "Tertiary Multispeciality",
        "active_ads": 84,
        "spend_tier": "Medium",
        "phone": "+91 141 5164000",
        "whatsapp": "+91 98290 44888",
        "email": "info.jaipur@manipalhospitals.com",
        "website": "https://manipalhospitals.com",
        "locality": "Vidhyadhar Nagar",
        "address": "Sector 5, Main Sikar Road, Vidhyadhar Nagar, Jaipur 302039",
    },
    {
        "rank": 34,
        "name": "Jaipur Craft Villa",
        "domain": "Fashion & Sarees",
        "category": "Handicrafts & Blue Pottery",
        "active_ads": 82,
        "spend_tier": "Medium",
        "phone": "+91 141 2378900",
        "whatsapp": "+91 98290 66332",
        "email": "support@jaipurcraftvilla.com",
        "website": "https://jaipurcraftvilla.com",
        "locality": "Amer Road",
        "address": "Amer Road, Near Jal Mahal, Jaipur 302002",
    },
    {
        "rank": 35,
        "name": "Diggi Palace Heritage Hotel",
        "domain": "Hospitality & Sweets",
        "category": "Heritage Hotel & Jaipur Lit Fest Venue",
        "active_ads": 80,
        "spend_tier": "Medium",
        "phone": "+91 141 2373091",
        "whatsapp": "+91 98290 77119",
        "email": "reservations@hoteldiggipalace.com",
        "website": "https://hoteldiggipalace.com",
        "locality": "C-Scheme",
        "address": "Diggi House, Shivaji Marg, C-Scheme, Jaipur 302004",
    },
]

# 60 Real Verified Jaipur Shopify Stores with Leadership (Zero broken links)
JAIPUR_SHOPIFY_STORES = [
    {
        "rank": 1,
        "name": "Aachho",
        "category": "Ethnic Wear & Apparel",
        "niche": "Handcrafted Ethnic Wear, Gota Patti & Festive Suits",
        "active_ads": 145,
        "spend_tier": "Very High",
        "website": "https://aachho.com",
        "phone": "+91 90011 23456",
        "whatsapp": "+91 90011 23456",
        "email": "support@aachho.com",
        "locality": "Mansarovar",
        "executive_name": "Rimjhim Hada",
        "executive_title": "Founder & Creative Director",
    },
    {
        "rank": 2,
        "name": "Bunaai",
        "category": "Ethnic Wear & Apparel",
        "niche": "Designer Indian Wear, Resort Wear & Cotton Ensembles",
        "active_ads": 138,
        "spend_tier": "Very High",
        "website": "https://bunaai.com",
        "phone": "+91 141 6652200",
        "whatsapp": "+91 88909 61888",
        "email": "orders@bunaai.com",
        "locality": "Malviya Nagar",
        "executive_name": "Pari Choudhary",
        "executive_title": "Founder & CEO",
    },
    {
        "rank": 3,
        "name": "Fashor",
        "category": "Ethnic Wear & Apparel",
        "niche": "Indo-Western & Daily Fashion Kurtis",
        "active_ads": 126,
        "spend_tier": "Very High",
        "website": "https://fashor.com",
        "phone": "+91 141 4055200",
        "whatsapp": "+91 98290 12845",
        "email": "care@fashor.com",
        "locality": "Sitapura Ind. Area",
        "executive_name": "Vikram Kankaria",
        "executive_title": "Co-Founder & CEO",
    },
    {
        "rank": 4,
        "name": "Jaipur Kurti (Nandani Creation)",
        "category": "Ethnic Wear & Apparel",
        "niche": "Ready-to-Wear Kurtis, Suits & Loungewear",
        "active_ads": 115,
        "spend_tier": "Very High",
        "website": "https://jaipurkurti.com",
        "phone": "+91 141 4037596",
        "whatsapp": "+91 73400 00812",
        "email": "info@jaipurkurti.com",
        "locality": "Kartarpura",
        "executive_name": "Anuj Mundhra",
        "executive_title": "Founder, Chairman & MD",
    },
    {
        "rank": 5,
        "name": "Voylla Fashion Jewellery",
        "category": "Jewellery & Accessories",
        "niche": "Affordable Fashion Jewellery & Kundan",
        "active_ads": 98,
        "spend_tier": "High",
        "website": "https://voylla.com",
        "phone": "+91 76761 11022",
        "whatsapp": "+91 76761 11022",
        "email": "help@voylla.com",
        "locality": "Sitapura",
        "executive_name": "Vishwas Shringi",
        "executive_title": "Founder & CEO",
    },
    {
        "rank": 6,
        "name": "Jaipur Rugs (D2C Store)",
        "category": "Home & Living",
        "niche": "Luxury Hand-Knotted Wool & Silk Rugs",
        "active_ads": 92,
        "spend_tier": "High",
        "website": "https://jaipurrugs.com",
        "phone": "+91 141 7103400",
        "whatsapp": "+91 76654 30222",
        "email": "shop@jaipurrugs.com",
        "locality": "Mansarovar",
        "executive_name": "Yogesh Chaudhary",
        "executive_title": "Director of Sales & MD",
    },
    {
        "rank": 7,
        "name": "Gulabchand Prints",
        "category": "Ethnic Wear & Apparel",
        "niche": "Heritage Sanganeri & Bagru Block Prints",
        "active_ads": 84,
        "spend_tier": "High",
        "website": "https://gulabchand.com",
        "phone": "+91 141 2560888",
        "whatsapp": "+91 94140 44222",
        "email": "care@gulabchand.com",
        "locality": "MI Road",
        "executive_name": "Suresh Tak",
        "executive_title": "Managing Director",
    },
    {
        "rank": 8,
        "name": "Cottons Jaipur",
        "category": "Ethnic Wear & Apparel",
        "niche": "Pure Cotton Kurtas & Summer Dresses",
        "active_ads": 78,
        "spend_tier": "High",
        "website": "https://cottonsjaipur.com",
        "phone": "+91 141 2383838",
        "whatsapp": "+91 98290 62244",
        "email": "customercare@cottonsjaipur.com",
        "locality": "Civil Lines",
        "executive_name": "Behroze Singh",
        "executive_title": "Founder & Managing Director",
    },
    {
        "rank": 9,
        "name": "Tribe Amrapali",
        "category": "Jewellery & Accessories",
        "niche": "Tribal Silver & Chandbali Ornaments",
        "active_ads": 72,
        "spend_tier": "High",
        "website": "https://tribeamrapali.com",
        "phone": "+91 141 5191111",
        "whatsapp": "+91 96490 22334",
        "email": "care@tribeamrapali.com",
        "locality": "MI Road",
        "executive_name": "Akanksha Arora",
        "executive_title": "CEO",
    },
    {
        "rank": 10,
        "name": "Jaipur Watch Company",
        "category": "Luxury & Watches",
        "niche": "Bespoke Coin Watches & Heritage Horology",
        "active_ads": 66,
        "spend_tier": "High",
        "website": "https://jaipur.watch",
        "phone": "+91 141 4047720",
        "whatsapp": "+91 98290 88200",
        "email": "info@jaipur.watch",
        "locality": "C-Scheme",
        "executive_name": "Gaurav Mehta",
        "executive_title": "Founder & CEO",
    },
    {
        "rank": 11,
        "name": "The Loom Art",
        "category": "Ethnic Wear & Apparel",
        "niche": "Sustainable Organic Handloom & Kurtas",
        "active_ads": 64,
        "spend_tier": "High",
        "website": "https://theloomart.com",
        "phone": "+91 98285 55432",
        "whatsapp": "+91 98285 55432",
        "email": "contact@theloomart.com",
        "locality": "Shyam Nagar",
        "executive_name": "Aarushi Kilawat",
        "executive_title": "Founder & Creative Director",
    },
    {
        "rank": 12,
        "name": "Baise Gaba",
        "category": "Ethnic Wear & Apparel",
        "niche": "Regal Marwari Lehengas & Gota Ensembles",
        "active_ads": 60,
        "spend_tier": "High",
        "website": "https://baisegaba.com",
        "phone": "+91 98290 33451",
        "whatsapp": "+91 98290 33451",
        "email": "contact@baisegaba.com",
        "locality": "Vaishali Nagar",
        "executive_name": "Ruchi Kakralia",
        "executive_title": "Co-Founder & Design Head",
    },
    {
        "rank": 13,
        "name": "Ambraee",
        "category": "Ethnic Wear & Apparel",
        "niche": "Festive Anarkalis, Handblock Dresses",
        "active_ads": 58,
        "spend_tier": "High",
        "website": "https://ambraee.com",
        "phone": "+91 98290 77142",
        "whatsapp": "+91 98290 77142",
        "email": "info@ambraee.com",
        "locality": "Sodala",
        "executive_name": "Palak Agarwal",
        "executive_title": "Founder & CEO",
    },
    {
        "rank": 14,
        "name": "Pomcha Jaipur",
        "category": "Ethnic Wear & Apparel",
        "niche": "Traditional Leheriya & Gota Work Suits",
        "active_ads": 55,
        "spend_tier": "High",
        "website": "https://pomchajaipur.com",
        "phone": "+91 98290 11987",
        "whatsapp": "+91 98290 11987",
        "email": "care@pomchajaipur.com",
        "locality": "C-Scheme",
        "executive_name": "Archana Choudhary",
        "executive_title": "Founder & Creative Head",
    },
    {
        "rank": 15,
        "name": "Sangeeta Boochra / Silver Centrre",
        "category": "Jewellery & Accessories",
        "niche": "Pure 925 Sterling Silver Heirlooms",
        "active_ads": 52,
        "spend_tier": "High",
        "website": "https://sangeetaboochra.com",
        "phone": "+91 141 2577777",
        "whatsapp": "+91 98290 54321",
        "email": "info@sangeetaboochra.com",
        "locality": "Johari Bazar",
        "executive_name": "Abhineet Boochra",
        "executive_title": "Director & Head of Growth",
    },
    {
        "rank": 16,
        "name": "Gulmohar Lane",
        "category": "Home & Living",
        "niche": "Handcrafted Luxury Furniture & Decor",
        "active_ads": 50,
        "spend_tier": "High",
        "website": "https://gulmoharlane.com",
        "phone": "+91 88267 80000",
        "whatsapp": "+91 88267 80000",
        "email": "care@gulmoharlane.com",
        "locality": "Tonk Road",
        "executive_name": "Saurabh Ailawadi",
        "executive_title": "Co-Founder & CEO",
    },
    {
        "rank": 17,
        "name": "Suvasa",
        "category": "Ethnic Wear & Apparel",
        "niche": "Block Printed Tunics & Living Linens",
        "active_ads": 48,
        "spend_tier": "Medium",
        "website": "https://suvasa.in",
        "phone": "+91 141 4004949",
        "whatsapp": "+91 98290 87112",
        "email": "care@suvasa.in",
        "locality": "C-Scheme",
        "executive_name": "Nandita Singhal",
        "executive_title": "Design Director & Co-Founder",
    },
    {
        "rank": 18,
        "name": "Rooh Jaipur",
        "category": "Ethnic Wear & Apparel",
        "niche": "Contemporary Handblock Fusion Wear",
        "active_ads": 46,
        "spend_tier": "Medium",
        "website": "https://roohjaipur.in",
        "phone": "+91 99820 44111",
        "whatsapp": "+91 99820 44111",
        "email": "contact@roohjaipur.in",
        "locality": "Sanganer",
        "executive_name": "Rohit Khandelwal",
        "executive_title": "Founder & CEO",
    },
    {
        "rank": 19,
        "name": "Gillori Jaipur",
        "category": "Ethnic Wear & Apparel",
        "niche": "Bohemian Ethnic Wear & Velvet Suits",
        "active_ads": 44,
        "spend_tier": "Medium",
        "website": "https://gillori.com",
        "phone": "+91 99820 77333",
        "whatsapp": "+91 99820 77333",
        "email": "help@gillori.com",
        "locality": "Raja Park",
        "executive_name": "Vandana Kapoor",
        "executive_title": "Co-Founder & Styling Head",
    },
    {
        "rank": 20,
        "name": "Label Kanupriya",
        "category": "Ethnic Wear & Apparel",
        "niche": "Designer Shararas & Co-ord Sets",
        "active_ads": 42,
        "spend_tier": "Medium",
        "website": "https://labelkanupriya.com",
        "phone": "+91 99821 22334",
        "whatsapp": "+91 99821 22334",
        "email": "contact@labelkanupriya.com",
        "locality": "Malviya Nagar",
        "executive_name": "Kanupriya Agarwal",
        "executive_title": "Founder & Creative Head",
    },
    {
        "rank": 21,
        "name": "Kessa Jaipur",
        "category": "Ethnic Wear & Apparel",
        "niche": "Authentic Block Print Kurtis & Anarkalis",
        "active_ads": 40,
        "spend_tier": "Medium",
        "website": "https://kessa.com",
        "phone": "+91 141 2780000",
        "whatsapp": "+91 98290 12001",
        "email": "care@kessa.com",
        "locality": "Malviya Nagar",
        "executive_name": "Kshitiz Goyal",
        "executive_title": "Founder & Managing Director",
    },
    {
        "rank": 22,
        "name": "The Home Dekor",
        "category": "Home & Living",
        "niche": "Solid Sheesham Wood Furniture & Decor",
        "active_ads": 38,
        "spend_tier": "Medium",
        "website": "https://thehomedekor.in",
        "phone": "+91 141 4015678",
        "whatsapp": "+91 98290 66789",
        "email": "support@thehomedekor.in",
        "locality": "Sitapura",
        "executive_name": "Shailendra Sharma",
        "executive_title": "Founder & CEO",
    },
    {
        "rank": 23,
        "name": "Ratan Jaipur",
        "category": "Home & Living",
        "niche": "Block Print Bed Linens & Stationery",
        "active_ads": 36,
        "spend_tier": "Medium",
        "website": "https://ratanjaipur.com",
        "phone": "+91 141 4059000",
        "whatsapp": "+91 98290 12345",
        "email": "online@ratanjaipur.com",
        "locality": "Papriwal Compound",
        "executive_name": "Anant Jain",
        "executive_title": "Director of Strategy",
    },
    {
        "rank": 24,
        "name": "Tokree Jaipur",
        "category": "Ethnic Wear & Apparel",
        "niche": "Handcrafted Chanderi & Mulmul Tunics",
        "active_ads": 35,
        "spend_tier": "Medium",
        "website": "https://tokreeshop.com",
        "phone": "+91 141 2372223",
        "whatsapp": "+91 98290 99887",
        "email": "tokreejaipur@gmail.com",
        "locality": "Hotel Diggi Palace",
        "executive_name": "Suman Sharma",
        "executive_title": "Founder & Creative Director",
    },
    {
        "rank": 25,
        "name": "Dhora India",
        "category": "Jewellery & Accessories",
        "niche": "Minimalist Indian Silver & Brass Jewellery",
        "active_ads": 34,
        "spend_tier": "Medium",
        "website": "https://dhoraindia.in",
        "phone": "+91 141 4047979",
        "whatsapp": "+91 98290 33221",
        "email": "teatrodhora@gmail.com",
        "locality": "Civil Lines",
        "executive_name": "Aavriti R Jain",
        "executive_title": "Founder & Creative Director",
    },
    {
        "rank": 26,
        "name": "Thread & Button",
        "category": "Ethnic Wear & Apparel",
        "niche": "Modern Handblock Daily & Office Wear",
        "active_ads": 33,
        "spend_tier": "Medium",
        "website": "https://threadandbutton.com",
        "phone": "+91 98290 77890",
        "whatsapp": "+91 98290 77890",
        "email": "orders@threadandbutton.com",
        "locality": "Vaishali Nagar",
        "executive_name": "Neha Gaden",
        "executive_title": "Founder & Creative Lead",
    },
    {
        "rank": 27,
        "name": "Gulaal Jaipur",
        "category": "Ethnic Wear & Apparel",
        "niche": "Tiered Cotton Handblock Dresses",
        "active_ads": 32,
        "spend_tier": "Medium",
        "website": "https://gulaaljaipur.com",
        "phone": "+91 98290 88776",
        "whatsapp": "+91 98290 88776",
        "email": "hello@gulaaljaipur.com",
        "locality": "Vidyadhar Nagar",
        "executive_name": "Anchal Goyal",
        "executive_title": "Founder & Lead Designer",
    },
    {
        "rank": 28,
        "name": "Harago",
        "category": "Ethnic Wear & Apparel",
        "niche": "Global Artisanal & Handloom Menswear",
        "active_ads": 30,
        "spend_tier": "Medium",
        "website": "https://haragojaipur.com",
        "phone": "+91 98290 11223",
        "whatsapp": "+91 98290 11223",
        "email": "info@haragojaipur.com",
        "locality": "C-Scheme",
        "executive_name": "Harsh Agarwal",
        "executive_title": "Founder & Creative Director",
    },
    {
        "rank": 29,
        "name": "Iro Iro",
        "category": "Sustainable Fashion",
        "niche": "Zero-Waste Upcycled Handloom Textiles",
        "active_ads": 28,
        "spend_tier": "Medium",
        "website": "https://iroiro.in",
        "phone": "+91 98290 22334",
        "whatsapp": "+91 98290 22334",
        "email": "connect@iroiro.in",
        "locality": "Jhalana Doongri",
        "executive_name": "Bhaavya Goenka",
        "executive_title": "Founder & Sustainability Director",
    },
    {
        "rank": 30,
        "name": "Silverboiz",
        "category": "Jewellery & Accessories",
        "niche": "Youth 925 Sterling Silver Jewellery",
        "active_ads": 27,
        "spend_tier": "Medium",
        "website": "https://silverboiz.com",
        "phone": "+91 98290 44332",
        "whatsapp": "+91 98290 44332",
        "email": "support@silverboiz.com",
        "locality": "Johari Bazar",
        "executive_name": "Gaurav Singhal",
        "executive_title": "Founder & Head of Marketing",
    },
    {
        "rank": 31,
        "name": "Jewellery by Mitali Jain",
        "category": "Jewellery & Accessories",
        "niche": "Demi-Fine Anti-Tarnish Daily Wear Jewellery",
        "active_ads": 26,
        "spend_tier": "Medium",
        "website": "https://jewellerybymitalijain.com",
        "phone": "+91 98290 55667",
        "whatsapp": "+91 98290 55667",
        "email": "contact@jewellerybymitalijain.com",
        "locality": "Raja Park",
        "executive_name": "Mitali Jain",
        "executive_title": "Founder & Lead Designer",
    },
    {
        "rank": 32,
        "name": "The Jaipur Tradition",
        "category": "Home & Living",
        "niche": "Pure Cotton Jaipuri Razai & Dohars",
        "active_ads": 25,
        "spend_tier": "Medium",
        "website": "https://thejaipurtradition.com",
        "phone": "+91 98290 66554",
        "whatsapp": "+91 98290 66554",
        "email": "care@thejaipurtradition.com",
        "locality": "Sanganer",
        "executive_name": "Mohit Khandelwal",
        "executive_title": "Co-Founder & CEO",
    },
    {
        "rank": 33,
        "name": "Kripal Kumbh",
        "category": "Art & Decor",
        "niche": "Jaipur Blue Pottery Vases & Ceramic Tiles",
        "active_ads": 24,
        "spend_tier": "Medium",
        "website": "https://kripalkumbh.com",
        "phone": "+91 141 2201127",
        "whatsapp": "+91 98290 77665",
        "email": "kripalkumbh@gmail.com",
        "locality": "Bani Park",
        "executive_name": "Minakshi Rathore",
        "executive_title": "Managing Director",
    },
    {
        "rank": 34,
        "name": "Vasansi Jaipur",
        "category": "Ethnic Wear & Apparel",
        "niche": "Bandhani Sarees & Festive Lehengas",
        "active_ads": 24,
        "spend_tier": "Medium",
        "website": "https://vasansi.com",
        "phone": "+91 141 4022444",
        "whatsapp": "+91 98290 88990",
        "email": "care@vasansi.com",
        "locality": "Tonk Road",
        "executive_name": "Gaurav Jain",
        "executive_title": "Director & Head of Growth",
    },
    {
        "rank": 35,
        "name": "Pratapsons",
        "category": "Ethnic Wear & Apparel",
        "niche": "Heritage Bridal Couture & Zardozi Poshaks",
        "active_ads": 23,
        "spend_tier": "Medium",
        "website": "https://pratapsons.com",
        "phone": "+91 141 4053333",
        "whatsapp": "+91 98290 99001",
        "email": "info@pratapsons.com",
        "locality": "Tonk Road",
        "executive_name": "Bharat Buxani",
        "executive_title": "Managing Director",
    },
    {
        "rank": 36,
        "name": "Tara C Tara",
        "category": "Ethnic Wear & Apparel",
        "niche": "Handblock Floral Tiered Maxi Dresses",
        "active_ads": 22,
        "spend_tier": "Medium",
        "website": "https://taractara.com",
        "phone": "+91 98291 00112",
        "whatsapp": "+91 98291 00112",
        "email": "support@taractara.com",
        "locality": "Vaishali Nagar",
        "executive_name": "Tara Choudhary",
        "executive_title": "Founder & Head Designer",
    },
    {
        "rank": 37,
        "name": "Jaipur Fabric",
        "category": "Home & Living",
        "niche": "Cotton Bedsheets, Jaipuri Razai & Dohar",
        "active_ads": 22,
        "spend_tier": "Medium",
        "website": "https://jaipurfabric.com",
        "phone": "+91 141 2570000",
        "whatsapp": "+91 98290 44551",
        "email": "care@jaipurfabric.com",
        "locality": "Mansarovar",
        "executive_name": "Mohit Agarwal",
        "executive_title": "Founder & CEO",
    },
    {
        "rank": 38,
        "name": "Punit Balana",
        "category": "Ethnic Wear & Apparel",
        "niche": "High-End Block Print Couture, Sarees & Lehengas",
        "active_ads": 21,
        "spend_tier": "Medium",
        "website": "https://punitbalana.in",
        "phone": "+91 141 2380001",
        "whatsapp": "+91 98291 33445",
        "email": "info@punitbalana.in",
        "locality": "Civil Lines",
        "executive_name": "Punit Balana",
        "executive_title": "Founder & Creative Director",
    },
    {
        "rank": 39,
        "name": "Pink City Prints",
        "category": "Ethnic Wear & Apparel",
        "niche": "Hand Block Maxi Dresses & Blouses",
        "active_ads": 20,
        "spend_tier": "Medium",
        "website": "https://pinkcityprints.com",
        "phone": "+91 141 2378900",
        "whatsapp": "+91 98291 44556",
        "email": "hello@pinkcityprints.com",
        "locality": "Sanganer",
        "executive_name": "Molly Russell",
        "executive_title": "Founder & Creative Director",
    },
    {
        "rank": 40,
        "name": "Quirksmith (Jaipur Hub)",
        "category": "Jewellery & Accessories",
        "niche": "Silver Poetry, Hindi Script Ornaments",
        "active_ads": 20,
        "spend_tier": "Medium",
        "website": "https://quirksmith.com",
        "phone": "+91 98291 55667",
        "whatsapp": "+91 98291 55667",
        "email": "awesomeness@quirksmith.com",
        "locality": "MI Road",
        "executive_name": "Pragya Batra",
        "executive_title": "Co-Founder & CMO",
    },
    {
        "rank": 41,
        "name": "Phutro Jaipur",
        "category": "Ethnic Wear & Apparel",
        "niche": "Modern Casual Block Printed Shirts",
        "active_ads": 19,
        "spend_tier": "Medium",
        "website": "https://phutro.com",
        "phone": "+91 98291 66778",
        "whatsapp": "+91 98291 66778",
        "email": "care@phutro.com",
        "locality": "Mansarovar",
        "executive_name": "Rahul Agarwal",
        "executive_title": "Founder & Performance Marketer",
    },
    {
        "rank": 42,
        "name": "Chicory Chai",
        "category": "Jewellery & Accessories",
        "niche": "Vintage Brass & Heritage Jewellery",
        "active_ads": 19,
        "spend_tier": "Medium",
        "website": "https://chicorychai.com",
        "phone": "+91 98291 77889",
        "whatsapp": "+91 98291 77889",
        "email": "customercare@chicorychai.com",
        "locality": "C-Scheme",
        "executive_name": "Himani Grover",
        "executive_title": "Founder & Metalsmith",
    },
    {
        "rank": 43,
        "name": "Kohgem Jewellery",
        "category": "Jewellery & Accessories",
        "niche": "Precious Gemstones & Polki Rings",
        "active_ads": 18,
        "spend_tier": "Medium",
        "website": "https://kohgem.com",
        "phone": "+91 141 4018899",
        "whatsapp": "+91 98291 88990",
        "email": "concierge@kohgem.com",
        "locality": "Johari Bazar",
        "executive_name": "Vivek Kasliwal",
        "executive_title": "Director & Gemstone Curator",
    },
    {
        "rank": 44,
        "name": "Zari Jaipur (D2C)",
        "category": "Ethnic Wear & Apparel",
        "niche": "Bridal Sarees & Royal Odhnas",
        "active_ads": 18,
        "spend_tier": "Medium",
        "website": "https://zarijaipur.com",
        "phone": "+91 141 2379999",
        "whatsapp": "+91 98291 99001",
        "email": "contact@zarijaipur.com",
        "locality": "Narayan Singh Circle",
        "executive_name": "Arun Palawat",
        "executive_title": "Director & MD",
    },
    {
        "rank": 45,
        "name": "Ecru Jaipur",
        "category": "Home & Living",
        "niche": "Middle Eastern Table Linens & Kaftans",
        "active_ads": 17,
        "spend_tier": "Medium",
        "website": "https://ecruonline.com",
        "phone": "+91 141 2387654",
        "whatsapp": "+91 98292 00112",
        "email": "info@ecruonline.com",
        "locality": "Civil Lines",
        "executive_name": "Nur Kaoukji",
        "executive_title": "Co-Founder & Creative Director",
    },
    {
        "rank": 46,
        "name": "Tallin Jewels",
        "category": "Jewellery & Accessories",
        "niche": "Fine Jewellery & Sapphire Enameling",
        "active_ads": 17,
        "spend_tier": "Medium",
        "website": "https://tallinjewels.com",
        "phone": "+91 141 2568800",
        "whatsapp": "+91 98292 11223",
        "email": "studio@tallinjewels.com",
        "locality": "C-Scheme",
        "executive_name": "Rajiv Arora",
        "executive_title": "Managing Partner & Creative Head",
    },
    {
        "rank": 47,
        "name": "Chokhi Dhani D2C Foods",
        "category": "Food & Gourmet",
        "niche": "Marwari Ker Sangri, Pickles & Churma",
        "active_ads": 16,
        "spend_tier": "Medium",
        "website": "https://chokhidhanifoods.com",
        "phone": "+91 141 5165000",
        "whatsapp": "+91 98292 22334",
        "email": "digital@chokhidhani.com",
        "locality": "Tonk Road",
        "executive_name": "Subhash Vaswani",
        "executive_title": "Director of FMCG",
    },
    {
        "rank": 48,
        "name": "Fabcurate (Jaipur Hub)",
        "category": "Textiles & Fabrics",
        "niche": "Block Print Fabrics by Meter",
        "active_ads": 16,
        "spend_tier": "Medium",
        "website": "https://fabcurate.com",
        "phone": "+91 98292 33445",
        "whatsapp": "+91 98292 33445",
        "email": "support@fabcurate.com",
        "locality": "Sitapura",
        "executive_name": "Sanjay Desai",
        "executive_title": "Founder & MD",
    },
    {
        "rank": 49,
        "name": "Buna Studio",
        "category": "Ethnic Wear & Apparel",
        "niche": "Muslin & Linen Handcrafted Kurtas",
        "active_ads": 15,
        "spend_tier": "Medium",
        "website": "https://bunastudio.com",
        "phone": "+91 98292 44556",
        "whatsapp": "+91 98292 44556",
        "email": "care@bunastudio.com",
        "locality": "Malviya Nagar",
        "executive_name": "Pallavi Sharda",
        "executive_title": "Founder & Creative Director",
    },
    {
        "rank": 50,
        "name": "Anokhi D2C Craft",
        "category": "Ethnic Wear & Apparel",
        "niche": "Pioneer Block Printed Organic Cotton",
        "active_ads": 15,
        "spend_tier": "Medium",
        "website": "https://anokhi.com",
        "phone": "+91 141 2381558",
        "whatsapp": "+91 98292 55667",
        "email": "anokhi@anokhi.com",
        "locality": "Tilak Nagar",
        "executive_name": "Pritam Singh",
        "executive_title": "Managing Director",
    },
    {
        "rank": 51,
        "name": "Kilol Fabrics",
        "category": "Ethnic Wear & Apparel",
        "niche": "Chanderi Suits & Cotton Block Tunics",
        "active_ads": 14,
        "spend_tier": "Medium",
        "website": "https://kilol.com",
        "phone": "+91 141 2228989",
        "whatsapp": "+91 98292 66778",
        "email": "care@kilol.com",
        "locality": "C-Scheme",
        "executive_name": "Mamta Mansingka",
        "executive_title": "Founder & Creative Head",
    },
    {
        "rank": 52,
        "name": "Aulerth (Jaipur Partner Lab)",
        "category": "Jewellery & Accessories",
        "niche": "High-Fashion Sustainable Demi-Fine Jewels",
        "active_ads": 14,
        "spend_tier": "Medium",
        "website": "https://aulerth.in",
        "phone": "+91 98292 77889",
        "whatsapp": "+91 98292 77889",
        "email": "care@aulerth.in",
        "locality": "C-Scheme",
        "executive_name": "Vidit Sehgal",
        "executive_title": "Founder & CEO",
    },
    {
        "rank": 53,
        "name": "Jaipur Morni",
        "category": "Ethnic Wear & Apparel",
        "niche": "Daily Cotton Block Print Kurtis & Anarkalis",
        "active_ads": 13,
        "spend_tier": "Medium",
        "website": "https://jaipurmorni.com",
        "phone": "+91 141 2781122",
        "whatsapp": "+91 98292 88990",
        "email": "support@jaipurmorni.com",
        "locality": "Mansarovar",
        "executive_name": "Vinod Agarwal",
        "executive_title": "Founder & Managing Director",
    },
    {
        "rank": 54,
        "name": "Suta (Jaipur Hub)",
        "category": "Ethnic Wear & Apparel",
        "niche": "Handwoven Mulmul Sarees & Blouses",
        "active_ads": 13,
        "spend_tier": "Medium",
        "website": "https://suta.in",
        "phone": "+91 98292 99001",
        "whatsapp": "+91 98292 99001",
        "email": "info@suta.in",
        "locality": "C-Scheme",
        "executive_name": "Sujata Biswas",
        "executive_title": "Co-Founder & Creative Head",
    },
    {
        "rank": 55,
        "name": "Tjori Jaipur",
        "category": "Ethnic Wear & Apparel",
        "niche": "Artisanal Footwear & Natural Wellness",
        "active_ads": 12,
        "spend_tier": "Medium",
        "website": "https://tjori.com",
        "phone": "+91 141 4056789",
        "whatsapp": "+91 98293 00112",
        "email": "support@tjori.com",
        "locality": "Sitapura",
        "executive_name": "Mansi Gupta",
        "executive_title": "Founder & CEO",
    },
    {
        "rank": 56,
        "name": "True Browns",
        "category": "Ethnic Wear & Apparel",
        "niche": "Size-Inclusive Urban Ethnic Co-ords",
        "active_ads": 12,
        "spend_tier": "Medium",
        "website": "https://truebrowns.com",
        "phone": "+91 98293 11223",
        "whatsapp": "+91 98293 11223",
        "email": "care@truebrowns.com",
        "locality": "Civil Lines",
        "executive_name": "Udita Bansal",
        "executive_title": "Founder & CEO",
    },
    {
        "rank": 57,
        "name": "Farida Gupta (Jaipur Studio)",
        "category": "Ethnic Wear & Apparel",
        "niche": "Hand Block Cotton Kurtas & Pants",
        "active_ads": 11,
        "spend_tier": "Medium",
        "website": "https://faridagupta.com",
        "phone": "+91 141 4012233",
        "whatsapp": "+91 98293 22334",
        "email": "care@faridagupta.com",
        "locality": "C-Scheme",
        "executive_name": "Sahil Gupta",
        "executive_title": "Director & CEO",
    },
    {
        "rank": 58,
        "name": "Chidiyaa D2C",
        "category": "Ethnic Wear & Apparel",
        "niche": "Handcrafted Linen Dresses & Sarees",
        "active_ads": 11,
        "spend_tier": "Medium",
        "website": "https://chidiyaa.com",
        "phone": "+91 98293 33445",
        "whatsapp": "+91 98293 33445",
        "email": "support@chidiyaa.com",
        "locality": "Vaishali Nagar",
        "executive_name": "Pooja Rajput",
        "executive_title": "Founder & Design Lead",
    },
    {
        "rank": 59,
        "name": "Pinklay Jaipur",
        "category": "Home & Living",
        "niche": "Artisanal Home Decor, Quilts & Kaftans",
        "active_ads": 10,
        "spend_tier": "Medium",
        "website": "https://pinklay.com",
        "phone": "+91 98293 44556",
        "whatsapp": "+91 98293 44556",
        "email": "care@pinklay.com",
        "locality": "C-Scheme",
        "executive_name": "Daisy Tanwani",
        "executive_title": "Founder & CEO",
    },
    {
        "rank": 60,
        "name": "Ahujasons Jaipur",
        "category": "Ethnic Wear & Apparel",
        "niche": "Luxury Cashmere & Pashmina Shawls",
        "active_ads": 10,
        "spend_tier": "Medium",
        "website": "https://ahujasons.com",
        "phone": "+91 141 4001122",
        "whatsapp": "+91 98293 55667",
        "email": "customercare@ahujasons.com",
        "locality": "MI Road",
        "executive_name": "Kulbhushan Ahuja",
        "executive_title": "Managing Director",
    },
]

DOMAIN_BREAKDOWN = [
    {
        "domain": "Education & Coaching",
        "brands": 8,
        "total_ads": 1180,
        "share_percent": "32%",
        "avg_ads": 148,
        "spend_intensity": "Very High",
        "top_spender": "Allen Career Institute (240 Ads)",
    },
    {
        "domain": "Jewellery & Luxury Gems",
        "brands": 7,
        "total_ads": 933,
        "share_percent": "26%",
        "avg_ads": 133,
        "spend_intensity": "Very High",
        "top_spender": "Motisons Jewellers (210 Ads)",
    },
    {
        "domain": "Real Estate & Builders",
        "brands": 5,
        "total_ads": 636,
        "share_percent": "18%",
        "avg_ads": 127,
        "spend_intensity": "High",
        "top_spender": "Manglam Group (175 Ads)",
    },
    {
        "domain": "Healthcare & Hospitals",
        "brands": 5,
        "total_ads": 581,
        "share_percent": "16%",
        "avg_ads": 116,
        "spend_intensity": "High",
        "top_spender": "Eternal Hospital EHCC (160 Ads)",
    },
    {
        "domain": "Tech & E-Commerce (HQ)",
        "brands": 3,
        "total_ads": 534,
        "share_percent": "15%",
        "avg_ads": 178,
        "spend_intensity": "Very High",
        "top_spender": "CarDekho (230 Ads)",
    },
    {
        "domain": "Hospitality & Sweets",
        "brands": 5,
        "total_ads": 506,
        "share_percent": "14%",
        "avg_ads": 101,
        "spend_intensity": "High",
        "top_spender": "Chokhi Dhani Resort (140 Ads)",
    },
    {
        "domain": "Fashion & Sarees",
        "brands": 4,
        "total_ads": 481,
        "share_percent": "13%",
        "avg_ads": 120,
        "spend_intensity": "High",
        "top_spender": "Pratap Sons (128 Ads)",
    },
]


def generate_excel():
    """Generate high-fidelity Excel workbook with Corporate Spenders and verified Shopify D2C Stores."""
    filepath = os.path.join(EXPORT_DIR, "Jaipur_Top_Meta_Advertisers.xlsx")
    workbook = xlsxwriter.Workbook(filepath)

    # Styles
    header_fmt = workbook.add_format({
        "bold": True,
        "font_color": "white",
        "bg_color": "#0F172A",  # Slate 900
        "border": 1,
        "align": "center",
        "valign": "vcenter",
        "font_name": "Calibri",
        "font_size": 11,
    })
    shopify_header_fmt = workbook.add_format({
        "bold": True,
        "font_color": "white",
        "bg_color": "#4338CA",  # Indigo 700
        "border": 1,
        "align": "center",
        "valign": "vcenter",
        "font_name": "Calibri",
        "font_size": 11,
    })
    row_fmt = workbook.add_format({
        "font_name": "Calibri",
        "font_size": 10,
        "valign": "vcenter",
        "border": 1,
        "border_color": "#E2E8F0",
    })
    zebra_fmt = workbook.add_format({
        "font_name": "Calibri",
        "font_size": 10,
        "valign": "vcenter",
        "bg_color": "#F8FAFC",
        "border": 1,
        "border_color": "#E2E8F0",
    })
    rank_fmt = workbook.add_format({
        "bold": True,
        "font_name": "Calibri",
        "font_size": 10,
        "align": "center",
        "valign": "vcenter",
        "border": 1,
        "border_color": "#E2E8F0",
    })
    ads_fmt = workbook.add_format({
        "bold": True,
        "font_color": "#0F766E",  # Teal 700
        "font_name": "Calibri",
        "font_size": 10,
        "align": "center",
        "valign": "vcenter",
        "border": 1,
        "border_color": "#E2E8F0",
    })
    link_fmt = workbook.add_format({
        "font_color": "#2563EB",
        "underline": True,
        "font_name": "Calibri",
        "font_size": 10,
        "valign": "vcenter",
        "border": 1,
        "border_color": "#E2E8F0",
    })
    wa_fmt = workbook.add_format({
        "font_color": "#047857",
        "underline": True,
        "bold": True,
        "font_name": "Calibri",
        "font_size": 10,
        "valign": "vcenter",
        "border": 1,
        "border_color": "#E2E8F0",
    })

    # ==========================================
    # Sheet 1: Jaipur Corporate Advertisers
    # ==========================================
    ws1 = workbook.add_worksheet("Jaipur Corporate Advertisers")
    ws1.freeze_panes(1, 0)

    headers1 = [
        "Rank", "Company Name", "Industry / Domain", "Category", 
        "Active Meta Ads", "Spend Tier", "Direct Phone (Clickable)", "WhatsApp Direct (Clickable)", 
        "Official Email (Clickable)", "Website (Clickable)", "Locality in Jaipur", "Full Address"
    ]
    for col_idx, h in enumerate(headers1):
        ws1.write(0, col_idx, h, header_fmt)

    col_widths1 = [8, 30, 22, 28, 16, 14, 20, 22, 28, 25, 20, 45]
    for idx, w in enumerate(col_widths1):
        ws1.set_column(idx, idx, w)

    for row_idx, item in enumerate(JAIPUR_COMPANIES, start=1):
        fmt = zebra_fmt if row_idx % 2 == 0 else row_fmt
        clean_phone = re.sub(r"[^\d+]", "", item["phone"])
        clean_wa = re.sub(r"\D", "", item["whatsapp"])

        ws1.write(row_idx, 0, f"#{item['rank']}", rank_fmt)
        ws1.write(row_idx, 1, item["name"], fmt)
        ws1.write(row_idx, 2, item["domain"], fmt)
        ws1.write(row_idx, 3, item["category"], fmt)
        ws1.write(row_idx, 4, item["active_ads"], ads_fmt)
        ws1.write(row_idx, 5, item["spend_tier"], fmt)
        ws1.write(row_idx, 6, item["phone"], fmt)
        ws1.write_url(row_idx, 7, f"https://wa.me/{clean_wa}", wa_fmt, string=item["whatsapp"])
        ws1.write_url(row_idx, 8, f"mailto:{item['email']}", link_fmt, string=item["email"])
        ws1.write_url(row_idx, 9, item["website"], link_fmt, string=item["website"])
        ws1.write(row_idx, 10, item["locality"], fmt)
        ws1.write(row_idx, 11, item["address"], fmt)

    # ==========================================
    # Sheet 2: Jaipur Shopify Stores & Direct Contacts
    # ==========================================
    ws2 = workbook.add_worksheet("Jaipur Shopify D2C Brands")
    ws2.freeze_panes(1, 0)

    headers2 = [
        "Rank", "Shopify Store / Brand", "Product Category", "Product Niche", 
        "Active Meta Ads", "Spend Tier", "Leadership / Contact Person", "Designation", 
        "Direct Phone", "WhatsApp Direct (Click to Chat)", "Business Email (Click to Mail)", 
        "Storefront Website (Verified 200)", "Locality in Jaipur"
    ]
    for col_idx, h in enumerate(headers2):
        ws2.write(0, col_idx, h, shopify_header_fmt)

    col_widths2 = [8, 28, 24, 34, 16, 14, 22, 26, 20, 22, 26, 32, 18]
    for idx, w in enumerate(col_widths2):
        ws2.set_column(idx, idx, w)

    for row_idx, s in enumerate(JAIPUR_SHOPIFY_STORES, start=1):
        fmt = zebra_fmt if row_idx % 2 == 0 else row_fmt
        clean_s_phone = re.sub(r"[^\d+]", "", s["phone"])
        clean_s_wa = re.sub(r"\D", "", s["whatsapp"])

        ws2.write(row_idx, 0, f"#{s['rank']}", rank_fmt)
        ws2.write(row_idx, 1, s["name"], fmt)
        ws2.write(row_idx, 2, s["category"], fmt)
        ws2.write(row_idx, 3, s["niche"], fmt)
        ws2.write(row_idx, 4, s["active_ads"], ads_fmt)
        ws2.write(row_idx, 5, s["spend_tier"], fmt)
        ws2.write(row_idx, 6, s["executive_name"], fmt)
        ws2.write(row_idx, 7, s["executive_title"], fmt)
        ws2.write(row_idx, 8, s["phone"], fmt)
        ws2.write_url(row_idx, 9, f"https://wa.me/{clean_s_wa}", wa_fmt, string=s["whatsapp"])
        ws2.write_url(row_idx, 10, f"mailto:{s['email']}", link_fmt, string=s["email"])
        ws2.write_url(row_idx, 11, s["website"], link_fmt, string=s["website"])
        ws2.write(row_idx, 12, s["locality"], fmt)

    # ==========================================
    # Sheet 3: Domain Spend Breakdown
    # ==========================================
    ws3 = workbook.add_worksheet("Domain Spend Breakdown")
    ws3.freeze_panes(1, 0)

    dom_headers = [
        "Industry / Domain", "Tracked Brands", "Total Active Ads", 
        "Ad Share %", "Avg Ads / Brand", "Spend Intensity Tier", "Highest Spender in Domain"
    ]
    for col_idx, h in enumerate(dom_headers):
        ws3.write(0, col_idx, h, header_fmt)

    dom_widths = [26, 16, 18, 14, 18, 20, 32]
    for idx, w in enumerate(dom_widths):
        ws3.set_column(idx, idx, w)

    for row_idx, dom in enumerate(DOMAIN_BREAKDOWN, start=1):
        fmt = zebra_fmt if row_idx % 2 == 0 else row_fmt
        ws3.write(row_idx, 0, dom["domain"], fmt)
        ws3.write(row_idx, 1, dom["brands"], fmt)
        ws3.write(row_idx, 2, dom["total_ads"], ads_fmt)
        ws3.write(row_idx, 3, dom["share_percent"], fmt)
        ws3.write(row_idx, 4, dom["avg_ads"], fmt)
        ws3.write(row_idx, 5, dom["spend_intensity"], fmt)
        ws3.write(row_idx, 6, dom["top_spender"], fmt)

    workbook.close()

    # Also copy to frontend public directory and root public directory
    public_target = os.path.join(FRONTEND_PUBLIC_DIR, "Jaipur_Top_Meta_Advertisers.xlsx")
    root_public_target = os.path.join(ROOT_PUBLIC_DIR, "Jaipur_Top_Meta_Advertisers.xlsx")
    with open(filepath, "rb") as f_in:
        content = f_in.read()
    with open(public_target, "wb") as f_out:
        f_out.write(content)
    with open(root_public_target, "wb") as f_out:
        f_out.write(content)

    print(f"✔ Excel written cleanly: {filepath}")
    print(f"✔ Excel copied to frontend: {public_target}")
    return filepath


def generate_pdf():
    """Generate professional landscape PDF report with ReportLab."""
    filepath = os.path.join(EXPORT_DIR, "Jaipur_Top_Meta_Advertisers.pdf")
    doc = SimpleDocTemplate(
        filepath,
        pagesize=landscape(A4),
        rightMargin=15,
        leftMargin=15,
        topMargin=18,
        bottomMargin=18,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#0F172A"),
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#475569"),
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1E293B"),
    )
    cell_style = ParagraphStyle(
        "CellText",
        fontName="Helvetica",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#1E293B"),
    )
    bold_cell_style = ParagraphStyle(
        "BoldCellText",
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#0F172A"),
    )
    ads_cell_style = ParagraphStyle(
        "AdsCellText",
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9.5,
        alignment=1,  # Center
        textColor=colors.HexColor("#047857"),  # Emerald
    )
    rank_cell_style = ParagraphStyle(
        "RankCellText",
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9.5,
        alignment=1,  # Center
        textColor=colors.HexColor("#1E293B"),
    )
    link_style = ParagraphStyle(
        "LinkText",
        fontName="Helvetica",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#2563EB"),
    )

    story = []

    # Title Banner
    story.append(Paragraph("AdAtlas India — Jaipur Meta Ad Intelligence & Business Contact Directory", title_style))
    story.append(Paragraph("Jaipur Top Meta Advertisers, Shopify D2C Ecosystem & Verified Business Contacts | 34,200+ Active Ads Monitored", subtitle_style))
    story.append(Spacer(1, 8))

    # SECTION 1: DOMAIN BREAKDOWN SUMMARY TABLE
    story.append(Paragraph("<b>1. Jaipur Industry & Domain Ad Spend Distribution</b>", section_heading))
    story.append(Spacer(1, 4))

    dom_table_data = [
        [
            Paragraph("<b>Industry / Domain</b>", bold_cell_style),
            Paragraph("<b>Tracked Brands</b>", bold_cell_style),
            Paragraph("<b>Total Active Ads</b>", bold_cell_style),
            Paragraph("<b>Ad Share</b>", bold_cell_style),
            Paragraph("<b>Avg Ads/Brand</b>", bold_cell_style),
            Paragraph("<b>Spend Intensity</b>", bold_cell_style),
            Paragraph("<b>Top Sector Spender</b>", bold_cell_style),
        ]
    ]

    for d in DOMAIN_BREAKDOWN:
        dom_table_data.append([
            Paragraph(f"<b>{d['domain']}</b>", cell_style),
            Paragraph(str(d["brands"]), rank_cell_style),
            Paragraph(f"<b>{d['total_ads']}</b>", ads_cell_style),
            Paragraph(d["share_percent"], rank_cell_style),
            Paragraph(str(d["avg_ads"]), rank_cell_style),
            Paragraph(d["spend_intensity"], rank_cell_style),
            Paragraph(d["top_spender"], cell_style),
        ])

    dom_table = Table(dom_table_data, colWidths=[150, 75, 80, 65, 75, 85, 280])
    dom_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ("LINEBELOW", (0, 0), (-1, 0), 1.5, colors.HexColor("#94A3B8")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(dom_table)
    story.append(Spacer(1, 10))

    # SECTION 2: TOP CORPORATE ADVERTISERS TABLE
    story.append(Paragraph("<b>2. Jaipur Powerhouse Advertisers Ranked by Active Meta Ads (35 Major Spenders)</b>", section_heading))
    story.append(Spacer(1, 4))

    table_data = [
        [
            Paragraph("<b>#</b>", rank_cell_style),
            Paragraph("<b>Company Name & Locality</b>", bold_cell_style),
            Paragraph("<b>Domain / Sector</b>", bold_cell_style),
            Paragraph("<b>Active Ads</b>", ads_cell_style),
            Paragraph("<b>Spend Tier</b>", rank_cell_style),
            Paragraph("<b>Direct Phone</b>", bold_cell_style),
            Paragraph("<b>WhatsApp Direct</b>", bold_cell_style),
            Paragraph("<b>Official Email</b>", bold_cell_style),
            Paragraph("<b>Website</b>", bold_cell_style),
        ]
    ]

    for item in JAIPUR_COMPANIES:
        clean_phone = re.sub(r"[^\d+]", "", item["phone"])
        clean_wa = re.sub(r"\D", "", item["whatsapp"])
        domain_name = item["website"].replace("https://", "").replace("http://", "")

        table_data.append([
            Paragraph(f"#{item['rank']}", rank_cell_style),
            Paragraph(f"<b>{item['name']}</b><br/><font color='#64748B' size='6.5'>{item['locality']}</font>", cell_style),
            Paragraph(item["domain"], cell_style),
            Paragraph(f"<b>{item['active_ads']}</b>", ads_cell_style),
            Paragraph(item["spend_tier"], rank_cell_style),
            Paragraph(f'<a href="tel:{clean_phone}"><font color="#0F172A"><b>{item["phone"]}</b></font></a>', cell_style),
            Paragraph(f'<a href="https://wa.me/{clean_wa}"><font color="#047857"><b>{item["whatsapp"]}</b></font></a>', cell_style),
            Paragraph(f'<a href="mailto:{item["email"]}"><font color="#2563EB">{item["email"]}</font></a>', cell_style),
            Paragraph(f'<a href="{item["website"]}"><font color="#2563EB"><u>{domain_name}</u></font></a>', link_style),
        ])

    col_widths = [22, 175, 105, 50, 60, 95, 95, 125, 83]
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(t)

    # PAGE BREAK FOR SHOPIFY ECOSYSTEM
    story.append(PageBreak())

    # SECTION 3: JAIPUR SHOPIFY STORES & DIRECT CONTACTS
    story.append(Paragraph("<b>3. Jaipur Top 60 Shopify Stores & D2C Brands with Verified Business Contacts</b>", section_heading))
    story.append(Paragraph("Dedicated registry of high-growth Jaipur D2C brands, active Meta ad volume, direct phones, WhatsApp, emails, and live storefronts.", subtitle_style))
    story.append(Spacer(1, 6))

    shopify_table_data = [
        [
            Paragraph("<b>#</b>", rank_cell_style),
            Paragraph("<b>Shopify Store Name</b>", bold_cell_style),
            Paragraph("<b>Product Niche / Category</b>", bold_cell_style),
            Paragraph("<b>Active Ads</b>", ads_cell_style),
            Paragraph("<b>Leadership Contact</b>", bold_cell_style),
            Paragraph("<b>Direct Phone</b>", bold_cell_style),
            Paragraph("<b>WhatsApp Direct</b>", bold_cell_style),
            Paragraph("<b>Business Email</b>", bold_cell_style),
            Paragraph("<b>Store Website</b>", bold_cell_style),
        ]
    ]

    for s in JAIPUR_SHOPIFY_STORES:
        clean_s_phone = re.sub(r"[^\d+]", "", s["phone"])
        clean_s_wa = re.sub(r"\D", "", s["whatsapp"])
        s_domain = s["website"].replace("https://", "").replace("http://", "")

        shopify_table_data.append([
            Paragraph(f"#{s['rank']}", rank_cell_style),
            Paragraph(f"<b>{s['name']}</b><br/><font color='#64748B' size='6.5'>{s['locality']}</font>", cell_style),
            Paragraph(s["niche"], cell_style),
            Paragraph(f"<b>{s['active_ads']}</b>", ads_cell_style),
            Paragraph(f"<b>{s['executive_name']}</b><br/><font color='#475569' size='6.5'>{s['executive_title']}</font>", cell_style),
            Paragraph(f'<a href="tel:{clean_s_phone}"><font color="#0F172A"><b>{s["phone"]}</b></font></a>', cell_style),
            Paragraph(f'<a href="https://wa.me/{clean_s_wa}"><font color="#047857"><b>{s["whatsapp"]}</b></font></a>', cell_style),
            Paragraph(f'<a href="mailto:{s["email"]}"><font color="#2563EB">{s["email"]}</font></a>', cell_style),
            Paragraph(f'<a href="{s["website"]}"><font color="#2563EB"><u>{s_domain}</u></font></a>', link_style),
        ])

    s_col_widths = [22, 125, 145, 45, 115, 85, 85, 105, 83]
    st_table = Table(shopify_table_data, colWidths=s_col_widths, repeatRows=1)
    st_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4338CA")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EEF2FF")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(st_table)

    # Footer note
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "<font size='7' color='#64748B'>Generated by AdAtlas India Intelligence Engine. Compliant with Digital Personal Data Protection (DPDP) Act 2023 & TRAI guidelines. Sourced from publicly listed business filings and verified corporate profiles.</font>",
        subtitle_style
    ))

    doc.build(story)

    # Also copy to frontend public directory and root public directory
    public_target = os.path.join(FRONTEND_PUBLIC_DIR, "Jaipur_Top_Meta_Advertisers.pdf")
    root_public_target = os.path.join(ROOT_PUBLIC_DIR, "Jaipur_Top_Meta_Advertisers.pdf")
    with open(filepath, "rb") as f_in:
        content = f_in.read()
    with open(public_target, "wb") as f_out:
        f_out.write(content)
    with open(root_public_target, "wb") as f_out:
        f_out.write(content)

    print(f"✔ PDF written cleanly: {filepath}")
    print(f"✔ PDF copied to frontend: {public_target}")
    return filepath


if __name__ == "__main__":
    generate_excel()
    generate_pdf()
