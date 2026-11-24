"""
CargoLink Logistics - Voice Note Assistant
Task 3: Confirmation UI for editing and approving extracted actions

This Streamlit app displays extracted logistics actions, allows users to
edit fields, confirm or discard each action, and download the final
confirmed list as JSON. Session state keeps the data across reruns.
"""

import json
from datetime import datetime
from typing import Any

import streamlit as st

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="CargoLink – Action Confirmation",
    page_icon="📦",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Sample extracted actions (simulates output from Task 2 LLM extraction)
# In a full pipeline these would come from the transcription + LLM step.
# ---------------------------------------------------------------------------
SAMPLE_ACTIONS: list[dict[str, Any]] = [
    {
        "id": "act-001",
        "action_type": "reschedule_delivery",
        "description": "Reschedule delivery for shipment SH-45821 to tomorrow 14:00 due to traffic delay on M2 motorway.",
        "shipment_id": "SH-45821",
        "priority": "high",
        "location": "Lahore warehouse → Islamabad hub",
        "requested_by": "Driver Ahmed",
        "deadline": "2026-11-25 14:00",
        "status": "pending",
    },
    {
        "id": "act-002",
        "action_type": "update_status",
        "description": "Mark shipment SH-39210 as delivered. Customer signature collected at gate 3.",
        "shipment_id": "SH-39210",
        "priority": "medium",
        "location": "Karachi Port – Gate 3",
        "requested_by": "Coordinator Sana",
        "deadline": "2026-11-24 18:00",
        "status": "pending",
    },
    {
        "id": "act-003",
        "action_type": "assign_driver",
        "description": "Assign backup driver Bilal to route R-17 because primary driver reported sick leave.",
        "shipment_id": "SH-50112",
        "priority": "high",
        "location": "Faisalabad depot",
        "requested_by": "Ops Manager Imran",
        "deadline": "2026-11-24 22:00",
        "status": "pending",
    },
    {
        "id": "act-004",
        "action_type": "request_documentation",
        "description": "Request updated customs clearance papers for container CT-8891 before evening departure.",
        "shipment_id": "CT-8891",
        "priority": "critical",
        "location": "Port Qasim",
        "requested_by": "Customs Liaison Farah",
        "deadline": "2026-11-24 16:30",
        "status": "pending",
    },
]

ACTION_TYPE_OPTIONS = [
    "reschedule_delivery",
    "update_status",
    "assign_driver",
    "request_documentation",
    "report_incident",
    "other",
]

PRIORITY_OPTIONS = ["critical", "high", "medium", "low"]


# ---------------------------------------------------------------------------
# Session-state helpers
# ---------------------------------------------------------------------------
def init_session_state() -> None:
    """Initialise session keys once per browser session."""
    if "actions" not in st.session_state:
        # Deep copy so we never mutate the module-level sample
        st.session_state.actions = [dict(a) for a in SAMPLE_ACTIONS]
    if "confirmed_actions" not in st.session_state:
        st.session_state.confirmed_actions = []
    if "deleted_ids" not in st.session_state:
        st.session_state.deleted_ids = set()
    if "edit_buffers" not in st.session_state:
        # Holds the in-progress edits for each action (keyed by action id)
        st.session_state.edit_buffers = {}


def get_pending_actions() -> list[dict[str, Any]]:
    """Return actions that are still pending (not confirmed and not deleted)."""
    confirmed_ids = {a["id"] for a in st.session_state.confirmed_actions}
    return [
        a
        for a in st.session_state.actions
        if a["id"] not in confirmed_ids and a["id"] not in st.session_state.deleted_ids
    ]


def save_action(action_id: str, updated: dict[str, Any]) -> None:
    """Move an action from pending → confirmed with the edited values."""
    updated = dict(updated)
    updated["status"] = "confirmed"
    updated["confirmed_at"] = datetime.utcnow().isoformat() + "Z"

    # Remove any previous confirmation of the same id (re-edit case)
    st.session_state.confirmed_actions = [
        a for a in st.session_state.confirmed_actions if a["id"] != action_id
    ]
    st.session_state.confirmed_actions.append(updated)

    # Clear the edit buffer for this action
    st.session_state.edit_buffers.pop(action_id, None)


def discard_action(action_id: str) -> None:
    """Mark an action as discarded so it no longer appears in the pending list."""
    st.session_state.deleted_ids.add(action_id)
    st.session_state.edit_buffers.pop(action_id, None)


def reset_demo() -> None:
    """Reset everything back to the original sample data (for testing)."""
    st.session_state.actions = [dict(a) for a in SAMPLE_ACTIONS]
    st.session_state.confirmed_actions = []
    st.session_state.deleted_ids = set()
    st.session_state.edit_buffers = {}


