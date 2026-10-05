import streamlit as st
import requests
import pandas as pd

BACKEND = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Smart Expense Management",
    page_icon="💰"
)

st.title("💰 Smart Expense Management")


# =========================
# ADD EXPENSE
# =========================

st.header("➕ Add Expense")

description = st.text_input("Description")
amount = st.number_input("Amount", min_value=0.0)
date = st.date_input("Date")

payment_method = st.selectbox(
    "Payment Method",
    ["Cash", "UPI", "Card", "Net Banking"]
)

if st.button("Add Expense"):

    data = {
        "description": description,
        "amount": amount,
        "date": str(date),
        "payment_method": payment_method
    }

    response = requests.post(
        BACKEND + "/expenses",
        json=data
    )

    if response.ok:
        result = response.json()

        st.success("Expense added")

        st.write("Category:", result["category"])
        st.write("Confidence:", result["confidence"])

    else:
        st.error(response.text)


# =========================
# BILL PHOTO
# =========================

st.header("🧾 Bill Photo")

file = st.file_uploader(
    "Upload Bill",
    type=["jpg", "jpeg", "png"]
)

question = st.text_input(
    "Ask something about this bill"
)

if st.button("Read Bill"):

    if file is None:

        st.warning("Please upload a bill")

    else:

        files = {
            "file": (
                file.name,
                file.getvalue(),
                file.type
            )
        }

        response = requests.post(
            BACKEND + "/expenses/bill-photo",
            files=files,
            params={
                "question": question
            }
        )

        if response.ok:

            result = response.json()

            st.success("Bill read successfully")

            # -----------------
            # BILL
            # -----------------

            st.subheader("Bill Details")

            bill = result["bill"]

            st.write("Merchant:", bill["merchant"])
            st.write("Amount:", bill["amount"])
            st.write("Date:", bill["date"])

            # -----------------
            # EXPENSE
            # -----------------

            st.subheader("Added Expense")

            expense = result["expense"]

            st.write("Description:", expense["description"])
            st.write("Amount:", expense["amount"])
            st.write("Category:", expense["category"])

            # -----------------
            # AI ANSWER
            # -----------------

            if result["rag_answer"]:

                st.subheader("🤖 Bill AI Answer")

                st.write(result["rag_answer"])

        else:

            st.error(response.text)


# =========================
# DASHBOARD
# =========================

st.header("📊 Dashboard")

month = st.text_input(
    "Month",
    "2026-10"
)

if st.button("Load Dashboard"):

    response = requests.get(
        BACKEND + "/dashboard",
        params={
            "month": month
        }
    )

    if response.ok:

        data = response.json()

        st.metric(
            "Total Expenses",
            data["total_expenses"]
        )

        st.metric(
            "Total Spending",
            f"₹{data['total_amount']}"
        )

        # Category chart

        st.subheader("Category Spending")

        category_data = pd.DataFrame({
            "Category": data["category_chart"]["labels"],
            "Amount": data["category_chart"]["values"]
        })

        if not category_data.empty:
            st.bar_chart(
                category_data.set_index("Category")
            )

        # Daily chart

        st.subheader("Daily Spending")

        daily_data = pd.DataFrame({
            "Date": data["daily_chart"]["dates"],
            "Amount": data["daily_chart"]["amounts"]
        })

        if not daily_data.empty:
            st.line_chart(
                daily_data.set_index("Date")
            )

        # Insights

        st.subheader("💡 Insights")

        for item in data["insights"]:
            st.write("•", item)

        # Budget

        st.subheader("💰 Budget")

        budget = data["budget"]

        st.write(
            "Budget:",
            f"₹{budget['amount']}"
        )

        st.write(
            "Spent:",
            f"₹{budget['spent']}"
        )

        st.write(
            "Remaining:",
            f"₹{budget['remaining']}"
        )

        st.write(
            "Status:",
            budget["status"]
        )

        # Forecast

        st.subheader("🔮 Forecast")

        forecast = data["forecast"]

        st.write(
            "Current Spending:",
            f"₹{forecast['current_spending']}"
        )

        st.write(
            "30 Day Forecast:",
            f"₹{forecast['forecasted_30_day_spending']}"
        )

        st.write(
            forecast["message"]
        )

        # Expenses

        st.subheader("📋 Expenses")

        if data["expenses"]:

            df = pd.DataFrame(data["expenses"])

            st.dataframe(
                df,
                use_container_width=True
            )

        else:

            st.info("No expenses found.")


# =========================
# AI ASSISTANT
# =========================

st.header("🤖 AI Expense Assistant")

que = st.text_input(
    "Ask about your expenses"
)

if st.button("Ask AI"):

    if que:

        response = requests.post(
            BACKEND + "/aiassistant",
            params={
                "que": que
            }
        )

        if response.ok:
            st.write(response.json())
        else:
            st.error(response.text)

    else:

        st.warning("Enter a question")