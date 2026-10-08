# 🚀 Smart Expense Tracker & AI Bill Manager

A full-stack AI-powered Expense Management web application with automated bill OCR receipt extraction, ML spending forecasting, category classification, and LLM expense insights.

---

## 📁 Project Structure

```text
simple_expense_backend_ai_bill__/
│
├── backend/                       # 🟢 FastAPI Backend (Deploy on Render)
│   ├── app.py                     # Main FastAPI application & API endpoints
│   ├── ai_assistant.py            # AI Chat Assistant (LangChain + Groq)
│   ├── ai_features.py             # OCR & Bill parsing logic
│   ├── forecast_ml.py             # Linear regression spending forecaster
│   ├── rag_feature.py             # Bill Q&A feature
│   ├── recurring_detector.py      # Recurring expense detection
│   ├── expense_model.pkl          # Trained ML categorization model
│   ├── expense_tf-idf.pkl         # Trained TF-IDF vectorizer
│   ├── requirements.txt           # Python dependencies
│   ├── Procfile                   # Process file for cloud runners
│   └── .env.example               # Example environment variables
│
├── frontend/                      # 🔵 Vanilla Web UI (Deploy on Vercel)
│   ├── index.html                 # Main user interface
│   ├── style.css                  # Responsive modern design & theme
│   ├── app.js                     # Frontend logic, charts & API requests
│   └── vercel.json                # Vercel deployment configuration
│
├── render.yaml                    # Render Blueprint configuration
├── .gitignore                     # Git ignore rules
└── README.md                      # Deployment & setup documentation
```

---

## 🛠️ 1. Deploy Backend to Render

### Step-by-Step Instructions:

1. **Push your code to GitHub**:
   Ensure all changes are committed and pushed to your GitHub repository.

2. **Log in to [Render](https://render.com)**:
   - Click **New +** > **Web Service**.
   - Connect your GitHub repository.

3. **Configure the Web Service**:
   - **Name**: `smart-expense-backend` (or your preferred name)
   - **Region**: Choose the closest region (e.g., Singapore, Frankfurt, Oregon)
   - **Root Directory**: `backend` *(Crucial! Set to `backend`)*
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variables**:
   In the **Environment Variables** section on Render, add:
   - `PYTHON_VERSION` = `3.11.8`
   - `GROQ_API_KEY` = *your_actual_groq_api_key*

5. **Deploy**:
   - Click **Create Web Service**.
   - Wait for the build to complete. Once active, copy your Render URL (e.g., `https://smart-expense-backend.onrender.com`).

---

## ⚡ 2. Deploy Frontend to Vercel

### Step-by-Step Instructions:

1. **Log in to [Vercel](https://vercel.com)**:
   - Click **Add New...** > **Project**.
   - Import your GitHub repository.

2. **Configure the Project**:
   - **Framework Preset**: Select **Other**.
   - **Root Directory**: Click *Edit* and select **`frontend`** *(Crucial!)*.
   - **Build and Output Settings**: Leave as default.

3. **Deploy**:
   - Click **Deploy**.
   - Once deployed, your frontend URL will be live (e.g., `https://smart-expense-frontend.vercel.app`).

---

## 🔗 3. Connect Frontend to your Render Backend

Once your Render backend is live:

1. Open [`frontend/app.js`](frontend/app.js).
2. Change the default backend URL on line 3:
   ```javascript
   const API_URL = localStorage.getItem("API_URL") || window.API_URL || "https://your-backend-name.onrender.com";
   ```
3. Commit and push to GitHub. Vercel will automatically redeploy!

*(Alternatively, users can dynamically configure it in browser console using `localStorage.setItem("API_URL", "https://your-backend-name.onrender.com")` without touching code).*

---

## 💻 4. Running Locally

### 1. Run Backend:
```bash
cd backend
python -m venv myenv
# Windows:
myenv\Scripts\activate
# Mac/Linux:
source myenv/bin/activate

pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

### 2. Run Frontend:
Simply open [`frontend/index.html`](frontend/index.html) in your browser or run a local server:
```bash
cd frontend
python -m http.server 3000
```
Open `http://localhost:3000` in your browser.
