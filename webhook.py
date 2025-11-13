from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# ----------------------------
# 🔹 Your Zendesk credentials
ZENDESK_DOMAIN = "https://retouchingacademy.zendesk.com"
ZENDESK_EMAIL = "syedamjadali415@gmail.com"  # your Zendesk login email
ZENDESK_TOKEN = "7V34wUewtCNvViQ9vZZMooof77xaleZYgmZHvn0U"
# ----------------------------


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # ✅ Check if the webhook is live
    if request.method == 'GET':
        return "Webhook is live and connected!"

    # ✅ Handle POST request from Dialogflow
    req = request.get_json(force=True)
    print("🔹 Received request:", req)

    intent = req.get('queryResult', {}).get('intent', {}).get('displayName')

    if intent == "Create_Ticket_Start":
        parameters = req.get('queryResult', {}).get('parameters', {})
        name = parameters.get('name')
        email = parameters.get('email')
        issue = parameters.get('issue')

        # ✅ If any field missing, ask again
        if not name:
            return jsonify({"fulfillmentText": "Please tell me your name."})
        if not email:
            return jsonify({"fulfillmentText": "Please provide your email address."})
        if not issue:
            return jsonify({"fulfillmentText": "Please describe your issue."})

        # ✅ Prepare Zendesk ticket data
        data = {
            "ticket": {
                "subject": f"Issue from {name}",
                "comment": {"body": f"Issue: {issue}\nUser email: {email}"},
                "priority": "normal"
            }
        }

        # ✅ Send data to Zendesk API
        response = requests.post(
            f"{ZENDESK_DOMAIN}/api/v2/tickets.json",
            json=data,
            auth=(f"{ZENDESK_EMAIL}/token", ZENDESK_TOKEN)
        )

        # ✅ Prepare response for Dialogflow
        if response.status_code == 201:
            reply = f"Thank you, {name}! Your ticket has been created. Our support team will contact you at {email}."
        else:
            reply = "Sorry, there was an error while creating your ticket. Please try again later."

        return jsonify({"fulfillmentText": reply})

    # ✅ Default fallback reply
    return jsonify({"fulfillmentText": "Okay, I noted that!"})


if __name__ == '__main__':
    app.run()
