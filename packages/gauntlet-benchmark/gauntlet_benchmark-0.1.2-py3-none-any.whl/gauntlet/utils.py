
from typing import List, Optional, Dict
from collections import deque, defaultdict
import random
import numpy as np

class PatternDetector:
    """Detects patterns in opponent behavior."""
    
    def __init__(self):
        self.min_pattern_length = 2
        self.max_pattern_length = 10
    
    def detect(self, history: List[int]) -> Optional[List[int]]:
        """Detect repeating patterns in history."""
        if len(history) < self.min_pattern_length * 2:
            return None
            
        for pattern_length in range(self.min_pattern_length, min(self.max_pattern_length, len(history) // 2)):
            pattern = history[-pattern_length:]
            if self._is_repeating_pattern(history, pattern):
                return pattern
        return None
    
    def _is_repeating_pattern(self, history: List[int], pattern: List[int]) -> bool:
        """Check if pattern repeats in recent history."""
        pattern_len = len(pattern)
        if len(history) < pattern_len * 2:
            return False
        
        for i in range(pattern_len):
            if history[-(pattern_len * 2) + i] != pattern[i]:
                return False
        return True

class CounterStrategy:
    """Implements counter-strategies against detected patterns."""
    
    def counter(self, pattern: Optional[List[int]]) -> int:
        """Generate counter-action for detected pattern."""
        if pattern is None:
            return random.randint(0, 2)
        
        # Predict next action in pattern
        predicted_action = pattern[0]  # Simplified prediction
        # Return counter-action (Rock->Paper, Paper->Scissors, Scissors->Rock)
        return (predicted_action + 1) % 3

class MetaLearner:
    """Meta-learning component for strategy adaptation."""
    
    def __init__(self):
        self.strategy_performance = defaultdict(float)
        self.current_strategy = "default"
        self.exploration_rate = 0.1
    
    def adjust(self, self_history: deque, opponent_history: List[int]) -> int:
        """Meta-adjustment based on performance history."""
        if len(self_history) < 10:
            return 0
        
        recent_performance = np.mean([reward for _, reward in list(self_history)[-10:]])
        if recent_performance < 0:
            return random.randint(-1, 1)  # Add randomness if performing poorly
        return 0
    
    def update(self, reward: float):
        """Update meta-learning based on reward."""
        self.strategy_performance[self.current_strategy] += reward


class TaskGenerator:
    """Generates diverse tasks for continual learning evaluation."""
    
    def __init__(self):
        self.task_types = ['adversarial', 'cooperative', 'mixed', 'noisy', 'distribution_shift']
    
    def generate_sequence(self, num_tasks: int) -> List[Dict]:
        """Generate a sequence of diverse tasks."""
        tasks = []
        
        for i in range(num_tasks):
            task_type = random.choice(self.task_types)
            task = self._generate_task(task_type, i)
            tasks.append(task)
        
        return tasks
    
    def _generate_task(self, task_type: str, task_id: int) -> Dict:
        """Generate a specific task based on type."""
        if task_type == 'adversarial':
            return {
                'id': task_id,
                'type': task_type,
                'challengers': ['AdaptiveCounter', 'NeuralAdversary'],
                'difficulty': 'hard'
            }
        elif task_type == 'cooperative':
            return {
                'id': task_id,
                'type': task_type,
                'challengers': ['TitForTat', 'Copycat'],
                'difficulty': 'medium'
            }
        elif task_type == 'noisy':
            return {
                'id': task_id,
                'type': task_type,
                'challengers': ['NoisyUniform', 'AdversarialNoise'],
                'difficulty': 'medium'
            }
        else:
            return {
                'id': task_id,
                'type': 'mixed',
                'challengers': random.sample(list(self.challengers.keys()), 3),
                'difficulty': 'varied'
            }

class ForgettingDetector:
    """Detects catastrophic forgetting in continual learning."""
    
    def compute_forgetting(self, task_performance: List[float], current_task: int) -> float:
        """Compute forgetting score based on performance degradation."""
        if current_task < 1:
            return 0.0
        
        # Compare current performance on old tasks vs original performance
        original_performance = task_performance[0]
        current_performance = task_performance[-1]
        
        forgetting = max(0, original_performance - current_performance)
        return forgetting

class PlasticityEvaluator:
    """Evaluates plasticity (ability to learn new tasks)."""
    
    def compute_plasticity(self, task_performance: float, task_id: int) -> float:
        """Compute plasticity score based on learning speed."""
        # Simplified plasticity computation
        baseline_performance = 0.33  # Random performance in RPS
        improvement = max(0, task_performance - baseline_performance)
        
        # Normalize by task difficulty (later tasks assumed harder)
        difficulty_factor = 1.0 + (task_id * 0.01)
        plasticity = improvement / difficulty_factor
        
        return min(plasticity, 1.0)
