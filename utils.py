import random
import os
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


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


def send_email(recipient_email: str, json_data: dict, image_path: str, image_name: str):
    """
    Sends an email with JSON data and an image attachment using Gmail.
    """
    sender_email = os.getenv("GMAIL_SENDER_EMAIL")
    app_password = os.getenv("GMAIL_APP_PASSWORD")

    if not sender_email or not app_password:
        print("ERROR: Gmail credentials not found in .env file.")
        return False

    try:
        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"New Car Listing Submission: {json_data['car']['brand']} {json_data['car']['model']}"

        # Attach the JSON data as the email body
        # Using json.dumps for a formatted, easy-to-read JSON string
        body = f"A new car has been listed.\n\nDetails:\n{json.dumps(json_data, indent=2)}"
        msg.attach(MIMEText(body, 'plain'))

        # Attach the image
        with open(image_path, 'rb') as f:
            part = MIMEApplication(f.read(), Name=image_name)
        part['Content-Disposition'] = f'attachment; filename="{image_name}"'
        msg.attach(part)

        # Connect to Gmail's SMTP server and send the email
        print(f"\n--- Sending email to {recipient_email} ---")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
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
        success = send_email(
            recipient_email=test_recipient,
            json_data=test_json,
            image_path=test_image_file_path,
            image_name=test_image_file_name
        )

        # 4. Report the result
        if success:
            print("\n--- Test finished successfully. Check your inbox! ---")
        else:
            print("\n--- Test failed. Please check the error messages above. ---")
