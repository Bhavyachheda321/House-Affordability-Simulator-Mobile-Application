"""
FinPlan India v4 — Gemini Conversational Onboarding
Structured chat that collects all required inputs and writes them to session state.
Gemini outputs a JSON block alongside each conversational response.
API key is read from st.secrets.
"""
import json
import re
import streamlit as st

# ── Gemini API call ───────────────────────────────────────────────────────────
def call_gemini(messages: list, system_prompt: str) -> str:
    """Call Gemini Flash via REST. Returns raw text response."""
    try:
        import urllib.request, json as _json
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
        except Exception:
            api_key = st.secrets.get("GEMINI_API_KEY", "")
        api_key = str(api_key).strip()
        if not api_key:
            return "ERROR: GEMINI_API_KEY not found in st.secrets."

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-1.5-flash:generateContent?key={api_key}"
        )

        # Build contents array from messages
        contents = []
        for m in messages:
            role = "user" if m["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": m["content"]}]})

        payload = _json.dumps({
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": contents,
            "generationConfig": {"temperature": 0.4, "maxOutputTokens": 1500},
        }).encode()

        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = _json.loads(resp.read())

        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"ERROR: {e}"


# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are FinPlan India's friendly financial planning assistant helping an Indian user set up their personalised financial plan.

Your job is to ask questions ONE AT A TIME in a warm, simple, jargon-free way.
When the user says they don't know something, look up the answer from your knowledge (e.g. average property appreciation in their city, current EPF rate, typical stamp duty) and tell them — then ask if they want to use that figure.

