import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import re

ROOT = Path(__file__).parent
DATA = ROOT / "enquiries.csv"
st.set_page_config(page_title="Aevyron | Smart Enquiry Triage", page_icon="✳", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root{--bg:#0d0f0e;--panel:#141916;--line:#28352d;--green:#4ade80;--muted:#9aa89e}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}
.stApp{background:radial-gradient(ellipse at 75% 0%,rgba(46,139,87,.13),transparent 38%),var(--bg);color:#f3f7f4}
.block-container{max-width:1450px;padding-top:1.8rem;padding-bottom:3rem}
h1,h2,h3{font-family:'Space Grotesk',sans-serif!important;letter-spacing:-.035em}
[data-testid="stSidebar"]{background:#101612;border-right:1px solid var(--line)}
[data-testid="stMetric"]{background:linear-gradient(145deg,#17221a,#121714);border:1px solid var(--line);padding:16px;border-radius:16px}
[data-testid="stMetricLabel"]{color:var(--muted)!important}[data-testid="stMetricValue"]{color:var(--green)!important}
div[data-testid="stForm"]{background:#141b16;padding:22px;border:1px solid var(--line);border-radius:18px}
.stTextInput input,.stTextArea textarea,.stSelectbox div[data-baseweb="select"]{background:#0d130f!important;color:#f3f7f4!important;border-color:#34453a!important;border-radius:10px!important}
.stButton button,.stFormSubmitButton button{background:var(--green)!important;color:#082012!important;border:0!important;border-radius:10px!important;font-weight:700!important;min-height:2.6rem}
.eyebrow{color:var(--green);font-size:.76rem;font-weight:700;letter-spacing:.18em;text-transform:uppercase}
.hero{padding:28px;background:linear-gradient(115deg,rgba(28,65,43,.58),rgba(20,25,22,.8));border:1px solid #2c4835;border-radius:22px;margin:16px 0}
.muted{color:#aab9af}
.pill{display:inline-block;border:1px solid #315840;background:#102519;color:#86efac;padding:5px 10px;border-radius:999px;font-size:.75rem;font-weight:700}
</style>
""", unsafe_allow_html=True)

CATEGORIES = {
 "AI & Automation":["ai","automation","chatbot","machine learning","llm","workflow","agent","generative"],
 "Web Development":["website","web app","web development","frontend","backend","landing page","portal"],
 "Data & Analytics":["data","analytics","dashboard","power bi","tableau","reporting","sql","visualization"],
 "Cloud & DevOps":["cloud","aws","azure","gcp","devops","deployment","hosting","infrastructure"],
 "Mobile App Development":["mobile app","android","ios","flutter","react native","app development"],
 "Consulting":["consulting","strategy","audit","advice","consultation","discovery"]
}
HIGH = ["urgent","asap","immediately","critical","production down","blocked","today","deadline","security issue"]
MED = ["soon","this week","quotation","quote","proposal","pricing","budget","timeline","meeting","demo"]
LOW = ["just exploring","exploring","curious","information","learn more","future","not urgent"]

COLUMNS = ["id","created_at","name","email","company","service","message","category","suggested_category","priority","status","reason"]

def load_data():
    if not DATA.exists(): return pd.DataFrame(columns=COLUMNS)
    try: return pd.read_csv(DATA).fillna("")
    except Exception: return pd.DataFrame(columns=COLUMNS)

def triage(message, service):
    text = (message or "").lower().strip()
    if not text: return "Needs Review", "Unassigned", "Low", "No message provided."
    scores = {c: sum(term in text for term in terms) for c,terms in CATEGORIES.items()}
    if service in scores: scores[service] += 2
    ordered = sorted(scores.values(), reverse=True)
    best = max(scores, key=scores.get)
    ambiguous = scores[best] == 0 or (len(ordered)>1 and ordered[0] == ordered[1])
    category = "Needs Review" if ambiguous else best
    if any(x in text for x in HIGH): priority, reason = "High", "Urgency or risk wording detected."
    elif any(x in text for x in MED): priority, reason = "Medium", "Timing or buying-intent wording detected."
    else: priority, reason = "Low", "No strong urgency signal detected; confirm with requester."
    if ambiguous: reason += " Category is ambiguous or no service keywords matched."
    return category, best if ambiguous else category, priority, reason

def clean(x): return re.sub(r"\s+"," ",str(x or "")).strip()

with st.sidebar:
    st.markdown('<div class="eyebrow">AEVYRON / OPERATIONS</div>', unsafe_allow_html=True)
    st.markdown("## ✳ Aevyron")
    st.caption("Smart Enquiry Triage")
    page = st.radio("WORKSPACE", ["Overview","New enquiry","Enquiry inbox","How it works"])
    st.divider()
    st.markdown('<span class="pill">RULE-BASED ASSISTANCE</span>', unsafe_allow_html=True)
    st.caption("Suggestions use message keywords. This is not a trained AI model.")
    st.divider()
    st.caption("Think smarter. Build beyond.")

df = load_data()
if page == "Overview":
    st.markdown('<div class="eyebrow">ENQUIRY OPERATIONS / OVERVIEW</div>', unsafe_allow_html=True)
    st.title("Turn incoming enquiries into clear next steps.")
    st.markdown('<div class="hero"><span class="pill">SMART ENQUIRY TRIAGE</span><h2 style="margin-top:16px">Less sorting. More meaningful follow-up.</h2><p class="muted">Capture customer enquiries, get transparent category and priority suggestions, and flag ambiguous messages for human review — in one focused workspace.</p></div>', unsafe_allow_html=True)
    total=len(df); high=int((df["priority"]=="High").sum()) if total else 0
    review=int((df["category"]=="Needs Review").sum()) if total else 0
    opened=int((df["status"]=="Open").sum()) if total else 0
    a,b,c,d=st.columns(4); a.metric("Total enquiries",total); b.metric("High priority",high); c.metric("Needs review",review); d.metric("Open follow-ups",opened)
    st.markdown("### Recent enquiries")
    if total: st.dataframe(df.tail(5).iloc[::-1],use_container_width=True,hide_index=True)
    else: st.info("No enquiries saved yet. Choose **New enquiry** in the sidebar to get started.")

elif page == "New enquiry":
    st.markdown('<div class="eyebrow">CAPTURE / CLASSIFY / FOLLOW UP</div>', unsafe_allow_html=True)
    st.title("New enquiry")
    st.write("Suggestions are generated locally using transparent keyword rules.")
    with st.form("enquiry_form", clear_on_submit=False):
        x,y=st.columns(2)
        with x:
            name=st.text_input("Contact name *",placeholder="e.g. Priya Sharma")
            email=st.text_input("Work email *",placeholder="name@company.com")
            company=st.text_input("Company",placeholder="Company name")
        with y:
            service=st.selectbox("Service of interest",["Not specified",*CATEGORIES.keys()])
            status=st.selectbox("Follow-up status",["Open","In progress","Closed"])
        message=st.text_area("Enquiry message *",placeholder="Tell us what you need help with...",height=150)
        submitted=st.form_submit_button("Triage and save enquiry",use_container_width=True)
    if submitted:
        errors=[]
        if not clean(name): errors.append("Contact name is required.")
        if not re.match(r"^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$",email.strip()): errors.append("Enter a valid email address.")
        if not clean(message): errors.append("Enquiry message is required.")
        if errors:
            for e in errors: st.error(e)
        else:
            category,suggested,priority,reason=triage(message,service)
            record={"id":"AEV-"+datetime.now().strftime("%y%m%d%H%M%S"),"created_at":datetime.now().isoformat(timespec="seconds"),"name":clean(name),"email":email.strip(),"company":clean(company),"service":service,"message":clean(message),"category":category,"suggested_category":suggested,"priority":priority,"status":status,"reason":reason}
            pd.concat([load_data(),pd.DataFrame([record])],ignore_index=True).to_csv(DATA,index=False)
            st.session_state["last_result"]=record
            st.success("Enquiry triaged and saved to enquiries.csv.")
    if st.session_state.get("last_result"):
        r=st.session_state["last_result"]
        st.markdown("### Triage result")
        a,b,c=st.columns(3); a.metric("Suggested category",r["category"]); b.metric("Suggested priority",r["priority"]); c.metric("Follow-up status",r["status"])
        st.info(r["reason"])
        if r["category"]=="Needs Review": st.warning("Human review recommended. Initial category hint: "+r["suggested_category"])

elif page == "Enquiry inbox":
    st.markdown('<div class="eyebrow">OPERATIONS / INBOX</div>', unsafe_allow_html=True)
    st.title("Enquiry inbox")
    st.caption("Saved records are stored in enquiries.csv beside the app.")
    if df.empty: st.info("Inbox is empty. Create an enquiry first.")
    else:
        a,b,c=st.columns(3)
        cat=a.selectbox("Category",["All",*sorted(df["category"].astype(str).unique())])
        pri=b.selectbox("Priority",["All","High","Medium","Low"])
        status=c.selectbox("Status",["All",*sorted(df["status"].astype(str).unique())])
        view=df.copy()
        if cat!="All": view=view[view.category==cat]
        if pri!="All": view=view[view.priority==pri]
        if status!="All": view=view[view.status==status]
        st.caption(f"{len(view)} matching enquiry/enquiries")
        st.dataframe(view,use_container_width=True,hide_index=True)
        st.download_button("Download filtered enquiries (CSV)",view.to_csv(index=False).encode("utf-8"),"aevyron_enquiries.csv","text/csv")
        with st.expander("Update follow-up status"):
            chosen=st.selectbox("Enquiry ID",view["id"].astype(str).tolist())
            new_status=st.selectbox("New status",["Open","In progress","Closed"])
            if st.button("Save status change"):
                all_df=load_data(); all_df.loc[all_df.id.astype(str)==chosen,"status"]=new_status
                all_df.to_csv(DATA,index=False); st.success("Status updated."); st.rerun()
else:
    st.markdown('<div class="eyebrow">TRANSPARENCY / OPERATING NOTES</div>', unsafe_allow_html=True)
    st.title("How the triage works")
    st.markdown("""
**Category suggestion**  
The app checks for keywords related to AI & Automation, Web Development, Data & Analytics, Cloud & DevOps, Mobile App Development, and Consulting. If no category is clear or multiple categories tie, it flags the enquiry as **Needs Review**.

**Priority suggestion**
- **High:** urgency or risk terms such as “urgent”, “ASAP”, “critical”, or “production down”.
- **Medium:** purchase-intent or timing terms such as “proposal”, “pricing”, “this week”, or “demo”.
- **Low:** no strong urgency signal detected; a person should confirm the actual deadline and impact.

**Human review**  
Category and priority are suggestions, not decisions. Review the message before taking action.

**Storage and privacy**  
This starter app saves records to a local `enquiries.csv`. Hosted local files may not persist across restarts or redeployments. Use a persistent database and access controls before collecting real customer data.

**Limitation**  
This version uses keyword rules, not a trained machine-learning model or external LLM. It does not send emails or automatically contact customers.
""")
