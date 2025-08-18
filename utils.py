import random
import os
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.message import EmailMessage
from datetime import datetime
import mimetypes
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

"""
Utility Functions for Car Listing Application

This module contains helper functions for:
1. Car type detection from images (currently a placeholder)
2. Email sending functionality with Gmail integration
3. Local fallback storage when email credentials are missing

These utilities support the main application workflow while
keeping the core logic separate from implementation details.
"""


def get_car_type(image_bytes: bytes) -> str:
    """
    Determine the car body type from an image.

    Note: This is currently a placeholder function that returns random car types.
    In a production environment, this would be replaced with a computer vision
    model that analyzes the image to detect the actual car type.

    Args:
        image_bytes (bytes): Raw binary image data

    Returns:
        str: Detected car type (e.g., "sedan", "SUV", etc.)
    """
    print("--- [Dummy Classifier] Analyzing image... ---")
    car_types = ["sedan", "SUV", "hatchback", "coupe", "convertible", "pickup truck"]
    # We can ignore the image_bytes for now and just return a random choice
    detected_type = random.choice(car_types)
    print(f"--- [Dummy Classifier] Detected type: {detected_type} ---")
    return detected_type


def send_email(
    recipient_email: str, json_data: dict, image_bytes: bytes, image_name: str
) -> bool:
    """
    Send car listing data and image via email.

    This function attempts to send an email with car listing details and the
    attached car image.

    Args:
        recipient_email (str): Email address to send the listing to
        json_data (dict): Structured car data in dictionary format
        image_bytes (bytes): Raw binary image data
        image_name (str): Original filename of the uploaded image

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # Retrieve credentials from environment variables
    sender_email = os.getenv("GMAIL_SENDER_EMAIL")
    app_password = os.getenv("GMAIL_APP_PASSWORD")

    # Check if credentials are available
    if not sender_email or not app_password:
        print("--- GMAIL CREDENTIALS NOT FOUND ---")
        print("Email sending is disabled. Saving artifacts to 'outbox/' instead.")

        # Fallback: Save the email content and image to a local 'outbox' directory.
        # This is a workaround to allow the app to run without Gmail credentials (for testing purposes).
        # Note: If the credentials are present but incorrect, the code will try to send the email and fail

        outbox_dir = "outbox"
        os.makedirs(outbox_dir, exist_ok=True)

        # Generate unique filenames with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_filename = os.path.join(outbox_dir, f"car_data_{timestamp}.json")
        image_filename = os.path.join(outbox_dir, f"{timestamp}_{image_name}")

        # Save JSON data and image to disk
        with open(json_filename, "w") as f:
            json.dump(json_data, f, indent=2)

        with open(image_filename, "wb") as f:
            f.write(image_bytes)

        print(f"✓ JSON saved to: {json_filename}")
        print(f"✓ Image saved to: {image_filename}")
        return False  # Email was not sent

    try:
        # Create the email message using the modern EmailMessage class
        msg = EmailMessage()
        msg["From"] = sender_email
        msg["To"] = recipient_email

        # Safely create the subject line
        brand = json_data.get("car", {}).get("brand", "N/A")
        model = json_data.get("car", {}).get("model", "N/A")
        msg["Subject"] = f"New Car Listing Submission: {brand} {model}"

        # Format JSON data as readable text for email body
        body = (
            f"A new car has been listed.\n\nDetails:\n{json.dumps(json_data, indent=2)}"
        )
        msg.set_content(body)

        # Attach the image with proper MIME type detection
        ctype, encoding = mimetypes.guess_type(image_name)
        if ctype is None or encoding is not None:
            # Default to binary if type can't be determined
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)

        # Add image as attachment with detected type
        msg.add_attachment(
            image_bytes, maintype=maintype, subtype=subtype, filename=image_name
        )

        # Connect to Gmail securely and send the message
        print(f"\n--- Sending email to {recipient_email} ---")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.send_message(msg)

        print("✓ Email sent successfully!")
        logging.info(f"Email sent successfully to {recipient_email}")
        return True

    except smtplib.SMTPAuthenticationError as e:
        error_message = "Email authentication failed. Please check the sender email and app password in the .env file."
        print(f"✗ {error_message}")
        logging.error(f"SMTPAuthenticationError: {e} - {error_message}")
        return False
    except (
        smtplib.SMTPConnectError,
        smtplib.SMTPServerDisconnected,
        ConnectionRefusedError,
    ) as e:
        error_message = "Could not connect to the email server. Please check your network connection and the SMTP server address."
        print(f"✗ {error_message}")
        logging.error(f"SMTP Connection Error: {type(e).__name__} - {e}")
        return False
    except Exception as e:
        error_message = "An unexpected error occurred while sending the email."
        print(f"✗ {error_message}")
        logging.error(f"Unexpected email error in send_email: {e}", exc_info=True)
        return False


# --- Module Test Code ---
if __name__ == "__main__":
    """
    Test the email functionality independently of the main application.
    This allows developers to verify email sending works correctly.
    """
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    print("===== EMAIL FUNCTIONALITY TEST =====")

    # Test data
    test_recipient = os.getenv("GMAIL_RECIPIENT_EMAIL")
    test_json = {
        "car": {
            "body_type": "sedan",
            "brand": "Test Brand",
            "model": "Test Model",
            "manufactured_year": 2023,
            "color": "Blue",
            "windows": "tinted",
            "price": {"amount": 500000, "currency": "L.E"},
        }
    }
    test_image_path = "test_car.jpg"

    # Validate test image exists
    if not os.path.exists(test_image_path):
        print("❌ TEST FAILED: Test image not found.")
        print(f"Please create a file named '{test_image_path}' in the project root.")
        print("You can use any JPG image of a car for testing.")
        exit(1)

    # Run the test
    print(f"• Reading test image: {test_image_path}")
    with open(test_image_path, "rb") as f:
        test_image_bytes = f.read()

    print("• Attempting to send email...")
    success = send_email(
        recipient_email=test_recipient,
        json_data=test_json,
        image_bytes=test_image_bytes,
        image_name=os.path.basename(test_image_path),
    )

    # Report results
    if success:
        print("\n✅ TEST PASSED: Email sent successfully!")
        print(f"Check inbox for: {test_recipient}")
    else:
        print("\n⚠️ TEST FINISHED: Email was not sent.")
        print("Check above logs for details or look in the 'outbox' directory.")
