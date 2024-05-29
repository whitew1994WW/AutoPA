# AutoPA

Streamlit proof of concept for a ChatGPT powered personal assistant who can:

- Manage a calendar, booking and cancelling appointments
- Messaging contacts
- Adding or creating contacts
- Handle multiple conversations at the same time

Its powered with LangGraph and ChatGPT. There is an agent that handles the incoming messages and has a tool to send messages to the boss, and another agent that handles a conversation with the boss with a tool to send messages to contacts. There are other tools for handling the appointment management and contact management.

See the below videos for a few examples of the functionality:

https://github.com/whitew1994WW/AutoPA/assets/33956588/ece35575-5c6d-4010-8bd0-209a33d10ec8

https://github.com/whitew1994WW/AutoPA/assets/33956588/520ed703-c00b-4aeb-956e-64b9b9ba1ee0

The calendar and appointments are mocked out to make for fast development.

## Running

To run the app, you will need to install the requirements and run the streamlit app.

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Red Teaming

I also added a feature for testing out the functionality of the assistant. You can select a 'task'and hit the red team button to generate conversational turns with the assistant.

You can add additional tasks or make the prompts harder if you wanted to try and break the assistant.

[red teaming](/examples/image.png)






