from abc import ABC, abstractmethod
from collections import deque, defaultdict
from typing import List, Optional, Dict, Tuple, Union, Callable
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from .environments import Environment
from .utils import PatternDetector, CounterStrategy, MetaLearner
from gymnasium.spaces import Space, Discrete, Box

class ChallengerAgent(ABC):
    """Abstract base class for challenger agents."""
    
    def __init__(self, name: str, difficulty: str = "medium"):
        self.name = name
        self.difficulty = difficulty
        self.history = deque(maxlen=1000)
        self.adaptation_rate = 0.1
    
    @abstractmethod
    def act(self, observation: torch.Tensor, opponent_history: Optional[List] = None) -> int:
        """Select an action given observation and opponent history."""
        pass
    
    # --- NEW REQUIRED PROPERTY ---
    @property
    @abstractmethod
    def compatible_action_space(self) -> Space:
        """The Gymnasium action space this challenger is compatible with."""
        pass
    
    @abstractmethod
    def update(self, reward: float, observation: torch.Tensor, action: int):
        """Update internal state based on outcome."""
        pass
    
    def reset(self):
        """Reset agent state for new episode."""
        self.history.clear()


class AdaptiveCounterAgent(ChallengerAgent):
    """Counter-exploiter that adapts to opponent patterns."""
    
    def __init__(self, name: str = "AdaptiveCounter"):
        super().__init__(name, "hard")
        self.pattern_detector = PatternDetector()
        self.counter_strategy = CounterStrategy()
        self.meta_learner = MetaLearner()
        self._action_space = Discrete(3) # This agent is hard-coded for RPS
 
    # --- NEW ---
    @property
    def compatible_action_space(self) -> Space:
        return self._action_space

    def act(self, observation: torch.Tensor, opponent_history: Optional[List] = None) -> int:
        """
        Select an action given observation and opponent history.
        
        CORRECTION: The modulo operation now correctly uses `3` (the number of actions in RPS)
        instead of `observation.shape[-1]` (the observation dimension), preventing the IndexError.
        """
        num_actions = 3  # For Rock-Paper-Scissors

        if opponent_history and len(opponent_history) > 10:
            pattern = self.pattern_detector.detect(opponent_history)
            counter_action = self.counter_strategy.counter(pattern)
            meta_adjustment = self.meta_learner.adjust(self.history, opponent_history)
            
            # Ensure the final action is within the valid range [0, 2]
            return (counter_action + meta_adjustment) % num_actions
        
        return random.randint(0, num_actions - 1)
    
    def update(self, reward: float, observation: torch.Tensor, action: int):
        self.history.append((action, reward))
        self.meta_learner.update(reward)

class PopulationBasedAgent(ChallengerAgent):
    """Agent that maintains a population of diverse strategies."""
    # --- NEW ---
    def __init__(self, name: str = "PopulationBased", population_size: int = 10):
        super().__init__(name, "expert")
        self.population = [self._create_diverse_strategy(i) for i in range(population_size)]
        self.selection_probs = np.ones(population_size) / population_size
        self.performance_history = defaultdict(list)
        self._action_space = Discrete(3) # This agent is hard-coded for RPS
    # --- NEW ---
    @property
    def compatible_action_space(self) -> Space:
        return self._action_space

    def _create_diverse_strategy(self, seed: int) -> Callable:
        """Create a diverse strategy based on seed."""
        np.random.seed(seed)
        # Added a default case to prevent returning None
        strategy_type = np.random.choice(['cyclic', 'frequency', 'pattern', 'mixed'])
        
        if strategy_type == 'cyclic':
            cycle = np.random.permutation(3).tolist()
            return lambda h: cycle[len(h) % len(cycle)] if h else 0
        elif strategy_type == 'frequency':
            freqs = np.random.dirichlet([1, 1, 1])
            return lambda h: np.random.choice(3, p=freqs)
        # Add more strategy types...
        else: # Default case for 'pattern', 'mixed', or any other type
            return lambda h: random.randint(0, 2)
        
    def act(self, observation: torch.Tensor, opponent_history: Optional[List] = None) -> int:
        selected_strategy = np.random.choice(self.population, p=self.selection_probs)
        return selected_strategy(opponent_history or [])
    
    def update(self, reward: float, observation: torch.Tensor, action: int):
        # Update selection probabilities based on performance
        self.history.append((action, reward))
        # Implement evolutionary selection logic here

