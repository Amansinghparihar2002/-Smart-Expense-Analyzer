# 💰 Smart Expense Analyzer — with Gemini AI Financial Advisor

A professional Streamlit dashboard that turns your credit card CSV into a full
financial intelligence suite — with charts, a health score, smart insights,
and a **Gemini-powered AI chatbot** that answers questions about your spending.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📊 Key Metrics | Total spend, transactions, top category, averages |
| ❤️ Health Score | Rule-based 0–100 score (Poor / Average / Good / Excellent) |
| 📉 5 Chart Types | Bar, Donut, Trend, Budget vs Guideline, Top Transactions |
| 💡 Smart Insights | Overspending alerts, savings tips, balance detection |
| 🔍 Live Filters | Category multi-select + date range — all views update instantly |
| 📋 Category Table | Totals, counts, averages, % share |
| 🗂️ Raw Data Explorer | Sortable transaction viewer |
| 🤖 AI Chatbot | Gemini 2.5 Flash reads your data and answers financial questions |

---

## 🗂️ Project Structure

```
expense_analyzer/
│
├── app.py              # Main Streamlit app (Dashboard + AI Chatbot tabs)
├── chatbot.py          # Gemini AI integration and context builder
├── data_processing.py  # Cleaning, time features, filter logic
├── insights.py         # Smart insights + Financial Health Score
├── charts.py           # 5 chart functions (matplotlib + seaborn)
├── requirements.txt    # Python dependencies
├── .env.example        # Template for your API key
└── README.md           # This file
```

---

## ▶️ How to Run

### Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Add your Gemini API key
Create a file called `.env` in the project folder:
```
GEMINI_API_KEY=your_gemini_api_key_here
```
Get a **free** key at: https://aistudio.google.com/app/apikey

### Step 3 — Run the app
```bash
streamlit run app.py
```

### Step 4 — Load your data
Click **Load from Path** in the sidebar (path is pre-filled).

### Step 5 — Chat with the AI
Click the **🤖 AI Financial Advisor** tab and ask anything about your spending.

---

## 🤖 AI Chatbot — How It Works

The chatbot uses **Gemini 2.5 Flash** (via `google-genai` SDK).

When you load your data, the app automatically:
1. Runs all insights and computes your health score
2. Builds a rich context string with all your financial data
3. Injects this context into Gemini's first message
4. Maintains a **multi-turn conversation** — the AI remembers what it said

**Example questions you can ask:**
- *"Why is my Entertainment spending so high?"*
- *"How can I improve from Average to Good health score?"*
- *"Give me a monthly savings plan based on my data."*
- *"Which category should I cut first?"*
- *"Am I overspending compared to typical benchmarks?"*

---

## 📄 CSV Format

| Column     | Example       |
|------------|---------------|
| `Date`     | `29-Oct-14`   |
| `Exp Type` | `Bills`       |
| `Amount`   | `82475`       |

Extra columns (City, Gender, Card Type) are ignored automatically.

---

## ❤️ Health Score Logic

| Score | Label     |
|-------|-----------|
| 80–100 | Excellent |
| 60–79  | Good      |
| 40–59  | Average   |
| 0–39   | Poor      |

Deductions for categories exceeding spending guidelines. Bonus for diversity.

---

## 🛠️ Tech Stack

| Tool          | Purpose              |
|---------------|----------------------|
| Streamlit     | Web UI               |
| Pandas        | Data processing      |
| Matplotlib    | Charts               |
| Seaborn       | Chart styling        |
| NumPy         | Numerical utils      |
| google-genai  | Gemini AI chatbot    |
| python-dotenv | API key management   |
