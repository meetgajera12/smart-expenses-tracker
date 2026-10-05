from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import tempfile
import os
from ai_features import extract_bill_details
from rag_feature import get_answer
from ai_assistant import ask_expense_ai


with open("expense_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("expense_tf-idf.pkl", "rb") as f:
    tfidf = pickle.load(f)

app = FastAPI(title="Smart Expense Management")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

expenses = [
    {
        "id": 1,
        "description": "Lunch at restaurant",
        "amount": 250.0,
        "date": "2026-10-01",
        "payment_method": "UPI",
        "category": "Food",
        "confidence": 0.95
    },
    {
        "id": 2,
        "description": "Bus ticket",
        "amount": 80.0,
        "date": "2026-10-02",
        "payment_method": "Cash",
        "category": "Transportation",
        "confidence": 0.92
    },
    {
        "id": 3,
        "description": "Movie ticket",
        "amount": 350.0,
        "date": "2026-10-03",
        "payment_method": "Card",
        "category": "Entertainment",
        "confidence": 0.94
    },
    {
        "id": 4,
        "description": "Grocery shopping",
        "amount": 1200.0,
        "date": "2026-10-05",
        "payment_method": "UPI",
        "category": "Shopping",
        "confidence": 0.96
    },
    {
        "id": 5,
        "description": "College books",
        "amount": 750.0,
        "date": "2026-10-07",
        "payment_method": "Cash",
        "category": "Education",
        "confidence": 0.91
    },
    {
        "id": 6,
        "description": "Electricity bill",
        "amount": 1800.0,
        "date": "2026-10-10",
        "payment_method": "UPI",
        "category": "Bills",
        "confidence": 0.97
    },
    {
        "id": 7,
        "description": "Medicine",
        "amount": 450.0,
        "date": "2026-10-12",
        "payment_method": "Card",
        "category": "Healthcare",
        "confidence": 0.93
    },
    {
        "id": 8,
        "description": "Dinner",
        "amount": 500.0,
        "date": "2026-10-15",
        "payment_method": "UPI",
        "category": "Food",
        "confidence": 0.95
    }
]

budget = {
    "amount": 0.0,
    "month": ""
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
    keyword: str = ""
):
    result = expenses

    if category:
        result = [e for e in result if e["category"].lower() == category.lower()]

    if payment_method:
        result = [
            e for e in result
            if e["payment_method"].lower() == payment_method.lower()
        ]

    if month:
        result = [e for e in result if e["date"].startswith(month)]

    if keyword:
        result = [
            e for e in result
            if keyword.lower() in e["description"].lower()
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
def dashboard(month: str = ""):
    selected = expenses

    if month:
        selected = [e for e in expenses if e["date"].startswith(month)]

    total_amount = sum(e["amount"] for e in selected)

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

    forecast = {
        "current_spending": round(total_amount, 2),
        "average_spending_per_active_day": 0,
        "forecasted_30_day_spending": 0,
        "message": "Not enough data for a forecast."
    }

    if daily_totals:
        average_daily = total_amount / len(daily_totals)
        forecasted = average_daily * 30

        forecast["average_spending_per_active_day"] = round(average_daily, 2)
        forecast["forecasted_30_day_spending"] = round(forecasted, 2)

        if budget["amount"] > 0 and forecasted > budget["amount"]:
            forecast["message"] = "Current spending rate may exceed the budget."
        else:
            forecast["message"] = "Current spending rate is within the budget."

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
        "expenses": selected
    }


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
