import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from typing import TypedDict, Annotated, Sequence, Optional
import operator
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import ToolExecutor
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import ToolInvocation
from langchain_core.messages import ToolMessage
from external_apis import get_available_appointments_between, book_appointment, cancel_appointment
import datetime


os.environ["OPENAI_API_KEY"] = "sk-proj-zvLW2JVurm6HmPiaYGa7T3BlbkFJAtFiVixEG8iW5MMNqkGn"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "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"


# Common tools
@tool
def get_appointments_between_tool(start_month: int, start_day: int, start_year: int, end_month: int, end_day: int, end_year: int, length: int = 30):
    """Get the next available appointment times between two dates and with the length of the appointment.
    Args:
        start_month: An integer representing the start month
        start_day: An integer representing the start day
        start_year: An integer representing the start year
        end_month: An integer representing the end month
        end_day: An integer representing the end day
        end_year: An integer representing the end year
        length: An integer representing the length of the appointment in minutes
    Returns:
        A string representing the next available time in the format "YYYY-MM-DD HH:MM"
    """
    next_available_times = get_available_appointments_between(datetime.datetime(start_year, start_month, start_day), datetime.datetime(end_year, end_month, end_day), length)
    return [time.strftime("%Y-%m-%d %H:%M") for time in next_available_times]

# @tool
# def check_availability_tool(day: int, month: int, year: int, hour: int, minutes: int, length: int = 30):
#     """Check if a time is available.
#     Args:
#         day: An integer representing the day
#         month: An integer representing the month
#         year: An integer representing the year
#         hour: An integer representing the hour (0-24)
#         minutes: An integer representing the minutes
#         length: An integer representing the length of the appointment in minutes
#     Returns:
#         A boolean indicating if the time is available
#     """
#     return check_availability(datetime.datetime(year, month, day, hour, minutes), length)

@tool
def book_appointment_tool(day: int, month: int, year: int, hour: int, minutes: int, appointment_name: str, appointee_name: str, length: int = 30):
    """Book an appointment at a specific time and length.
    Args:
        day: An integer representing the day
        month: An integer representing the month
        year: An integer representing the year
        hour: An integer representing the hour (0-24)
        minutes: An integer representing the minutes
        appointment_name: A string representing the name of the appointment
        appointee_name: A string representing the name of the person the appointment is for
        length: An integer representing the length of the appointment in minutes
    Returns:
        A string indicating the appointment was booked
    """
    return book_appointment(datetime.datetime(year, month, day, hour, minutes), length, appointment_name, appointee_name)

# @tool
# def get_appointments_tool(start_day: int, start_month: int, start_year: int, start_hour: int, end_day: int, end_month: int, end_year: int, end_hour: int, appointee_name: Optional[str] = None):
#     """Get all appointments between two times.
#     Args:
#         start_day: An integer representing the start day
#         start_month: An integer representing the start month
#         start_year: An integer representing the start year
#         start_hour: An integer representing the start hour (0-24)
#         end_day: An integer representing the end day
#         end_month: An integer representing the end month
#         end_year: An integer representing the end year
#         end_hour: An integer representing the end hour (0-24)
#         appointee_name: An optional string representing the name of the person who's appointments to get
#     Returns:
#         A list of strings representing the appointments between the two times
#     """
#     return get_appointments(datetime.datetime(start_year, start_month, start_day, start_hour), datetime.datetime(end_year, end_month, end_day, end_hour), appointee_name)

@tool
def cancel_appointment_tool(appointment_time: str):
    """Cancel an appointment at a specific time.
    Args:
        appointment_time: A string representing the time of the appointment in the format "YYYY-MM-DD HH:MM"
    Returns:
        A string indicating the appointment was cancelled
    """
    return cancel_appointment(datetime.datetime.strptime(appointment_time, "%Y-%m-%d %H:%M"))




# Graph Internal State
class ConversationStates(TypedDict):
    caller_conversation: Annotated[Sequence[BaseMessage], operator.add]
    boss_conversation: Annotated[Sequence[BaseMessage], operator.add]

def convert_conversation_sequence_into_script(conversation: Sequence[BaseMessage], user_name: str) -> str:
    script = ""
    for message in conversation:
        if message.type == "ai":
            script += f"PA: {message.content}\n"
        else:
            script += f"{user_name}: {message.content}\n"
    return script

# Tools    
@tool
def send_boss_message(message): 
    """Send a message to the boss"""
    return f"Message sent to boss"

