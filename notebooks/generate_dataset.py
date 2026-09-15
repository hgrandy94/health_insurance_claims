import csv
import random
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path


random.seed(20260908)
OUTPUT_DIR = Path(__file__).parent

FIRST_NAMES = ["Amelia", "Oliver", "Isla", "George", "Ava", "Arthur", "Emily", "Harry", "Grace", "Jack", "Sophie", "Noah", "Poppy", "Leo", "Ella", "Oscar", "Evie", "Charlie", "Mia", "Henry"]
LAST_NAMES = ["Bennett", "Clarke", "Davies", "Edwards", "Foster", "Graham", "Hughes", "Jenkins", "Khan", "Lewis", "Marshall", "Morgan", "Patel", "Reed", "Shaw", "Taylor", "Turner", "Walker", "Webb", "Wright"]
REGIONS = ["London", "South East", "South West", "East of England", "West Midlands", "East Midlands", "Yorkshire and the Humber", "North West", "North East", "Wales", "Scotland"]
PROVIDERS = [
    ("PRV001", "Northbridge Private Hospital", "London"),
    ("PRV002", "Riverside Diagnostics", "South East"),
    ("PRV003", "Cedar Grove Clinic", "South West"),
    ("PRV004", "Westmoor Orthopaedics", "West Midlands"),
    ("PRV005", "Harbourview Specialist Centre", "North West"),
    ("PRV006", "Meadowlands Day Hospital", "Yorkshire and the Humber"),
    ("PRV007", "Kingswell Cardiology Group", "Scotland"),
    ("PRV008", "Oakfield Imaging Centre", "East of England"),
    ("PRV009", "Southbank Physiotherapy Network", "London"),
    ("PRV010", "Lakeside Surgical Centre", "North East"),
]
TREATMENTS = [
    ("Consultation", "M25.5", 180, 650),
    ("MRI scan", "M54.5", 450, 950),
    ("Physiotherapy", "M25.5", 75, 420),
    ("Cataract procedure", "H25.9", 1800, 4200),
    ("Minor surgery", "L98.9", 900, 2800),
    ("Cardiology review", "I10", 220, 850),
    ("Cancer treatment", "C50.9", 2500, 12000),
    ("Mental health therapy", "F41.9", 90, 900),
    ("Day-case surgery", "K40.9", 1400, 5000),
]


def write_csv(filename, rows, fieldnames):
    with (OUTPUT_DIR / filename).open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))


def money(value):
    return f"{Decimal(str(value)).quantize(Decimal('0.01')):.2f}"


def build_policyholders():
    rows = []
    for number in range(1, 301):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        joined = random_date(date(2018, 1, 1), date(2023, 12, 31))
        rows.append({
            "policyholder_id": f"PH{number:05d}",
            "policy_number": f"DEMO-POL-{number:06d}",
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": random_date(date(1940, 1, 1), date(2002, 12, 31)).isoformat(),
            "postcode_area": random.choice(["SW", "SE", "EC", "BS", "B", "M", "LS", "EH", "CF", "NE"]),
            "region": random.choice(REGIONS),
            "plan_type": random.choice(["Essentials", "Comprehensive", "Premium", "Corporate Select"]),
            "cover_start_date": joined.isoformat(),
            "cover_status": random.choices(["Active", "Lapsed", "Cancelled"], weights=[88, 7, 5])[0],
            "annual_premium_gbp": money(random.randint(950, 5200)),
            "employer_sponsored": random.choice(["Yes", "No"]),
        })
    return rows


