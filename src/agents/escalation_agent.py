def escalation_agent(priority):
    if priority == "high":
        return True, "Customer Support Tier 2", 24
    return False, "Customer Support", 72
