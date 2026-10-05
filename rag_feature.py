from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel
from dotenv import load_dotenv


load_dotenv()


model = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_retries=5,
    reasoning_effort="low"
)


class QueAns(BaseModel):
    que: str
    ans: str


def get_answer(text, question):

    if not text:
        return "No bill text was found."

    system_message = SystemMessage(
        content=f"""
You are a bill question-answering assistant.

The following is the complete OCR text of a bill.

The OCR text may contain:
- broken lines
- incorrect spacing
- item names and prices on separate lines
- minor OCR mistakes

Understand the bill using the complete text.

Answer the user's question using ONLY the information
available in this bill.

Do not invent information.

If the answer cannot be found in the bill, return exactly:

I could not find the answer in this bill.

Complete bill text:

{text}
"""
    )

    human_message = HumanMessage(
        content=question
    )

    response = model.with_structured_output(
        QueAns
    ).invoke(
        [
            system_message,
            human_message
        ]
    )

    return response.ans