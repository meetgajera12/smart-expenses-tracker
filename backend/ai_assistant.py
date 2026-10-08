from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()

model = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_retries=5,
    reasoning_effort="low"
)


def ask_expense_ai(expenses, question):

    if not expenses:
        return "There are no expenses to analyze."

    expense_text = ""

    for expense in expenses:
        expense_text = expense_text + (
            "Date: " + str(expense.get("date", "")) +
            ", Description: " + str(expense.get("description", "")) +
            ", Amount: ₹" + str(expense.get("amount", 0)) +
            ", Category: " + str(expense.get("category", "")) +
            ", Payment: " + str(expense.get("payment_method", "")) +
            "\n"
        )

    system_message = SystemMessage(
        content=f"""
You are a simple expense assistant.

Use ONLY the expense data provided below.

Answer the user's question using the available expense data.

Do not invent expenses, amounts, dates or categories.

If the requested information cannot be found, say:
"I could not find that information in your expenses."

Keep the answer short and clear.

Expense data:

{expense_text}
"""
    )

    human_message = HumanMessage(content=question)


    response = model.invoke([
        system_message,
        human_message
    ])

    return response.content