def build_claims(policyholders):
    rows = []
    for number in range(1, 801):
        policyholder = random.choice(policyholders)
        treatment, diagnosis, low, high = random.choice(TREATMENTS)
        service_date = random_date(date(2022, 1, 1), date(2025, 12, 31))
        submitted_date = service_date + timedelta(days=random.randint(1, 35))
        provider_id, provider_name, provider_region = random.choice(PROVIDERS)
        billed = random.uniform(low, high)
        approved = billed * random.uniform(0.72, 1.0)
        rows.append({
            "claim_id": f"CLM{number:07d}",
            "policyholder_id": policyholder["policyholder_id"],
            "provider_id": provider_id,
            "provider_name": provider_name,
            "provider_region": provider_region,
            "service_date": service_date.isoformat(),
            "submitted_date": submitted_date.isoformat(),
            "claim_type": treatment,
            "diagnosis_code": diagnosis,
            "billed_amount_gbp": money(billed),
            "approved_amount_gbp": money(approved),
            "claim_status": random.choices(["Paid", "Partially paid", "Declined", "Withdrawn"], weights=[72, 16, 9, 3])[0],
            "submission_channel": random.choices(["Member portal", "Provider portal", "Post", "Telephone"], weights=[48, 37, 5, 10])[0],
            "provider_region_match": "Yes" if provider_region == policyholder["region"] else "No",
        })

    # Deliberately plant explainable review patterns for fraud-analysis demos.
    for number in range(1, 21):
        claim = rows[number * 17 - 1]
        claim["billed_amount_gbp"] = money(9800 + number * 125)
        claim["approved_amount_gbp"] = money(float(claim["billed_amount_gbp"]) * 0.25)
        claim["submitted_date"] = (date.fromisoformat(claim["service_date"]) + timedelta(days=2)).isoformat()
        claim["submission_channel"] = "Provider portal"
    return rows


def build_investigations(claims):
    rows = []
    review_claims = {claim["claim_id"]: index for index, claim in enumerate(claims) if index % 17 == 16}
    for number, claim in enumerate(claims, start=1):
        claim_id = claim["claim_id"]
        index = number - 1
        high_value = float(claim["billed_amount_gbp"]) >= 9000
        same_provider_count = 1 + ((index * 7) % 8)
        risk_points = (45 if high_value else 0) + (20 if index % 29 == 0 else 0) + (15 if same_provider_count >= 7 else 0)
        if claim_id in review_claims:
            flag = "High-value claim; unusual amount"
            risk_points = max(risk_points, 65)
            event_count = 3
        elif risk_points >= 45:
            flag = "High-value claim"
            event_count = 2
        elif index % 31 == 0:
            flag = "Repeated provider/member pattern"
            risk_points = max(risk_points, 35)
            event_count = 2
        else:
            flag = "No automated concern"
            event_count = 1

        for sequence in range(1, event_count + 1):
            if sequence == 1:
                stage = "Automated screening"
                outcome = "Evidence requested" if flag != "No automated concern" else "Cleared"
            elif sequence == event_count and high_value:
                stage = "SIU review"
                outcome = "Referred to SIU"
            else:
                stage = "Analyst review"
                outcome = "No concern identified"
            review_date = date.fromisoformat(claim["submitted_date"]) + timedelta(days=random.randint(0, 5) + (sequence - 1) * 7)
            rows.append({
                "investigation_id": f"INV{len(rows) + 1:07d}",
                "claim_id": claim_id,
                "review_sequence": sequence,
                "investigation_stage": stage,
                "review_created_date": review_date.isoformat(),
                "risk_score": min(99, risk_points + random.randint(0, 12) + (sequence - 1) * 4),
                "primary_flag": flag,
                "provider_claims_last_90_days": same_provider_count,
                "member_claims_last_90_days": 1 + ((index * 5) % 5),
                "duplicate_document_signal": "Yes" if index % 47 == 0 else "No",
                "identity_mismatch_signal": "Yes" if index % 61 == 0 else "No",
                "investigation_outcome": outcome,
                "investigation_closed_date": (review_date + timedelta(days=random.randint(6, 45))).isoformat() if outcome != "Cleared" else "",
                "analyst_notes": "Synthetic demonstration record; review outcome is simulated." if outcome != "Cleared" else "Synthetic demonstration record; no concern identified.",
            })
    return rows


policyholders = build_policyholders()
claims = build_claims(policyholders)
investigations = build_investigations(claims)

write_csv("policyholders.csv", policyholders, list(policyholders[0]))
write_csv("claims.csv", claims, list(claims[0]))
write_csv("claim_investigations.csv", investigations, list(investigations[0]))