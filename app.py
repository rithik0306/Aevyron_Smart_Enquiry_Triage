
import re
from pathlib import Path

import pandas as pd
import streamlit as st


# --------------------------------------------------
# 1. APP CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Nexonic | Smart Enquiry Triage",
    page_icon="📩",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------------------------------------
# NEXONIC BRANDING AND UI STYLES
# --------------------------------------------------
st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
      :root { --nx-bg: #100D24; --nx-purple: #8B5CF6; --nx-cyan: #45E5E0; --nx-text: #F5F3FF; }
      .stApp { background: linear-gradient(135deg, #100D24 0%, #17112F 55%, #100D24 100%); color: var(--nx-text); }
      html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
      .block-container { max-width: 1120px; padding-top: 2rem; padding-bottom: 3rem; }
      .nx-header { display:flex; align-items:center; gap:16px; padding:20px 24px; margin-bottom:22px;
        border:1px solid rgba(139,92,246,.35); border-radius:22px;
        background:linear-gradient(115deg, rgba(139,92,246,.17), rgba(69,229,224,.055)); }
      .nx-logo { width:58px; height:58px; flex:0 0 58px; }
      .nx-brand { font-size:27px; font-weight:800; letter-spacing:3px; color:#fff; line-height:1.2; }
      .nx-tagline { color:#B7A0FF; font-size:13px; margin-top:5px; letter-spacing:.3px; }
      .nx-title { font-size:30px; font-weight:750; color:#fff; margin:8px 0 4px; }
      .nx-subtitle { color:#C5BEDB; font-size:15px; margin-bottom:20px; }
      [data-testid="stForm"], [data-testid="stDataFrame"], [data-testid="stMetric"] {
        border:1px solid rgba(183,160,255,.18); border-radius:16px; }
      [data-testid="stForm"] { background:rgba(255,255,255,.035); padding:22px; }
      [data-testid="stMetric"] { background:rgba(139,92,246,.10); padding:16px; }
      [data-testid="stMetricValue"] { color:#fff; }
      h1, h2, h3, p, label { color:var(--nx-text); }
      div.stButton > button, div.stFormSubmitButton > button, div.stDownloadButton > button {
        background:linear-gradient(90deg, #8B5CF6, #6D4AE8); color:white; border:0;
        border-radius:10px; font-weight:650; min-height:44px; }
      div.stButton > button:hover, div.stFormSubmitButton > button:hover, div.stDownloadButton > button:hover {
        border:1px solid #45E5E0; color:white; }
      [data-baseweb="input"] > div, [data-baseweb="textarea"] > div, [data-baseweb="select"] > div {
        background:#19142F; border-color:#494064; border-radius:10px; }
      [data-testid="stAlert"] { border-radius:12px; }
      hr { border-color:rgba(183,160,255,.2); }
      .nx-footer { text-align:center; color:#A69BBF; font-size:12px; padding-top:12px; }
    </style>
    <div class="nx-header">
      <svg class="nx-logo" viewBox="0 0 100 100" role="img" aria-label="Nexonic connected-node logo">
        <g stroke="#45E5E0" stroke-width="3" fill="none" stroke-linecap="round">
          <path d="M20 50 L43 25 L70 37 L78 68 L48 78 Z M43 25 L48 78 M20 50 L70 37"/>
        </g>
        <g fill="#8B5CF6" stroke="#B7A0FF" stroke-width="2">
          <circle cx="20" cy="50" r="7"/><circle cx="43" cy="25" r="7"/>
          <circle cx="70" cy="37" r="7"/><circle cx="78" cy="68" r="7"/><circle cx="48" cy="78" r="7"/>
        </g>
      </svg>
      <div><div class="nx-brand">NEXONIC</div><div class="nx-tagline">Think smarter. Build beyond.</div></div>
    </div>
    <div class="nx-title">Smart Enquiry Triage</div>
    <div class="nx-subtitle">Organise customer enquiries, suggest priority, and prepare a reply for human review.</div>
    """,
    unsafe_allow_html=True
)

st.info(
    "Rule-based prototype — this is not a trained AI model. "
    "Review the category, priority, and draft reply before use."
)


# --------------------------------------------------
# 2. FILE CONFIGURATION
# --------------------------------------------------

DATA_FILE = Path("enquiries.csv")


# --------------------------------------------------
# 3. CATEGORY KEYWORDS
# --------------------------------------------------

CATEGORIES = {
    "Sales": [
        "price",
        "pricing",
        "cost",
        "buy",
        "purchase",
        "quote",
        "quotation",
        "plan",
        "product",
        "demo",
        "interested in",
        "features",
        "subscription"
    ],

    "Support": [
        "error",
        "issue",
        "problem",
        "not working",
        "help",
        "bug",
        "broken",
        "unable",
        "failed",
        "crash",
        "login",
        "can't access",
        "cannot access"
    ],

    "Billing": [
        "invoice",
        "payment",
        "refund",
        "charged",
        "billing",
        "receipt",
        "overcharged",
        "subscription fee"
    ]
}


# --------------------------------------------------
# 4. URGENCY KEYWORDS
# --------------------------------------------------

URGENT_KEYWORDS = [
    "urgent",
    "asap",
    "immediately",
    "critical",
    "outage",
    "system down",
    "blocked",
    "deadline today",
    "cannot work",
    "can't work"
]


# --------------------------------------------------
# 5. KEYWORD MATCHING FUNCTION
# --------------------------------------------------

def contains_keyword(text: str, keyword: str) -> bool:
    """
    Check whether a keyword or phrase appears in the text.
    Ignore uppercase/lowercase differences and avoid matching
    a keyword inside a larger word.
    """

    pattern = r"\b" + re.escape(keyword.lower()) + r"\b"

    return re.search(pattern, text.lower()) is not None


# --------------------------------------------------
# 6. ENQUIRY CATEGORISATION
# --------------------------------------------------

def categorise(text: str) -> str:
    """
    Categorise an enquiry using keyword rules.

    Return Needs Review if:
    - No category keywords match.
    - Multiple categories have the same highest score.
    """

    scores = {
        category: sum(
            1
            for keyword in keywords
            if contains_keyword(text, keyword)
        )
        for category, keywords in CATEGORIES.items()
    }

    highest_score = max(scores.values())

    # No matching category keywords.
    if highest_score == 0:
        return "Needs Review"

    # Find all categories with the highest score.
    winners = [
        category
        for category, score in scores.items()
        if score == highest_score
    ]

    # More than one category has the same highest score.
    if len(winners) > 1:
        return "Needs Review"

    return winners[0]


# --------------------------------------------------
# 7. PRIORITY SUGGESTION
# --------------------------------------------------

def suggest_priority(text: str) -> str:
    """
    Suggest High when explicit urgency keywords are present.
    Otherwise suggest Normal.

    This is a keyword-based suggestion, not an AI prediction.
    """

    if any(
        contains_keyword(text, keyword)
        for keyword in URGENT_KEYWORDS
    ):
        return "High"

    return "Normal"


# --------------------------------------------------
# 8. DRAFT REPLY GENERATION
# --------------------------------------------------

def draft_reply(category: str, customer_name: str) -> str:
    """
    Prepare a draft reply based on the selected category.
    The reply is a draft and should be reviewed before sending.
    """

    name = customer_name.strip() or "there"

    replies = {
        "Sales": (
            f"Hi {name}, thanks for your interest. We have received "
            "your enquiry and will share relevant product and pricing "
            "details after reviewing your requirements."
        ),

        "Support": (
            f"Hi {name}, thanks for reporting this. We have received "
            "your support enquiry and will review the details. If possible, "
            "please share the steps that led to the issue."
        ),

        "Billing": (
            f"Hi {name}, thanks for contacting us about billing. We have "
            "received your enquiry and will review the payment or invoice "
            "details before responding."
        ),

        "Needs Review": (
            f"Hi {name}, thanks for contacting us. Our team will review "
            "your message and route it to the right person before responding."
        )
    }

    return replies.get(
        category,
        f"Hi {name}, thanks for contacting us. Our team will review your enquiry."
    )


# --------------------------------------------------
# 9. LOAD EXISTING CSV DATA
# --------------------------------------------------

def load_enquiries() -> pd.DataFrame:
    """
    Load existing enquiries from the CSV file.
    Return an empty DataFrame if the file does not exist.
    """

    if DATA_FILE.exists():
        try:
            return pd.read_csv(DATA_FILE)
        except (pd.errors.EmptyDataError, pd.errors.ParserError):
            st.warning(
                "The existing CSV file could not be read. "
                "A new file will be created when you save an enquiry."
            )

    return pd.DataFrame()


# --------------------------------------------------
# 10. CUSTOMER ENQUIRY FORM
# --------------------------------------------------

st.subheader("📩  Customer Enquiry Form")

with st.form("enquiry_form"):

    customer_name = st.text_input(
        "Customer Name",
        placeholder="Enter customer name"
    )

    customer_email = st.text_input(
        "Customer Email",
        placeholder="customer@example.com"
    )

    message = st.text_area(
        "Customer Message",
        placeholder="Enter the customer's enquiry here..."
    )

    priority_choice = st.selectbox(
        "Priority",
        ["Auto-suggest", "Normal", "High"],
        index=0
    )

    submitted = st.form_submit_button(
        "Analyse and Save Enquiry",
        use_container_width=True
    )


# --------------------------------------------------
# 11. PROCESS AND SAVE ENQUIRY
# --------------------------------------------------

if submitted:

    if not customer_name.strip():
        st.error("Please enter the customer's name.")

    elif not customer_email.strip():
        st.error("Please enter the customer's email.")

    elif not message.strip():
        st.error("Please enter the customer's message.")

    else:
        # Determine category and suggested priority.
        category = categorise(message)
        suggested_priority = suggest_priority(message)

        # Use the automatic suggestion or manual selection.
        if priority_choice == "Auto-suggest":
            priority = suggested_priority
        else:
            priority = priority_choice

        # Create the enquiry record.
        record = {
            "customer_name": customer_name.strip(),
            "customer_email": customer_email.strip(),
            "message": message.strip(),
            "category": category,
            "priority": priority,
            "suggested_priority": suggested_priority,
            "status": (
                "Needs human review"
                if category == "Needs Review"
                else "Needs human review before sending reply"
            ),
            "draft_reply": draft_reply(
                category,
                customer_name
            )
        }

        # Save the enquiry to CSV while preserving previous records.
        try:
            existing_data = load_enquiries()

            new_record = pd.DataFrame([record])

            if existing_data.empty:
                updated_data = new_record
            else:
                # Keep existing columns and add new fields if needed.
                updated_data = pd.concat(
                    [existing_data, new_record],
                    ignore_index=True
                )

            updated_data.to_csv(DATA_FILE, index=False)

            st.success("Enquiry analysed and saved successfully!")

            # Show results.
            st.subheader("✨  Enquiry Analysis")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Category",
                    record["category"]
                )

            with col2:
                st.metric(
                    "Selected Priority",
                    record["priority"]
                )

            st.caption(
                f"Rule-based priority suggestion: "
                f"{record['suggested_priority']}"
            )

            if category == "Needs Review":
                st.warning(
                    "This message could not be categorised confidently "
                    "using the current keyword rules. Please review it manually."
                )

            st.write("**Review Status:**", record["status"])

            st.subheader("💬  Draft Reply")

            st.text_area(
                "Review this draft before sending",
                value=record["draft_reply"],
                height=150,
                key="latest_draft_reply"
            )

            st.caption(
                "The application does not send emails. "
                "Copy and review the draft before using it."
            )

        except (OSError, PermissionError) as error:
            st.error(
                f"Could not save the CSV file. "
                f"Check whether the file is open in Excel. Details: {error}"
            )


# --------------------------------------------------
# 12. DISPLAY SAVED ENQUIRIES
# --------------------------------------------------

st.divider()

st.subheader("🗂️  Saved Enquiries")

saved_data = load_enquiries()

if not saved_data.empty:

    st.dataframe(
        saved_data,
        use_container_width=True,
        hide_index=True
    )

    # Download the saved records.
    csv_data = saved_data.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Enquiries CSV",
        data=csv_data,
        file_name="nexonic_enquiries.csv",
        mime="text/csv",
        use_container_width=True
    )

else:
    st.info(
        "No enquiries have been saved yet. "
        "Submit the form above to create your first record."
    )


# --------------------------------------------------
# 13. FOOTER
# --------------------------------------------------

st.divider()

st.markdown(
    '<div class="nx-footer">NEXONIC &nbsp;•&nbsp; Think smarter. Build beyond. &nbsp;•&nbsp; Rule-based prototype — human review required.</div>',
    unsafe_allow_html=True
)
