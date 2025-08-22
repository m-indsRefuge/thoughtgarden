# file: backend/app/services/trainer.py
import torch
import torch.nn as nn
import torch.optim as optim
from typing import List, Dict, Any, Optional
import logging
from uuid import uuid4
import os
import random
from datetime import datetime

from app.services.planning_models import PlanningModel, create_state_vector
from app.services.reward_model import RewardModel
from app.schemas.schemas import ReasoningGraph
from app.schemas.dsl import Strategy

logger = logging.getLogger("tes_backend")

# --- Trainer Class ---
class Trainer:
    def __init__(
        self,
        planning_model: PlanningModel,
        reward_model: Optional[RewardModel] = None,
        optimizer_config: Optional[Dict[str, Any]] = None,
        gradient_clip: float = 1.0
    ):
        self.planning_model = planning_model
        self.reward_model = reward_model
        optimizer_config = optimizer_config or {}
        self.optimizer = self._setup_optimizer(optimizer_config)
        
        # Match LogSoftmax output
        self.policy_loss_fn = nn.NLLLoss()
        self.value_loss_fn = nn.MSELoss()
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.planning_model.to(self.device)
        if self.reward_model:
            self.reward_model.to(self.device)
        
        self.gradient_clip = gradient_clip
        logger.info(f"Trainer initialized on device {self.device}")

    def _setup_optimizer(self, config: Dict[str, Any]):
        return optim.Adam(
            self.planning_model.parameters(),
            lr=config.get("learning_rate", 1e-4),
            weight_decay=config.get("weight_decay", 1e-5)
        )

    def run_training_step(self, data_batch: List[Dict[str, Any]]):
        """
        Run a single training step on a batch of experience.
        """
        self.optimizer.zero_grad()
        
        # Prepare tensors
        states = torch.stack([d["state"] for d in data_batch]).float().to(self.device)
        true_actions = torch.tensor([d["action_index"] for d in data_batch], dtype=torch.long).to(self.device)
        observed_rewards = torch.tensor([d["reward"] for d in data_batch], dtype=torch.float32).to(self.device)
        
        # Forward pass
        predicted_policy_log_probs, predicted_value = self.planning_model(states)
        
        # Compute losses
        policy_loss = self.policy_loss_fn(predicted_policy_log_probs, true_actions)
        value_loss = self.value_loss_fn(predicted_value.view(-1), observed_rewards)
        total_loss = policy_loss + value_loss
        
        # Backprop
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.planning_model.parameters(), self.gradient_clip)
        self.optimizer.step()
        
        logger.info(
            f"Step complete | Total Loss: {total_loss.item():.4f}, "
            f"Policy Loss: {policy_loss.item():.4f}, Value Loss: {value_loss.item():.4f}"
        )
    
    def save_checkpoint(self, base_dir: str = "./checkpoints"):
        """
        Save planning model checkpoint with timestamped filename.
        """
        os.makedirs(base_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(base_dir, f"planning_model_{timestamp}.pt")
        torch.save(self.planning_model.state_dict(), path)
        logger.info(f"Checkpoint saved to {path}")
        return path

# --- Conceptual Training Loop ---
def run_full_training_loop(
    epochs: int,
    batch_size: int,
    data_buffer: List[Dict[str, Any]],
    optimizer_config: Optional[Dict[str, Any]] = None
):
    """
    Example training loop using the Trainer class.
    """
    planning_model = PlanningModel()
    reward_model = RewardModel()  # placeholder; integrate if needed
    trainer = Trainer(planning_model, reward_model, optimizer_config)

    logger.info("Starting training loop.")
    
    for epoch in range(epochs):
        logger.info(f"--- Epoch {epoch + 1}/{epochs} ---")
        
        if len(data_buffer) == 0:
            logger.warning("Data buffer empty. Skipping epoch.")
            continue
        
        # Sample batch with replacement if buffer smaller than batch size
        if len(data_buffer) < batch_size:
            data_batch = random.choices(data_buffer, k=batch_size)
        else:
            data_batch = random.sample(data_buffer, batch_size)
        
        trainer.run_training_step(data_batch)
        
        # Save checkpoint every 5 epochs
        if (epoch + 1) % 5 == 0:
            trainer.save_checkpoint()
    
    logger.info("Training loop finished.")
