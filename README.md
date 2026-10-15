# 💰 Smart Expense Tracker & AI Bill Manager

[![Live Demo](https://img.shields.io/badge/Live_Demo-Vercel-black?style=for-the-badge&logo=vercel)](https://smart-expenses-trackerr.vercel.app/)
[![API Backend](https://img.shields.io/badge/API_Backend-Render-46E3B7?style=for-the-badge&logo=render)](https://smart-expenses-tracker-h4v7.onrender.com/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Groq](https://img.shields.io/badge/AI_Inference-Groq-F05A28?style=for-the-badge)](https://groq.com)

A full-stack, AI-powered personal finance management web application. It combines automated **OCR bill scanning**, **RAG receipt question-answering**, **Machine Learning expense categorization**, **Linear Regression spending forecasting**, **recurring subscription detection**, and a **conversational AI financial assistant**.

---

## 🌐 Live Links

- **🚀 Live Web App:** [https://smart-expenses-trackerr.vercel.app/](https://smart-expenses-trackerr.vercel.app/)
- **⚡ Backend API (Render):** [https://smart-expenses-tracker-h4v7.onrender.com/](https://smart-expenses-tracker-h4v7.onrender.com/)
- **📖 API Documentation (Swagger):** [https://smart-expenses-tracker-h4v7.onrender.com/docs](https://smart-expenses-tracker-h4v7.onrender.com/docs)

---

## ✨ Key Features

### 1. 📊 Interactive Analytics Dashboard
- Real-time summary cards: **Total Spent**, **Active Budget**, **Remaining Balance**, and **Budget Usage %**.
- Interactive **Chart.js** visualizations:
  - **Category Breakdown** (Donut / Pie chart)
  - **Daily Spending Timeline** (Bar chart)
- Dynamic budget alerts (Within budget, Warning at 80%+, and Exceeded alerts).

### 2. 🧾 AI Bill Scanner & Item Extraction (OCR)
- Upload receipts or bill images (`.jpg`, `.png`, `.jpeg`).
- Uses **RapidOCR (ONNX Runtime)** to extract:
  - Merchant / Store name
  - Transaction date
  - Total bill amount
  - Individual purchased line items & prices
- Automatically creates a new categorized expense directly from the scanned receipt.

### 3. 🔍 Bill RAG Q&A
- Ask natural language questions about any uploaded receipt (e.g., *"What was the price of Handi Paneer?"* or *"Was any tax charged?"*).
- Powered by **LangChain** and **Groq LLM** (`openai/gpt-oss-20b`) analyzing raw OCR context.

### 4. 🏷️ Smart ML Expense Categorizer
- Automatically predicts expense categories (Food, Transportation, Bills, Entertainment, Shopping, Healthcare, Education) as you type descriptions.
- Powered by a trained **TF-IDF Vectorizer + Scikit-Learn Classifier** with real-time confidence scores.

### 5. 📈 ML Spending Forecasting
- Trains a **Linear Regression** model on daily spending velocity to forecast:
  - Expected total spend for the next **30 days**
  - Expected spending over the next **7 days**
  - Daily spending pace / burn rate

### 6. 🔄 Recurring Expense & Subscription Detector
- Automatically identifies recurring bills and monthly subscriptions (e.g., Netflix, Spotify, Rent, Wi-Fi, Gym, Electricity) using **Pandas** pattern matching.
- Highlights recurring commitments to prevent forgotten subscriptions.

### 7. 💬 Conversational AI Financial Assistant
- An integrated chat assistant that answers queries about your financial habits (e.g., *"How much did I spend on food this month?"*, *"What was my highest single expense?"*).
- Uses **Groq** high-speed LLM inference with context-grounded prompt engineering.

### 8. 📋 Comprehensive Expense Ledger
- Full search, filter, and sorting capabilities:
  - Filter by Month (`YYYY-MM`), Category, and Payment Method (Cash, UPI, Card, Net Banking).
  - Search by description keywords and filter by date/amount ranges.
  - Delete expenses and view itemized receipt breakdowns.

---

## 🛠️ Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | HTML5, Modern CSS3 (Glassmorphism & Material Design), JavaScript (ES6+), Chart.js |
| **Backend** | Python 3.11, FastAPI, Uvicorn, Pydantic |
| **AI / LLM** | Groq API, LangChain (`langchain-groq`), RapidOCR (`rapidocr_onnxruntime`), Pillow |
| **Machine Learning & Data** | Scikit-Learn (Linear Regression & TF-IDF), Pandas, NumPy |
| **Hosting & Deployment** | Vercel (Frontend), Render (FastAPI Backend) |

---

## 📁 Project Structure

```text
simple_expense_backend_ai_bill__/
├── backend/                       # FastAPI Backend
│   ├── app.py                     # Main application & REST API routes
│   ├── ai_assistant.py            # AI Chat Assistant (LangChain + Groq)
│   ├── ai_features.py             # RapidOCR Receipt & Bill parser
│   ├── forecast_ml.py             # Linear Regression Spending Forecaster
│   ├── rag_feature.py             # Bill RAG Question-Answering
│   ├── recurring_detector.py      # Subscription & Recurring detector
│   ├── expense_model.pkl          # Pre-trained ML Category Classifier
│   ├── expense_tf-idf.pkl         # Pre-trained TF-IDF Vectorizer
│   ├── requirements.txt           # Python backend dependencies
│   ├── Procfile                   # Process file for cloud runners
│   └── .env.example               # Template for environment variables
│
├── frontend/                      # Frontend Web App
│   ├── index.html                 # Single Page Application UI
│   ├── style.css                  # Modern UI styles & responsive layout
│   ├── app.js                     # Client logic, Chart.js integrations & API calls
│   └── vercel.json                # Vercel deployment configuration
│
├── render.yaml                    # Render Blueprint configuration
├── .gitignore                     # Git ignore rules
└── README.md                      # Project documentation
```

---

## 🚀 Getting Started Locally

### Prerequisites
- **Python 3.10+** installed
- A modern web browser
- Free **[Groq API Key](https://console.groq.com/)** (for AI Assistant and Bill RAG)

---

### 1. Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows:
   python -m venv myenv
   myenv\Scripts\activate

   # macOS / Linux:
   python3 -m venv myenv
   source myenv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file inside the `backend` folder:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

5. **Start the FastAPI server:**
   ```bash
   uvicorn app:app --reload --port 8000
   ```
   The backend will be running at `http://127.0.0.1:8000`. You can inspect the interactive Swagger API docs at `http://127.0.0.1:8000/docs`.

---

### 2. Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd ../frontend
   ```

2. **Launch a simple local web server:**
   ```bash
   # Using Python:
   python -m http.server 3000
   ```

3. **Open the App:**
   Open your browser and visit: `http://localhost:3000`

> 💡 **Tip:** The frontend automatically connects to `http://127.0.0.1:8000` when running locally, or to the live Render backend when hosted on Vercel.

---

## 📡 API Endpoints Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Root health check |
| `GET` | `/expenses` | List all expenses with optional filters (`category`, `payment_method`, `month`, `keyword`, `min_amount`, `max_amount`) |
| `POST` | `/expenses` | Add a new manual expense with auto ML category prediction |
| `DELETE` | `/expenses/{id}` | Delete an expense by ID |
| `POST` | `/budget` | Set monthly budget amount and target month |
| `GET` | `/dashboard` | Fetch complete dashboard analytics, charts, budget metrics, and ML forecast |
| `GET` | `/forecast` | Get Linear Regression spending forecast for the month |
| `GET` | `/expenses/recurring`| Detect and list all recurring subscriptions |
| `POST` | `/expenses/bill-photo`| Upload bill image for OCR extraction, auto expense creation, and optional RAG Q&A |
| `POST` | `/aiassistant?que=...`| Ask conversational financial questions to the Groq AI Assistant |

---

## ☁️ Deployment

### Backend to Render
1. Create a new **Web Service** on [Render](https://render.com).
2. Connect your GitHub repository.
3. Configure the settings:
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`
4. In **Environment Variables**, add:
   - `PYTHON_VERSION`: `3.11.8`
   - `GROQ_API_KEY`: `your_groq_api_key`

### Frontend to Vercel
1. Import your GitHub repository in [Vercel](https://vercel.com).
2. Set the **Root Directory** to `frontend`.
3. Set **Framework Preset** to `Other`.
4. Deploy!

---

## 📄 License

This project is licensed under the MIT License - feel free to use, modify, and distribute it for personal and educational projects.
