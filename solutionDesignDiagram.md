```mermaid
graph TD;

    %% Define Node Styles for Clarity
    classDef user fill:#cde4ff,stroke:#6a8eae,stroke-width:2px;
    classDef internal fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    classDef external fill:#fff9c4,stroke:#f57f17,stroke-width:2px;
    classDef data fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px;

    %% --- Define Subgraphs to Group Components ---
    subgraph "User & UI"
        User([<fa:fa-user> User])
        App("Streamlit UI <br> (app.py)")
    end

    subgraph "Application Core Functionality"
        LLM_Processor("LLM Processor <br> (llm_parser.py)")
        Image_Classifier("Image Classifier (Dummy) <br> (utils.py)")
        Email_Utility("Email Utility <br> (utils.py)")
    end
    
    subgraph "External Systems & Services"
        Azure("Azure OpenAI Service")
        Gmail("Gmail SMTP Server")
    end

    subgraph "Configuration & Local Storage"
        EnvConfig(".env File")
        LocalFilesystem("Local Filesystem <br> ('outbox/')")
    end

    %% --- Define Connections Between Components ---

    %% User interacts with the UI
    User -- "Interacts with Web App" --> App

    %% App orchestrates the backend
    App -- "Sends Image for Classification" --> Image_Classifier
    App -- "Sends Text for Parsing" --> LLM_Processor
    App -- "Sends Final Data for Emailing" --> Email_Utility

    %% Backend modules interact with external services
    LLM_Processor -- "Makes API Call" --> Azure
    Email_Utility -- "Sends Email via" --> Gmail
    
    %% Email Utility's unique fallback mechanism
    Email_Utility -- "Fallback: Saves Files to" --> LocalFilesystem

    %% Configuration dependency
    EnvConfig -- "Provides Azure OpenAI (GPT-4o mini Model) Credentials" --> LLM_Processor
    EnvConfig -- "Provides GMAIL Credentials & Configurations" --> Email_Utility
    
    %% Apply Styles
    class User user;
    class App,LLM_Processor,Image_Classifier,Email_Utility internal;
    class Azure,Gmail external;
    class EnvConfig,LocalFilesystem data;
