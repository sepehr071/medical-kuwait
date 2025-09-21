import logging
import re
from typing import Dict, Any
from flask import current_app
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

class SMSService:
    """SMS service using Twilio API for sending OTP messages"""

    def __init__(self):
        """Initialize Twilio SMS service"""
        self.account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
        self.auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')
        self.from_number = current_app.config.get('TWILIO_SMS_FROM')

        # Log configuration for debugging
        current_app.logger.info(f"SMS Service Init - SID: {self.account_sid[:10] if self.account_sid else 'None'}...")
        current_app.logger.info(f"SMS Service Init - From: {self.from_number}")
        current_app.logger.info(f"SMS Service Init - Token: {'Present' if self.auth_token else 'None'}")

        if not all([self.account_sid, self.auth_token, self.from_number]):
            missing = []
            if not self.account_sid:
                missing.append('TWILIO_ACCOUNT_SID')
            if not self.auth_token:
                missing.append('TWILIO_AUTH_TOKEN')
            if not self.from_number:
                missing.append('TWILIO_SMS_FROM')
            
            error_msg = f"Missing required Twilio configuration: {', '.join(missing)}"
            current_app.logger.error(error_msg)
            raise ValueError(error_msg)

        try:
            self.client = Client(self.account_sid, self.auth_token)
            current_app.logger.info("Twilio SMS client initialized successfully.")
        except Exception as e:
            current_app.logger.error(f"Failed to initialize Twilio client: {str(e)}")
            raise

    def validate_phone_number(self, phone_number: str) -> str:
        """
        Validate and format phone number for SMS.

        Args:
            phone_number (str): Phone number to validate

        Returns:
            str: Formatted phone number in E.164 format

        Raises:
            ValueError: If phone number is invalid or not in E.164 format
        """
        if not phone_number:
            raise ValueError("Phone number cannot be empty")

        # Remove any spaces, dashes, or parentheses
        clean_number = re.sub(r'[\s\-\(\)]', '', phone_number)

        # Add + prefix if missing
        if not clean_number.startswith('+'):
            # If it starts with 1 and has 11 digits, assume US number
            if len(clean_number) == 11 and clean_number.startswith('1'):
                clean_number = '+' + clean_number
            elif len(clean_number) == 10:
                clean_number = '+1' + clean_number
            else:
                clean_number = '+' + clean_number

        # Validate E.164 format (+ followed by 1-15 digits)
        e164_pattern = r'^\+[1-9]\d{1,14}$'
        if not re.match(e164_pattern, clean_number):
            raise ValueError(
                f"Invalid phone number format: {clean_number}. "
                "Please use E.164 format (e.g., +1234567890)"
            )

        return clean_number

    def send_sms_message(self, to_number: str, message: str) -> Dict[str, Any]:
        """
        Send an SMS message to the specified number.

        Args:
            to_number (str): Recipient's phone number
            message (str): Message content to send

        Returns:
            Dict[str, Any]: Dictionary containing message details and status
        """
        # Validate inputs
        if not message or not message.strip():
            raise ValueError("Message content cannot be empty")

        # Validate and format phone number
        formatted_to_number = self.validate_phone_number(to_number)

        try:
            # Send message via Twilio
            current_app.logger.info(f"Sending SMS to {formatted_to_number}")

            message_instance = self.client.messages.create(
                from_=self.from_number,
                to=formatted_to_number,
                body=message.strip()
            )

            # Log success
            current_app.logger.info(f"SMS sent successfully. SID: {message_instance.sid}")

            # Return message details
            return {
                'success': True,
                'message_sid': message_instance.sid,
                'to': formatted_to_number,
                'from': self.from_number,
                'status': message_instance.status,
                'message': message.strip(),
                'date_created': str(message_instance.date_created),
                'error': None
            }

        except TwilioRestException as e:
            # Handle Twilio-specific errors
            error_msg = f"Twilio API error: {e.msg} (Code: {e.code})"
            current_app.logger.error(error_msg)

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
            current_app.logger.error(error_msg)

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

    def send_otp(self, phone_number: str, otp_code: str, purpose: str = 'login') -> bool:
        """
        Send OTP via SMS

        Args:
            phone_number (str): Phone number to send OTP to
            otp_code (str): OTP code to send
            purpose (str): Purpose of OTP ('login' or 'phone_change')

        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            message_body = self._create_message(otp_code, purpose)

            # Send SMS directly using Twilio
            send_result = self.send_sms_message(phone_number, message_body)

            if send_result['success']:
                current_app.logger.info(f"[SMS] OTP sent successfully to {phone_number}. SID: {send_result['message_sid']}")
                return True
            else:
                current_app.logger.error(f"[SMS] Failed to send OTP to {phone_number}: {send_result['error']}")
                return False

        except Exception as e:
            current_app.logger.error(f"Failed to send OTP to {phone_number}: {str(e)}")
            return False

    def _create_message(self, otp_code: str, purpose: str) -> str:
        """Create SMS message based on purpose"""
        if purpose == 'login':
            return f"Your Kuwait Medical Clinic login code is: {otp_code}. This code expires in 5 minutes."
        elif purpose == 'phone_change':
            return f"Your Kuwait Medical Clinic phone verification code is: {otp_code}. This code expires in 5 minutes."
        else:
            return f"Your Kuwait Medical Clinic verification code is: {otp_code}. This code expires in 5 minutes."