QUESTION SEQUENCE (ask in order, skip if already confirmed):
1. Current age
2. City (offer: Mumbai, Delhi NCR, Bengaluru, Pune, Hyderabad, Chennai, Kolkata, Ahmedabad, Other)
3. Marital status → if married, ask if spouse earns income
4. If spouse earns: spouse monthly take-home and their expected annual salary growth %
5. Monthly take-home salary (what lands in bank account after all deductions)
6. Expected annual salary growth % (promotions + increments)
7. Annual bonus (net of tax, 0 if none)
8. Tax regime (New or Old) — if unsure, explain simply and recommend
9. Monthly expenses (excluding rent) — if unsure, suggest 40–50% of take-home as a starting point
10. Monthly rent currently paid (0 if living with parents)
11. Does employer deduct EPF/PF from salary? → if yes: monthly PF deduction shown on payslip, and current EPF balance (tell them to check EPFO passbook on umang.gov.in or epfindia.gov.in)
12. Does employer contribute to NPS? → if yes: annual employer NPS amount
13. Current savings — ask about each: Mutual Funds/Stocks, PPF balance, Gold, Fixed Deposits, Emergency Fund. For each, user can say "none" or "I don't know"
14. Monthly SIP amount currently running
15. Any existing loans? → if yes: total outstanding, monthly EMI, interest rate %
16. Do you want to plan for buying a house? → if yes: target budget today, rough timeline (years from now)
17. Do you want to save for a wedding/marriage? → if yes: estimated cost today, years from now
18. Do you want to plan for a child's education? → if yes: estimated cost today, years from now
19. Target retirement age and desired monthly spending at retirement (in today's money)

RULES:
- Ask only ONE question per message.
- Keep each message under 80 words.
- Be warm and conversational — this is someone's financial future.
- When the user doesn't know: provide a sensible default from your knowledge and ask if they'd like to use it.
- Never use financial jargon without explaining it.
- After EACH user reply, output:
  1. Your conversational next question (plain text)
  2. On a new line: <<<JSON_START>>> then a JSON object of ALL confirmed values so far, then <<<JSON_END>>>

JSON keys to use (only include keys that have been confirmed):
{
  "age": integer,
  "city": string,
  "married": boolean,
  "has_spouse_income": boolean,
  "spouse_monthly_salary": number,
  "spouse_salary_growth": number,
  "monthly_salary": number,
  "salary_growth": number,
  "annual_bonus": number,
  "old_regime": boolean,
  "monthly_expenses": number,
  "rent_monthly": number,
  "epf_monthly": number,
  "epf_value": number,
  "employer_nps_annual": number,
  "mf_value": number,
  "stocks_value": number,
  "ppf_value": number,
  "gold_value": number,
  "fd_value": number,
  "has_emergency_fund": boolean,
  "emergency_fund_value": number,
  "sip_total_monthly": number,
  "has_loans_flag": boolean,
  "loans_outstanding": number,
  "loan_emi_monthly": number,
  "loan_interest_rate": number,
  "want_house": boolean,
  "house_budget": number,
  "house_years": number,
  "want_marriage_savings": boolean,
  "marriage_cost": number,
  "marriage_years": number,
  "want_child_education": boolean,
  "child_education_cost": number,
  "child_education_years": number,
  "retirement_age": integer,
  "retirement_monthly_spend": number
}

Example response format:
That's great! Now, do you currently pay rent, or are you living with family?
<<<JSON_START>>>
{"age": 28, "city": "Bengaluru", "monthly_salary": 85000}
<<<JSON_END>>>
""".strip()


# ── JSON extraction ───────────────────────────────────────────────────────────
def extract_json_and_message(raw: str) -> tuple[str, dict]:
    """
    Split Gemini's response into (conversational_text, confirmed_values_dict).
    Returns (raw, {}) if no JSON block found.
    """
    pattern = r"<<<JSON_START>>>(.*?)<<<JSON_END>>>"
    match = re.search(pattern, raw, re.DOTALL)
    if not match:
        return raw.strip(), {}
    message  = raw[:match.start()].strip()
    json_str = match.group(1).strip()
    try:
        confirmed = json.loads(json_str)
    except json.JSONDecodeError:
        confirmed = {}
    return message, confirmed


# ── Apply confirmed values to session state ───────────────────────────────────
# Maps JSON key → (session_state_key, type_cast)
KEY_MAP = {
    "age":                    ("age",                    int),
    "city":                   ("city",                   str),
    "married":                ("married",                bool),
    "has_spouse_income":      ("has_spouse_income",      bool),
    "spouse_monthly_salary":  ("spouse_monthly_salary",  float),
    "spouse_salary_growth":   ("spouse_salary_growth",   float),
    "monthly_salary":         ("monthly_salary",         float),
    "salary_growth":          ("salary_growth",          float),
    "annual_bonus":           ("annual_bonus",           float),
    "old_regime":             ("old_regime",             bool),
    "monthly_expenses":       ("monthly_expenses",       float),
    "rent_monthly":           ("rent_monthly",           float),
    "epf_monthly":            ("epf_monthly",            float),
    "epf_value":              ("epf_value",              float),
    "employer_nps_annual":    ("employer_nps_annual",    float),
    "mf_value":               ("mf_value",               float),
    "stocks_value":           ("stocks_value",           float),
    "ppf_value":              ("ppf_value",              float),
    "gold_value":             ("gold_value",             float),
    "fd_value":               ("fd_value",               float),
    "has_emergency_fund":     ("has_emergency_fund",     bool),
    "emergency_fund_value":   ("emergency_fund_value",   float),
    "sip_total_monthly":      ("sip_total_monthly",      float),
    "has_loans_flag":         ("has_loans_flag",         bool),
    "loans_outstanding":      ("loans_outstanding",      float),
    "loan_emi_monthly":       ("loan_emi_monthly",       float),
    "loan_interest_rate":     ("loan_interest_rate",     float),
    "want_house":             ("want_house",             bool),
    "house_budget":           ("house_budget",           float),
    "house_years":            ("house_years",            int),
    "want_marriage_savings":  ("want_marriage_savings",  bool),
    "marriage_cost":          ("marriage_cost",          float),
    "marriage_years":         ("marriage_years",         int),
    "want_child_education":   ("want_child_education",   bool),
    "child_education_cost":   ("child_education_cost",   float),
    "child_education_years":  ("child_education_years",  int),
    "retirement_age":         ("retirement_age",         int),
    "retirement_monthly_spend":("retirement_monthly_spend", float),
}


def apply_confirmed_to_session(confirmed: dict):
    """Write all confirmed Gemini values into Streamlit session state."""
    for json_key, (ss_key, cast) in KEY_MAP.items():
        if json_key in confirmed and confirmed[json_key] is not None:
            try:
                val = cast(confirmed[json_key])
                st.session_state[ss_key] = val
            except (TypeError, ValueError):
                pass
    # Derive city-specific defaults (lazy import to avoid Cloud import errors)
    try:
        from pages_content.calculations import CITY_PROPERTY_APPRECIATION, CITY_LIFESTYLE_INFLATION
        city = st.session_state.get("city", "Other")
        if city in CITY_PROPERTY_APPRECIATION:
            st.session_state["property_appr_rate"] = CITY_PROPERTY_APPRECIATION[city]
        if city in CITY_LIFESTYLE_INFLATION:
            st.session_state["lifestyle_inflation"] = CITY_LIFESTYLE_INFLATION[city]
    except Exception:
        pass


# ── Completeness check ────────────────────────────────────────────────────────
REQUIRED_KEYS = [
    "age", "monthly_salary", "monthly_expenses", "retirement_age",
    "retirement_monthly_spend",
]

def is_onboarding_complete(confirmed: dict) -> bool:
    return all(confirmed.get(k) is not None and confirmed.get(k) != 0
               for k in REQUIRED_KEYS)


# ── Render chat UI ────────────────────────────────────────────────────────────
def render():
    s = st.session_state

    # Initialise chat state
    if "gemini_chat_history" not in s:
        s["gemini_chat_history"] = []
    if "gemini_confirmed" not in s:
        s["gemini_confirmed"] = {}
    if "gemini_onboarding_done" not in s:
        s["gemini_onboarding_done"] = False

    # Opening message on first load
    if not s["gemini_chat_history"]:
        opening = (
            "👋 Hi! I'm your FinPlan India assistant. I'll ask you a few questions "
            "to build your personalised financial plan — takes about 5 minutes.\n\n"
            "Let's start with the basics. **How old are you?**"
        )
        s["gemini_chat_history"].append({"role": "assistant", "content": opening})

    # ── Chat display ──────────────────────────────────────────────────────────
    chat_container = st.container()
    with chat_container:
        for msg in s["gemini_chat_history"]:
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(msg["content"])

    # ── Completion check ──────────────────────────────────────────────────────
    if is_onboarding_complete(s["gemini_confirmed"]):
        st.success("✅ All key details collected! Review below and click **Review & Edit my details** to verify before we build your plan.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Review & Edit my details", type="primary", use_container_width=True):
                apply_confirmed_to_session(s["gemini_confirmed"])
                s["step"] = 1   # Go to guided form for review
                s["mode"] = "form"
                st.rerun()
        with col2:
            if st.button("🔄 Start over", use_container_width=True):
                s["gemini_chat_history"] = []
                s["gemini_confirmed"] = {}
                st.rerun()
        return

    # ── Input box ─────────────────────────────────────────────────────────────
    user_input = st.chat_input("Type your answer…")

    if user_input:
        # Append user message
        s["gemini_chat_history"].append({"role": "user", "content": user_input})

        # Build messages list for API (exclude opening assistant message from system)
        api_messages = [
            m for m in s["gemini_chat_history"]
            if not (m["role"] == "assistant" and "I'm your FinPlan India assistant" in m["content"])
        ]
        # Add opening context as first user message if empty
        if not api_messages:
            api_messages = [{"role": "user", "content": user_input}]

        with st.spinner(""):
            raw = call_gemini(api_messages, SYSTEM_PROMPT)

        if raw.startswith("ERROR:"):
            st.error(raw)
            return

        message_text, confirmed = extract_json_and_message(raw)

        # Merge into cumulative confirmed dict
        s["gemini_confirmed"].update(confirmed)

        # Append assistant reply (without the JSON block)
        s["gemini_chat_history"].append({"role": "assistant", "content": message_text})
        st.rerun()
