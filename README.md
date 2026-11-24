# CargoLink Logistics – Voice Note Assistant  
Confirmation UI for Editing & Approving Extracted Actions

**Intern:** Waqar Nadeem  
**Client:** CargoLink Logistics  
**Technology:** Artificial Intelligence / Streamlit  
**Level:** Advanced  

---

### What this task delivers

An interactive Streamlit page that:

1. Loads a list of extracted logistics actions into `st.session_state`.
2. Renders an editable form for **each** action (action type, shipment ID, priority, location, requested-by, deadline, description).
3. Provides **Confirm / Save** and **Discard** buttons that update session state.
4. Lets the user download the final confirmed list as a clean `.json` file.
5. Keeps all state alive across Streamlit reruns for the lifetime of the browser session.

This is the third building block of the end-to-end voice-note pipeline:

| Task | Focus |
|------|--------|
| 1 | Whisper transcription pipeline |
| 2 | LLM-driven action extraction (function calling) |
| **3** | **Confirmation UI (this repo)** |
| 4 | Accuracy evaluation dashboard (WER) |
| 5 | Secure CI/CD + hand-over package |

---

### How to run locally

```bash
# 1. Clone / enter the repo
cd cargolink-voice-assistant-task3

# 2. Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the app
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

### What you will see

- **Pending actions** – each action appears as a card with editable fields.
- **Confirm / Save** – moves the (possibly edited) action into the confirmed list and marks it with a timestamp.
- **Discard** – removes the action from the pending list.
- **Confirmed actions** section – expandable JSON view of everything already approved.
- **Download confirmed actions (JSON)** – produces a timestamped file ready for downstream systems.
- Sidebar metrics + a **Reset to sample data** button for easy testing.

---

### Design decisions & why they matter

| Decision | Rationale |
|----------|-----------|
| `st.session_state` for the action lists | Required by the brief; survives every widget interaction and page rerun inside the same browser tab. |
| One `st.form` per action | Prevents the whole page from re-running on every keystroke; only submits when the user clicks Save or Discard. |
| Explicit Confirm / Discard buttons | Matches the mentor checklist (“save and discard buttons”). |
| `st.download_button` with in-memory JSON | No server-side file write needed; the user receives a clean download immediately. |
| Sample actions hard-coded | Lets the UI be tested independently of Task 1 & 2. In production the list would be injected from the LLM extraction step. |
| Deep-copy of sample data on init | Guarantees the original sample is never mutated. |

---

### Session-state keys used

| Key | Purpose |
|-----|---------|
| `actions` | Full list of actions that entered the confirmation stage |
| `confirmed_actions` | Actions the user has approved (downloadable) |
| `deleted_ids` | IDs of discarded actions |
| `edit_buffers` | Temporary working copy of each pending action while the user is editing |

---

### Mentor checklist mapping

| Criterion | How it is satisfied |
|-----------|---------------------|
| Editable form appears for each action with save and discard buttons | `render_action_card()` creates a form + Confirm/Save + Discard for every pending item |
| Confirmed actions are saved to a JSON file downloadable by the user | `st.download_button` serialises `st.session_state.confirmed_actions` |
| Session state persists across page reloads during the same session | All data lives in `st.session_state`; Streamlit keeps it for the lifetime of the WebSocket session |

---

### Project structure

```
cargolink-voice-assistant-task3/
├── app.py              # Main Streamlit application
├── requirements.txt    # streamlit
└── README.md           # This file
```

---

### Short note on what I did and why

I built a focused Streamlit confirmation UI that takes a list of logistics actions (simulated from the previous LLM extraction task), stores them in session state, and gives the user a clean way to edit, confirm or discard each one.  

The form-per-action pattern keeps the UI responsive and makes the Save/Discard intent explicit. Confirmed actions are immediately available for download as JSON so the next stage of the pipeline (or a human coordinator) can consume them without further processing.  

Everything is self-contained so the mentor can run `streamlit run app.py` and verify the three required behaviours in under a minute.

---

*Ezitech Software House – CargoLink Logistics internship · Task 3*
