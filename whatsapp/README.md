# WhatsApp Message Sender with Twilio

A Python script to send WhatsApp messages using Twilio's WhatsApp Business API. This implementation is designed to work with the Twilio Sandbox for easy testing and development.

## Features

- ✅ Send simple text WhatsApp messages
- ✅ Phone number validation (E.164 format)
- ✅ Comprehensive error handling
- ✅ Environment variable configuration
- ✅ Detailed logging
- ✅ Easy-to-use Python class
- ✅ Multiple usage examples

## Prerequisites

1. **Python 3.7+** installed on your system
2. **Twilio Account** - [Sign up for free](https://www.twilio.com/try-twilio)
3. **WhatsApp account** on your mobile device
4. **Twilio Sandbox for WhatsApp** activated (explained below)

## Installation

1. **Clone or download** this project to your local machine

2. **Install required Python packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env with your actual Twilio credentials
   ```

## Configuration

### Step 1: Get Twilio Credentials

1. Go to the [Twilio Console](https://console.twilio.com/)
2. Copy your **Account SID** and **Auth Token**
3. Note these down for the next step

### Step 2: Activate Twilio Sandbox for WhatsApp

1. Go to the [Try WhatsApp page](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn)
2. Click **Confirm** to acknowledge the terms
3. You'll see a QR code and a sandbox number (usually `+1 415 523 8886`)
4. **Join the sandbox** by either:
   - Scanning the QR code with WhatsApp, OR
   - Sending `join <your-sandbox-code>` to `+1 415 523 8886`
5. You should receive a confirmation message

### Step 3: Configure Environment Variables

Edit your `.env` file with your actual credentials:

```env
# Your Twilio credentials from the Console
TWILIO_ACCOUNT_SID=your_actual_account_sid_here
TWILIO_AUTH_TOKEN=your_actual_auth_token_here

# Twilio Sandbox WhatsApp number (default)
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# Optional: Set logging level
LOG_LEVEL=INFO
```

## Usage

### Basic Usage

```python
from whatsapp_sender import WhatsAppSender

# Initialize the sender
sender = WhatsAppSender()

# Send a message
result = sender.send_message(
    to_number="+1234567890",  # Replace with recipient's number
    message="Hello from Python!"
)

# Check if message was sent successfully
if result['success']:
    print(f"Message sent! SID: {result['message_sid']}")
else:
    print(f"Failed to send: {result['error']}")
```

### Command Line Usage

You can run the script directly for interactive messaging:

```bash
python whatsapp_sender.py
```

### Run Examples

Explore various usage patterns:

```bash
python example_usage.py
```

This will show examples of:
- Simple text messages
- Multiple recipients
- Error handling
- Interactive mode
- Phone number validation

## Phone Number Format

All phone numbers must be in **E.164 format**:

- ✅ `+1234567890` (correct)
- ✅ `+919876543210` (correct)
- ❌ `1234567890` (missing +)
- ❌ `(123) 456-7890` (wrong format)

The script automatically adds the `whatsapp:` prefix required by Twilio.

## API Reference

### WhatsAppSender Class

#### `__init__()`
Initializes the WhatsApp sender with credentials from environment variables.

**Raises:**
- `ValueError`: If required environment variables are missing
- `TwilioRestException`: If Twilio client initialization fails

#### `send_message(to_number: str, message: str) -> Dict[str, Any]`
Sends a WhatsApp message to the specified number.

**Parameters:**
- `to_number` (str): Recipient's phone number in E.164 format
- `message` (str): Message content to send

**Returns:**
Dictionary with the following keys:
- `success` (bool): Whether the message was sent successfully
- `message_sid` (str): Twilio message SID (if successful)
- `to` (str): Formatted recipient number
- `from` (str): Sender number
- `status` (str): Message status
- `message` (str): Message content
- `date_created` (datetime): When message was created
- `error` (str): Error message (if failed)

#### `validate_phone_number(phone_number: str) -> str`
Validates and formats a phone number for WhatsApp.

**Parameters:**
- `phone_number` (str): Phone number to validate

**Returns:**
- Formatted phone number with `whatsapp:` prefix

**Raises:**
- `ValueError`: If phone number is invalid

## Troubleshooting

### Common Issues

#### 1. "TWILIO_ACCOUNT_SID environment variable is required"
**Solution:** Make sure your `.env` file exists and contains valid credentials.

#### 2. "Invalid phone number format"
**Solution:** Use E.164 format (e.g., `+1234567890`) for all phone numbers.

#### 3. "Twilio API error: Permission denied"
**Solution:** 
- Verify your Account SID and Auth Token are correct
- Ensure the recipient has joined your Twilio Sandbox

#### 4. "The message From/To pair violates a blacklist rule"
**Solution:** Make sure the recipient number has joined your Twilio Sandbox by sending the join code.

#### 5. "Message body is required"
**Solution:** Ensure your message content is not empty.

### Testing Your Setup

1. **Verify credentials:** Check that your `.env` file has the correct Twilio credentials
2. **Test phone validation:** Run the validation examples in `example_usage.py`
3. **Send test message:** Try sending a message to your own WhatsApp number
4. **Check Twilio logs:** Visit the [Twilio Console](https://console.twilio.com/) to see message logs

### Getting Help

If you're still having issues:

1. Check the [Twilio WhatsApp documentation](https://www.twilio.com/docs/whatsapp)
2. Verify your Twilio account status and balance
3. Make sure you've joined the Twilio Sandbox
4. Check the Twilio Console for detailed error messages

## Twilio Sandbox Limitations

The Twilio Sandbox has some limitations:

- ⚠️ **24-hour session:** Recipients must message your sandbox number first, or messages will be limited
- ⚠️ **Pre-approved contacts:** Only joined contacts can receive messages
- ⚠️ **Testing only:** Not suitable for production use
- ⚠️ **Template restrictions:** Limited message templates available

For production use, you'll need to register for WhatsApp Business API.

## Security Best Practices

- ✅ Keep your `.env` file secure and never commit it to version control
- ✅ Use environment variables for all sensitive data
- ✅ Validate all user inputs
- ✅ Monitor your Twilio usage and costs
- ✅ Use proper error handling

## File Structure

```
whatsapp-sender/
├── whatsapp_sender.py    # Main WhatsApp sender class
├── example_usage.py      # Usage examples and demos
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── .env                 # Your actual credentials (create this)
└── README.md           # This documentation
```

## Dependencies

- [`twilio`](https://pypi.org/project/twilio/) - Official Twilio Python library
- [`python-dotenv`](https://pypi.org/project/python-dotenv/) - Environment variable loading

## License

This project is provided as-is for educational and development purposes. Please review Twilio's terms of service and WhatsApp's business policies before using in production.

---

**Happy messaging! 🚀📱**