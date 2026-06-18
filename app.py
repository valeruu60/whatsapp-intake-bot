 
import os
 
from dotenv import load_dotenv
load_dotenv()  # reads .env so you don't have to export vars manually
 
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
 
import database
import airtable_export
from questions import QUESTIONS
 
app = Flask(__name__)
 
ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
FROM_NUMBER = os.environ.get("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
APPROVED_TEMPLATE_SID = os.environ.get("TWILIO_APPROVED_TEMPLATE_SID", "")
 
client = Client(ACCOUNT_SID, AUTH_TOKEN)
 
 
# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def download_media(media_url, number, key):
    """Download an attachment the user sent. Twilio media URLs require auth."""
    import requests
 
    resp = requests.get(media_url, auth=(ACCOUNT_SID, AUTH_TOKEN))
    resp.raise_for_status()
    ext = {
        "application/pdf": ".pdf",
        "image/jpeg": ".jpg",
        "image/png": ".png",
    }.get(resp.headers.get("Content-Type", ""), ".bin")
 
    os.makedirs("uploads", exist_ok=True)
    safe = number.replace("whatsapp:", "").replace("+", "")
    path = os.path.join("uploads", f"{safe}_{key}{ext}")
    with open(path, "wb") as f:
        f.write(resp.content)
    return path
 
 
def build_summary(answers):
    """Human-readable recap shown before final confirmation."""
    lines = ["Here's what I've got — please check it:\n"]
    for q in QUESTIONS:
        val = answers.get(q["key"], "")
        if q["type"] == "file":
            val = "✅ file received" if val else "❌ missing"
        lines.append(f"• *{q['key'].replace('_', ' ').title()}*: {val}")
    lines.append("\nReply *YES* to submit, or *RESTART* to start over.")
    return "\n".join(lines)
 
 
def interpret_choice(text, options):
    """Accept either '2' or 'Sale' for a choice question. Returns option or None."""
    text = text.strip()
    if text.isdigit():
        i = int(text) - 1
        if 0 <= i < len(options):
            return options[i]
    for opt in options:
        if text.lower() == opt.lower():
            return opt
    return None
 
 
# --------------------------------------------------------------------------- #
# The webhook — every message lands here
# --------------------------------------------------------------------------- #
@app.route("/webhook", methods=["POST"])
def webhook():
    number = request.form.get("From")
    profile_name = request.form.get("ProfileName", "there")
    body = request.form.get("Body", "").strip()
    num_media = int(request.form.get("NumMedia", "0"))
 
    resp = MessagingResponse()
    convo = database.get_conversation(number)
 
    # ----- Global commands ------------------------------------------------- #
    if body.lower() == "restart":
        database.start_conversation(number, profile_name)
        resp.message(QUESTIONS[0]["prompt"])
        return str(resp)
 
    # ----- No conversation yet, or a fresh greeting ------------------------ #
    if convo is None:
        database.start_conversation(number, profile_name)
        resp.message(QUESTIONS[0]["prompt"])
        return str(resp)
 
    state = convo["state"]
 
    # ----- They already submitted and we're reviewing --------------------- #
    if state == "under_review":
        resp.message(
            "Thanks — your submission is still being reviewed by our team. "
            "We'll message you here as soon as it's confirmed. 🙏"
        )
        return str(resp)
 
    # ----- They were approved; this new message continues the journey ------ #
    if state == "approved":
        # A fresh 24h window is open now because they messaged us. Continue here.
        resp.message(
            f"Welcome back, {convo['profile_name']}! ✅ Your documents were "
            "confirmed. The next stage of your application can now begin — "
            "a team member will follow up shortly."
        )
        # (Here you'd kick off whatever "stage 2" is for your process.)
        return str(resp)
 
    # ----- Final confirmation step ---------------------------------------- #
    if state == "confirming":
        if body.lower() in ("yes", "y", "confirm"):
            record_id = airtable_export.export_submission(
                number, convo["profile_name"], convo["answers"]
            )
            database.set_state(number, "under_review", airtable_id=record_id or "")
            resp.message(
                "Perfect — your application has been submitted! 🎉\n\n"
                "Our team will review your documents (this usually takes a couple "
                "of days). We'll message you here once everything is confirmed."
            )
        else:
            resp.message("Reply *YES* to submit, or *RESTART* to start over.")
        return str(resp)
 
    # ----- We're still collecting answers --------------------------------- #
    q_index = convo["q_index"]
 
    # Safety: if index is past the end, move to confirming.
    if q_index >= len(QUESTIONS):
        database.set_state(number, "confirming")
        resp.message(build_summary(convo["answers"]))
        return str(resp)
 
    current = QUESTIONS[q_index]
 
    # Validate + store the answer based on question type.
    if current["type"] == "file":
        if num_media > 0:
            media_url = request.form.get("MediaUrl0")
            path = download_media(media_url, number, current["key"])
            database.save_answer(number, current["key"], path)
        else:
            resp.message("Please send an *attachment* (photo or PDF) for this step.")
            return str(resp)
 
    elif current["type"] == "choice":
        choice = interpret_choice(body, current["options"])
        if choice is None:
            resp.message("Please reply with one of the numbers or options listed above.")
            return str(resp)
        database.save_answer(number, current["key"], choice)
 
    else:  # text
        if not body:
            resp.message("Please type your answer for this step.")
            return str(resp)
        database.save_answer(number, current["key"], body)
 
    # Move on: either ask the next question or go to confirmation.
    convo = database.get_conversation(number) 
    if convo is None:
        return str(resp) 
    next_index = convo["q_index"]
    if next_index < len(QUESTIONS):
        resp.message(QUESTIONS[next_index]["prompt"])
    else:
        database.set_state(number, "confirming")
        resp.message(build_summary(convo["answers"]))
 
    return str(resp)
 
 
# --------------------------------------------------------------------------- #
# Developer-side approval — call this when YOU finish reviewing
# --------------------------------------------------------------------------- #
def approve_and_notify(number):
    """
    Mark a submission approved and proactively notify the person.
    Because days have passed, this MUST be an approved template (outside the
    24h window). Set TWILIO_APPROVED_TEMPLATE_SID in .env.
    """
    convo = database.get_conversation(number)
    if not convo:
        return {"error": "no conversation for that number"}
 
    airtable_export.mark_record_status(convo.get("airtable_id"), "Approved")
    database.set_state(number, "approved")
 
    name = convo["profile_name"]
    if APPROVED_TEMPLATE_SID:
        msg = client.messages.create(
            from_=FROM_NUMBER,
            to=number,
            content_sid=APPROVED_TEMPLATE_SID,
            content_variables=f'{{"1": "{name}"}}',
        )
    else:
        # Sandbox/testing fallback (only works if still inside 24h window).
        msg = client.messages.create(
            from_=FROM_NUMBER,
            to=number,
            body=f"Hi {name}, your documents have been confirmed. ✅ Please reply "
                 "to this message to continue your application.",
        )
    return {"status": "approved", "sid": msg.sid}
 
 
@app.route("/approve", methods=["POST"])
def approve_route():
    """
    Trigger approval from outside the code (a button, a script, a cron job).
    Body: {"number": "whatsapp:+1555..."}
    """
    data = request.get_json(force=True)
    return jsonify(approve_and_notify(data["number"]))
 
 
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})
 
 
if __name__ == "__main__":
    database.init_db()
    app.run(port=5001, debug=True)