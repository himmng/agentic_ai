# src/extractors/fullstory_extractor.py

from typing import List, Dict
from collections import Counter

# Define sets for different event types
ERROR_EVENT_TYPES = {"error"}
BILLING_EVENTS = {"Payment_Attempt", "View_Bill"}
SUPPORT_EVENTS = {"Contact_Support"}
SUCCESS_EVENTS = {"Login_Success"}

def extract_relevant_fields_fullstory(sessions: List[Dict]) -> List[Dict]:
    """
    Extracts AI-ready behavioral signals from FullStory session data.
    Includes journey summary, signals (errors, billing, support, success), and customer metadata.
    """

    extracted_sessions = []

    for session in sessions:
        customer_id = session.get("customer_id")
        session_id = session.get("session_id")
        platform = session.get("platform")
        region = session.get("region")
        device_id = session.get("device_id")
        session_start = session.get("session_start_time")
        session_end = session.get("session_end_time")

        signals = []
        journey_steps = []
        event_type_counter = Counter()
        error_detected = False
        payment_failed = False
        support_contacted = False

        for event in session.get("events", []):
            event_type = event.get("event_type")
            event_time = event.get("event_time")
            event_props = event.get("event_properties", {})

            event_type_counter[event_type] += 1

            # --- ERROR SIGNALS ---
            if event_type in ERROR_EVENT_TYPES:
                error_detected = True
                signals.append({
                    "signal_type": "app_or_transaction_error",
                    "event_time": event_time,
                    "context": {
                        "error_type": event_props.get("error_type"),
                        "error_message": event_props.get("error_message"),
                        "http_status": event_props.get("http_status")
                    }
                })

                if event_props.get("error_type") == "PaymentDeclined":
                    payment_failed = True

            # --- CUSTOM EVENTS ---
            if event_type == "custom_event":
                name = event_props.get("name")

                # Billing related
                if name in BILLING_EVENTS:
                    signals.append({
                        "signal_type": "billing_interaction",
                        "event_time": event_time,
                        "context": {
                            "action": name,
                            "details": event_props.get("properties", {})
                        }
                    })

                # Support contact
                if name in SUPPORT_EVENTS:
                    support_contacted = True
                    signals.append({
                        "signal_type": "customer_service_contact",
                        "event_time": event_time,
                        "context": event_props.get("properties", {})
                    })

                # Success indicators
                if name in SUCCESS_EVENTS:
                    signals.append({
                        "signal_type": "successful_task_completion",
                        "event_time": event_time,
                        "context": {
                            "task": name,
                            "details": event_props.get("properties", {})
                        }
                    })

            # --- INPUT / UX FRICTION ---
            if event_type == "input_change":
                interaction = event_props.get("interaction_type")
                if interaction == "change":
                    signals.append({
                        "signal_type": "user_input_activity",
                        "event_time": event_time,
                        "context": {
                            "field": event_props.get("field_name")
                        }
                    })

            # --- PAGE FLOW TRACKING ---
            if event_type == "page_view":
                journey_steps.append(event_props.get("page_name", "unknown_page"))

        # --- HIGH-LEVEL JOURNEY SUMMARY ---
        journey_summary_parts = []

        if payment_failed:
            journey_summary_parts.append("payment failure encountered")
        if support_contacted:
            journey_summary_parts.append("customer contacted support")
        if error_detected and not payment_failed:
            journey_summary_parts.append("application error encountered")
        if not journey_summary_parts:
            journey_summary_parts.append("journey completed without major friction")

        journey_summary = "; ".join(journey_summary_parts)

        # --- Build extracted object ---
        extracted_sessions.append({
            "customer_id": customer_id,
            "session_id": session_id,
            "device_id": device_id,
            "platform": platform,
            "region": region,
            "session_start_time": session_start,
            "session_end_time": session_end,
            "signals": signals,
            "journey_steps": journey_steps,
            "journey_summary": journey_summary
        })

    return extracted_sessions
