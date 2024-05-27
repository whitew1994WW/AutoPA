from langchain_core.messages import HumanMessage, AIMessage
from langsmith import Client
from langchain.adapters.openai import convert_message_to_dict
from boss_agent import boss_app
from caller_agent import caller_app
from persistant_state import BOSS_CONVERSATION, CALLER_CONVERSATIONS, CONTACT_MANAGER
from IPython.display import Image


class DualChatAgent:
    @staticmethod
    def get_caller_graph_image() -> Image:
        return Image(caller_app.get_graph(xray=True).draw_mermaid_png())
    
    @staticmethod
    def get_boss_graph_image() -> Image:
        return Image(boss_app.get_graph(xray=True).draw_mermaid_png())
    
    @staticmethod
    def receive_message_from_caller(message, caller_number):
        CALLER_CONVERSATIONS[caller_number].append(HumanMessage(content=message, type="human"))
        if CONTACT_MANAGER.is_contact_in_list(phone_number=caller_number):
            contact = CONTACT_MANAGER.get_contact(phone_number=caller_number)
            print(f"Contact found: {contact}")
        else:
            print("Contact not found")
            contact = ""
        state = {
            "caller_conversation": CALLER_CONVERSATIONS[caller_number],
            "boss_conversation": BOSS_CONVERSATION,
            "contact_details": str(contact)
        }
        new_state = caller_app.invoke(state)
        new_state['BOSS_CONVERSATION'] = BOSS_CONVERSATION
        DualChatAgent.log_caller_graph_to_langsmith(state, new_state, "caller_graph")
        CALLER_CONVERSATIONS[caller_number].extend(new_state["caller_conversation"][len(CALLER_CONVERSATIONS[caller_number]):])
    
    @staticmethod
    def receive_message_from_boss(message):
        BOSS_CONVERSATION.append(HumanMessage(content=message, type="human"))
        state = {
            "boss_conversation": BOSS_CONVERSATION,
        }
        new_state = boss_app.invoke(state)
        DualChatAgent.log_boss_graph_to_langsmith(state, new_state, "boss_graph")
        BOSS_CONVERSATION.extend(new_state["boss_conversation"][len(BOSS_CONVERSATION):])
        
    
    @staticmethod
    def log_boss_graph_to_langsmith(initial_state, succeeded_state, dataset_name):
        client = Client()
        try:
            dataset_name = dataset_name + "_all_convo_turns"
            dataset = client.create_dataset(dataset_name)
            sanitised_dataset = client.create_dataset(dataset_name.replace("_all_convo_turns", "_sanitised"))
        except:
            pass
        boss_tools_used = []
        for message in succeeded_state["boss_conversation"][len(initial_state["boss_conversation"]):]:
            if message.type == "ai" and message.tool_calls:
                for tool_call in message.tool_calls:
                    boss_tools_used.append({"name": tool_call["name"], "args": tool_call["args"]})

        if len(succeeded_state["boss_conversation"]) > len(initial_state["boss_conversation"]):
            boss_response = convert_message_to_dict(succeeded_state["boss_conversation"][-1])
        else:
            boss_response = ""

        output = {
            "boss_response": boss_response,
            "boss_tools_used": boss_tools_used,
        }
        converted_initial_state = initial_state
        converted_initial_state["boss_conversation"] = [convert_message_to_dict(message) for message in initial_state["boss_conversation"]]
        client.create_example(
            inputs=initial_state,
            outputs=output,
            dataset_name=dataset_name
        )
        

    @staticmethod
    def log_caller_graph_to_langsmith(initial_state, succeeded_state, dataset_name):
        client = Client()
        try:
            dataset_name = dataset_name + "_all_convo_turns"
            dataset = client.create_dataset(dataset_name)
            sanitised_dataset = client.create_dataset(dataset_name.replace("_all_convo_turns", "_sanitised"))
        except:
            pass
        # Get all the tools used since the last human message
        caller_tools_used = []
        for message in succeeded_state["caller_conversation"][len(initial_state["caller_conversation"]):]:
            if message.type == "ai" and message.tool_calls:
                for tool_call in message.tool_calls:
                    caller_tools_used.append({"name": tool_call["name"], "args": tool_call["args"]})

        # Check if there are more caller or boss messages
        if len(succeeded_state["caller_conversation"]) > len(initial_state["caller_conversation"]):
            caller_response = convert_message_to_dict(succeeded_state["caller_conversation"][-1])
        else:
            caller_response = ""

        output = {
            "caller_response": caller_response,
            "caller_tools_used": caller_tools_used,
        }
        converted_initial_state = initial_state
        converted_initial_state["caller_conversation"] = [convert_message_to_dict(message) for message in initial_state["caller_conversation"]]
        converted_initial_state["boss_conversation"] = [convert_message_to_dict(message) for message in initial_state["boss_conversation"]]
        client.create_example(
            inputs=initial_state,
            outputs=output,
            dataset_name=dataset_name
        )
        
