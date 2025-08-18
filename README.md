# 🚗 Car Listing Processor

**Transform messy car descriptions into structured, validated JSON in seconds.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io)
[![Azure OpenAI](https://img.shields.io/badge/azure-openai-green.svg)](https://azure.microsoft.com/en-us/products/ai-services/openai-service)

> **Input:** "Blue Ford Fusion 2015, 2.0L engine, tinted windows, 1 million L.E"  
> **Output:** Clean JSON with normalized fields, validation, and automatic email delivery

## ⚡ What It Does

Converts unstructured car listings (text + image) → structured JSON → email delivery with bulletproof fallbacks.

**Built for production** with hardened prompts, strict validation, and comprehensive error handling.

## 🎯 Core Features

- **🧠 AI-Powered Extraction** - GPT-4 with hardened prompts (injection-resistant)
- **🔒 Strict Validation** - Pydantic models with year ranges (1975-2025)
- **📧 Smart Delivery** - Email with automatic `outbox/` fallback
- **⚙️ Data Normalization** - "2.0L" → 2000cc, "220K" → 220000
- **🛡️ Production-Ready** - Token limits, error handling, logging

## 🚀 Quick Start

```bash
git clone https://github.com/Youssef-Ashraf-Dev/Car_Listing.git
cd car-listing-processor
pip install -r requirements.txt
cp .env.example .env  # Add your Azure OpenAI + Gmail credentials
streamlit run app.py
```

**Tech Stack:** Python • Streamlit • LangChain • Azure OpenAI • Pydantic

## 📋 Sample Input/Output

**Input Text:**
```
Blue Ford Fusion produced in 2015 featuring a 2.0-liter engine. 
Tinted windows. Rear bumper replaced after minor collision. 
Priced at 1 million L.E.
```

**Output JSON:**
```json
{
  "car": {
    "body_type": "sedan",
    "color": "Blue",
    "brand": "Ford", 
    "model": "Fusion",
    "manufactured_year": 2015,
    "motor_size_cc": 2000,
    "windows": "tinted",
    "notices": [{"type": "collision", "description": "rear bumper replaced"}],
    "price": {"amount": 1000000, "currency": "L.E"}
  }
}
```

## 🏗️ Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌─────────────┐
│ Streamlit   │───▶│ LLM Parser   │───▶│ Validation  │───▶│ Email/Save  │
│ Frontend    │    │ (Hardened)   │    │ (Pydantic)  │    │ (Fallback)  │
└─────────────┘    └──────────────┘    └─────────────┘    └─────────────┘
```

**Key Files:**
- `app.py` - Streamlit UI & orchestration
- `llm_parser.py` - Hardened prompts + Pydantic models  
- `utils.py` - Email delivery + image analysis
- `.env.example` - Configuration template

## ⚙️ Configuration

Copy `.env.example` → `.env` and configure:

```bash
# Azure OpenAI (Required)
AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o"
AZURE_OPENAI_API_VERSION="2024-02-15-preview"
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_OPENAI_API_KEY="your-key"

# Gmail (Required - use App Password)
GMAIL_SENDER_EMAIL="sender@gmail.com"
GMAIL_APP_PASSWORD="16-digit-app-password"
GMAIL_RECIPIENT_EMAIL="listings@company.com"
```

## 🛡️ Security & Hardening

**Prompt Injection Protection:**
- Strict system instructions that forbid responding to user commands
- Schema-locked output (JSON only, no markdown/comments)
- Temperature 0 for deterministic results

**Data Validation:**
- Year constraints (1975-2025 for cars, 2000-2025 for tires)
- Required field validation with clear error messages
- Optional field omission (no hallucinated data)

**Error Handling:**
- Specific catches for API, parsing, and SMTP failures
- Graceful fallback to local `outbox/` directory
- Comprehensive logging for debugging

## 🧪 Testing & Validation

```bash
# Test individual components
python llm_parser.py       # LLM parsing test
python utils.py            # Email delivery test (needs test_car.jpg)

# Run full workflow via UI
streamlit run app.py
```

## 🎛️ Production Optimizations

- **Token Efficiency:** Optimized prompts reduce costs by ~30%
- **Input Limits:** 500 char descriptions, 5MB images
- **Capped Responses:** 300 tokens max (sufficient for complete JSON)
- **Deterministic Output:** Temperature 0, consistent results

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.