# ============================================================================
# Corrected NeuralAdversaryAgent with Lazy Initialization
# ============================================================================


class NeuralAdversaryAgent(ChallengerAgent):
    """
    Neural network-based adversary that dynamically adapts its input size
    to the environment it is playing in.
    """
    
    # --- START: CORRECTED __init__ METHOD ---
    def __init__(self, name: str = "NeuralAdversary", hidden_dim: int = 64, 
                 action_space: Space = Discrete(3), noise_level: float = 0.0):
        super().__init__(name, "expert")
        # Store the provided action space
        self._action_space = action_space
        
        # Derive properties directly from the action space, making the agent general
        self.is_continuous = isinstance(self._action_space, Box)
        if self.is_continuous:
            self.action_dim = self._action_space.shape[0]
        else:
            self.action_dim = self._action_space.n
            
        self.hidden_dim = hidden_dim # Store hidden_dim for later use
        self.noise_level = noise_level

        # Lazy Initialization for the network and optimizer
        self.network = None
        self.optimizer = None
        self.memory = deque(maxlen=10000)
    # --- END: CORRECTED __init__ METHOD ---

    # --- NEW REQUIRED PROPERTY ---
    @property
    def compatible_action_space(self) -> Space:
        """The Gymnasium action space this challenger is compatible with."""
        return self._action_space

    def _initialize_network(self, observation: torch.Tensor):
        """
        Builds the neural network and optimizer based on the shape of the
        first observation tensor received from the environment.
        """
        input_dim = observation.shape[-1]
        device = observation.device
        

        if self.is_continuous:
            self.network = nn.Sequential(
                nn.Linear(input_dim, self.hidden_dim),
                nn.ReLU(),
                nn.Linear(self.hidden_dim, self.hidden_dim),
                nn.ReLU(),
                nn.Linear(self.hidden_dim, self.action_dim * 2),
            )
        else:
            self.network = nn.Sequential(
                nn.Linear(input_dim, self.hidden_dim),
                nn.ReLU(),
                nn.Linear(self.hidden_dim, self.hidden_dim),
                nn.ReLU(),
                nn.Linear(self.hidden_dim, self.action_dim),
                nn.Softmax(dim=-1)
            )
        
        self.network.to(device)
        self.optimizer = optim.Adam(self.network.parameters(), lr=1e-3)

    def act(self, observation: torch.Tensor, opponent_history: Optional[List] = None) -> Union[int, List[float]]:
        if self.network is None:
            self._initialize_network(observation)

        if len(observation.shape) == 1:
            observation = observation.unsqueeze(0)
        
        with torch.no_grad():
            if self.is_continuous:
                output = self.network(observation)
                mean = output[:, :self.action_dim]
                log_std = output[:, self.action_dim:]
                std = torch.exp(log_std)
                action = torch.normal(mean, std)
                action = torch.clamp(action, -1.0, 1.0)
                return action.squeeze().tolist()
            else:
                action_probs = self.network(observation)
                action = torch.multinomial(action_probs, 1).item()
                return action
    
    def update(self, reward: float, observation: torch.Tensor, action: Union[int, List[float]]):
        if self.network is None:
            return

        self.memory.append((observation.cpu(), action, reward))
        if len(self.memory) > 32:
            self._train_batch()
    
    def _train_batch(self):
        if self.optimizer is None:
            return

        batch = random.sample(self.memory, min(32, len(self.memory)))
        observations, actions, rewards = zip(*batch)
        
        device = next(self.network.parameters()).device
        observations = torch.stack(observations).to(device)
        rewards = torch.tensor(rewards, dtype=torch.float32).to(device)
        
        if self.is_continuous:
            actions = torch.tensor(actions, dtype=torch.float32).to(device)
            output = self.network(observations)
            mean = output[:, :self.action_dim]
            log_std = output[:, self.action_dim:]
            std = torch.exp(log_std)
            dist = torch.distributions.Normal(mean, std)
            log_probs = dist.log_prob(actions).sum(dim=-1)
            loss = -(log_probs * rewards).mean()
        else:
            actions = torch.tensor(actions, dtype=torch.long).to(device)
            action_probs = self.network(observations)
            selected_probs = action_probs.gather(1, actions.unsqueeze(1)).squeeze()
            loss = -(torch.log(selected_probs + 1e-9) * rewards).mean()
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def reset(self):
        super().reset()


