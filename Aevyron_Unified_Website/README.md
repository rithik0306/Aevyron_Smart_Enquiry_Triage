# Aevyron Unified Website + Triage Prototype

## What's included
- `index.html`: unified Aevyron company website with all eight agreed products in one Products section.
- `triage_app/`: the current Streamlit Smart Enquiry Triage prototype source, requirements, and the uploaded CSV sample.

## Product status
- **Aevyron Triage**: current keyword-rule-based Streamlit prototype.
- **Aevyron Studio**: planned custom software creation service.
- **Aevyron FSM**: planned Field Service Management product.
- **Aevyron Insights, Flow, Assist, Invoice, Sites**: planned products/services.
- Aevyron Leads is intentionally excluded.

## Preview the website
Open `index.html` in a browser. The website is static HTML/CSS/JavaScript.

## Run the Triage prototype locally
From the `triage_app` directory:
```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```
Using `.venv\Scripts\python.exe` avoids needing to activate the virtual environment in PowerShell.

## Important integration notes
The website's Triage section opens the existing Streamlit deployment in a new tab. The Streamlit app is not yet embedded into or migrated to the static website because it has its own Python runtime and CSV-based storage. For a truly single-origin product experience, the app needs a backend deployment and integration plan.
The Streamlit app uses keyword rules, not a trained AI model. CSV storage is for testing and may not persist on hosted restarts/redeployments. Do not use it for sensitive production customer data without authentication, access controls, and persistent storage.
Contact and demo forms retain the existing FormSubmit-based behavior. Delivery depends on the email address being verified/configured with FormSubmit.
