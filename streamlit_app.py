
import os

os.environ["OPENAI_API_KEY"] = "sk-proj-zvLW2JVurm6HmPiaYGa7T3BlbkFJAtFiVixEG8iW5MMNqkGn"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "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"
os.environ["LANGCHAIN_PROJECT"] = "PersonalPA"

import streamlit as st
from chat_agents import DualChatAgent
from datetime import datetime
from persistant_state import BOSS_CONVERSATION, CALLER_CONVERSATIONS, APPOINTMENT_MANAGER

def get_response(user_input):
    # This is a simple echo function. Replace this with your actual processing logic.
    return f"You said: {user_input}"

def caller_sent_message():
    print('caller sent message')
    user_input = st.session_state[f"input_caller"]
    DualChatAgent.receive_message_from_caller(user_input, st.session_state.current_caller)
    st.session_state[f"input_caller"] = ""

def boss_sent_message():
    print('boss sent message')
    user_input = st.session_state[f"input_boss"]
    DualChatAgent.receive_message_from_boss(user_input)
    st.session_state[f"input_boss"] = ""

def submit_form():
    """Handle form submission."""
    appointment_time = datetime(int(datetime.now().year), int(st.session_state.month), int(st.session_state.day), int(st.session_state.time[:2]), int(st.session_state.time[3:5]))
    duration = int(st.session_state.duration)
    APPOINTMENT_MANAGER.book_appointment(appointment_time, duration)

def main():
    st.set_page_config(layout="wide")
    st.title("Personal PA PoC")
    # Create a text box and button to create a new conversation
    new_conversation = st.text_input("New Caller Name", key="caller_name")
    if st.button("Start New Conversation"):
        CALLER_CONVERSATIONS[new_conversation] = []

    # Create dropdown to select the caller
    caller_name = st.selectbox("Select Caller", list(CALLER_CONVERSATIONS.keys()))
    st.session_state.current_caller = caller_name

    # Form to submit meeting start and end times
        # Sidebar for input form
    with st.sidebar.form("new_meeting_form"):
        st.write(f"Current datetime: {datetime.now()}")
        st.write("### New Meeting Details")
        # Inputs for the start time and duration
        start_time_input = st.text_input("Appointment month", key="month", value=f"{datetime.now().month}")
        start_time_input = st.text_input("Appointment day", key="day", value=f"{datetime.now().day}")
        start_time_input = st.text_input("Appointment time", key="time", value=f"{datetime.now().hour}:00")

        duration_input = st.text_input("Duration (minutes)", key="duration", value="30")
        # Submit button for the form
        submitted = st.form_submit_button("Submit", on_click=submit_form)
        if submitted:
            st.success("Meeting added!")


    col1, col2, col3 = st.columns(3)

    with col3:
        st.header("Boss Conversation")
        st.write(BOSS_CONVERSATION)
        st.header("Caller Conversation")
        if caller_name is not None and caller_name in CALLER_CONVERSATIONS:
            st.write(CALLER_CONVERSATIONS[caller_name])
        st.header("Appointments")
        appointments = APPOINTMENT_MANAGER.booked_appointments
        st.write([str(appointment) for appointment in appointments])

    with col1:
        st.subheader("Caller & PA")
        st.text_input("Caller:", key="input_caller", on_change=lambda: caller_sent_message())
        if caller_name is not None and caller_name in CALLER_CONVERSATIONS:
            for message in CALLER_CONVERSATIONS[caller_name]:
                if message.content == '':
                    continue
                st.markdown(f"**{message.type}:** {message.content}")

    with col2:
        st.subheader("PA & Boss")
        st.text_input("Boss:", key="input_boss", on_change=lambda: boss_sent_message())
        for message in BOSS_CONVERSATION:
            if message.content == '':
                continue
            st.markdown(f"**{message.type}:** {message.content}")



if __name__ == "__main__":
    main()