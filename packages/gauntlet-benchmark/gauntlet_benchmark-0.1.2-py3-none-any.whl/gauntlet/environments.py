from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Union
import torch

from gymnasium.spaces import Space, Discrete, Box

class Environment(ABC):
    """Abstract environment interface."""
    
    @abstractmethod
    def reset(self) -> torch.Tensor:
        pass
    
    @abstractmethod
    def step(self, actions: List[int]) -> Tuple[torch.Tensor, List[float], bool, Dict]:
        pass
    
    @property
    @abstractmethod
    def observation_space(self) -> Space:
        pass
    
    @property
    @abstractmethod
    def action_space(self) -> Space:
        pass
    
    @property
    def num_actions(self) -> int:
        """Get number of actions (for discrete) or action dimension (for continuous)."""
        if isinstance(self.action_space, Discrete):
            return self.action_space.n
        elif isinstance(self.action_space, Box):
            return self.action_space.shape[0]
        else:
            raise ValueError(f"Unsupported action space type: {type(self.action_space)}")
    
    @property
    def is_continuous_action(self) -> bool:
        """Check if environment uses continuous actions."""
        return isinstance(self.action_space, Box)
    
    @property
    def is_discrete_action(self) -> bool:
        """Check if environment uses discrete actions."""
        return isinstance(self.action_space, Discrete)

class GeneralizedEnvironment(Environment):
    """Generalized environment wrapper that supports both discrete and continuous actions."""
    
    def __init__(self, base_env: Environment):
        self.base_env = base_env
        self._validate_action_space()
    
    def _validate_action_space(self):
        """Validate that the action space is supported."""
        if not (isinstance(self.action_space, (Discrete, Box))):
            raise ValueError(f"Unsupported action space: {type(self.action_space)}")
    
    def reset(self) -> torch.Tensor:
        return self.base_env.reset()
    
    def step(self, actions: List[Union[int, float]]) -> Tuple[torch.Tensor, List[float], bool, Dict]:
        # Validate actions based on action space
        if self.is_discrete_action:
            actions = [int(action) for action in actions]
            for action in actions:
                if not (0 <= action < self.num_actions):
                    raise ValueError(f"Discrete action {action} out of range [0, {self.num_actions})")
        elif self.is_continuous_action:
            actions = [float(action) for action in actions]
            for action in actions:
                if not (self.action_space.low[0] <= action <= self.action_space.high[0]):
                    raise ValueError(f"Continuous action {action} out of bounds")
        
        return self.base_env.step(actions)
    
    @property
    def observation_space(self) -> Space:
        return self.base_env.observation_space
    
    @property
    def action_space(self) -> Space:
        return self.base_env.action_space
