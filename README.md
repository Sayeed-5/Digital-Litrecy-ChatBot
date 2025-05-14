# Digital Tools Assistant Chatbot

A responsive, user-friendly chatbot widget designed to help users learn how to use popular digital tools like WhatsApp, Paytm, Google Maps, and Google Pay.

## Features

- Interactive floating chat widget
- Pre-loaded FAQs about common digital tools
- Step-by-step guidance for common tasks
- Optional AI integration with DeepSeek via OpenRouter
- Mobile-responsive design
- Suggestion chips for common questions

## Project Structure

```
ChatBot/
├── app.py                 # Flask application
├── data/                  # Data directory
│   └── faqs.json          # FAQ database
├── static/                # Static files
│   ├── css/
│   │   └── style.css      # Chatbot styling
│   ├── js/
│   │   └── chatbot.js     # Chatbot functionality
│   └── images/            # Image assets
├── templates/
│   └── index.html         # Main HTML template
└── requirements.txt       # Python dependencies
```

## Setup Instructions

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the Flask application:
   ```
   python app.py
   ```

3. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## AI Integration (Optional)

The chatbot includes an option to use AI for more dynamic responses:

1. Create an account at [OpenRouter](https://openrouter.ai/)
2. Get your API key
3. Toggle "Use AI for responses" in the chatbot interface
4. Enter your API key and save

## Customization

You can customize the FAQ database by editing the `data/faqs.json` file. The file will be created automatically on first run with default FAQs.

## Embedding on Your Website

To embed this chatbot on your website, include the following code:

```html
<script src="path/to/chatbot.js"></script>
<link rel="stylesheet" href="path/to/style.css">
<div id="digital-tools-chatbot"></div>
```

## License

MIT
