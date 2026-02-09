from typing import List, Dict

def extract_relevant_fields_fullstory(sessions: List[Dict]) -> List[Dict]:
    """
    Extract AI-ready behavioral signals from FullStory session data.
    This version captures all events, journey steps, and session metadata
    without predefined categorizations.
    """
    extracted_sessions = []

    for session in sessions:
        customer_id = session.get("customer_id")
        session_id = session.get("session_id")
        platform = session.get("platform")
        region = session.get("region")
        session_start = session.get("session_start_time")
        session_end = session.get("session_end_time")

        signals = []
        journey_steps = []

        for event in session.get("events", []):
            event_type = event.get("event_type")
            event_time = event.get("event_time")
            event_props = event.get("event_properties", {})

            # Capture event details
            signals.append({
                "event_type": event_type,
                "event_time": event_time,
                "details": event_props
            })

            # Capture page views as journey steps
            if event_type == "page_view":
                journey_steps.append(event_props.get("page_name", "unknown_page"))

        # Build session object
        extracted_sessions.append({
            "customer_id": customer_id,
            "session_id": session_id,
            "platform": platform,
            "region": region,
            "session_start_time": session_start,
            "session_end_time": session_end,
            "signals": signals,
            "journey_steps": journey_steps
        })

    return extracted_sessions
