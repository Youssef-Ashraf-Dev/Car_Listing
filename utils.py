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


def get_car_type(image_bytes: bytes) -> str:
    """
    Dummy function to simulate image classification.
    In a real application, this would call a CV model.
    It accepts image_bytes to match the future model's expected input.
    """
    print("--- [Dummy Classifier] Analyzing image... ---")
    car_types = ["sedan", "SUV", "hatchback", "coupe", "convertible", "pickup truck"]
    # We can ignore the image_bytes for now and just return a random choice
    detected_type = random.choice(car_types)
    print(f"--- [Dummy Classifier] Detected type: {detected_type} ---")
    return detected_type


def send_email(recipient_email: str, json_data: dict, image_bytes: bytes, image_name: str):
    """
    Sends an email with JSON data and an image attachment using Gmail.
    This function is now more robust, accepting image bytes directly and handling
    potential missing credentials or data gracefully.
    """
    sender_email = os.getenv("GMAIL_SENDER_EMAIL")
    app_password = os.getenv("GMAIL_APP_PASSWORD")

    if not sender_email or not app_password:
        print("--- GMAIL CREDENTIALS NOT FOUND ---")
        print("Email sending is disabled. Saving artifacts to 'outbox/' instead.")
        
        # Fallback: Save the email content and image to a local 'outbox' directory.
        outbox_dir = "outbox"
        os.makedirs(outbox_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_filename = os.path.join(outbox_dir, f"car_data_{timestamp}.json")
        image_filename = os.path.join(outbox_dir, f"{timestamp}_{image_name}")

        with open(json_filename, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        with open(image_filename, 'wb') as f:
            f.write(image_bytes)
            
        print(f"Saved JSON to {json_filename}")
        print(f"Saved image to {image_filename}")
        return False # Indicate that the email was not sent.

    try:
        # Create the email message using the modern EmailMessage class
        msg = EmailMessage()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        
        # Safely create the subject line
        brand = json_data.get("car", {}).get("brand", "N/A")
        model = json_data.get("car", {}).get("model", "N/A")
        msg['Subject'] = f"New Car Listing Submission: {brand} {model}"

        # Attach the JSON data as the email body
        body = f"A new car has been listed.\n\nDetails:\n{json.dumps(json_data, indent=2)}"
        msg.set_content(body)

        # Attach the image from bytes
        # Determine MIME type from filename extension
        ctype, encoding = mimetypes.guess_type(image_name)
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream' # Generic fallback
        maintype, subtype = ctype.split('/', 1)
        
        msg.add_attachment(image_bytes, maintype=maintype, subtype=subtype, filename=image_name)

        # Connect to Gmail's SMTP server using SMTP_SSL for security and send the email
        print(f"\n--- Sending email to {recipient_email} ---")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, app_password)
            server.send_message(msg)
        
        print("--- Email sent successfully! ---")
        return True

    except Exception as e:
        print(f"--- FAILED to send email: {e} ---")
        return False


# --- Test Block ---
# This block is for testing the send_email function.
if __name__ == "__main__":
    from dotenv import load_dotenv

    # Load environment variables from .env file
    load_dotenv()

    print("--- Running Test for send_email() ---")

    # 1. Define your test data
    test_recipient = os.getenv("GMAIL_RECIPIENT_EMAIL")
    test_json = {
      "car": {
        "body_type": "sedan",
        "brand": "Test Brand",
        "model": "Test Model",
        "manufactured_year": 2023,
        "price": {
          "amount": 500000,
          "currency": "L.E"
        }
      }
    }
    test_image_file_path = "test_car.jpg"
    test_image_file_name = "test_car.jpg"

    # 2. Check if the image file exists before trying to send
    if not os.path.exists(test_image_file_path):
        print(f"ERROR: Test image not found at '{test_image_file_path}'.")
        print("Please download a test image and save it in the project folder.")
    else:
        # 3. Call the function
        with open(test_image_file_path, 'rb') as f:
            test_image_bytes = f.read()

        success = send_email(
            recipient_email=test_recipient,
            json_data=test_json,
            image_bytes=test_image_bytes,
            image_name=test_image_file_name
        )

        # 4. Report the result
        if success:
            print("\n--- Test finished successfully. Check your inbox! ---")
        else:
            print("\n--- Test failed. Please check the error messages above. ---")
