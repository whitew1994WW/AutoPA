from langchain_core.messages import HumanMessage, AIMessage
from langsmith import Client
from langchain.adapters.openai import convert_message_to_dict
from boss_agent import boss_app
from caller_agent import caller_app


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
        DualChatAgent.log_to_langsmith(state, new_state, "caller_graph")
        return new_state
    
    @staticmethod
    def receive_message_from_boss(message, state):
        state["boss_conversation"].append(HumanMessage(content=message, type="human"))
        new_state = boss_app.invoke(state)
        DualChatAgent.log_to_langsmith(state, new_state, "boss_graph")
        return new_state
    
    @staticmethod
    def log_to_langsmith(initial_state, succeeded_state, dataset_name):
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

        boss_tools_used = []
        for message in succeeded_state["boss_conversation"][len(initial_state["boss_conversation"]):]:
            if message.type == "ai" and message.tool_calls:
                for tool_call in message.tool_calls:
                    boss_tools_used.append({"name": tool_call["name"], "args": tool_call["args"]})

        # Check if there are more caller or boss messages
        if len(succeeded_state["caller_conversation"]) > len(initial_state["caller_conversation"]):
            caller_response = convert_message_to_dict(succeeded_state["caller_conversation"][-1])
        else:
            caller_response = ""

        if len(succeeded_state["boss_conversation"]) > len(initial_state["boss_conversation"]):
            boss_response = convert_message_to_dict(succeeded_state["boss_conversation"][-1])
        else:
            boss_response = ""
        output = {
            "caller_response": caller_response,
            "boss_response": boss_response,
            "caller_tools_used": caller_tools_used,
            "boss_tools_used": boss_tools_used,
        }
        converted_initial_state = initial_state
        converted_initial_state["caller_conversation"] = [convert_message_to_dict(message) for message in initial_state["caller_conversation"]]
        converted_initial_state["boss_conversation"] = [convert_message_to_dict(message) for message in initial_state["boss_conversation"]]
        client.create_example(
            inputs=initial_state,
            outputs=output,
            dataset_name=dataset_name
        )
        

