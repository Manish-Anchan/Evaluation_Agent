from pydantic import BaseModel
from typing import List, Annotated, TypedDict
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages : Annotated[List, add_messages]
    topic : str
    next_question : str
    count : int 
