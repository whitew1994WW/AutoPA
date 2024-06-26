from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage
from langgraph.prebuilt import ToolExecutor
from langgraph.prebuilt import ToolInvocation
from langchain_core.messages import ToolMessage
import datetime
from common import convert_conversation_sequence_into_script, log_prompt_output_to_langsmith, llm
from generic_tools import get_potential_appointments, get_current_appointments, book_appointment, cancel_appointment, get_contact, add_or_update_contact, delete_contact
from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage
from persistant_state import BOSS_CONVERSATION
   
# Graph Internal State
class CallerConversationStates(TypedDict):
    contact_details: str
    caller_conversation: Annotated[Sequence[BaseMessage], operator.add]
    boss_conversation: Annotated[Sequence[BaseMessage], operator.add]


@tool
def send_boss_message(message: str): 
    """Send a message to the boss"""
    BOSS_CONVERSATION.append(AIMessage(content=message))
    return f"Message sent to boss"

# Edges
def should_continue_caller(state: CallerConversationStates):
    messages = state["caller_conversation"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"

# Nodes
def call_caller_model(state: CallerConversationStates):
    print(state["boss_conversation"])
    state["boss_conversation"] = convert_conversation_sequence_into_script(state["boss_conversation"], "Boss")
    state["current_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    response = caller_model.invoke(state)
    log_prompt_output_to_langsmith(state, response, "caller_prompt")
    return {"caller_conversation": [response]}


def call_caller_tool(state: CallerConversationStates):
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
            boss_messages.append(AIMessage(content=tool_call["args"]["message"]))

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
    
    



caller_pa_prompt = """You are a personal assistant bot. All messages that would be sent to your boss (Will) are instead sent to you. You have to do the following:

- If there is any contact information missing (phone number, email, notes) then you should ask the caller for it and use the add_contact or update_contact tools to update the address book
- Manage communication with the caller so that you only have to contact your boss when necessary
- Manage your bosses calendar. You can book and cancel appointments
- Manage your bosses contacts. You can add, update, and delete contacts from the address book
- Follow the instructions of your boss and these rules
- Inform your boss of any important information that the caller provides
- Not provide any information from the contact list to the caller
- Pay attention to the notes in the contact details, they may contain important information

Current time: {current_time}
Current caller contact details: {contact_details}

You have two conversations going on, in this case you are speaking to the caller, but your private conversation history with the boss is below:

{boss_conversation}

"""

caller_chat_template = ChatPromptTemplate.from_messages([
    ("system", caller_pa_prompt),
    ("placeholder", "{caller_conversation}"),
])
caller_tools = [send_boss_message, book_appointment, cancel_appointment, get_potential_appointments, get_current_appointments, get_contact, add_or_update_contact, delete_contact]
caller_tool_executor = ToolExecutor(caller_tools)
caller_model = caller_chat_template | llm.bind_tools(caller_tools)


# Graph 
caller_workflow = StateGraph(CallerConversationStates)

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