class MetaLearnerAgent(ChallengerAgent):
    def __init__(self, action_space: Space = Discrete(3)):
        super().__init__("MetaLearner", "medium")
        self.meta = MetaLearner()
        self._action_space = action_space
        self._action_history = deque(maxlen=100)
    
    @property
    def compatible_action_space(self) -> Space:
        return self._action_space
    
    def act(self, observation: torch.Tensor, opponent_history: Optional[List] = None) -> int:
        adj = self.meta.adjust(self.history, opponent_history or [])
        # Map adjustment {-1,0,1} into valid discrete action space
        if isinstance(self._action_space, Discrete):
            n = int(self._action_space.n)
            base = 0
            return (base + adj) % n
        return 0
    
    def update(self, reward: float, observation: torch.Tensor, action: int):
        self.meta.update(float(reward))
        self._action_history.append(int(action))
    
    def reset(self):
        super().reset()
        self._action_history.clear()

class ForgivingTFTBot(ChallengerAgent):
    def __init__(self, action_space: Space = Discrete(2)):
        super().__init__("ForgivingTFT", "medium")
        self._action_space = action_space
        self.defect_streak = 0
    
    @property
    def compatible_action_space(self) -> Space:
        return self._action_space
    
    def act(self, observation: torch.Tensor, opponent_history: Optional[List] = None) -> int:
        if not opponent_history:
            return 0
        last = int(opponent_history[-1])
        if last == 1:
            self.defect_streak += 1
        else:
            self.defect_streak = max(0, self.defect_streak - 1)
        if self.defect_streak >= 2:
            return 1
        return last
    
    def update(self, reward: float, observation: torch.Tensor, action: int):
        pass
    
    def reset(self):
        super().reset()
        self.defect_streak = 0

class KuhnBluffer(ChallengerAgent):
    def __init__(self):
        super().__init__("Kuhn_Bluffer", "medium")
        self._action_space = Discrete(2)
    
    @property
    def compatible_action_space(self) -> Space:
        return self._action_space
    
    def act(self, observation: torch.Tensor, opponent_history: Optional[List] = None) -> int:
        if observation.dim() > 1:
            observation = observation[0]
        card = int(torch.argmax(observation).item())
        if card == 0:
            return 1  # bluff with J
        if card == 2:
            return 0  # slow-play K
        return random.randint(0, 1)
    
    def update(self, reward: float, observation: torch.Tensor, action: int):
        pass

class KuhnConservative(ChallengerAgent):
    def __init__(self):
        super().__init__("Kuhn_Conservative", "medium")
        self._action_space = Discrete(2)
    
    @property
    def compatible_action_space(self) -> Space:
        return self._action_space
    
    def act(self, observation: torch.Tensor, opponent_history: Optional[List] = None) -> int:
        if observation.dim() > 1:
            observation = observation[0]
        card = int(torch.argmax(observation).item())
        if card < 2:
            return 0
        return 1
    
    def update(self, reward: float, observation: torch.Tensor, action: int):
        pass
