from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage
from langsmith import Client
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model='gpt-4o')

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

def log_prompt_output_to_langsmith(initial_state, response, dataset_name):
    client = Client()
    try:
        dataset_name = dataset_name + "_all_convo_turns"
        dataset = client.create_dataset(dataset_name)
        sanitised_dataset = client.create_dataset(dataset_name.replace("_all_convo_turns", "_sanitised"))
    except:
        pass
    
    client.create_example(
        inputs=initial_state,
        outputs=response,
        dataset_name=dataset_name
    )

    