 
import os
from pyairtable import Api
 
AIRTABLE_TOKEN = os.environ.get("AIRTABLE_TOKEN", "")
AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID", "")
AIRTABLE_TABLE = os.environ.get("AIRTABLE_TABLE", "Applications")
 
# The Airtable column that holds the applicant's WhatsApp number.
PHONE_COLUMN = os.environ.get("AIRTABLE_PHONE_COLUMN", "WhatsApp Number")
 
 
def _table():
    api = Api(AIRTABLE_TOKEN)
    return api.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE)
 
 
def _digits(s):
    """Keep only digits, so '+254 712...' and 'whatsapp:+254712...' compare equal."""
    return "".join(ch for ch in str(s) if ch.isdigit())
 
 
def get_status_by_number(number):
    """
    Find the applicant's record by phone number and return their Status
    (e.g. 'Accepted', 'Not accepted', 'Under review'). None if not found.
    Matches on digits so formatting differences don't matter.
    """
    if not (AIRTABLE_TOKEN and AIRTABLE_BASE_ID):
        print("[airtable] No credentials set.")
        return None
    target = _digits(number)
    try:
        for rec in _table().all():
            wa = _digits(rec.get("fields", {}).get(PHONE_COLUMN, ""))
            if wa and (wa == target or target.endswith(wa) or wa.endswith(target)):
                return rec["fields"].get("Status")
        print(f"[airtable] no record found for {number}")
        return None
    except Exception as e:
        print(f"[airtable] get_status_by_number failed: {e}")
        return None