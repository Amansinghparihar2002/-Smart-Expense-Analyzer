# chatbot.py
# Gemini AI Chatbot integration for Smart Expense Analyzer
# Uses google-genai (2025/2026 SDK) with gemini-2.5-flash model

from google import genai
import os
from dotenv import load_dotenv

# Load GEMINI_API_KEY from your .env file (create one if you don't have it)
load_dotenv()

# Client is created lazily so importing this module never fails without an API key.
_client = None

def _get_client():
    """Returns a cached Gemini client, creating it on first call."""
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _client


def build_system_context(insights_list, summary_stats):
    """
    Builds a detailed context string containing:
    - Overall expense summary
    - Category-level statistics
    - Monthly statistics
    - Generated insights
    """

    # ---------------------------------------------------------
    # INSIGHTS
    # ---------------------------------------------------------
    insight_lines = "\n".join(
        f"  - [{i['type'].upper()}] {i['message']}"
        for i in insights_list
    )

    # ---------------------------------------------------------
    # CATEGORY DATA
    # ---------------------------------------------------------
    category_data = summary_stats.get("category_data", {})

    category_lines = []

    for category, data in category_data.items():
        category_lines.append(
            f"  - {category}: "
            f"Total Spend = ₹{data.get('total_spend', 0):,.0f}, "
            f"Transactions = {data.get('transactions', 0):,}, "
            f"Average Transaction = ₹{data.get('avg_amount', 0):,.0f}, "
            f"Percentage of Total = {data.get('percentage', 0):.1f}%"
        )

    category_context = "\n".join(category_lines)

    # ---------------------------------------------------------
    # MONTHLY DATA
    # ---------------------------------------------------------
    monthly_data = summary_stats.get("monthly_data", {})

    monthly_lines = []

    for month, data in monthly_data.items():
        monthly_lines.append(
            f"  - {month}: "
            f"Total Spend = ₹{data.get('total_spend', 0):,.0f}, "
            f"Transactions = {data.get('transactions', 0):,}"
        )

    monthly_context = "\n".join(monthly_lines)

    # ---------------------------------------------------------
    # COMPLETE AI CONTEXT
    # ---------------------------------------------------------
    context = f"""
You are a smart, friendly financial advisor assistant embedded inside
a personal expense analysis dashboard called "Smart Expense Analyzer".

You have access to the user's ACTUAL expense data.

IMPORTANT RULES:
1. Use ONLY the data provided below.
2. Never invent numbers.
3. When the user asks for a category amount, use the CATEGORY DATA section.
4. When the user asks for monthly spending, use the MONTHLY DATA section.
5. Always give the exact amount when the data provides it.
6. Use ₹ for currency.
7. If the requested information is not available, clearly say that it is not available.
8. Be concise and practical.
9. You can perform calculations using the provided numbers.
10. For category comparisons, subtract the relevant category amounts.
11. For percentage questions, use the percentage provided in CATEGORY DATA.
12. For savings calculations, calculate the requested percentage of the relevant category spending.
13. For category rankings, sort categories by Total Spend.
14. For monthly rankings, compare Total Spend in MONTHLY DATA.
15. For transaction rankings, compare Transactions in CATEGORY DATA.
16. Show the calculation when the user specifically asks for it.
17. Never invent income, salary, rent, savings, investments, or other information not present in the dataset.
18. If information is unavailable, clearly say that it is not available.

==================================================
OVERALL EXPENSE SUMMARY
==================================================

Total Spend:
₹{summary_stats.get('total_spend', 0):,.0f}

Total Transactions:
{summary_stats.get('n_txns', 0):,}

Average Transaction:
₹{summary_stats.get('avg_txn', 0):,.0f}

Top Category:
{summary_stats.get('top_cat', 'N/A')}

Months Covered:
{summary_stats.get('n_months', 0)}

Financial Health:
{summary_stats.get('health_score', 0)}/100
({summary_stats.get('health_label', 'N/A')})

==================================================
CATEGORY DATA
==================================================

{category_context}

==================================================
MONTHLY DATA
==================================================

{monthly_context}

==================================================
SMART INSIGHTS
==================================================

{insight_lines}

==================================================
YOUR JOB
==================================================

Answer questions about the user's expenses using the data above.

Examples:

If the user asks:
"What is the total amount spent on Bills?"

Look inside CATEGORY DATA and return the exact
Bills Total Spend value.

If the user asks:
"How many Bills transactions do I have?"

Look inside CATEGORY DATA and return the Bills transaction count.

If the user asks:
"What percentage of my spending is Food?"

Look inside CATEGORY DATA and return the Food percentage.

If the user asks:
"Which month had the highest spending?"

Compare the Total Spend values in MONTHLY DATA.

If the user asks:
"How can I reduce my spending?"

Use the CATEGORY DATA and SMART INSIGHTS to provide practical advice.

Keep normal answers around 2–5 sentences.
Use bullet points when useful.
""".strip()

    return context


def get_chatbot_response(user_input, insights_list, summary_stats, chat_history=None):
    """
    Sends the user's question + full expense context to Gemini and returns a response.

    Parameters:
    - user_input   : string — what the user typed
    - insights_list: list of insight dicts from generate_insights()
    - summary_stats: dict with expense summary numbers
    - chat_history : list of {"role": "user"/"model", "parts": "..."} dicts
                     for multi-turn conversation (optional)

    Returns:
    - response_text: string from Gemini
    """
    if not user_input or not user_input.strip():
        return "Please type a question first."

    # Check API key is set
    if not os.getenv("GEMINI_API_KEY"):
        return (
            "⚠️ Gemini API key not found.\n\n"
            "Please create a `.env` file in the project folder with:\n"
            "```\nGEMINI_API_KEY=your_key_here\n```\n"
            "Get a free key at: https://aistudio.google.com/app/apikey"
        )

    # Build the system context from live data
    system_context = build_system_context(insights_list, summary_stats)

    # Build the prompt
    if not chat_history:
        full_message = f"""
{system_context}

---

User Question:
{user_input}
""".strip()
    else:
        # For now, include previous conversation as plain text.
        # This keeps compatibility with the current google-genai SDK.
        history_text = "\n".join(
            f"{turn.get('role', 'user').upper()}: {turn.get('parts', '')}"
            for turn in chat_history
        )

        full_message = f"""
{system_context}

=== PREVIOUS CONVERSATION ===
{history_text}

=== CURRENT USER QUESTION ===
{user_input}
""".strip()

    try:
        response = _get_client().models.generate_content(
            model="gemini-2.5-flash",
            contents=full_message,
        )

        return response.text

    except Exception as e:
        error_msg = str(e)

        # Friendly error messages for common issues
        if "API_KEY" in error_msg.upper() or "401" in error_msg:
            return "❌ Invalid API key. Please check your GEMINI_API_KEY in the .env file."
        elif "QUOTA" in error_msg.upper() or "429" in error_msg:
            return "❌ API quota exceeded. Please wait a moment and try again."
        elif "SAFETY" in error_msg.upper():
            return "⚠️ The response was blocked by safety filters. Please rephrase your question."
        else:
            return f"❌ Error communicating with Gemini: {error_msg}"


def get_suggested_questions(top_cat, health_label):
    """
    Returns a list of context-aware suggested starter questions
    based on the user's actual spending data.
    """
    return [
        f"Why is my {top_cat} spending so high?",
        f"How can I improve my {health_label} financial health score?",
        "What are my top 3 areas to cut spending?",
        "Am I overspending compared to typical benchmarks?",
        "Give me a monthly savings plan based on my data.",
        "Which category should I focus on reducing first?",
    ]
