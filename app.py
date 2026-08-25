
import os
 
from dotenv import load_dotenv
load_dotenv()
 
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
 
import database
import airtable_export
 
app = Flask(__name__)
 
ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
FROM_NUMBER = os.environ.get("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
FORM_URL = os.environ.get("FORM_URL", "")
 
client = Client(ACCOUNT_SID, AUTH_TOKEN)
 
POSITIVE = {"accepted", "approved"}
VIEW_PHRASES = {"view my result", "view result", "view update", "view"}
 
 
# --------------------------------------------------------------------------- #
# Messaging helpers
# --------------------------------------------------------------------------- #
def send_link_message(resp, name):
    resp.message(
        f"Welcome to FinAgra, {name}! 🌱\n\n"
        f"To apply, please fill out this short form:\n{FORM_URL}\n\n"
        "Once you submit, our team will review your application and message you "
        "here with your result."
    )
 
 
def send_result_message(number, decision):
    d = (decision or "").lower()
    if decision is None or d == "under review" or d == "":
        text = ("We don't have a result for you just yet — "
                "we'll message you as soon as your application is reviewed.")
    elif d in POSITIVE:
        text = ("Congratulations! 🎉 Your application has been *accepted*. "
                "A team member will reach out shortly with next steps.")
    else:
        text = ("Thank you for applying. Unfortunately your application was "
                "*not successful* this time. We'd be glad to help you reapply "
                "in the future.")
    client.messages.create(from_=FROM_NUMBER, to=number, body=text)
    print(f"[notify] sent result ({decision}) to {number}")
 
 
def send_nudge(number, name):
    """Developer-triggered: tell the person they have an update."""
    client.messages.create(
        from_=FROM_NUMBER, to=number,
        body=f"Hi {name}, there's an update on your FinAgra application. "
             "Reply *view my result* to see it.",
    )
    print(f"[notify] sent nudge to {number}")
 
 
def notify_status_update(number):
    """Called after you change Status in Airtable. Sends the nudge."""
    convo = database.get_conversation(number)
    name = convo["profile_name"] if convo else "there"
    if not convo:
        database.start_conversation(number, name)
    send_nudge(number, name)
    database.set_state(number, "awaiting_view")
    return {"status": "nudge_sent", "number": number}
 
 
# --------------------------------------------------------------------------- #
# Webhook — every inbound message
# --------------------------------------------------------------------------- #
@app.route("/webhook", methods=["POST"])
def webhook():
    number = request.form.get("From")
    profile_name = request.form.get("ProfileName", "there")
    body = request.form.get("Body", "").strip()
 
    resp = MessagingResponse()
    convo = database.get_conversation(number)
 
    # "view my result" — read their decision from Airtable and send it.
    if body.lower() in VIEW_PHRASES:
        decision = airtable_export.get_status_by_number(number)
        send_result_message(number, decision)
        database.set_state(number, "decided")
        return ("", 204)  # we already sent via API; no TwiML reply needed
 
    # Brand new person, or any greeting -> send the form link.
    if convo is None:
        database.start_conversation(number, profile_name)
        send_link_message(resp, profile_name)
        return str(resp)
 
    state = convo["state"]
 
    if state == "awaiting_view":
        resp.message("You have an update! Reply *view my result* to see it.")
        return str(resp)
 
    if state == "decided":
        resp.message("You've already received your result. "
                     "A team member will follow up if there are next steps.")
        return str(resp)
 
    # Default: (re)send the form link.
    send_link_message(resp, profile_name)
    return str(resp)
 
 
# --------------------------------------------------------------------------- #
# Developer trigger: call after changing Status in Airtable
# --------------------------------------------------------------------------- #
@app.route("/notify", methods=["POST"])
def notify_route():
    """Body: {"number": "whatsapp:+254..."}"""
    data = request.get_json(force=True)
    return jsonify(notify_status_update(data["number"]))
 
 
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})
 
 
if __name__ == "__main__":
    database.init_db()
    app.run(port=5001, debug=True)
 
