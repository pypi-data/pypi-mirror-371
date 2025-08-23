# Gauntlet MARL Benchmark Package
__version__ = "0.1.1"

# Expose the most important classes to the top level
from .benchmark import EnhancedGauntletBenchmark
from .configs import EvaluationConfig, RobustnessMetrics
from .challengers import ChallengerAgent, NeuralAdversaryAgent  # Add any others you want to be user-creatable
from .environments import Environment, GeneralizedEnvironment

