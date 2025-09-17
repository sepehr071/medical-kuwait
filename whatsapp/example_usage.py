#!/usr/bin/env python3
"""
WhatsApp Sender Usage Examples
==============================

This script demonstrates how to use the WhatsAppSender class to send
WhatsApp messages using Twilio's API.

Make sure to:
1. Install dependencies: pip install -r requirements.txt
2. Set up your .env file with Twilio credentials
3. Join the Twilio Sandbox for WhatsApp before testing
"""

import sys
from whatsapp_sender import WhatsAppSender, setup_logging


def example_simple_message():
    """Example: Send a simple text message"""
    print("=== Example 1: Simple Text Message ===")
    
    try:
        # Initialize sender
        sender = WhatsAppSender()
        
        # Send message
        result = sender.send_message(
            to_number="+1234567890",  # Replace with actual recipient number
            message="Hello! This is a test message from Python using Twilio WhatsApp API."
        )
        
        # Check result
        if result['success']:
            print(f"✅ Message sent successfully!")
            print(f"   Message SID: {result['message_sid']}")
            print(f"   Status: {result['status']}")
            print(f"   Sent to: {result['to']}")
        else:
            print(f"❌ Failed to send message: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error in example: {str(e)}")


def example_multiple_messages():
    """Example: Send messages to multiple recipients"""
    print("\n=== Example 2: Multiple Messages ===")
    
    try:
        # Initialize sender
        sender = WhatsAppSender()
        
        # List of recipients and messages
        messages = [
            {
                "to": "+1234567890",  # Replace with actual numbers
                "message": "Hello from Python! This is message 1."
            },
            {
                "to": "+1987654321",  # Replace with actual numbers
                "message": "Hello from Python! This is message 2."
            }
        ]
        
        # Send messages
        results = []
        for msg_data in messages:
            result = sender.send_message(msg_data["to"], msg_data["message"])
            results.append(result)
            
            if result['success']:
                print(f"✅ Message sent to {result['to']} - SID: {result['message_sid']}")
            else:
                print(f"❌ Failed to send to {result['to']}: {result['error']}")
        
        # Summary
        successful = sum(1 for r in results if r['success'])
        total = len(results)
        print(f"\n📊 Summary: {successful}/{total} messages sent successfully")
        
    except Exception as e:
        print(f"❌ Error in example: {str(e)}")


def example_with_error_handling():
    """Example: Proper error handling"""
    print("\n=== Example 3: Error Handling ===")
    
    try:
        # Initialize sender
        sender = WhatsAppSender()
        
        # Test cases with potential errors
        test_cases = [
            {
                "to": "+1234567890",  # Valid number
                "message": "This should work",
                "description": "Valid message"
            },
            {
                "to": "invalid_number",  # Invalid number format
                "message": "This will fail",
                "description": "Invalid phone number"
            },
            {
                "to": "+1234567890",
                "message": "",  # Empty message
                "description": "Empty message"
            }
        ]
        
        for i, test in enumerate(test_cases, 1):
            print(f"\nTest {i}: {test['description']}")
            try:
                result = sender.send_message(test["to"], test["message"])
                
                if result['success']:
                    print(f"✅ Success: {result['message_sid']}")
                else:
                    print(f"❌ Failed: {result['error']}")
                    
            except Exception as e:
                print(f"❌ Exception: {str(e)}")
                
    except Exception as e:
        print(f"❌ Error in example: {str(e)}")


def interactive_example():
    """Example: Interactive message sending"""
    print("\n=== Example 4: Interactive Mode ===")
    
    try:
        # Initialize sender
        sender = WhatsAppSender()
        
        print("📱 Interactive WhatsApp Message Sender")
        print("Enter 'quit' to exit\n")
        
        while True:
            # Get recipient
            to_number = input("Enter recipient phone number (E.164 format, e.g., +1234567890): ").strip()
            if to_number.lower() == 'quit':
                break
                
            # Get message
            message = input("Enter your message: ").strip()
            if message.lower() == 'quit':
                break
            
            # Send message
            result = sender.send_message(to_number, message)
            
            if result['success']:
                print(f"✅ Message sent! SID: {result['message_sid']}\n")
            else:
                print(f"❌ Failed to send: {result['error']}\n")
                
        print("👋 Goodbye!")
        
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"❌ Error in interactive mode: {str(e)}")


def example_validation_demo():
    """Example: Phone number validation demo"""
    print("\n=== Example 5: Phone Number Validation ===")
    
    try:
        # Initialize sender
        sender = WhatsAppSender()
        
        # Test various phone number formats
        test_numbers = [
            "+1234567890",           # Valid E.164
            "whatsapp:+1234567890",  # Valid with whatsapp prefix
            "+919876543210",         # Valid international (India)
            "1234567890",            # Invalid (no +)
            "+123",                  # Invalid (too short)
            "+123456789012345678",   # Invalid (too long)
            "",                      # Invalid (empty)
            "invalid",               # Invalid (not numeric)
        ]
        
        print("Testing phone number validation:")
        for number in test_numbers:
            try:
                validated = sender.validate_phone_number(number)
                print(f"✅ {number:20} → {validated}")
            except ValueError as e:
                print(f"❌ {number:20} → Error: {str(e)}")
                
    except Exception as e:
        print(f"❌ Error in validation demo: {str(e)}")


def main():
    """Main function to run all examples"""
    print("🚀 WhatsApp Sender Examples")
    print("=" * 50)
    
    # Setup logging
    setup_logging('INFO')
    
    # Check if .env file exists
    import os
    if not os.path.exists('.env'):
        print("⚠️  Warning: .env file not found!")
        print("   Please copy .env.example to .env and fill in your Twilio credentials.")
        print("   Then run this script again.\n")
        
        choice = input("Do you want to continue with examples anyway? (y/N): ")
        if choice.lower() != 'y':
            print("👋 Setup your .env file first!")
            return
    
    # Run examples
    try:
        # Note: These examples use placeholder phone numbers
        # Replace with actual numbers for testing
        print("📝 Note: Replace phone numbers in examples with actual numbers for testing")
        print("-" * 70)
        
        example_validation_demo()      # Start with validation (no API calls)
        
        # For API examples, ask user if they want to continue
        choice = input("\nDo you want to run API examples? (requires valid .env setup) (y/N): ")
        if choice.lower() == 'y':
            example_simple_message()
            example_multiple_messages()
            example_with_error_handling()
            
            # Ask for interactive mode
            choice = input("\nDo you want to try interactive mode? (y/N): ")
            if choice.lower() == 'y':
                interactive_example()
        
        print("\n✨ All examples completed!")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {str(e)}")


if __name__ == "__main__":
    main()