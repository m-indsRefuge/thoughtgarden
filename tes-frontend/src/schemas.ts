// file: src/schemas.ts
// This file defines the data structures for the frontend,
// ensuring type safety and consistency with the backend.

export type NodeType = "user_input" | "ai_expansion" | "choice" | "counterpoint" | "reflection";
export type EdgeRelation = "expands" | "contradicts" | "supports" | "chooses" | "summarizes";

export interface NodeMetadata {
    timestamp: string;
    depth: number;
    confidence?: number;
    lens?: string;
}

export interface Node {
    id: string;
    type: NodeType;
    content: string;
    metadata: NodeMetadata;
}

export interface Edge {
    source: string;
    target: string;
    relation: EdgeRelation;
}

export interface ReasoningGraph {
    nodes: Node[];
    edges: Edge[];
}

export interface UserInput {
    message: string;
}

export interface ExperimentCreate {
    title: string;
    description: string;
}

export interface ExperimentData {
    id: number;
    title: string;
    data: {
        description: string;
        graph?: ReasoningGraph;
    };
}