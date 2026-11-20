"""Default settings. Everything here can be changed later from the Settings tab."""

# Fixed per-country display config (colours / labels for each category).
COUNTRY_META = {
    "India": {
        "flag": "🇮🇳",
        "currency": "INR",
        "categories": {
            "North": {"label": "HIGH RISK", "tone": "red"},
            "South": {"label": "LOW RISK", "tone": "green"},
            "Other": {"label": "NEEDS REVIEW", "tone": "amber"},
        },
        "unknown": {"label": "NOT FOUND", "tone": "grey",
                    "text": "We couldn't match this to a known region. Check the spelling or add it in Settings."},
    },
    "Pakistan": {
        "flag": "🇵🇰",
        "currency": "PKR",
        "categories": {
            "Restricted": {"label": "RESTRICTED", "tone": "red"},
            "Allowed": {"label": "ALLOWED", "tone": "green"},
        },
        # Pakistan: anything not on the restricted list is treated as allowed.
        "unknown": {"label": "NOT ON RESTRICTED LIST", "tone": "green",
                    "text": "No match with any restricted region. Double-check the spelling "
                            "(try typing fewer letters to see similar names)."},
    },
}

_INDIA = {
    "North": {
        "Delhi": ["New Delhi", "Noida", "Gurgaon", "Gurugram", "Faridabad", "Ghaziabad"],
        "Punjab": ["Amritsar", "Ludhiana", "Jalandhar", "Patiala", "Mohali", "Bathinda", "Gurdaspur"],
        "Haryana": ["Ambala", "Karnal", "Panipat", "Rohtak", "Hisar", "Sonipat"],
        "Himachal Pradesh": ["Shimla", "Manali", "Dharamshala", "Solan"],
        "Jammu and Kashmir": ["Srinagar", "Jammu", "Anantnag", "Baramulla"],
        "Ladakh": ["Leh", "Kargil"],
        "Uttarakhand": ["Dehradun", "Haridwar", "Rishikesh", "Nainital"],
        "Uttar Pradesh": ["Lucknow", "Kanpur", "Agra", "Varanasi", "Meerut", "Allahabad", "Prayagraj", "Aligarh", "Bareilly", "Moradabad"],
        "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer", "Bikaner"],
        "Chandigarh": [],
    },
    "South": {
        "Kerala": ["Kochi", "Cochin", "Thiruvananthapuram", "Trivandrum", "Kozhikode", "Calicut", "Thrissur", "Kollam", "Kannur"],
        "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Trichy", "Salem", "Vellore", "Tirunelveli"],
        "Karnataka": ["Bengaluru", "Bangalore", "Mysuru", "Mysore", "Mangaluru", "Mangalore", "Hubli", "Belgaum"],
        "Andhra Pradesh": ["Visakhapatnam", "Vizag", "Vijayawada", "Guntur", "Tirupati", "Nellore"],
        "Telangana": ["Hyderabad", "Warangal", "Secunderabad", "Karimnagar", "Nizamabad"],
        "Puducherry": ["Pondicherry"],
        "Lakshadweep": [],
    },
    "Other": {
        "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad"],
        "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot"],
        "Goa": ["Panaji"],
        "Madhya Pradesh": ["Bhopal", "Indore", "Gwalior", "Jabalpur"],
        "Chhattisgarh": ["Raipur", "Bilaspur"],
        "West Bengal": ["Kolkata", "Calcutta", "Howrah", "Siliguri"],
        "Bihar": ["Patna", "Gaya", "Muzaffarpur"],
        "Jharkhand": ["Ranchi", "Jamshedpur", "Dhanbad"],
        "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela"],
        "Assam": ["Guwahati", "Dibrugarh"],
        "Meghalaya": ["Shillong"],
        "Manipur": ["Imphal"],
        "Mizoram": ["Aizawl"],
        "Nagaland": ["Kohima"],
        "Tripura": ["Agartala"],
        "Arunachal Pradesh": ["Itanagar"],
        "Sikkim": ["Gangtok"],
        "Andaman and Nicobar Islands": ["Port Blair"],
        "Dadra and Nagar Haveli and Daman and Diu": ["Daman", "Silvassa"],
    },
}


def _india_regions():
    out = []
    for cat, states in _INDIA.items():
        for state, cities in states.items():
            out.append({"name": state, "category": cat, "aliases": []})
            for c in cities:
                out.append({"name": f"{c} ({state})", "category": cat, "aliases": [c]})
    return out


_PAKISTAN_RESTRICTED = [
    ("Bajaur", ["Bajor", "Bajour", "Bajaur Agency"]),
    ("Chenab Nagar", ["Chanab Nager", "Chenab Nager", "Rabwah", "Rabwa"]),
    ("Chiniot", ["Chinute", "Chinyot", "Chiniyot"]),
    ("Khyber", ["Khaibar", "Khyber Agency", "Khyber District", "Landi Kotal"]),
    ("Malakand", ["Malakund", "Malakand Division"]),
    ("Mardan", ["Murdan"]),
    ("Nowshera", ["Nowshehra", "Nowshara", "Nowshehra"]),
]

DEFAULT_SETTINGS = {
    "version": 1,
    "countries": {
        "India": {
            "buffer": 10,
            "living": {"London": 13761, "Main": 10539},
            "regions": _india_regions(),
        },
        "Pakistan": {
            "buffer": 30,
            "living": {"London": 13761, "Main": 10539},
            "regions": [
                {"name": n, "category": "Restricted", "aliases": a}
                for n, a in _PAKISTAN_RESTRICTED
            ],
        },
    },
}
