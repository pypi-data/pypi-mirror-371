from dataclasses import dataclass
from typing import Optional
import torch

# Try to import nashpy for Nash equilibrium computation
try:
    import nashpy
    NASH_AVAILABLE = True
except ImportError:
    NASH_AVAILABLE = False

@dataclass
class EvaluationConfig:
    """Configuration for Gauntlet evaluation."""
    num_episodes: int = 1000
    max_episode_steps: int = 200
    batch_size: int = 32
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    seed: int = 42
    parallel_workers: int = 0
    save_trajectories: bool = False
    compute_exploitability: bool = True
    enable_continual_eval: bool = True
    population_size: int = 5
    tournament_rounds: int = 2
    
    # New configuration options for generalization
    support_continuous_actions: bool = True
    support_multi_agent: bool = True
    max_agents: int = 1000  # For large-scale evaluations
    vectorized_evaluation: bool = False
    
    # Visualization configuration
    save_visualizations: bool = True
    visualization_format: str = "png"  # png, pdf, svg
    dpi: int = 300
    style: str = "seaborn-v0_8"  # matplotlib style
    
    # Metrics configuration
    use_nashpy_metrics: bool = NASH_AVAILABLE
    compute_transfer_metrics: bool = True
    compute_population_diversity: bool = True
    regret_bound: float = 1.0  # Upper bound for regret computation

@dataclass
class ContinualConfig:
    """Configuration for continual learning evaluation."""
    num_tasks: int = 100
    task_transition_episodes: int = 50
    forgetting_threshold: float = 0.1
    plasticity_threshold: float = 0.05
    memory_replay: bool = True
    replay_buffer_size: int = 10000

@dataclass
class RobustnessMetrics:
    """Comprehensive robustness metrics."""
    overall_win_rate: float = 0.0
    min_win_rate: float = 0.0
    max_win_rate: float = 0.0
    win_rate_std: float = 0.0
    avg_reward: float = 0.0
    worst_case_reward: float = 0.0
    exploitability: float = 0.0
    regret: float = 0.0
    adaptation_rate: float = 0.0
    forgetting_rate: float = 0.0
    plasticity_score: float = 0.0
    population_diversity: float = 0.0
    # May be unavailable if no formal (A,B) is provided
    nash_conv: Optional[float] = None
    
    # New metrics for transfer learning and population analysis
    forward_transfer: float = 0.0
    backward_transfer: float = 0.0
    population_entropy: float = 0.0
    jensen_shannon_divergence: float = 0.0
    nash_equilibrium_distance: float = 0.0
    regret_bound_achieved: bool = False
    # --- NEW (general-sum support) ---
    general_sum: bool = False
    cooperation_rate: float = 0.0
    social_welfare: float = 0.0
    cc_rate_tft: float = 0.0
    # Domain-specific extras (not folded into robustness score)
    ipd_exploitability_proxy: float = 0.0
    cc_rate_grudger: float = 0.0
    
    @property
    def robustness_score(self) -> float:
        """Comprehensive robustness score combining multiple metrics.
        Ensures each component is on [0,1] and the weighted sum also stays in [0,1].
        """
        def clip01(x: float) -> float:
            try:
                return float(min(1.0, max(0.0, x)))
            except Exception:
                return 0.0

        # Normalize reward-like signals to [0,1] using dynamic ranges when available.
        # Fallback to legacy [-1,1] and [-2,2] assumptions if ranges are not provided.
        if hasattr(self, 'reward_min') and hasattr(self, 'reward_max') and isinstance(getattr(self, 'reward_min'), (int, float)) and isinstance(getattr(self, 'reward_max'), (int, float)) and getattr(self, 'reward_max') > getattr(self, 'reward_min'):
            avg_reward_n = clip01((self.avg_reward - getattr(self, 'reward_min')) / (getattr(self, 'reward_max') - getattr(self, 'reward_min')))
        else:
            avg_reward_n = clip01((self.avg_reward + 1.0) / 2.0)

        if hasattr(self, 'social_welfare'):
            if hasattr(self, 'social_welfare_min') and hasattr(self, 'social_welfare_max') and isinstance(getattr(self, 'social_welfare_min'), (int, float)) and isinstance(getattr(self, 'social_welfare_max'), (int, float)) and getattr(self, 'social_welfare_max') > getattr(self, 'social_welfare_min'):
                social_welfare_n = clip01((self.social_welfare - getattr(self, 'social_welfare_min')) / (getattr(self, 'social_welfare_max') - getattr(self, 'social_welfare_min')))
            else:
                social_welfare_n = clip01((self.social_welfare + 2.0) / 4.0)
        else:
            social_welfare_n = 0.0
        low_exploitability = clip01(1.0 - self.exploitability)
        low_regret = clip01(1.0 - self.regret)
        low_variance = clip01(1.0 - self.win_rate_std)
        fwd_transfer = clip01(self.forward_transfer)
        population_div = clip01(self.population_diversity)
        min_wr = clip01(self.min_win_rate)
        overall_wr = clip01(self.overall_win_rate)

        if self.general_sum:
            # General-sum emphasis
            weights = {
                'avg_reward': 0.30,
                'social_welfare': 0.20,
                'cooperation': 0.15,
                'low_exploitability': 0.12,
                'low_regret': 0.10,
                'population_diversity': 0.08,
                'low_variance': 0.05,
            }
            score = (
                weights['avg_reward'] * avg_reward_n +
                weights['social_welfare'] * social_welfare_n +
                weights['cooperation'] * clip01(self.cooperation_rate) +
                weights['low_exploitability'] * low_exploitability +
                weights['low_regret'] * low_regret +
                weights['population_diversity'] * population_div +
                weights['low_variance'] * low_variance
            )
        else:
            # Zero-sum emphasis
            weights = {
                'overall_wr': 0.25,
                'min_wr': 0.15,
                'low_exploitability': 0.12,
                'low_regret': 0.12,
                'adaptation_rate': 0.10,
                'plasticity': 0.08,
                'forward_transfer': 0.08,
                'low_forgetting': 0.05,
                'population_diversity': 0.05,
            }
            score = (
                weights['overall_wr'] * overall_wr +
                weights['min_wr'] * min_wr +
                weights['low_exploitability'] * low_exploitability +
                weights['low_regret'] * low_regret +
                weights['adaptation_rate'] * clip01(self.adaptation_rate) +
                weights['plasticity'] * clip01(self.plasticity_score) +
                weights['forward_transfer'] * fwd_transfer +
                weights['low_forgetting'] * clip01(1.0 - self.forgetting_rate) +
                weights['population_diversity'] * population_div
            )

        return clip01(score)
