import logging
from flask import current_app
from whatsapp.whatsapp_sender import WhatsAppSender

class SMSService:
    """SMS service can be replaced with actual SMS provider, with Twilio WhatsApp now integrated"""
    
    def __init__(self):
        self.provider = current_app.config.get('SMS_PROVIDER', 'placeholder')
        
        self.whatsapp_sender = None
        if self.provider == 'twilio_whatsapp':
            try:
                # WhatsAppSender loads its own env vars but we can ensure they are set in main app config too
                # Alternatively, pass them explicitly if WhatsAppSender constructor accepts them
                self.whatsapp_sender = WhatsAppSender(
                    account_sid=current_app.config.get('TWILIO_ACCOUNT_SID'),
                    auth_token=current_app.config.get('TWILIO_AUTH_TOKEN'),
                    from_number=current_app.config.get('TWILIO_WHATSAPP_FROM')
                )
                current_app.logger.info("WhatsAppSender initialized for Twilio WhatsApp.")
            except Exception as e:
                current_app.logger.error(f"Failed to initialize WhatsAppSender: {str(e)}")
                self.provider = 'placeholder' # Fallback to placeholder if WhatsAppSender fails
                self.whatsapp_sender = None
            
    def send_otp(self, phone_number, otp_code, purpose='login'):
        """
        Send OTP via SMS or WhatsApp
        
        Args:
            phone_number (str): Phone number to send OTP to
            otp_code (str): OTP code to send
            purpose (str): Purpose of OTP ('login' or 'phone_change')
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            message_body = self._create_message(otp_code, purpose)
            
            if self.provider == 'twilio_whatsapp' and self.whatsapp_sender:
                # The WhatsAppSender module handles E.164 formatting and whatsapp: prefix
                send_result = self.whatsapp_sender.send_message(
                    to_number=phone_number,
                    message=message_body
                )
                if send_result['success']:
                    current_app.logger.info(f"[WhatsApp] OTP sent successfully to {phone_number}. SID: {send_result['message_sid']}")
                    return True
                else:
                    current_app.logger.error(f"[WhatsApp] Failed to send OTP to {phone_number}: {send_result['error']}")
                    return False
            else:
                # Placeholder implementation - just log the OTP
                current_app.logger.info(f"[SMS PLACEHOLDER] Sending OTP to {phone_number}")
                current_app.logger.info(f"[SMS PLACEHOLDER] Message: {message_body}")
                current_app.logger.info(f"[SMS PLACEHOLDER] OTP Code: {otp_code}")
                # For placeholder, always return True
                return True
                
        except Exception as e:
            current_app.logger.error(f"Failed to send OTP to {phone_number}: {str(e)}")
            return False
    
    def _create_message(self, otp_code, purpose):
        """Create SMS message based on purpose"""
        if purpose == 'login':
            return f"Your Kuwait Medical Clinic login code is: {otp_code}. This code expires in 5 minutes."
        elif purpose == 'phone_change':
            return f"Your Kuwait Medical Clinic phone verification code is: {otp_code}. This code expires in 5 minutes."
        else:
            return f"Your Kuwait Medical Clinic verification code is: {otp_code}. This code expires in 5 minutes."