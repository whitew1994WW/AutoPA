import streamlit as st
from chat_agents import DualChatAgent

def get_response(user_input):
    # This is a simple echo function. Replace this with your actual processing logic.
    return f"You said: {user_input}"

def caller_sent_message():
    user_input = st.session_state[f"input_caller"]
    st.session_state.dual_agent_state = DualChatAgent.receive_message_from_caller(user_input, st.session_state.dual_agent_state)
    st.session_state[f"input_caller"] = ""

def boss_sent_message():
    user_input = st.session_state[f"input_boss"]
    st.session_state.dual_agent_state = DualChatAgent.receive_message_from_boss(user_input, st.session_state.dual_agent_state)
    st.session_state[f"input_boss"] = ""

def main():
    st.set_page_config(layout="wide")
    st.title("Personal PA PoC")

    # Initialize session state for both chats if not already present
    if "messages_caller" not in st.session_state:
        st.session_state.messages_caller = []
    if "messages_boss" not in st.session_state:
        st.session_state.messages_boss = []
    if "dual_agent_state" not in st.session_state:
        st.session_state.dual_agent_state = DualChatAgent.get_initial_state()


    col1, col2, col3 = st.columns(3)

    with col3:
        st.write(st.session_state.dual_agent_state)

    with col1:
        st.subheader("Caller & PA")
        st.text_input("Caller:", key="input_caller", on_change=lambda: caller_sent_message())
        for message in st.session_state.dual_agent_state["caller_conversation"]:
            if message.content == '':
                continue
            st.markdown(f"**{message.type}:** {message.content}")

    with col2:
        st.subheader("PA & Boss")
        st.text_input("Boss:", key="input_boss", on_change=lambda: boss_sent_message())
        for message in st.session_state.dual_agent_state["boss_conversation"]:
            if message.content == '':
                continue
            st.markdown(f"**{message.type}:** {message.content}")



if __name__ == "__main__":
    main()