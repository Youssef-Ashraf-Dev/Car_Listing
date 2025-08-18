## Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant Streamlit_UI as Streamlit UI (app.py)
    participant LLM_Processor as LLM Processor (llm_parser.py)
    participant Azure_OpenAI as Azure OpenAI Service
    participant Image_Classifier as Image Classifier (utils.py)
    participant Email_Utility as Email Utility (utils.py)
    participant Gmail_SMTP as Gmail SMTP Server
    participant Local_Filesystem as Local Filesystem ('outbox/')

    User->>Streamlit_UI: 1. Uploads Image & Enters Description
    User->>Streamlit_UI: 2. Clicks "Submit Listing"

    activate Streamlit_UI

    %% --- Initial Client-Side Validation in app.py ---
    alt Input is Valid (File & Text exist, size is correct)
        Streamlit_UI->>Streamlit_UI: 3. Calls process_submission()
        
        %% --- Main Processing Workflow ---
        Streamlit_UI->>LLM_Processor: 4. Invoke Chain with description
        activate LLM_Processor
        LLM_Processor->>Azure_OpenAI: 5. API Request (Prompt)
        Azure_OpenAI-->>LLM_Processor: 6. API Response (JSON-like text)
        LLM_Processor-->>Streamlit_UI: 7. Returns Structured Pydantic Object
        deactivate LLM_Processor

        %% --- Application-Level Validation in app.py ---
        Streamlit_UI->>Streamlit_UI: 8. Validates critical fields (brand, model, etc.)
        
        Streamlit_UI->>Image_Classifier: 9. get_car_type(image_bytes)
        activate Image_Classifier
        Image_Classifier-->>Streamlit_UI: 10. Returns Car Type (String)
        deactivate Image_Classifier

        Note over Streamlit_UI: 11. Combines LLM result with Car Type

        Streamlit_UI->>Email_Utility: 12. send_email(final_data, image)
        activate Email_Utility

        %% --- Fallback Logic in utils.py ---
        alt Gmail Credentials Found: path a
            Email_Utility->>Gmail_SMTP: 13a. Sends message via SMTP
            Gmail_SMTP-->>Email_Utility: Response
            Email_Utility-->>Streamlit_UI: 14a. Returns email_sent = True
        else Credentials NOT Found: path b
            Email_Utility->>Local_Filesystem: 13b. Saves JSON & Image to 'outbox/'
            Local_Filesystem-->>Email_Utility: Confirmation
            Email_Utility-->>Streamlit_UI: 14b. Returns email_sent = False
        end
        deactivate Email_Utility

        Streamlit_UI-->>User: 15. Displays Success Message & JSON Data

    else Input is Invalid
        Streamlit_UI-->>User: 3. Displays Validation Error Message(s)
    end
    
    deactivate Streamlit_UI