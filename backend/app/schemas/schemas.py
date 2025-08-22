# file: app/schemas/schemas.py (Final Corrected Version)
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field
from sqlmodel import SQLModel, Field as SQLField
from datetime import datetime

# --- Node and Edge Schemas for the Reasoning Graph ---

NodeType = Literal["user_input", "ai_expansion", "choice", "counterpoint", "reflection"]
EdgeRelation = Literal["expands", "contradicts", "supports", "chooses", "summarizes"]


class NodeMetadata(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    depth: int = 0
    confidence: Optional[float] = None
    lens: Optional[str] = None
    winning_strategy: Optional[str] = None # This line is the required addition


class Node(BaseModel):
    id: str = Field(
        ...,
        description="A unique ID for the node (e.g., a UUID or hash).",
        examples=["node-12345"]
    )
    type: NodeType = Field(..., description="The type of the reasoning node.")
    content: str = Field(..., description="The textual content of the node.")
    metadata: NodeMetadata = Field(..., description="Structured metadata for the node.")


class Edge(BaseModel):
    source: str = Field(..., description="The ID of the source node.")
    target: str = Field(..., description="The ID of the target node.")
    relation: EdgeRelation = Field(..., description="The relationship between the nodes.")


class ReasoningGraph(BaseModel):
    nodes: List[Node] = Field(
        ...,
        description="A list of all nodes in the reasoning graph."
    )
    edges: List[Edge] = Field(
        ...,
        description="A list of all edges connecting the nodes."
    )


# --- API Input & Output Schemas ---

class UserInput(BaseModel):
    message: str = Field(..., description="The user's message.")


class ExperimentCreate(BaseModel):
    title: str
    description: str


class ExperimentData(BaseModel):
    description: str
    graph: Optional[ReasoningGraph] = None