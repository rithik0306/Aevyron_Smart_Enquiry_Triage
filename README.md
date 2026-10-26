# Aevyron Smart Enquiry Triage

Fresh Streamlit starter app with Aevyron branding, dark forest-green UI, enquiry capture, keyword-based categories, priority suggestions, Needs Review, inbox filters, and CSV export.

## Run locally (Windows / VS Code)

Open this folder in VS Code, then run in the terminal:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

If PowerShell blocks activation, use Command Prompt:

```bat
.venv\Scripts\activate.bat
pip install -r requirements.txt
streamlit run app.py
```

## Deploy
Push this folder to a **new** GitHub repository, then create a new app in Streamlit Community Cloud using `app.py`.

## Important
- Keyword rules only; this is not a trained AI model.
- No email is sent by this app.
- CSV storage is for testing. Hosted local files may not persist across restarts or redeployments.
- Keep the old Nexonic app unchanged until this new app is tested.
