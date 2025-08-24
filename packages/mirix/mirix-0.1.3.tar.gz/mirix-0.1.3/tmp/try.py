import os
from mirix import Mirix
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

assistant = Mirix(
  api_key=API_KEY,
  model_provider="azure_opena",
  config_path=".local/mirix_jplml_azure.yaml",
)

out = assistant.add("Remember me this week's schedule：Monday–Friday (Workdays): 08:30–09:00: Arrive at work/home office, check emails, review calendar, plan tasks for the day. 09:00–10:30: Coding session (feature development, bug fixes, code reviews). 10:30–10:45: Short break (coffee, walk, chat with colleagues). 10:45–12:00: Continue coding, attend stand-up meeting, sync with team. 12:00–13:00: Lunch break. 13:00–15:00: Coding session (implementing new features, writing tests). 15:00–15:15: Break (stretch, snack). 15:15–17:00: Pair programming, debugging, or technical discussion. 17:00–17:30: Wrap up, update tickets, commit/push code, plan for tomorrow. Saturday (Weekend): 09:00–10:00: Leisure (reading, breakfast, light exercise). 10:00–12:00: Personal coding project, open-source contribution, or learning new tech. 12:00–13:00: Lunch. 13:00–15:00: Continue personal project or tech learning. 15:00–18:00: Social activities, hobbies, or relaxation. Sunday (Weekend): 09:00–11:00: Leisure (family time, outdoor activity). 11:00–13:00: Review personal goals, plan for the week, light coding or reading. 13:00–14:00: Lunch. 14:00–18:00: Rest, hobbies, prepare for the upcoming workweek.")

response = assistant.chat("What's my schedule for this week?")

print(response)

# assistant.clear_conversation_history()
