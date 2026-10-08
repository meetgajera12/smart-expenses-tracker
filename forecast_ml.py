from sklearn.linear_model import LinearRegression


def ml_forecast_expenses(expense_list, budget_amount=0.0):
    """
    Simple and beginner-friendly Machine Learning Expense Forecasting.
    Uses Linear Regression to learn daily spending patterns and forecast future expenses.
    """
    if not expense_list:
        return {
            "current_spending": 0.0,
            "forecasted_30_day_spending": 0.0,
            "next_7_days_spending": 0.0,
            "average_spending_per_active_day": 0.0,
            "message": "Add expenses to generate an ML forecast."
        }

    # Step 1: Calculate total spending per day
    daily_totals = {}
    for item in expense_list:
        date_str = item.get("date", "")
        amount = float(item.get("amount", 0.0))
        daily_totals[date_str] = daily_totals.get(date_str, 0.0) + amount

    # Sort dates chronologically
    sorted_dates = sorted(daily_totals.keys())
    total_spent = sum(daily_totals.values())

    # Step 2: Prepare Training Data for ML
    # X = Day index [1], [2], [3]...
    # y = Cumulative spending up to that day
    X = []
    y = []
    running_total = 0.0

    for index, date_str in enumerate(sorted_dates, start=1):
        running_total += daily_totals[date_str]
        X.append([index])
        y.append(running_total)

    # Step 3: Train the Linear Regression ML Model
    ml_model = LinearRegression()
    ml_model.fit(X, y)

    # Step 4: Predict 30-Day Total Spending
    predicted_30 = float(ml_model.predict([[30]])[0])
    if predicted_30 < total_spent:
        predicted_30 = total_spent

    # Step 5: Predict Next 7 Days Additional Spending
    active_days_count = len(X)
    target_future_day = min(active_days_count + 7, 30)
    pred_next_7_total = float(ml_model.predict([[target_future_day]])[0])
    next_7_spending = max(0.0, pred_next_7_total - total_spent)

    # Step 6: Daily Spending Pace (Slope of regression line)
    daily_rate = float(ml_model.coef_[0])
    if daily_rate <= 0:
        daily_rate = total_spent / max(len(daily_totals), 1)

    # Step 7: Generate friendly forecast advice
    if budget_amount > 0:
        if predicted_30 > budget_amount:
            over = predicted_30 - budget_amount
            message = f"ML model predicts you may exceed your monthly budget by ₹{over:.2f}."
        else:
            remaining = budget_amount - predicted_30
            message = f"ML model predicts you will stay within budget with ₹{remaining:.2f} remaining."
    else:
        message = f"ML model predicts spending will reach ~₹{predicted_30:.2f} by month-end."

    return {
        "current_spending": round(total_spent, 2),
        "forecasted_30_day_spending": round(predicted_30, 2),
        "next_7_days_spending": round(next_7_spending, 2),
        "average_spending_per_active_day": round(daily_rate, 2),
        "message": message
    }