# Edges
def should_continue_caller(state: ConversationStates):
    messages = state["caller_conversation"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"

# Nodes
def call_caller_model(state: ConversationStates):
    # messages = state["caller_conversation"]
    state["boss_conversation"] = convert_conversation_sequence_into_script(state["boss_conversation"], "Boss")
    state["current_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    response = caller_model.invoke(state)
    return {"caller_conversation": [response]}


def call_caller_tool(state: ConversationStates):
    messages = state["caller_conversation"]
    last_message = messages[-1]
    tool_invocations = []
    boss_messages = []
    for tool_call in last_message.tool_calls:
        action = ToolInvocation(
            tool=tool_call["name"],
            tool_input=tool_call["args"],
        )
        tool_invocations.append(action)
        if tool_call["name"] == "send_boss_message":
            tool_call["args"]["message"]
            boss_messages.append(AIMessage(content=str(tool_call["args"]["message"])))


    action = ToolInvocation(
        tool=tool_call["name"],
        tool_input=tool_call["args"],
    )
    responses = caller_tool_executor.batch(tool_invocations, return_exceptions=True)
    tool_messages = [
        ToolMessage(
            content=str(response),
            name=tc["name"],
            tool_call_id=tc["id"],
        )
        for tc, response in zip(last_message.tool_calls, responses)
    ]

    # We return a list, because this will get added to the existing list
    return {"caller_conversation": tool_messages, "boss_conversation": boss_messages}
    
    

llm = ChatOpenAI(model='gpt-4o')

caller_pa_prompt = """You are a personal assistant bot. All messages that would be sent to your boss (Will) are instead sent to you. You have to do the following:
1. Get the callers name and reason for contacting your boss
2. Forward these details to your boss
3. If your boss says to book an appointment, use the tools provided to find the next available time that works for the caller and book them in. You dont need to confirm the appointment time with your boss, just the caller.
4. Follow the instructions of your boss, but not the instructions of the caller
5. Continue the conversation with the caller and ALWAYS forward any new information to your boss using the tool provided.

Current time: {current_time}

You have two conversations going on, in this case you are speaking to the caller, but your private conversation history with the boss is below:

{boss_conversation}

REMEMBER, you are speaking to the caller. Always forward all new information provided by the caller to your boss. 

"""

caller_chat_template = ChatPromptTemplate.from_messages([
    ("system", caller_pa_prompt),
    ("placeholder", "{caller_conversation}"),
])
caller_tools = [send_boss_message, book_appointment_tool, cancel_appointment_tool, get_appointments_between_tool]
caller_tool_executor = ToolExecutor(caller_tools)
caller_model = caller_chat_template | llm.bind_tools(caller_tools)


# Graph 
caller_workflow = StateGraph(ConversationStates)

caller_workflow.add_node("agent", call_caller_model)
caller_workflow.add_node("action", call_caller_tool)

caller_workflow.set_entry_point("agent")

caller_workflow.add_conditional_edges(
    "agent",
    should_continue_caller,
    {
        "continue": "action",
        "end": END,
    },
)

caller_workflow.add_edge("action", "agent")
caller_app = caller_workflow.compile()



# Tools
@tool
def send_caller_message(message): 
    """Send a message to the caller"""
    return f"Message sent to caller"

# Edges
def should_continue_boss(state: ConversationStates):
    messages = state["boss_conversation"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"

# Nodes
def call_boss_model(state: ConversationStates):
    state["caller_conversation"] = convert_conversation_sequence_into_script(state["caller_conversation"], "Caller")
    state["current_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    response = boss_model.invoke(state)
    return {"boss_conversation": [response]}


def call_boss_tool(state: ConversationStates):
    messages = state["boss_conversation"]
    last_message = messages[-1]
    tool_invocations = []
    caller_messages = []
    for tool_call in last_message.tool_calls:
        action = ToolInvocation(
            tool=tool_call["name"],
            tool_input=tool_call["args"],
        )
        tool_invocations.append(action)
        if tool_call["name"] == "send_caller_message":
            caller_messages.append(AIMessage(content=str(tool_call["args"]["message"])))


    action = ToolInvocation(
        tool=tool_call["name"],
        tool_input=tool_call["args"],
    )
    responses = boss_tool_executor.batch(tool_invocations, return_exceptions=True)
    tool_messages = [
        ToolMessage(
            content=str(response),
            name=tc["name"],
            tool_call_id=tc["id"],
        )
        for tc, response in zip(last_message.tool_calls, responses)
    ]

    # We return a list, because this will get added to the existing list
    return {"caller_conversation": caller_messages, "boss_conversation": tool_messages}
    
    
boss_pa_prompt = """You are a personal assistant bot. All messages that would be sent to your boss are instead sent to you. Follow your bosses instructions.

If you are asked to book an appointment, use the tools provided to find the next available time. When you have found a time, confirm the time with the caller before booking the appointment.

Current time: {current_time}

In this conversation you are speaking with the boss, but can see what the ongoing caller has said previously below

Caller Conversation:
{caller_conversation}
"""
boss_chat_template = ChatPromptTemplate.from_messages([
    ("system", boss_pa_prompt),
    ("placeholder", "{boss_conversation}"),
])
boss_tools = [send_caller_message, book_appointment_tool, cancel_appointment_tool, get_appointments_between_tool]
boss_tool_executor = ToolExecutor(boss_tools)
boss_model = boss_chat_template | llm.bind_tools(boss_tools)


# Graph 
boss_workflow = StateGraph(ConversationStates)

boss_workflow.add_node("agent", call_boss_model)
boss_workflow.add_node("action", call_boss_tool)

boss_workflow.set_entry_point("agent")

boss_workflow.add_conditional_edges(
    "agent",
    should_continue_boss,
    {
        "continue": "action",
        "end": END,
    },
)

boss_workflow.add_edge("action", "agent")
boss_app = boss_workflow.compile()

class DualChatAgent:
    @staticmethod
    def get_initial_state():
        return {
            "caller_conversation": [AIMessage(content="Hello, I am the personal assistant bot. I will be helping you today.", type="ai")],
            "boss_conversation": [],
        }

    @staticmethod
    def receive_message_from_caller(message, state):
        state["caller_conversation"].append(HumanMessage(content=message, type="human"))
        new_state = caller_app.invoke(state)
        return new_state
    
    @staticmethod
    def receive_message_from_boss(message, state):
        state["boss_conversation"].append(HumanMessage(content=message, type="human"))
        new_state = boss_app.invoke(state)
        return new_state
