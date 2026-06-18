 
import os
 
from pyairtable import Api
 
AIRTABLE_TOKEN = os.environ.get("AIRTABLE_TOKEN", "")
AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID", "")
AIRTABLE_TABLE = os.environ.get("AIRTABLE_TABLE", "Submissions")
 
 
def export_submission(number, profile_name, answers):
    """
    Create one Airtable record from a finished questionnaire.
    Returns the new record's id (so we can update its status later).
 
    `answers` is a dict like {"legal_name": "...", "title_deed": "uploads/..png"}.
    For file questions the value is the local file path. Airtable attachment
    fields need a *public URL*, so in this starter we just record the filename in
    a text column. In production you'd upload the file to S3 (or similar), then
    pass {"url": "..."} to an attachment field instead.
    """
    if not (AIRTABLE_TOKEN and AIRTABLE_BASE_ID):
        print("[airtable] No credentials set; skipping export.")
        return None
 
    api = Api(AIRTABLE_TOKEN)
    table = api.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE)
 
    # Map our answers onto Airtable fields. Field names here must match the
    # column names in your base exactly (case-sensitive).
    fields = {
        "WhatsApp Number": number.replace("whatsapp:", ""),
        "Profile Name": profile_name,
        "Legal Name": answers.get("legal_name", ""),
        "Date of Birth": answers.get("date_of_birth", ""),
        "ID Number": answers.get("id_number", ""),
        "Property Address": answers.get("property_address", ""),
        "Parcel Number": answers.get("parcel_number", ""),
        "Transaction Type": answers.get("transaction_type", ""),
        "Title Deed File": os.path.basename(answers.get("title_deed", "") or ""),
        "ID Document File": os.path.basename(answers.get("id_document", "") or ""),
        "Notes": answers.get("notes", ""),
        "Status": "Under review",
    }
 
    record = table.create(fields)
    print(f"[airtable] created record {record['id']}")
    return record["id"]
 
 
def mark_record_status(record_id, status):
    """Update the Status field of an existing record (e.g. to 'Approved')."""
    if not (AIRTABLE_TOKEN and AIRTABLE_BASE_ID and record_id):
        return
    api = Api(AIRTABLE_TOKEN)
    table = api.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE)
    table.update(record_id, {"Status": status})
    print(f"[airtable] record {record_id} -> {status}")
 