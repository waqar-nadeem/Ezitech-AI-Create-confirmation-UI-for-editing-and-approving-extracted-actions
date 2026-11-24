# Task 3 Submission Note

**What I did**

I created a complete Streamlit confirmation UI (`app.py`) that:

- Loads four realistic sample logistics actions into `st.session_state` (simulating the output of Task 2).
- Renders an independent editable form for every pending action with fields for action type, shipment ID, priority, location, requested-by, deadline and description.
- Provides **Confirm / Save** and **Discard** buttons that update session state immediately.
- Displays all confirmed actions and offers a one-click **Download confirmed actions (JSON)** button.
- Keeps the entire state alive across Streamlit reruns for the duration of the browser session.
- Includes a sidebar with live metrics and a “Reset to sample data” button so testing is easy.

**Why**

The mentor checklist requires three concrete behaviours: editable forms with save/discard, JSON download of confirmed actions, and session-state persistence. The form-per-action + explicit buttons pattern satisfies the first two points cleanly; storing everything in `st.session_state` satisfies the third. Hard-coding sample actions lets the UI be reviewed independently of the still-in-progress transcription and LLM steps.

**How to verify**

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then edit a few fields, press Confirm / Save or Discard, and use the download button. Session state survives ordinary page interactions.

**Repository contents**

- `app.py` – the working Streamlit application  
- `requirements.txt` – single dependency (streamlit)  
- `README.md` – full documentation and design rationale  
- `SUBMISSION_NOTE.md` – this short note  
- `.gitignore`
