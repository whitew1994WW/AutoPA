from external_apis import AppointmentManager, ContactManager
from typing import List
import random

class RedTeamTasker:
    def __init__(self):
        self.task= self.get_red_team_task()

    def get_red_team_task(self):
        options = [
            'Book an appointment', 
            'Book and then cancel an appointment', 
            'Get the available appointments', 
            'Leave a message for the boss'
        ]
        return random.choice(options)
    
APPOINTMENT_MANAGER = AppointmentManager()
CONTACT_MANAGER = ContactManager()
BOSS_CONVERSATION = []
CALLER_CONVERSATIONS = {"default": []}  
RED_TEAM_TASKER = RedTeamTasker()
