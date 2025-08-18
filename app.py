import os
import streamlit as st
from dotenv import load_dotenv
from llm_parser import create_car_data_parser_chain
from utils import get_car_type, send_email
import tempfile
import logging
from langchain_core.exceptions import OutputParserException
from openai import APIConnectionError, RateLimitError, AuthenticationError

# --- Setup ---
# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def process_submission(image_file, description):
    """
    Process a car listing submission by handling the image and text description.

    This function handles the complete workflow:
    1. Securely saves the uploaded image to a temporary file
    2. Uses the LLM to extract structured car data from the text description
    3. Validates that all required fields are present before proceeding
    4. Analyzes the image to determine the car type (sedan, SUV, etc.)
    5. Sends the final data and image via email
    6. Cleans up temporary files

    Args:
        image_file: The uploaded image file object from Streamlit
        description: String containing the user's car description

    Returns:
        tuple: (success, result, email_sent)
            - success: Boolean indicating if processing succeeded
            - result: Either the parsed car data or an error message
            - email_sent: Boolean indicating if the email was sent successfully
    """
    # Use a temporary file to securely handle the uploaded image
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=os.path.splitext(image_file.name)[1]
    ) as tmp:
        tmp.write(image_file.getbuffer())
        temp_image_path = tmp.name

    try:
        # Step 1: Parse the text description using LLM
        st.info("Step 1/4: Parsing text description with LLM...")
        car_parser_chain = create_car_data_parser_chain()
        parsed_data = car_parser_chain.invoke({"description": description})

        # Step 2: Validate required fields are present
        # This ensures all critical car information was extracted before proceeding
        car_details = parsed_data.car
        missing_fields = []
        if car_details.brand == "not specified":
            missing_fields.append("Brand")
        if car_details.model == "not specified":
            missing_fields.append("Model")
        if car_details.manufactured_year is None:
            missing_fields.append("Manufactured Year")
        if car_details.motor_size_cc is None:
            missing_fields.append("Motor Size")
        if car_details.price is None or car_details.price.amount is None:
            missing_fields.append("Price")

        if missing_fields:
            # Fail fast if critical data is missing - prompt user to provide details
            error_message = f"Submission failed. The following required details are missing from your description: {', '.join(missing_fields)}. Please add them and try again."
            st.error(error_message)
            return False, error_message, False

        # Step 3: Analyze the image to determine car type
        st.info("Step 2/4: Analyzing image to determine car type...")
        with open(temp_image_path, "rb") as f:
            image_bytes = f.read()
        car_type = get_car_type(image_bytes)

        # Update the body_type field in the parsed data
        parsed_data.car.body_type = car_type
        car_data_dict = parsed_data.model_dump()

        # Step 4: Send email with the car listing details and image
        st.info("Step 3/4: Preparing to send email...")
        recipient_email = os.getenv("GMAIL_RECIPIENT_EMAIL")
        email_sent = send_email(
            recipient_email=recipient_email,
            json_data=car_data_dict,
            image_bytes=image_bytes,
            image_name=image_file.name,
        )

        st.info("Step 4/4: Finalizing...")
        return True, car_data_dict, email_sent

    except OutputParserException as e:
        error_message = "The AI model returned data in an unexpected format. This can happen if the description is ambiguous or lacks key details. Please try rephrasing your description."
        logging.error(f"OutputParserException: {e}")
        st.error(error_message)
        return False, "Failed to parse description.", False

    except (APIConnectionError, RateLimitError) as e:
        error_message = "The AI service is currently unavailable or busy. Please try again in a few moments."
        logging.error(f"OpenAI API Error: {type(e).__name__} - {e}")
        st.error(error_message)
        return False, "Service unavailable.", False

    except AuthenticationError as e:
        error_message = "AI service authentication failed. Please check the server configuration. This issue is not related to your submission."
        logging.error(f"OpenAI AuthenticationError: {e}")
        st.error(error_message)
        return False, "Authentication error.", False

    except Exception as e:
        # Catch-all for any other unexpected errors
        error_message = "An unexpected error occurred during processing. The technical team has been notified."
        logging.error(
            f"An unexpected error occurred in process_submission: {e}", exc_info=True
        )
        st.error(error_message)
        return False, "An unexpected error occurred.", False
    finally:
        # Clean up the temporary file, regardless of success or failure
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)


