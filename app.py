from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import tempfile
import os
from ai_features import extract_bill_details
from rag_feature import get_answer
from ai_assistant import ask_expense_ai
from forecast_ml import ml_forecast_expenses
from recurring_detector import detect_recurring_expenses


with open("expense_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("expense_tf-idf.pkl", "rb") as f:
    tfidf = pickle.load(f)

app = FastAPI(title="Smart Expense Management")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

expenses = [
    # --- Recurring September Baseline ---
    {
        "id": 1,
        "description": "Apartment House Rent",
        "amount": 12000.0,
        "date": "2026-09-05",
        "payment_method": "Net Banking",
        "category": "Bills",
        "confidence": 0.99
    },
    {
        "id": 2,
        "description": "Netflix Monthly Subscription",
        "amount": 649.0,
        "date": "2026-09-01",
        "payment_method": "Card",
        "category": "Entertainment",
        "confidence": 0.98
    },
    {
        "id": 3,
        "description": "Spotify Premium Individual Plan",
        "amount": 119.0,
        "date": "2026-09-05",
        "payment_method": "UPI",
        "category": "Entertainment",
        "confidence": 0.97
    },
    {
        "id": 4,
        "description": "Electricity power bill payment",
        "amount": 1500.0,
        "date": "2026-09-10",
        "payment_method": "UPI",
        "category": "Bills",
        "confidence": 0.97
    },
    {
        "id": 5,
        "description": "High-speed broadband wifi bill",
        "amount": 799.0,
        "date": "2026-09-15",
        "payment_method": "UPI",
        "category": "Bills",
        "confidence": 0.96
    },
    {
        "id": 6,
        "description": "Gym Fitness Membership",
        "amount": 1200.0,
        "date": "2026-09-16",
        "payment_method": "UPI",
        "category": "Healthcare",
        "confidence": 0.95
    },

    # --- October Current Active Expenses ---
    {
        "id": 7,
        "description": "Netflix Monthly Subscription",
        "amount": 649.0,
        "date": "2026-10-01",
        "payment_method": "Card",
        "category": "Entertainment",
        "confidence": 0.98
    },
    {
        "id": 8,
        "description": "Lunch at restaurant",
        "amount": 250.0,
        "date": "2026-10-01",
        "payment_method": "UPI",
        "category": "Food",
        "confidence": 0.95
    },
    {
        "id": 9,
        "description": "Bus ticket to office",
        "amount": 80.0,
        "date": "2026-10-02",
        "payment_method": "Cash",
        "category": "Transportation",
        "confidence": 0.92
    },
    {
        "id": 10,
        "description": "Movie tickets & snacks",
        "amount": 480.0,
        "date": "2026-10-03",
        "payment_method": "Card",
        "category": "Entertainment",
        "confidence": 0.94
    },
    {
        "id": 11,
        "description": "Apartment House Rent",
        "amount": 12000.0,
        "date": "2026-10-05",
        "payment_method": "Net Banking",
        "category": "Bills",
        "confidence": 0.99
    },
    {
        "id": 12,
        "description": "Spotify Premium Individual Plan",
        "amount": 119.0,
        "date": "2026-10-05",
        "payment_method": "UPI",
        "category": "Entertainment",
        "confidence": 0.97
    },
    {
        "id": 13,
        "description": "Weekly grocery shopping",
        "amount": 1850.0,
        "date": "2026-10-06",
        "payment_method": "UPI",
        "category": "Shopping",
        "confidence": 0.96
    },
    {
        "id": 14,
        "description": "College books & stationary supplies",
        "amount": 750.0,
        "date": "2026-10-07",
        "payment_method": "Cash",
        "category": "Education",
        "confidence": 0.91
    },
    {
        "id": 15,
        "description": "Petrol fuel refill for car",
        "amount": 1100.0,
        "date": "2026-10-09",
        "payment_method": "Card",
        "category": "Transportation",
        "confidence": 0.94
    },
    {
        "id": 16,
        "description": "Electricity power bill payment",
        "amount": 1500.0,
        "date": "2026-10-10",
        "payment_method": "UPI",
        "category": "Bills",
        "confidence": 0.97
    },
    {
        "id": 17,
        "description": "Pharmacy medicine prescription",
        "amount": 450.0,
        "date": "2026-10-12",
        "payment_method": "Card",
        "category": "Healthcare",
        "confidence": 0.93
    },
    {
        "id": 18,
        "description": "Swiggy dinner order with friends",
        "amount": 560.0,
        "date": "2026-10-14",
        "payment_method": "UPI",
        "category": "Food",
        "confidence": 0.95
    },
    {
        "id": 19,
        "description": "High-speed broadband wifi bill",
        "amount": 799.0,
        "date": "2026-10-15",
        "payment_method": "UPI",
        "category": "Bills",
        "confidence": 0.96
    },
    {
        "id": 20,
        "description": "Gym Fitness Membership",
        "amount": 1200.0,
        "date": "2026-10-16",
        "payment_method": "UPI",
        "category": "Healthcare",
        "confidence": 0.95
    },
    {
        "id": 21,
        "description": "Metro rail monthly smart card",
        "amount": 400.0,
        "date": "2026-10-17",
        "payment_method": "UPI",
        "category": "Transportation",
        "confidence": 0.93
    },
    {
        "id": 22,
        "description": "Amazon online shopping purchase",
        "amount": 1450.0,
        "date": "2026-10-18",
        "payment_method": "Card",
        "category": "Shopping",
        "confidence": 0.95
    },
    {
        "id": 23,
        "description": "Starbucks coffee & pastries",
        "amount": 340.0,
        "date": "2026-10-20",
        "payment_method": "UPI",
        "category": "Food",
        "confidence": 0.92
    },
    {
        "id": 24,
        "description": "Mobile phone prepaid recharge",
        "amount": 299.0,
        "date": "2026-10-21",
        "payment_method": "UPI",
        "category": "Bills",
        "confidence": 0.98
    },
    {
        "id": 25,
        "description": "HARISHANKER VEG RESTO bill",
        "amount": 1864.4,
        "date": "2026-10-22",
        "payment_method": "UPI",
        "category": "Food",
        "confidence": 0.96,
        "bill_photo": True,
        "bill_items": [
            {"name": "Handi Paneer"},
            {"name": "Sev Tamatar"},
            {"name": "Plain Raita"},
            {"name": "Jeera Rice"},
            {"name": "Tava Roti Butter"},
            {"name": "Vanilla Ice Cream"}
        ]
    }
]

budget = {
    "amount": 32000.0,
    "month": "2026-10"
}


class Expense(BaseModel):
    description: str
    amount: float
    date: str
    payment_method: str = "Cash"


class Budget(BaseModel):
    amount: float
    month: str


def predict_category(description):
    text = tfidf.transform([description])
    prediction = model.predict(text)[0]

    confidence = None

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(text)[0]
        confidence = float(max(probabilities))

    return str(prediction), confidence


@app.get("/")
def home():
    return {"message": "Smart Expense Backend is running"}


@app.post("/expenses")
def add_expense(expense: Expense):
    category, confidence = predict_category(expense.description)

    new_expense = {
        "id": len(expenses) + 1,
        "description": expense.description,
        "amount": expense.amount,
        "date": expense.date,
        "payment_method": expense.payment_method,
        "category": category,
        "confidence": confidence
    }

    expenses.append(new_expense)
    return new_expense


@app.get("/expenses")
def get_expenses(
    category: str = "",
    payment_method: str = "",
    month: str = "",
    keyword: str = "",
    min_amount: float = 0.0,
    max_amount: float = 0.0,
    start_date: str = "",
    end_date: str = ""
):
    result = expenses

    if category:
        result = [e for e in result if e.get("category", "").lower() == category.lower()]

    if payment_method:
        result = [
            e for e in result
            if e.get("payment_method", "").lower() == payment_method.lower()
        ]

    if month:
        result = [e for e in result if str(e.get("date", "")).startswith(month)]

    if start_date:
        result = [e for e in result if str(e.get("date", "")) >= start_date]

    if end_date:
        result = [e for e in result if str(e.get("date", "")) <= end_date]

    if min_amount > 0:
        result = [e for e in result if float(e.get("amount", 0)) >= min_amount]

    if max_amount > 0:
        result = [e for e in result if float(e.get("amount", 0)) <= max_amount]

    if keyword:
        result = [
            e for e in result
            if keyword.lower() in str(e.get("description", "")).lower()
        ]

    return {"count": len(result), "expenses": result}


@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    for expense in expenses:
        if expense["id"] == expense_id:
            expenses.remove(expense)
            return {"message": "Expense deleted successfully"}

    raise HTTPException(status_code=404, detail="Expense not found")


@app.post("/budget")
def set_budget(data: Budget):
    if data.amount < 0:
        raise HTTPException(status_code=400, detail="Budget cannot be negative")

    budget["amount"] = data.amount
    budget["month"] = data.month

    return {"message": "Budget saved", "budget": budget}


@app.get("/dashboard")
def dashboard(
    month: str = "",
    category: str = "",
    payment_method: str = ""
):
    selected = expenses

    if month:
        selected = [e for e in selected if str(e.get("date", "")).startswith(month)]

    if category:
        selected = [e for e in selected if str(e.get("category", "")).lower() == category.lower()]

    if payment_method:
        selected = [
            e for e in selected
            if str(e.get("payment_method", "")).lower() == payment_method.lower()
        ]

    total_amount = sum(float(e["amount"]) for e in selected)

    category_totals = {}

    for expense in selected:
        category = expense["category"]
        category_totals[category] = category_totals.get(category, 0) + expense["amount"]

    category_totals = dict(
        sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    )

    daily_totals = {}

    for expense in selected:
        day = expense["date"]
        daily_totals[day] = daily_totals.get(day, 0) + expense["amount"]

    daily_totals = dict(sorted(daily_totals.items()))

    insights = []

    if selected:
        highest_category = max(category_totals, key=category_totals.get)
        highest_amount = category_totals[highest_category]

        insights.append(
            f"{highest_category} is your highest spending category: ₹{highest_amount:.2f}."
        )
        insights.append(f"Total spending is ₹{total_amount:.2f}.")
    else:
        insights.append("No expenses found.")

    budget_info = {
        "amount": budget["amount"],
        "month": budget["month"],
        "spent": total_amount,
        "remaining": budget["amount"] - total_amount,
        "percentage_used": 0,
        "status": "No budget set"
    }

    if budget["amount"] > 0:
        percentage = (total_amount / budget["amount"]) * 100
        budget_info["percentage_used"] = round(percentage, 2)

        if percentage > 100:
            budget_info["status"] = "Budget exceeded"
            insights.append(
                f"You have exceeded your budget by ₹{total_amount - budget['amount']:.2f}."
            )
        elif percentage >= 80:
            budget_info["status"] = "Budget warning"
            insights.append(f"You have used {percentage:.1f}% of your budget.")
        else:
            budget_info["status"] = "Within budget"
            insights.append(f"You have used {percentage:.1f}% of your budget.")

    # ML Expense Forecasting using Linear Regression
    forecast = ml_forecast_expenses(selected, budget["amount"])

    return {
        "month": month if month else "all",
        "total_expenses": len(selected),
        "total_amount": total_amount,
        "category_chart": {
            "labels": list(category_totals.keys()),
            "values": list(category_totals.values())
        },
        "daily_chart": {
            "dates": list(daily_totals.keys()),
            "amounts": list(daily_totals.values())
        },
        "category_totals": category_totals,
        "budget": budget_info,
        "insights": insights,
        "forecast": forecast,
        "recurring_expenses": detect_recurring_expenses(expenses),
        "expenses": selected
    }


@app.get("/expenses/recurring")
def get_recurring():
    """
    Returns detected recurring subscription / utility expenses.
    """
    return {
        "count": len(detect_recurring_expenses(expenses)),
        "recurring_expenses": detect_recurring_expenses(expenses)
    }


@app.get("/forecast")
def get_forecast(month: str = ""):
    selected = expenses
    if month:
        selected = [e for e in expenses if e["date"].startswith(month)]
    return ml_forecast_expenses(selected, budget["amount"])


# Bill photo AI feature

@app.post("/expenses/bill-photo")
async def add_bill_photo(
    file: UploadFile = File(...),
    question: str = ""
):
    file_data = await file.read()

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".jpg"
    )

    temp_file.write(file_data)
    temp_file.close()

    try:
        bill = extract_bill_details(temp_file.name)

        description = bill["merchant"]

        if not description:
            description = "Bill expense"

        for item in bill["items"]:
            description = description + " " + item["name"]

        category, confidence = predict_category(description)

        new_expense = {
            "id": len(expenses) + 1,
            "description": description,
            "amount": bill["amount"],
            "date": bill["date"],
            "payment_method": "Cash",
            "category": category,
            "confidence": confidence,
            "bill_items": bill["items"],
            "bill_photo": True
        }

        expenses.append(new_expense)

        # RAG answer
        rag_answer = ""

        if question:
            rag_answer = get_answer(
                bill["raw_text"],
                question
            )

        return {
            "message": "Bill read and expense added",
            "bill": bill,
            "expense": new_expense,
            "rag_question": question,
            "rag_answer": rag_answer
        }

    finally:
        os.remove(temp_file.name)


@app.post("/aiassistant")
def ans_assistant(que: str):
    answer = ask_expense_ai(expenses,que)

    return answer
