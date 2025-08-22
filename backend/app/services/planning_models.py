# file: backend/app/services/planning_models.py
import torch
import torch.nn as nn
from typing import Dict, Any, Optional
from app.schemas.schemas import ReasoningGraph
from app.schemas.dsl import Strategy, ActionType
import logging

logger = logging.getLogger("tes_backend")

# --- Default Dimensions ---
STATE_VECTOR_DIM = 256  # Compact state vector for efficiency
DEFAULT_HIDDEN_DIM = 512

# --- Shared Trunk ---
class SharedTrunk(nn.Module):
    """
    Lightweight shared trunk for feature extraction.
    """
    def __init__(self, input_dim: int = STATE_VECTOR_DIM, hidden_dim: int = DEFAULT_HIDDEN_DIM):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

# --- Policy Head ---
class PolicyHead(nn.Module):
    """
    Policy head predicting a distribution over actions.
    """
    def __init__(self, hidden_dim: int = DEFAULT_HIDDEN_DIM, output_dim: int = len(ActionType.__args__)):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, output_dim),
            nn.LogSoftmax(dim=-1)  # Stable training with NLLLoss
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

# --- Value Head ---
class ValueHead(nn.Module):
    """
    Value head predicting expected utility of state.
    """
    def __init__(self, hidden_dim: int = DEFAULT_HIDDEN_DIM):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1),
            nn.Tanh()  # Output between -1 and 1
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

# --- Full Planning Model ---
class PlanningModel(nn.Module):
    """
    Full model combining shared trunk with policy and value heads.
    """
    def __init__(self, input_dim: int = STATE_VECTOR_DIM, hidden_dim: int = DEFAULT_HIDDEN_DIM, 
                 output_dim: int = len(ActionType.__args__)):
        super().__init__()
        self.trunk = SharedTrunk(input_dim, hidden_dim)
        self.policy_head = PolicyHead(hidden_dim, output_dim)
        self.value_head = ValueHead(hidden_dim)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        # Ensure batch dimension
        if x.dim() == 1:
            x = x.unsqueeze(0)  # Convert [state_dim] -> [1, state_dim]
        trunk_features = self.trunk(x)
        policy_output = self.policy_head(trunk_features)
        value_output = self.value_head(trunk_features)
        logger.debug(f"Forward pass shapes: policy={policy_output.shape}, value={value_output.shape}")
        return policy_output, value_output

# --- Helper: Create State Vector ---
def create_state_vector(graph: ReasoningGraph, strategy: Strategy, 
                        memories: Dict[str, Any], batch_size: Optional[int] = None) -> torch.Tensor:
    """
    Generates a compact state vector from strategy, graph, and memory.
    Currently uses dummy embeddings; replace with real encoders later.
    """
    # Dummy embeddings
    strategy_vec = torch.randn(64)
    graph_vec = torch.randn(128)
    memory_vec = torch.randn(64)

    state_vector = torch.cat([strategy_vec, graph_vec, memory_vec])
    if batch_size is not None:
        state_vector = state_vector.unsqueeze(0).repeat(batch_size, 1)

    logger.debug(f"Created state vector of shape: {state_vector.shape}")
    return state_vector
