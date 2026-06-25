from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Keywords for classification
KEYWORDS = {
    "wrong_transfer": [
        "wrong number", "wrong account", "wrong person", "sent to wrong",
        "transferred to wrong", "mistaken transfer", "wrong recipient",
        "wrong bkash", "ভুল নম্বর", "ভুল একাউন্ট"
    ],
    "payment_failed": [
        "payment failed", "transaction failed", "failed but balance",
        "deducted but", "not received", "balance deducted", "money gone",
        "didn't go through", "পেমেন্ট ফেল", "ব্যালেন্স কাটা"
    ],
    "refund_request": [
        "refund", "money back", "get back", "return my money",
        "cancel transaction", "reverse", "revert", "রিফান্ড", "টাকা ফেরত"
    ],
    "phishing_or_social_engineering": [
        "otp", "pin", "password", "asking for", "someone called",
        "called me", "sms asking", "give otp", "share otp", "verify otp",
        "asked my pin", "asked for pin", "fraud call", "fake bkash",
        "পিন", "ওটিপি", "পাসওয়ার্ড"
    ],
}

def classify_message(message: str):
    msg = message.lower()

    # Detect case type
    case_type = "other"
    for ct, keywords in KEYWORDS.items():
        if any(kw in msg for kw in keywords):
            case_type = ct
            break

    # Determine severity
    if case_type == "phishing_or_social_engineering":
        severity = "critical"
    elif case_type in ("wrong_transfer", "payment_failed"):
        severity = "high"
    elif case_type == "refund_request":
        severity = "low"
    else:
        severity = "low"

    # Determine department
    department_map = {
        "wrong_transfer": "dispute_resolution",
        "payment_failed": "payments_ops",
        "refund_request": "customer_support",
        "phishing_or_social_engineering": "fraud_risk",
        "other": "customer_support",
    }
    department = department_map[case_type]

    # Human review required for critical or phishing
    human_review_required = severity == "critical" or case_type == "phishing_or_social_engineering"

    # Also flag high severity wrong_transfer for human review
    if case_type == "wrong_transfer":
        human_review_required = True

    # Generate agent summary (safe — never asks for PIN/OTP)
    summaries = {
        "wrong_transfer": "Customer reports sending money to an unintended recipient and is requesting a transfer reversal.",
        "payment_failed": "Customer reports a failed transaction where the balance may have been deducted without successful delivery.",
        "refund_request": "Customer is requesting a refund or reversal of a recent transaction.",
        "phishing_or_social_engineering": "Customer reports a suspicious contact attempting to obtain sensitive account information.",
        "other": "Customer has submitted a general inquiry or complaint that requires agent review.",
    }
    agent_summary = summaries[case_type]

    # Confidence: higher if strong keyword match
    strong_match = any(
        any(kw in msg for kw in kws)
        for ct, kws in KEYWORDS.items()
        if ct == case_type
    )
    confidence = 0.88 if strong_match and case_type != "other" else 0.55

    return {
        "case_type": case_type,
        "severity": severity,
        "department": department,
        "agent_summary": agent_summary,
        "human_review_required": human_review_required,
        "confidence": confidence,
    }


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "QueueStorm Ticket Sorter"}), 200


@app.route("/sort-ticket", methods=["POST"])
def sort_ticket():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    ticket_id = data.get("ticket_id")
    message = data.get("message")

    if not ticket_id:
        return jsonify({"error": "ticket_id is required"}), 400
    if not message:
        return jsonify({"error": "message is required"}), 400

    result = classify_message(message)

    return jsonify({
        "ticket_id": ticket_id,
        "case_type": result["case_type"],
        "severity": result["severity"],
        "department": result["department"],
        "agent_summary": result["agent_summary"],
        "human_review_required": result["human_review_required"],
        "confidence": result["confidence"],
    }), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