# ---------------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------------
def render_action_card(action: dict[str, Any], index: int) -> None:
    """
    Render one editable form card for a single action.
    Uses a unique form key so Streamlit treats each card independently.
    """
    action_id = action["id"]

    # Initialise / retrieve the edit buffer for this action
    if action_id not in st.session_state.edit_buffers:
        st.session_state.edit_buffers[action_id] = dict(action)

    buffer = st.session_state.edit_buffers[action_id]

    with st.container(border=True):
        st.markdown(f"### Action {index + 1}: `{action_id}`")

        # --- Form -----------------------------------------------------------
        with st.form(key=f"form_{action_id}", clear_on_submit=False):
            col1, col2 = st.columns(2)

            with col1:
                action_type = st.selectbox(
                    "Action type",
                    options=ACTION_TYPE_OPTIONS,
                    index=ACTION_TYPE_OPTIONS.index(buffer.get("action_type", "other"))
                    if buffer.get("action_type") in ACTION_TYPE_OPTIONS
                    else len(ACTION_TYPE_OPTIONS) - 1,
                    key=f"type_{action_id}",
                )
                shipment_id = st.text_input(
                    "Shipment / Container ID",
                    value=buffer.get("shipment_id", ""),
                    key=f"ship_{action_id}",
                )
                priority = st.selectbox(
                    "Priority",
                    options=PRIORITY_OPTIONS,
                    index=PRIORITY_OPTIONS.index(buffer.get("priority", "medium"))
                    if buffer.get("priority") in PRIORITY_OPTIONS
                    else 2,
                    key=f"prio_{action_id}",
                )

            with col2:
                location = st.text_input(
                    "Location",
                    value=buffer.get("location", ""),
                    key=f"loc_{action_id}",
                )
                requested_by = st.text_input(
                    "Requested by",
                    value=buffer.get("requested_by", ""),
                    key=f"req_{action_id}",
                )
                deadline = st.text_input(
                    "Deadline (YYYY-MM-DD HH:MM)",
                    value=buffer.get("deadline", ""),
                    key=f"dl_{action_id}",
                )

            description = st.text_area(
                "Description",
                value=buffer.get("description", ""),
                height=100,
                key=f"desc_{action_id}",
            )

            # Buttons inside the form
            btn_col1, btn_col2, _ = st.columns([1, 1, 3])
            with btn_col1:
                save_clicked = st.form_submit_button(
                    "✅ Confirm / Save",
                    type="primary",
                    use_container_width=True,
                )
            with btn_col2:
                discard_clicked = st.form_submit_button(
                    "🗑️ Discard",
                    type="secondary",
                    use_container_width=True,
                )

            if save_clicked:
                updated = {
                    "id": action_id,
                    "action_type": action_type,
                    "description": description.strip(),
                    "shipment_id": shipment_id.strip(),
                    "priority": priority,
                    "location": location.strip(),
                    "requested_by": requested_by.strip(),
                    "deadline": deadline.strip(),
                    "status": "confirmed",
                }
                # Keep original fields that we don't expose for edit
                for k, v in action.items():
                    if k not in updated:
                        updated[k] = v
                save_action(action_id, updated)
                st.success(f"Action {action_id} confirmed and saved.")
                st.rerun()

            if discard_clicked:
                discard_action(action_id)
                st.warning(f"Action {action_id} discarded.")
                st.rerun()


def render_confirmed_section() -> None:
    """Show the list of already-confirmed actions and the download button."""
    confirmed = st.session_state.confirmed_actions

    st.divider()
    st.subheader(f"✅ Confirmed actions ({len(confirmed)})")

    if not confirmed:
        st.info("No actions confirmed yet. Edit and save actions above.")
        return

    # Compact table view
    for a in confirmed:
        with st.expander(f"{a['id']} – {a.get('action_type', 'unknown')} ({a.get('priority', '')})"):
            st.json(a)

    # Download button
    json_str = json.dumps(confirmed, indent=2, ensure_ascii=False)
    st.download_button(
        label="⬇️ Download confirmed actions (JSON)",
        data=json_str,
        file_name=f"cargolink_confirmed_actions_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        type="primary",
        use_container_width=False,
    )


# ---------------------------------------------------------------------------
# Main app
# ---------------------------------------------------------------------------
def main() -> None:
    init_session_state()

    st.title("📦 CargoLink Logistics – Action Confirmation")
    st.caption(
        "Task 3 · Review, edit and approve actions extracted from voice notes. "
        "Confirmed actions are stored in session state and can be downloaded as JSON."
    )

    # Sidebar – demo controls & status
    with st.sidebar:
        st.header("Session status")
        pending = get_pending_actions()
        st.metric("Pending actions", len(pending))
        st.metric("Confirmed actions", len(st.session_state.confirmed_actions))
        st.metric("Discarded actions", len(st.session_state.deleted_ids))

        st.divider()
        st.markdown("**Demo controls**")
        if st.button("🔄 Reset to sample data", use_container_width=True):
            reset_demo()
            st.rerun()

        st.caption(
            "Session state persists across page interactions and browser "
            "reruns for the lifetime of this browser tab."
        )

    # Main area – pending action cards
    pending = get_pending_actions()

    if not pending:
        st.success("All actions have been reviewed. Nothing left to confirm.")
    else:
        st.subheader(f"Pending actions ({len(pending)})")
        st.markdown(
            "Edit any field, then press **Confirm / Save** to approve or "
            "**Discard** to reject the action."
        )
        for idx, action in enumerate(pending):
            render_action_card(action, idx)

    # Confirmed section + download
    render_confirmed_section()

    # Footer note
    st.divider()
    st.caption(
        "Built for CargoLink Logistics internship · Task 3 – Confirmation UI · "
        "Streamlit session_state + JSON download"
    )


if __name__ == "__main__":
    main()
