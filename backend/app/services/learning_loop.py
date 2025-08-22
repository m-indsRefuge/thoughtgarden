# file: backend/app/services/learning_loop.py
import torch
from typing import List, Dict, Any
import logging
import random
import asyncio

from app.services.mcts_service import find_best_strategy
from app.services.planning_models import PlanningModel, create_state_vector, ActionType
from app.services.reward_model import RewardModel
from app.services.trainer import Trainer
from app.schemas.schemas import ReasoningGraph
from app.schemas.dsl import Strategy

logger = logging.getLogger("tes_backend")

class LearningLoop:
    """
    Orchestrates the continuous learning pipeline for the Thought Garden.
    Manages data collection (replay buffer) and triggers model training.
    """
    def __init__(self, buffer_size: int = 1000, batch_size: int = 64):
        self.planning_model = PlanningModel()
        self.reward_model = RewardModel()
        self.trainer = Trainer(self.planning_model, self.reward_model)
        self.replay_buffer = []
        self.buffer_size = buffer_size
        self.batch_size = batch_size
        logger.info(f"LearningLoop initialized with buffer size {buffer_size} and batch size {batch_size}.")

    async def collect_experience(self, graph: ReasoningGraph, candidate_strategies: List[Strategy]):
        """
        Runs MCTS to find the best strategy and stores the experience in the replay buffer.
        """
        try:
            best_strategy = await find_best_strategy(graph, candidate_strategies)
            
            # This is a conceptual step. In a real scenario, we would get the actual
            # reward from the user's next turn or a high-fidelity simulator.
            # For now, we use a random value.
            reward = random.uniform(0.5, 1.0)
            
            # Convert the strategy's first action to an index for the policy head
            action_index = self._action_to_index(best_strategy.actions[0].type)
            
            state_vector = create_state_vector(
                graph,
                best_strategy,
                memories={} # We would pass real memories here
            )

            experience = {
                "state": state_vector,
                "action_index": action_index,
                "reward": reward
            }
            
            self.replay_buffer.append(experience)
            if len(self.replay_buffer) > self.buffer_size:
                self.replay_buffer.pop(0) # Simple FIFO eviction
            
            logger.info(f"Experience collected. Buffer size: {len(self.replay_buffer)}")
        
        except Exception as e:
            logger.error(f"Error collecting experience: {e}")

    async def train_if_ready(self):
        """
        Triggers a training step if enough data is available in the buffer.
        """
        if len(self.replay_buffer) >= self.batch_size:
            logger.info("Training buffer is full enough. Starting training.")
            data_batch = random.sample(self.replay_buffer, self.batch_size)
            self.trainer.run_training_step(data_batch)
            self.replay_buffer.clear() # Clear buffer after training for simplicity
            
            # Save checkpoint after training
            self.trainer.save_checkpoint()

    def _action_to_index(self, action_type: str) -> int:
        """
        Maps an action string to its index for the policy network.
        """
        action_mapping = {action_type: i for i, action_type in enumerate(ActionType.__args__)}
        return action_mapping.get(action_type, 0) # Default to 0 if not found

# This instance will be used by other services
learning_loop = LearningLoop()