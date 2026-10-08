import pandas as pd
from datetime import datetime


def clean_merchant_name(description):
    """
    Extract a clean merchant or subscription name from description.
    Example: 'Netflix subscription plan' -> 'Netflix'
    """
    desc_lower = str(description).lower().strip()

    # Common recurring subscription keywords
    keywords = [
        "netflix", "spotify", "electricity", "rent", "broadband",
        "wifi", "gym", "water bill", "mobile recharge", "hotstar",
        "prime", "youtube", "cloud storage", "newspaper", "gas bill"
    ]

    for kw in keywords:
        if kw in desc_lower:
            return kw.title()

    # If no keyword matches, use first two words
    words = description.strip().split()
    if len(words) >= 2:
        return f"{words[0]} {words[1]}".title()
    elif words:
        return words[0].title()
    return "Unknown"


def detect_recurring_expenses(expenses):
    """
    Simple and beginner-friendly Recurring Expense Detection.
    Finds expenses that repeat with similar amounts and regular time intervals.
    """
    if not expenses or len(expenses) < 2:
        return []

    # 1. Convert expenses list into a simple pandas DataFrame
    df = pd.DataFrame(expenses)

    # Ensure required columns exist
    if "description" not in df.columns or "amount" not in df.columns or "date" not in df.columns:
        return []

    # 2. Add a clean merchant name column
    df["merchant"] = df["description"].apply(clean_merchant_name)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Drop rows with invalid dates or 0 amount
    df = df.dropna(subset=["date"])
    df = df[df["amount"] > 0]

    # Sort by date
    df = df.sort_values(by="date")

    recurring_list = []

    # 3. Group expenses by merchant name
    grouped = df.groupby("merchant")

    for merchant, group in grouped:
        count = len(group)

        # Check if the merchant appears at least 2 times OR is a known subscription
        known_subscriptions = ["Netflix", "Spotify", "Electricity", "Rent", "Broadband", "Gym", "Mobile Recharge"]
        is_known = merchant in known_subscriptions

        if count >= 2 or (count >= 1 and is_known):
            amounts = group["amount"].tolist()
            dates = group["date"].tolist()

            avg_amount = round(sum(amounts) / len(amounts), 2)
            last_amount = round(amounts[-1], 2)
            category = group["category"].iloc[-1] if "category" in group.columns else "General"

            # 4. Determine frequency based on days between dates
            frequency = "Monthly"  # Default common frequency

            if len(dates) >= 2:
                # Calculate average difference in days between consecutive payments
                day_diffs = []
                for i in range(1, len(dates)):
                    diff = (dates[i] - dates[i - 1]).days
                    day_diffs.append(diff)

                avg_days = sum(day_diffs) / len(day_diffs)

                if 5 <= avg_days <= 9:
                    frequency = "Weekly"
                elif 25 <= avg_days <= 35:
                    frequency = "Monthly"
                elif 80 <= avg_days <= 100:
                    frequency = "Quarterly"
                elif avg_days >= 330:
                    frequency = "Yearly"
                else:
                    frequency = "Monthly"

            recurring_list.append({
                "merchant": merchant,
                "amount": last_amount,
                "avg_amount": avg_amount,
                "frequency": frequency,
                "category": category,
                "count": count,
                "last_date": dates[-1].strftime("%Y-%m-%d")
            })

    # Sort by amount descending
    recurring_list.sort(key=lambda x: x["amount"], reverse=True)
    return recurring_list
