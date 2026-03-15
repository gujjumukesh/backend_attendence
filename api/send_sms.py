from flask import Flask, request, jsonify
from twilio.rest import Client
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Twilio credentials - securely loaded from environment variables
account_sid = os.environ.get('TWILIO_ACCOUNT_SID', '')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN', '')
twilio_number = os.environ.get('TWILIO_PHONE_NUMBER', '')

# Create a Twilio client
client = Client(account_sid, auth_token)

def format_phone_number(phone):
    """Format phone number to E.164 format"""
    # Remove any non-digit characters
    phone = ''.join(filter(str.isdigit, str(phone)))
    # Add country code if not present (assuming India +91)
    if len(phone) == 10:
        phone = '+91' + phone
    elif not phone.startswith('+'):
        phone = '+' + phone
    return phone

@app.route('/api/send-sms', methods=['POST'])
def send_sms():
    try:
        data = request.json
        phone_number = format_phone_number(data.get('mobile_no') or data.get('to'))
        message_text = data['message']
        roll_no = data.get('roll_no') or data.get('studentId')

        # Get verified numbers from Twilio
        verified_numbers = [number.phone_number 
                        for number in client.outgoing_caller_ids.list()]

        if phone_number not in verified_numbers:
            return jsonify({
                'success': False,
                'error': 'Phone number not verified. For Twilio trial accounts, please verify the recipient\'s number first at https://www.twilio.com/console/phone-numbers/verified'
            }), 400

        # Send SMS
        message = client.messages.create(
            body=message_text,
            from_=twilio_number,
            to=phone_number
        )

        # Log successful message
        current_date = datetime.now().strftime('%Y-%m-%d')
        print(f"SMS sent successfully to {phone_number} for roll_no {roll_no} on {current_date}")

        return jsonify({
            'success': True,
            'message_sid': message.sid,
            'status': 'sent',
            'sent_at': current_date
        })

    except Exception as e:
        error_message = str(e)
        print(f"Error sending SMS: {error_message}")
        return jsonify({
            'success': False,
            'error': error_message,
            'status': 'failed'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)