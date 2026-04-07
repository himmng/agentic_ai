class LLMBackedGenerator:
    def __init__(self, provider):
        self.provider = provider

    def generate_inmoment_text(self, nps):
        prompt = f"""
        Generate a realistic customer feedback comment.
        NPS score: {nps}

        Rules:
        - If NPS <= 6 → negative
        - If NPS 7-8 → neutral
        - If NPS >= 9 → positive
        - Keep it short (1-2 sentences)
        """

        return self.provider.generate(prompt)

    def generate_fullstory_event(self, event_type):
        prompt = f"""
        Describe a realistic user action for event type: {event_type}.
        Output JSON with:
        - action
        - element
        - intent
        """

        return self.provider.generate(prompt)