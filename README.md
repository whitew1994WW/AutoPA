# AutoPA

Streamlit proof of concept for a ChatGPT powered personal assistant who can:

- Manage a calendar, booking and cancelling appointments
- Messaging contacts
- Adding or creating contacts
- Handle multiple conversations at the same time

Its powered with LangGraph and ChatGPT. There is an agent that handles the incoming messages and has a tool to send messages to the boss, and another agent that handles a conversation with the boss with a tool to send messages to contacts. There are other tools for handling the appointment management and contact management.

See the below videos for a few examples of the functionality:


- [AutoPA Demo](/examples/2024-05-29%2019-32-08.mp4)

- [AutoPA Demo 2](/examples/2024-05-29%2019-37-57.mp4)

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






