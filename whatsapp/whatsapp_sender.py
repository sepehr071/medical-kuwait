#!/usr/bin/env python3
"""
WhatsApp Message Sender using Twilio API
==========================================

A Python script to send WhatsApp messages using Twilio's WhatsApp Business API.
Designed to work with Twilio Sandbox for testing purposes.

Author: AI Assistant
Dependencies: twilio, python-dotenv
"""

import re
import logging
from typing import Optional, Dict, Any
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException


class WhatsAppSender:
    """
    A class to handle WhatsApp message sending via Twilio API.
    
    This class provides methods to send simple text messages through
    Twilio's WhatsApp Business API.
    It can be initialized with credentials passed directly, or it can attempt
    to load them from environment variables if running as a standalone script.
    """
    
    def __init__(self, account_sid: Optional[str] = None, auth_token: Optional[str] = None,
                 from_number: Optional[str] = None):
        """
        Initialize the WhatsApp sender with Twilio credentials.
        
        Args:
            account_sid (str, optional): Twilio Account SID. If None, tries to load from env.
            auth_token (str, optional): Twilio Auth Token. If None, tries to load from env.
            from_number (str, optional): Twilio WhatsApp sender number. If None, tries to load from env.
        
        Raises:
            ValueError: If required environment variables are not set or passed.
            TwilioRestException: If Twilio client initialization fails.
        """
        # If credentials are not passed, try to load from environment variables
        if not account_sid or not auth_token or not from_number:
            from dotenv import load_dotenv
            load_dotenv()
            account_sid = account_sid or os.getenv('TWILIO_ACCOUNT_SID')
            auth_token = auth_token or os.getenv('TWILIO_AUTH_TOKEN')
            from_number = from_number or os.getenv('TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')

        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        
        # Validate that required credentials are present
        if not self.account_sid:
            raise ValueError("TWILIO_ACCOUNT_SID environment variable (or passed argument) is required")
        if not self.auth_token:
            raise ValueError("TWILIO_AUTH_TOKEN environment variable (or passed argument) is required")
        if not self.from_number:
            raise ValueError("TWILIO_WHATSAPP_FROM environment variable (or passed argument) is required")
        
        # Initialize Twilio client
        try:
            self.client = Client(self.account_sid, self.auth_token)
            logging.info("Twilio client initialized successfully")
        except Exception as e:
            raise TwilioRestException(f"Failed to initialize Twilio client: {str(e)}")
    
    def validate_phone_number(self, phone_number: str) -> str:
        """
        Validate and format phone number for WhatsApp.
        
        Args:
            phone_number (str): Phone number to validate (with or without whatsapp: prefix)
            
        Returns:
            str: Formatted phone number with whatsapp: prefix
            
        Raises:
            ValueError: If phone number is invalid or not in E.164 format
        """
        if not phone_number:
            raise ValueError("Phone number cannot be empty")
        
        # Remove whatsapp: prefix if present for validation
        clean_number = phone_number.replace('whatsapp:', '').strip()
        
        # Validate E.164 format (+ followed by 1-15 digits)
        e164_pattern = r'^\+[1-9]\d{1,14}$'
        if not re.match(e164_pattern, clean_number):
            raise ValueError(
                f"Invalid phone number format: {clean_number}. "
                "Please use E.164 format (e.g., +1234567890)"
            )
        
        # Return with whatsapp: prefix
        return f"whatsapp:{clean_number}"
    
    def send_message(self, to_number: str, message: str) -> Dict[str, Any]:
        """
        Send a WhatsApp message to the specified number.
        
        Args:
            to_number (str): Recipient's phone number (E.164 format with or without whatsapp: prefix)
            message (str): Message content to send
            
        Returns:
            Dict[str, Any]: Dictionary containing message details and status
            
        Raises:
            ValueError: If input parameters are invalid
            TwilioRestException: If message sending fails
        """
        # Validate inputs
        if not message or not message.strip():
            raise ValueError("Message content cannot be empty")
        
        # Validate and format phone number
        formatted_to_number = self.validate_phone_number(to_number)
        
        try:
            # Send message via Twilio
            logging.info(f"Sending WhatsApp message to {formatted_to_number}")
            
            message_instance = self.client.messages.create(
                from_=self.from_number,
                to=formatted_to_number,
                body=message.strip()
            )
            
            # Log success
            logging.info(f"Message sent successfully. SID: {message_instance.sid}")
            
            # Return message details
            return {
                'success': True,
                'message_sid': message_instance.sid,
                'to': formatted_to_number,
                'from': self.from_number,
                'status': message_instance.status,
                'message': message.strip(),
                'date_created': message_instance.date_created,
                'error': None
            }
            
        except TwilioRestException as e:
            # Handle Twilio-specific errors
            error_msg = f"Twilio API error: {e.msg} (Code: {e.code})"
            logging.error(error_msg)
            
            return {
                'success': False,
                'message_sid': None,
                'to': formatted_to_number,
                'from': self.from_number,
                'status': 'failed',
                'message': message.strip(),
                'date_created': None,
                'error': error_msg
            }
            
        except Exception as e:
            # Handle unexpected errors
            error_msg = f"Unexpected error: {str(e)}"
            logging.error(error_msg)
            
            return {
                'success': False,
                'message_sid': None,
                'to': formatted_to_number,
                'from': self.from_number,
                'status': 'failed',
                'message': message.strip(),
                'date_created': None,
                'error': error_msg
            }


def setup_logging(level: str = 'INFO') -> None:
    """
    Setup logging configuration.
    
    Args:
        level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


if __name__ == "__main__":
    # Example usage when script is run directly
    setup_logging('INFO')
    
    try:
        # NOTE: For standalone usage, place your Twilio credentials directly here or in a local .env
        # This allows the example to run without relying on the main app's config
        TWILIO_ACCOUNT_SID_EXAMPLE = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        TWILIO_AUTH_TOKEN_EXAMPLE = "your_auth_token_here"
        TWILIO_WHATSAPP_FROM_EXAMPLE = "whatsapp:+14155238886"

        sender = WhatsAppSender(
            account_sid=TWILIO_ACCOUNT_SID_EXAMPLE,
            auth_token=TWILIO_AUTH_TOKEN_EXAMPLE,
            from_number=TWILIO_WHATSAPP_FROM_EXAMPLE
        )
        
        # Example message
        recipient = input("Enter recipient phone number (E.164 format, e.g., +1234567890): ")
        message_text = input("Enter your message: ")
        
        # Send message
        result = sender.send_message(recipient, message_text)
        
        # Display result
        if result['success']:
            print(f"✅ Message sent successfully!")
            print(f"Message SID: {result['message_sid']}")
            print(f"Status: {result['status']}")
        else:
            print(f"❌ Failed to send message: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")