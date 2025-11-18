from flask import Flask, render_template, request, jsonify
import json
import os
import requests

app = Flask(__name__)

CONFIG_FILE = 'config.json'

def load_config():
    """Load configuration from config file or create with defaults if it doesn't exist"""
    default_config = {
        "openrouter_api_key": "",  
        "ai_enabled": True  
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return default_config
    else:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=4)
        return default_config

config = load_config()

def load_faqs():
    try:
        with open('data/faqs.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "whatsapp": {
                "What is WhatsApp?": "WhatsApp is a free messaging app owned by Meta that allows you to send messages, make voice and video calls, and share media with other users worldwide.",
                "How do I send a photo on WhatsApp?": "To send a photo on WhatsApp: 1) Open a chat, 2) Tap the attachment icon (paperclip or +), 3) Select 'Gallery' or 'Camera', 4) Choose or take a photo, 5) Add a caption if desired, 6) Tap send.",
                "How do I make a video call on WhatsApp?": "To make a video call: 1) Open the chat with the person you want to call, 2) Tap the video call icon in the top right corner, 3) Wait for them to answer."
            },
            "paytm": {
                "What is Paytm?": "Paytm is an Indian digital payment and financial services company that allows you to make payments, transfer money, pay bills, and shop online.",
                "How do I add money to Paytm wallet?": "To add money to Paytm wallet: 1) Open Paytm app, 2) Tap on your profile or 'Balance', 3) Select 'Add Money', 4) Enter amount, 5) Choose payment method, 6) Complete the transaction.",
                "How do I pay using Paytm QR code?": "To pay using Paytm QR code: 1) Open Paytm app, 2) Tap 'Scan' at the bottom, 3) Point your camera at the merchant's QR code, 4) Enter amount, 5) Tap 'Pay'."
            },
            "googlemaps": {
                "How do I find directions on Google Maps?": "To find directions on Google Maps: 1) Open Google Maps app, 2) Tap on the 'Directions' icon, 3) Enter your destination and starting point, 4) Choose your mode of transportation (car, public transit, walking), 5) Tap 'Start' to begin navigation.",
                "How do I save a location on Google Maps?": "To save a location on Google Maps: 1) Search for the location, 2) Tap on the location name at the bottom, 3) Tap 'Save', 4) Choose a list to save it to (Favorites, Want to go, etc.).",
                "How do I share my location on Google Maps?": "To share your location: 1) Tap on your profile icon, 2) Select 'Location sharing', 3) Tap 'Share location', 4) Choose how long to share and with whom, 5) Tap 'Share'."
            },
            "googlepay": {
                "What is Google Pay?": "Google Pay is a digital wallet and online payment system developed by Google that allows you to make payments, send money to friends, and store payment information securely.",
                "How do I set up Google Pay?": "To set up Google Pay: 1) Download the Google Pay app, 2) Sign in with your Google account, 3) Add a payment method (credit/debit card or bank account), 4) Set up a PIN or biometric authentication.",
                "How do I send money using Google Pay?": "To send money: 1) Open Google Pay app, 2) Tap 'Pay' or 'New payment', 3) Enter recipient's phone number or select from contacts, 4) Enter amount, 5) Add a note (optional), 6) Tap 'Pay'."
            }
        }

os.makedirs('data', exist_ok=True)
if not os.path.exists('data/faqs.json'):
    with open('data/faqs.json', 'w') as f:
        json.dump(load_faqs(), f, indent=4)

@app.route('/')
def index():
    return render_template('index.html', ai_enabled=config['ai_enabled'])

@app.route('/api/query', methods=['POST'])
def query():
    data = request.json
    user_query = data.get('query', '').lower()
    use_ai = data.get('use_ai', False)
    
    print(f"Query received: '{user_query}', AI enabled: {use_ai}")
    
    # Load FAQs
    faqs = load_faqs()
    
    # Search for matching FAQs
    response = search_faqs(user_query, faqs)
    
    if not response:
        # If no FAQ match, try AI response (if enabled)
        if use_ai and config['ai_enabled']:
            try:
                print(f"Using AI for response. API key present: {bool(config['openrouter_api_key'])}")
                # Use admin's API key from config
                response = get_ai_response(user_query, config['openrouter_api_key'])
                print(f"AI response received: {response[:50]}...")
            except Exception as e:
                print(f"Error getting AI response: {str(e)}")
                response = f"I'm having trouble connecting to my AI brain. Let's stick with what I know for now."
        else:
            response = "I'm not sure about that. Try asking about WhatsApp, Paytm, Google Maps, or Google Pay!"
    
    return jsonify({"response": response})

@app.route('/api/admin/config', methods=['POST'])
def update_config():
    """Admin endpoint to update configuration"""
    # In a real application, you would add authentication here
    data = request.json
    
    if 'api_key' in data:
        config['openrouter_api_key'] = data['api_key']
    
    if 'ai_enabled' in data:
        config['ai_enabled'] = data['ai_enabled']
    
    # Save updated config
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)
    
    return jsonify({"status": "success"})

@app.route('/admin')
def admin_panel():
    """Admin panel to configure the chatbot"""
    return render_template('admin.html', config=config)

def search_faqs(query, faqs):
    # Convert query to lowercase for case-insensitive matching
    query = query.lower()
    
    # Check for exact matches in FAQs
    for app, app_faqs in faqs.items():
        for question, answer in app_faqs.items():
            if query in question.lower():
                return answer
    
    # Check for keyword matches
    keywords = {
        "whatsapp": ["whatsapp", "message", "chat", "call", "video call", "voice call", "status", "photo", "image"],
        "paytm": ["paytm", "payment", "wallet", "money", "transfer", "bill", "recharge", "qr", "scan"],
        "googlemaps": ["google maps", "maps", "direction", "location", "navigation", "place", "route"],
        "googlepay": ["google pay", "gpay", "pay", "upi", "payment", "money", "transfer"]
    }
    
    for app, app_keywords in keywords.items():
        if any(keyword in query for keyword in app_keywords):
            for question, answer in faqs[app].items():
                for keyword in query.split():
                    if keyword in question.lower() and len(keyword) > 3:  # Only match on meaningful keywords
                        return answer
    
    return None

def get_ai_response(query, api_key):
    """Get response from DeepSeek API via OpenRouter"""
    if not api_key:
        print("No API key provided for AI response")
        return "AI responses are not available at the moment. Please try asking about our FAQs instead."
        
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000"  # Required by OpenRouter
    }
    
    data = {
        "model": "deepseek/deepseek-chat",  # Using DeepSeek model
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that provides clear, step-by-step guidance on how to use digital tools like WhatsApp, Paytm, Google Maps, and Google Pay. Keep responses concise and easy to understand."},
            {"role": "user", "content": query}
        ]
    }
    
    print(f"Sending request to OpenRouter API")
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code != 200:
        print(f"OpenRouter API error: {response.status_code} - {response.text}")
        return f"Sorry, I couldn't get a response from the AI service (Error {response.status_code})."
    
    response_data = response.json()
    print(f"OpenRouter API response received")
    
    try:
        return response_data['choices'][0]['message']['content']
    except (KeyError, IndexError) as e:
        print(f"Error parsing OpenRouter response: {str(e)}")
        print(f"Response data: {response_data}")
        return "I couldn't get a response from my AI brain right now. Please try asking about WhatsApp, Paytm, Google Maps, or Google Pay directly!"

if __name__ == '__main__':
    app.run(debug=True)

