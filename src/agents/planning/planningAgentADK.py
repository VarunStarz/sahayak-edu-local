from google.adk.agents import LlmAgent

class PlanningAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            name="PlanningAgent",
            model="gemini-2.0-flash",
            description="Handles scheduling operations, google calender sync and notifications and reminders.",
            instruction="Schedules reminders and tasks in the google calender for the teacher."
        )

    # Optionally add custom vision logic
    # def process_image(self, ...):
    #     pass
