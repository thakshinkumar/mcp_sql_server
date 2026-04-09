"""Q-Learning agent for query optimization."""

import logging
import hashlib
import random
from typing import Dict, List, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


class QLearningAgent:
    """Q-Learning agent for selecting optimal SQL queries."""
    
    def __init__(self, config):
        self.config = config
        self.enabled = config.rl.enabled
        self.alpha = config.rl.learning_rate
        self.gamma = config.rl.discount_factor
        self.epsilon = config.rl.epsilon
        self.epsilon_decay = config.rl.epsilon_decay
        self.min_epsilon = config.rl.min_epsilon
        
        # Q-table: {state_hash: {action_id: q_value}}
        self.q_table = defaultdict(lambda: defaultdict(float))
        
        # Statistics
        self.stats = {
            "total_updates": 0,
            "explorations": 0,
            "exploitations": 0
        }
    
    def get_state(self, nl_query: str, candidates: List[str]) -> str:
        """Generate state representation."""
        # State features: query pattern, number of candidates
        state_features = {
            "query_length": len(nl_query),
            "num_candidates": len(candidates),
            "has_join": any("join" in c.lower() for c in candidates),
            "has_subquery": any("(" in c and "select" in c.lower() for c in candidates),
            "has_aggregation": any(agg in nl_query.lower() for agg in ["count", "sum", "avg", "max", "min"])
        }
        
        # Hash state features
        state_str = str(sorted(state_features.items()))
        state_hash = hashlib.md5(state_str.encode()).hexdigest()[:16]
        
        return state_hash
    
    def select_action(self, state: str, num_actions: int) -> int:
        """Select action using epsilon-greedy policy."""
        if not self.enabled:
            return 0  # Default to first candidate
        
        # Exploration vs exploitation
        if random.random() < self.epsilon:
            # Explore: random action
            action = random.randint(0, num_actions - 1)
            self.stats["explorations"] += 1
            logger.info(f"RL: Exploring - selected action {action}")
        else:
            # Exploit: best known action
            q_values = self.q_table[state]
            if q_values:
                action = max(range(num_actions), 
                           key=lambda a: q_values.get(a, 0.0))
            else:
                action = 0  # Default if no history
            self.stats["exploitations"] += 1
            logger.info(f"RL: Exploiting - selected action {action} (Q={q_values.get(action, 0.0):.3f})")
        
        return action
    
    def update(self, state: str, action: int, reward: float, next_state: str = None):
        """Update Q-value using Q-learning update rule."""
        if not self.enabled:
            return
        
        current_q = self.q_table[state][action]
        
        if next_state:
            # Q(s,a) = Q(s,a) + α[r + γ*max(Q(s',a')) - Q(s,a)]
            max_next_q = max(self.q_table[next_state].values()) if self.q_table[next_state] else 0.0
            new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        else:
            # Terminal state
            new_q = current_q + self.alpha * (reward - current_q)
        
        self.q_table[state][action] = new_q
        self.stats["total_updates"] += 1
        
        # Decay epsilon
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
        
        logger.info(f"RL Update: state={state[:8]}, action={action}, reward={reward:.3f}, "
                   f"Q: {current_q:.3f} -> {new_q:.3f}, ε={self.epsilon:.3f}")
    
    def calculate_reward(self, metrics: Dict) -> float:
        """Calculate reward from query execution metrics."""
        if not metrics.get("success", False):
            return -10.0  # Penalty for failed queries
        
        # Reward = -1 * (normalized_latency + normalized_cost)
        # Lower latency and cost = higher reward
        latency_ms = metrics.get("execution_time_ms", 1000)
        cost = metrics.get("estimated_cost", 100)
        
        # Normalize (assuming max latency 10s, max cost 1000)
        normalized_latency = min(latency_ms / 10000.0, 1.0)
        normalized_cost = min(cost / 1000.0, 1.0)
        
        reward = -1.0 * (normalized_latency + normalized_cost)
        
        return reward
    
    def get_stats(self) -> Dict:
        """Get agent statistics."""
        return {
            "enabled": self.enabled,
            "total_updates": self.stats["total_updates"],
            "explorations": self.stats["explorations"],
            "exploitations": self.stats["exploitations"],
            "epsilon": self.epsilon,
            "q_table_size": len(self.q_table)
        }
    
    def save_q_table(self, conn):
        """Save Q-table to database."""
        if not self.enabled:
            return
        
        cursor = conn.cursor()
        try:
            for state_hash, actions in self.q_table.items():
                for action_id, q_value in actions.items():
                    cursor.execute("""
                        MERGE INTO q_table AS target
                        USING (SELECT ? AS state_hash, ? AS action_id, ? AS q_value) AS source
                        ON target.state_hash = source.state_hash AND target.action_id = source.action_id
                        WHEN MATCHED THEN
                            UPDATE SET q_value = source.q_value, visit_count = visit_count + 1, last_updated = GETDATE()
                        WHEN NOT MATCHED THEN
                            INSERT (state_hash, action_id, q_value, visit_count, last_updated)
                            VALUES (source.state_hash, source.action_id, source.q_value, 1, GETDATE());
                    """, (state_hash, action_id, q_value))
            conn.commit()
            logger.info(f"Saved Q-table with {len(self.q_table)} states")
        except Exception as e:
            logger.error(f"Failed to save Q-table: {e}")
        finally:
            cursor.close()
    
    def load_q_table(self, conn):
        """Load Q-table from database."""
        if not self.enabled:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT state_hash, action_id, q_value FROM q_table")
            rows = cursor.fetchall()
            
            for state_hash, action_id, q_value in rows:
                self.q_table[state_hash][action_id] = q_value
            
            logger.info(f"Loaded Q-table with {len(self.q_table)} states")
        except Exception as e:
            logger.error(f"Failed to load Q-table: {e}")
        finally:
            cursor.close()
