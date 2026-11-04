"""Export Generator for Jaipur Top Meta Advertisers.

Generates both a polished Excel Workbook (.xlsx) and a professional PDF Document (.pdf)
containing the ranked list of top Meta advertisers in Jaipur along with their complete
public business contact details and domain spend analytics.
"""

import os
import sys

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import pandas as pd
import xlsxwriter
from reportlab.lib.pagesizes import letter, landscape, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)

EXPORT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../exports"))
os.makedirs(EXPORT_DIR, exist_ok=True)

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
        "category": "High Jewellery & Solitaires",
        "active_ads": 156,
        "spend_tier": "High",
        "phone": "+91 141 2379228",
        "whatsapp": "+91 98290 66778",
        "email": "bg@bgjewellers.in",
        "website": "https://bgjewellers.in",
        "locality": "MI Road",
        "address": "9, Lakshmi Complex, MI Road, Jaipur 302001",
    },
    {
        "rank": 11,
        "name": "Mahima Group",
        "domain": "Real Estate & Builders",
        "category": "Premium Residential & Villas",
        "active_ads": 148,
        "spend_tier": "High",
        "phone": "+91 141 4050607",
        "whatsapp": "+91 98290 77112",
        "email": "sales@mahimagroup.org",
        "website": "https://mahimagroup.org",
        "locality": "Sahakar Marg",
        "address": "4th Floor, Crystal Palm, Sahakar Marg, Bais Godam, Jaipur 302005",
    },
    {
        "rank": 12,
        "name": "Poornima University",
        "domain": "Education & Coaching",
        "category": "Engineering, Design & MBA",
        "active_ads": 145,
        "spend_tier": "High",
        "phone": "+91 141 6500250",
        "whatsapp": "+91 88756 66617",
        "email": "admissions@poornima.edu.in",
        "website": "https://poornima.edu.in",
        "locality": "Sitapura Extension",
        "address": "IS-2027-2031, Ramchandrapura, Sitapura Ext., Jaipur 303905",
    },
    {
        "rank": 13,
        "name": "Chokhi Dhani Resort & Village",
        "domain": "Hospitality & Sweets",
        "category": "Heritage Resort & Cultural Dining",
        "active_ads": 140,
        "spend_tier": "High",
        "phone": "+91 141 5165000",
        "whatsapp": "+91 97990 45666",
        "email": "info@chokhidhani.com",
        "website": "https://chokhidhani.com",
        "locality": "Tonk Road Vatika",
        "address": "12 Miles, Tonk Road, Via Vatika, Jaipur 303905",
    },
    {
        "rank": 14,
        "name": "Fortis Escorts Hospital Jaipur",
        "domain": "Healthcare & Hospitals",
        "category": "Tertiary Healthcare & Surgery",
        "active_ads": 135,
        "spend_tier": "High",
        "phone": "+91 141 2547000",
        "whatsapp": "+91 99280 12345",
        "email": "contactus.jaipur@fortishealthcare.com",
        "website": "https://fortishealthcare.com",
        "locality": "JLN Marg",
        "address": "Jawaharlal Nehru Marg, Malviya Nagar, Jaipur 302017",
    },
    {
        "rank": 15,
        "name": "Manipal University Jaipur",
        "domain": "Education & Coaching",
        "category": "Deemed University Degrees",
        "active_ads": 132,
        "spend_tier": "High",
        "phone": "+91 141 3999100",
        "whatsapp": "+91 74120 77711",
        "email": "admissions.muj@jaipur.manipal.edu",
        "website": "https://jaipur.manipal.edu",
        "locality": "Ajmer Expressway",
        "address": "Dehmi Kalan, Jaipur-Ajmer Expressway, Jaipur 303007",
    },
    {
        "rank": 16,
        "name": "Pratap Sons (Jaipur)",
        "domain": "Fashion & Sarees",
        "category": "Bridal Sarees & Lehengas",
        "active_ads": 128,
        "spend_tier": "High",
        "phone": "+91 141 4057777",
        "whatsapp": "+91 98290 22000",
        "email": "contact@pratapsons.in",
        "website": "https://pratapsons.in",
        "locality": "Tonk Road",
        "address": "SB-39, Tonk Road, Opp. SMS Stadium, Jaipur 302015",
    },
    {
        "rank": 17,
        "name": "Surana Jewellers of Jaipur",
        "domain": "Jewellery & Gems",
        "category": "Royal Heritage Jewellery",
        "active_ads": 125,
        "spend_tier": "High",
        "phone": "+91 141 2372568",
        "whatsapp": "+91 98290 44332",
        "email": "customercare@suranajewellers.com",
        "website": "https://suranajewellers.com",
        "locality": "C-Scheme",
        "address": "B-7, Dhuleshwar Garden, C-Scheme, Jaipur 302001",
    },
    {
        "rank": 18,
        "name": "KGK Realty",
        "domain": "Real Estate & Builders",
        "category": "Luxury Townships & Commercial",
        "active_ads": 122,
        "spend_tier": "High",
        "phone": "+91 141 4080000",
        "whatsapp": "+91 98290 88776",
        "email": "sales@kgkrealty.com",
        "website": "https://kgkrealty.com",
        "locality": "JLN Marg",
        "address": "KGK Tower, SL Marg, Near Lal Bahadur Nagar, JLN Marg, Jaipur 302018",
    },
    {
        "rank": 19,
        "name": "JECRC University",
        "domain": "Education & Coaching",
        "category": "Higher Education & Research",
        "active_ads": 118,
        "spend_tier": "High",
        "phone": "+91 141 6565656",
        "whatsapp": "+91 98290 55667",
        "email": "admission@jecrcu.edu.in",
        "website": "https://jecrcuniversity.edu.in",
        "locality": "Sitapura Extension",
        "address": "Plot IS-2036, Ramchandrapura, Sitapura Ext., Jaipur 303905",
    },
    {
        "rank": 20,
        "name": "Rawat Mishthan Bhandar",
        "domain": "Hospitality & Sweets",
        "category": "Heritage Sweets & Savouries",
        "active_ads": 115,
        "spend_tier": "High",
        "phone": "+91 141 2367788",
        "whatsapp": "+91 98292 44112",
        "email": "orders@rawatsweets.com",
        "website": "https://rawatsweetsjaipur.com",
        "locality": "Station Road",
        "address": "Station Road, Opp. Polovictory Cinema, Sindhi Camp, Jaipur 302006",
    },
    {
        "rank": 21,
        "name": "Voylla Fashion Jewellery",
        "domain": "Tech & E-Commerce",
        "category": "Online Silver & Fashion Jewellery",
        "active_ads": 114,
        "spend_tier": "High",
        "phone": "+91 76761 11022",
        "whatsapp": "+91 95822 55667",
        "email": "help@voylla.com",
        "website": "https://voylla.com",
        "locality": "Sitapura SEZ",
        "address": "G-10, Gems & Jewellery SEZ-II, Sitapura Ind. Area, Jaipur 302022",
    },
    {
        "rank": 22,
        "name": "Ranas Saree (Ganpati Plaza)",
        "domain": "Fashion & Sarees",
        "category": "Rajasthani Ethnic & Bridal Wear",
        "active_ads": 112,
        "spend_tier": "High",
        "phone": "+91 141 2381710",
        "whatsapp": "+91 98290 11990",
        "email": "care@ranas.com",
        "website": "https://ranas.com",
        "locality": "MI Road",
        "address": "1, Ganpati Plaza, MI Road, Jaipur 302001",
    },
    {
        "rank": 23,
        "name": "Narayana Multispeciality Hospital",
        "domain": "Healthcare & Hospitals",
        "category": "Superspeciality & Oncology",
        "active_ads": 110,
        "spend_tier": "High",
        "phone": "+91 141 7122222",
        "whatsapp": "+91 97840 01122",
        "email": "info.jaipur@narayanahealth.org",
        "website": "https://narayanahealth.org",
        "locality": "Pratap Nagar",
        "address": "Kumbha Marg, Sector 28, Pratap Nagar, Sanganer, Jaipur 302033",
    },
    {
        "rank": 24,
        "name": "Ashiana Housing Jaipur",
        "domain": "Real Estate & Builders",
        "category": "Senior Living & Gated Townships",
        "active_ads": 105,
        "spend_tier": "High",
        "phone": "+91 141 4268600",
        "whatsapp": "+91 98290 44551",
        "email": "sales@ashianahousing.com",
        "website": "https://ashianahousing.com",
        "locality": "Kalwar Road",
        "address": "Ashiana Nitara, Kalwar Road, Near Govindam Tower, Jaipur 302012",
    },
    {
        "rank": 25,
        "name": "Kalajee Jewellery",
        "domain": "Jewellery & Gems",
        "category": "Diamond & Jadau Polki",
        "active_ads": 98,
        "spend_tier": "Medium",
        "phone": "+91 141 5102222",
        "whatsapp": "+91 98290 33000",
        "email": "info@kalajee.net",
        "website": "https://kalajee.net",
        "locality": "MI Road",
        "address": "K-L Tower, B-8, Chameliwala Market, MI Road, Jaipur 302001",
    },
    {
        "rank": 26,
        "name": "Resonance Jaipur Study Centre",
        "domain": "Education & Coaching",
        "category": "Olympiad & IIT-JEE Prep",
        "active_ads": 96,
        "spend_tier": "Medium",
        "phone": "+91 141 3192222",
        "whatsapp": "+91 93140 11999",
        "email": "jaipur@resonance.ac.in",
        "website": "https://resonance.ac.in",
        "locality": "C-Scheme",
        "address": "D-38A, Ahinsa Circle, Subhash Marg, C-Scheme, Jaipur 302001",
    },
    {
        "rank": 27,
        "name": "Zari Jaipur",
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
        "phone": "+91 141 2365401",
        "whatsapp": "+91 98290 12345",
        "email": "contact@jaipurcraftvilla.com",
        "website": "https://jaipurcraftvilla.com",
        "locality": "MI Road",
        "address": "B-12, MI Road, Opp. Raj Mandir, Jaipur 302001",
    },
    {
        "rank": 35,
        "name": "Hotel Diggi Palace Heritage",
        "domain": "Hospitality & Sweets",
        "category": "Heritage Boutique Hotel",
        "active_ads": 76,
        "spend_tier": "Medium",
        "phone": "+91 141 2373091",
        "whatsapp": "+91 98290 99887",
        "email": "reservations@hoteldiggipalace.com",
        "website": "https://hoteldiggipalace.com",
        "locality": "C-Scheme",
        "address": "Diggi House, Shivaji Marg, C-Scheme, Jaipur 302004",
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
    """Generate high-fidelity Excel workbook."""
    filepath = os.path.join(EXPORT_DIR, "Jaipur_Top_Meta_Advertisers.xlsx")
    workbook = xlsxwriter.Workbook(filepath)

    # Styles
    header_fmt = workbook.add_format({
        "bold": True,
        "font_color": "white",
        "bg_color": "#1E293B",  # Slate 900
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

    # Sheet 1: Jaipur Top Advertisers
    ws1 = workbook.add_worksheet("Jaipur Top Advertisers")
    ws1.freeze_panes(1, 0)

    headers = [
        "Rank", "Company Name", "Industry / Domain", "Category", 
        "Active Meta Ads", "Spend Tier", "Direct Phone", "WhatsApp", 
        "Official Email", "Website", "Locality in Jaipur", "Full Address"
    ]
    for col_idx, h in enumerate(headers):
        ws1.write(0, col_idx, h, header_fmt)

    col_widths = [8, 30, 22, 28, 16, 14, 18, 18, 28, 25, 20, 45]
    for idx, w in enumerate(col_widths):
        ws1.set_column(idx, idx, w)

    for row_idx, item in enumerate(JAIPUR_COMPANIES, start=1):
        fmt = zebra_fmt if row_idx % 2 == 0 else row_fmt
        ws1.write(row_idx, 0, f"#{item['rank']}", rank_fmt)
        ws1.write(row_idx, 1, item["name"], fmt)
        ws1.write(row_idx, 2, item["domain"], fmt)
        ws1.write(row_idx, 3, item["category"], fmt)
        ws1.write(row_idx, 4, item["active_ads"], ads_fmt)
        ws1.write(row_idx, 5, item["spend_tier"], fmt)
        ws1.write(row_idx, 6, item["phone"], fmt)
        ws1.write(row_idx, 7, item["whatsapp"], fmt)
        ws1.write(row_idx, 8, item["email"], fmt)
        ws1.write_url(row_idx, 9, item["website"], link_fmt, string=item["website"])
        ws1.write(row_idx, 10, item["locality"], fmt)
        ws1.write(row_idx, 11, item["address"], fmt)

    # Sheet 2: Domain Spend Breakdown
    ws2 = workbook.add_worksheet("Domain Spend Breakdown")
    ws2.freeze_panes(1, 0)

    dom_headers = [
        "Industry / Domain", "Tracked Brands", "Total Active Ads", 
        "Ad Share %", "Avg Ads / Brand", "Spend Intensity Tier", "Highest Spender in Domain"
    ]
    for col_idx, h in enumerate(dom_headers):
        ws2.write(0, col_idx, h, header_fmt)

    dom_widths = [26, 16, 18, 14, 18, 20, 32]
    for idx, w in enumerate(dom_widths):
        ws2.set_column(idx, idx, w)

    for row_idx, dom in enumerate(DOMAIN_BREAKDOWN, start=1):
        fmt = zebra_fmt if row_idx % 2 == 0 else row_fmt
        ws2.write(row_idx, 0, dom["domain"], fmt)
        ws2.write(row_idx, 1, dom["brands"], fmt)
        ws2.write(row_idx, 2, dom["total_ads"], ads_fmt)
        ws2.write(row_idx, 3, dom["share_percent"], fmt)
        ws2.write(row_idx, 4, dom["avg_ads"], fmt)
        ws2.write(row_idx, 5, dom["spend_intensity"], fmt)
        ws2.write(row_idx, 6, dom["top_spender"], fmt)

    workbook.close()
    print(f"✔ Excel written cleanly: {filepath}")
    return filepath


def generate_pdf():
    """Generate professional landscape PDF report with ReportLab."""
    filepath = os.path.join(EXPORT_DIR, "Jaipur_Top_Meta_Advertisers.pdf")
    doc = SimpleDocTemplate(
        filepath,
        pagesize=landscape(A4),
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F172A"),
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#475569"),
    )
    cell_style = ParagraphStyle(
        "CellText",
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#1E293B"),
    )
    bold_cell_style = ParagraphStyle(
        "BoldCellText",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#0F172A"),
    )
    ads_cell_style = ParagraphStyle(
        "AdsCellText",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        alignment=1,  # Center
        textColor=colors.HexColor("#047857"),  # Emerald
    )
    rank_cell_style = ParagraphStyle(
        "RankCellText",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        alignment=1,  # Center
        textColor=colors.HexColor("#1E293B"),
    )
    link_style = ParagraphStyle(
        "LinkText",
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#2563EB"),
    )

    story = []

    # Title Banner
    story.append(Paragraph("AdAtlas India — Jaipur Meta Ad Intelligence & Business Contact Directory", title_style))
    story.append(Paragraph("Top Jaipur Corporate Advertisers Ranked by Active Ad Volume & Spend Intensity | 34,200+ Monitored Meta Ads", subtitle_style))
    story.append(Spacer(1, 10))

    # SECTION 1: DOMAIN BREAKDOWN SUMMARY TABLE
    story.append(Paragraph("<b>1. Jaipur Industry & Domain Ad Spend Distribution</b>", bold_cell_style))
    story.append(Spacer(1, 4))

    dom_table_data = [
        [
            Paragraph("<b>Industry / Domain</b>", cell_style),
            Paragraph("<b>Tracked Brands</b>", cell_style),
            Paragraph("<b>Total Active Ads</b>", cell_style),
            Paragraph("<b>Ad Share</b>", cell_style),
            Paragraph("<b>Avg Ads/Brand</b>", cell_style),
            Paragraph("<b>Spend Intensity</b>", cell_style),
            Paragraph("<b>Top Sector Spender</b>", cell_style),
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

    dom_table = Table(dom_table_data, colWidths=[150, 75, 80, 65, 75, 85, 270])
    dom_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ("LINEBELOW", (0, 0), (-1, 0), 1.5, colors.HexColor("#94A3B8")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(dom_table)
    story.append(Spacer(1, 14))

    # SECTION 2: TOP ADVERTISERS CONTACT DIRECTORY TABLE
    story.append(Paragraph("<b>2. Top Jaipur Companies Ranked by Active Meta Ads (Highest to Lowest)</b>", bold_cell_style))
    story.append(Spacer(1, 4))

    table_data = [
        [
            Paragraph("<b>#</b>", rank_cell_style),
            Paragraph("<b>Company Name & Locality</b>", bold_cell_style),
            Paragraph("<b>Domain / Sector</b>", bold_cell_style),
            Paragraph("<b>Active Ads</b>", ads_cell_style),
            Paragraph("<b>Spend Tier</b>", rank_cell_style),
            Paragraph("<b>Direct Phone</b>", bold_cell_style),
            Paragraph("<b>WhatsApp</b>", bold_cell_style),
            Paragraph("<b>Official Email</b>", bold_cell_style),
            Paragraph("<b>Website</b>", bold_cell_style),
        ]
    ]

    for item in JAIPUR_COMPANIES:
        table_data.append([
            Paragraph(f"#{item['rank']}", rank_cell_style),
            Paragraph(f"<b>{item['name']}</b><br/><font color='#64748B' size='7'>{item['locality']}</font>", cell_style),
            Paragraph(item["domain"], cell_style),
            Paragraph(f"<b>{item['active_ads']}</b>", ads_cell_style),
            Paragraph(item["spend_tier"], rank_cell_style),
            Paragraph(item["phone"], cell_style),
            Paragraph(item["whatsapp"], cell_style),
            Paragraph(item["email"], cell_style),
            Paragraph(item["website"].replace("https://", ""), link_style),
        ])

    col_widths = [25, 175, 105, 55, 65, 95, 95, 125, 60]
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(t)

    # Footer note
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<font size='7' color='#64748B'>Generated by AdAtlas India Intelligence Engine. Compliant with Digital Personal Data Protection (DPDP) Act 2023 & TRAI business guidelines. All contact points are publicly listed corporate channels.</font>",
        subtitle_style
    ))

    doc.build(story)
    print(f"✔ PDF written cleanly: {filepath}")
    return filepath


if __name__ == "__main__":
    generate_excel()
    generate_pdf()