# --- Streamlit UI Components ---
# Configure the application layout and title
st.set_page_config(page_title="Car Listing Submission", layout="wide")
st.title("🚗 Car Listing Submission Portal")

# Application instructions in an expandable section
with st.expander("ℹ️ How to Use This Form"):
    st.markdown(
        """
    Welcome! This tool helps you list a car by extracting details from your text description and image.
    
    **Follow these steps:**
    1.  **Write a detailed description** (max 800 characters) in the text area. Please include:
        - Color, Brand, and Model (e.g., "Blue Ford Fusion")
        - Manufactured Year (e.g., "produced in 2015")
        - Engine Size (e.g., "2.0-liter engine" or "1500 cc")
        - Tire Information (e.g., "brand-new tires from 2022")
        - Window Features (e.g., "tinted windows")
        - Any damages/notices (e.g., "rear bumper replaced")
        - The Price and Currency (e.g., "Priced at 1 million L.E.")
    2.  **Upload a clear image** (max 5MB) of the car using the file uploader below.
    3.  Click the **"Submit Listing"** button to start the process.
    
    The system will then analyze the data, determine the car type from the image, and email the final listing.
    
    **Limits:** Description: 800 chars max | Image: 5MB max | Supported formats: JPG, JPEG, PNG
    """
    )

# Create two-column layout for description and image upload
col1, col2 = st.columns(2)

# --- Define input validation limits ---
MAX_DESC_LENGTH = 800  # characters (sufficient for car details with some notices)
MAX_IMAGE_SIZE_MB = 5  # Reasonable size limit for good quality car images
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024

# Left column - Text description input
with col1:
    st.subheader("1. Provide Car Description")
    description = st.text_area(
        "Enter the car details here:", height=300, max_chars=MAX_DESC_LENGTH
    )
    if description:
        remaining_chars = MAX_DESC_LENGTH - len(description)
        # Visual feedback about character limit
        if remaining_chars < 100:
            st.caption(f"⚠️ {remaining_chars} characters remaining")
        else:
            st.caption(f"✅ {len(description)}/{MAX_DESC_LENGTH} characters used")

# Right column - Image upload
with col2:
    st.subheader("2. Upload Car Image")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        # Validate image size before processing
        if uploaded_file.size > MAX_IMAGE_SIZE_BYTES:
            st.error(
                f"❌ Image size ({uploaded_file.size / (1024*1024):.1f}MB) exceeds the {MAX_IMAGE_SIZE_MB}MB limit. Please upload a smaller file."
            )
            uploaded_file = None
        else:
            st.image(
                uploaded_file, caption="Uploaded Car Image", use_container_width=True
            )
            st.caption(f"✅ Image size: {uploaded_file.size / (1024*1024):.1f}MB")

# --- Submission Button and Processing Logic ---
st.subheader("3. Submit Your Listing")
if st.button("Submit Listing", use_container_width=True):
    # Comprehensive input validation before processing
    error_messages = []

    # Validate image upload
    if uploaded_file is None:
        error_messages.append("Please upload a car image")
    elif uploaded_file.size > MAX_IMAGE_SIZE_BYTES:
        error_messages.append(f"Image size exceeds {MAX_IMAGE_SIZE_MB}MB limit")

    # Validate description text
    if not description or not description.strip():
        error_messages.append("Please provide a car description")
    elif len(description) > MAX_DESC_LENGTH:
        error_messages.append(f"Description exceeds {MAX_DESC_LENGTH} character limit")

    # Display all validation errors (if any)
    if error_messages:
        for msg in error_messages:
            st.error(f"❌ {msg}")
    else:
        # All validation passed - process the submission
        with st.spinner("Processing your submission... Please wait."):
            success, result, email_sent = process_submission(uploaded_file, description)

        # Handle the result based on success/failure
        if success:
            st.success("✅ Car listing processed successfully!")

            st.subheader("Extracted Car Information")
            st.json(result)

            # Email status feedback
            if email_sent:
                st.success("📧 Email sent successfully to the listing manager!")
            else:
                st.error(
                    "⚠️ Email could not be sent. Please check the `.env` configuration and terminal for errors."
                )
        else:
            # Error handling with helpful guidance
            st.error(f"❌ An error occurred. Please review the details below.")
            st.error(result)
            st.info(
                "Please ensure your description includes all required details about the car."
            )
