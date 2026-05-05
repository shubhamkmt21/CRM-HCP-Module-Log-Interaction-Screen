import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import Interaction
import random

def main():
    db = SessionLocal()
    
    # 1. Clean all recent interactions except Dr. Smith
    try:
        interactions = db.query(Interaction).all()
        deleted_count = 0
        for i in interactions:
            if "smith" not in i.hcp_name.lower():
                db.delete(i)
                deleted_count += 1
        db.commit()
        print(f"Deleted {deleted_count} old interactions.")
    except Exception as e:
        print("Error deleting:", e)
        db.rollback()
    
    # 2. Put random doctor names and cases
    doctors = [
        "Dr. Emily Chen", "Dr. Marcus Johnson", "Dr. Sarah Williams",
        "Dr. David Lee", "Dr. Robert Garcia", "Dr. Lisa Taylor",
        "Dr. James Wilson", "Dr. Anita Desai"
    ]
    
    cases = [
        {
            "type": "Meeting",
            "notes": "Discussed the new clinical trial results for CardiQ. HCP showed strong interest in the safety profile.",
            "materials": "CardiQ Phase 3 Clinical Summary",
            "samples": "CardiQ Starter Pack x5",
            "sentiment": "Positive",
            "outcomes": "Agreed to start 3 patients on trial.",
            "actions": "Follow up in 2 weeks to check on patient progress."
        },
        {
            "type": "Virtual",
            "notes": "Brief telemedicine check-in regarding recent supply chain issues for NeuroZen. HCP was slightly frustrated but understanding.",
            "materials": "Supply Chain Update PDF",
            "samples": "None",
            "sentiment": "Neutral",
            "outcomes": "Clarified delivery timelines.",
            "actions": "Send confirmation email once shipment is dispatched."
        },
        {
            "type": "Call",
            "notes": "Cold call to introduce the updated formulation of Respira. HCP was busy and requested an email summary instead.",
            "materials": "None",
            "samples": "None",
            "sentiment": "Negative",
            "outcomes": "HCP ended call quickly.",
            "actions": "Send short executive summary via email."
        },
        {
            "type": "Meeting",
            "notes": "Lunch and learn session with the whole clinic. Presented data on OncoBoost efficacy in late-stage patients.",
            "materials": "OncoBoost Slide Deck, Efficacy Whitepaper",
            "samples": "OncoBoost Demo Kits",
            "sentiment": "Positive",
            "outcomes": "Entire staff is now trained on the new administration protocol.",
            "actions": "Schedule next quarter's lunch and learn."
        },
        {
            "type": "Email",
            "notes": "Sent requested documentation on drug-drug interactions between our product and common blood thinners.",
            "materials": "DDI Guidelines Document",
            "samples": "None",
            "sentiment": "Neutral",
            "outcomes": "Provided necessary medical information.",
            "actions": "Wait for HCP to review and follow up next month."
        }
    ]
    
    try:
        added_count = 0
        for _ in range(8):  # add 8 random entries
            doc = random.choice(doctors)
            case = random.choice(cases)
            new_int = Interaction(
                hcp_name=doc,
                interaction_type=case["type"],
                interaction_date="2026-05-05",
                interaction_time="10:00",
                attendees="N/A",
                notes=case["notes"],
                materials_shared=case["materials"],
                samples_distributed=case["samples"],
                sentiment=case["sentiment"],
                outcomes=case["outcomes"],
                action_items=case["actions"]
            )
            db.add(new_int)
            added_count += 1
        db.commit()
        print(f"Added {added_count} random interactions.")
    except Exception as e:
        print("Error adding:", e)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
