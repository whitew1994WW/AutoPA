from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage
from langgraph.prebuilt import ToolExecutor
from langgraph.prebuilt import ToolInvocation
from langchain_core.messages import ToolMessage
import datetime
from common import convert_conversation_sequence_into_script, log_prompt_output_to_langsmith, llm
from generic_tools import get_potential_appointments, get_current_appointments, book_appointment, cancel_appointment
from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage
from persistant_state import BOSS_CONVERSATION, CALLER_CONVERSATIONS, CONTACT_MANAGER

class BossConversationStates(TypedDict):
    boss_conversation: Annotated[Sequence[BaseMessage], operator.add]

# Tools
@tool
def send_caller_message(message: str, caller_name: str):
    """Send a message to the caller"""
    contact = CONTACT_MANAGER.get_contact(name=caller_name)
    if contact.phone_number not in CALLER_CONVERSATIONS:
        CALLER_CONVERSATIONS[contact.phone_number] = []
    CALLER_CONVERSATIONS[contact.phone_number].append(AIMessage(content=message))
    return f"Message sent to caller"

# Edges
def should_continue_boss(state: BossConversationStates):
    messages = state["boss_conversation"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"

# Nodes
def call_boss_model(state: BossConversationStates):
    state["current_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    response = boss_model.invoke(state)
    log_prompt_output_to_langsmith(state, response, "boss_prompt")
    return {"boss_conversation": [response]}


def call_boss_tool(state: BossConversationStates):
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
    return {"boss_conversation": tool_messages}
    
    
boss_pa_prompt = """You are a personal assistant bot. All messages that would be sent to your boss are instead sent to you. Follow your bosses instructions.

If you are asked to book an appointment by your boss, message the person who the appointment is for using the send_caller_message tool to continue the conversation with them seperately.

Current time: {current_time}

In this conversation you are speaking with the boss.
"""
boss_chat_template = ChatPromptTemplate.from_messages([
    ("system", boss_pa_prompt),
    ("placeholder", "{boss_conversation}"),
])
boss_tools = [send_caller_message, book_appointment, cancel_appointment, get_potential_appointments, get_current_appointments]
boss_tool_executor = ToolExecutor(boss_tools)
boss_model = boss_chat_template | llm.bind_tools(boss_tools)


# Graph 
boss_workflow = StateGraph(BossConversationStates)

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
