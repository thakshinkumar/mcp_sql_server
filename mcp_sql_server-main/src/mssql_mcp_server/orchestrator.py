"""Main orchestrator for voice-enabled self-optimizing SQL server."""

import logging
import pymssql
from typing import Dict, List, Any

from .config import config
from .nl_to_sql.llm_client import LLMClient
from .optimizer.cost_evaluator import CostEvaluator
from .rl.q_learning_agent import QLearningAgent
from .schema import create_metrics_tables

logger = logging.getLogger(__name__)


class SQLOrchestrator:
    """Orchestrates NL-to-SQL conversion, optimization, and learning."""
    
    def __init__(self):
        self.config = config
        self.llm_client = LLMClient(config)
        self.cost_evaluator = CostEvaluator(config)
        self.rl_agent = QLearningAgent(config)
        self._initialized = False
    
    def initialize(self, conn):
        """Initialize orchestrator with database connection."""
        if self._initialized:
            return
        
        try:
            # Create metrics tables
            create_metrics_tables(conn)
            
            # Load Q-table from database
            self.rl_agent.load_q_table(conn)
            
            self._initialized = True
            logger.info("Orchestrator initialized successfully")
        except Exception as e:
            logger.error(f"Orchestrator initialization failed: {e}")
    
    def process_query(self, user_input: str, conn) -> Dict[str, Any]:
        """Process user query through the full pipeline."""
        self.initialize(conn)
        
        result = {
            "input": user_input,
            "candidates": [],
            "selected_sql": None,
            "result": None,
            "metrics": {},
            "error": None
        }
        
        try:
            # Step 2: Generate SQL candidates
            logger.info(f"Generating SQL candidates for: {user_input}")
            candidates = self.llm_client.generate_sql(user_input)
            result["candidates"] = candidates
            
            if not candidates:
                raise ValueError("No SQL candidates generated")
            
            # Step 3: RL agent selects best candidate
            state = self.rl_agent.get_state(user_input, candidates)
            action = self.rl_agent.select_action(state, len(candidates))
            selected_sql = candidates[action]
            result["selected_sql"] = selected_sql
            
            logger.info(f"Selected candidate {action}: {selected_sql[:100]}")
            
            # Step 4: Execute and evaluate
            metrics = self.cost_evaluator.evaluate_query(conn, selected_sql)
            result["metrics"] = metrics
            
            if metrics["success"]:
                # For SELECT queries, fetch results
                if selected_sql.strip().upper().startswith("SELECT"):
                    cursor = conn.cursor()
                    try:
                        cursor.execute(selected_sql)
                        rows = cursor.fetchall()
                        if cursor.description:
                            columns = [desc[0] for desc in cursor.description]
                            result["result"] = {
                                "columns": columns,
                                "rows": [list(row) for row in rows]
                            }
                        else:
                            result["result"] = {"message": "Query executed successfully"}
                    finally:
                        cursor.close()
                else:
                    # For DDL/DML queries, they were already executed in cost_evaluator
                    result["result"] = {
                        "message": f"Query executed successfully. Rows affected: {metrics['rows_affected']}"
                    }
                
                # Step 5: RL feedback
                reward = self.rl_agent.calculate_reward(metrics)
                self.rl_agent.update(state, action, reward)
                
                # Save metrics to database (don't let this fail the whole query)
                try:
                    self._save_query_history(conn, user_input, selected_sql, metrics, candidates, action)
                except Exception as save_error:
                    logger.warning(f"Failed to save query history: {save_error}")
                
                # Periodically save Q-table
                try:
                    if self.rl_agent.stats["total_updates"] % 10 == 0:
                        self.rl_agent.save_q_table(conn)
                except Exception as qtable_error:
                    logger.warning(f"Failed to save Q-table: {qtable_error}")
            
            else:
                result["error"] = metrics.get("error", "Query execution failed")
                # Negative reward for failed query
                self.rl_agent.update(state, action, -10.0)
        
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            # Only set error if we don't already have a successful result
            if not result.get("result"):
                result["error"] = str(e)
            else:
                # We have a result, so log the error but don't fail the request
                logger.warning(f"Post-execution error (query succeeded): {e}")
        
        return result
    
    def _save_query_history(self, conn, nl_query: str, selected_sql: str, 
                           metrics: Dict, candidates: List[str], selected_idx: int):
        """Save query execution history to database."""
        cursor = conn.cursor()
        try:
            # Insert query history
            cursor.execute("""
                INSERT INTO query_history 
                (original_nl, generated_sql, execution_time_ms, cost_estimate, 
                 rows_affected, success, error_message, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                nl_query,
                selected_sql,
                metrics.get("execution_time_ms", 0),
                metrics.get("estimated_cost", 0),
                metrics.get("rows_affected", 0),
                metrics.get("success", False),
                metrics.get("error"),
                "default_user"
            ))
            
            # Get inserted ID
            cursor.execute("SELECT @@IDENTITY")
            history_id = cursor.fetchone()[0]
            
            # Insert all candidates
            for idx, candidate in enumerate(candidates):
                cursor.execute("""
                    INSERT INTO query_candidates
                    (query_history_id, candidate_sql, estimated_cost, actual_cost,
                     execution_time_ms, selected)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    history_id,
                    candidate,
                    0,  # Would need to evaluate each
                    metrics.get("estimated_cost", 0) if idx == selected_idx else 0,
                    metrics.get("execution_time_ms", 0) if idx == selected_idx else 0,
                    idx == selected_idx
                ))
            
            conn.commit()
            logger.info(f"Saved query history (ID: {history_id})")
        
        except Exception as e:
            logger.error(f"Failed to save query history: {e}")
        finally:
            cursor.close()
    
    def get_stats(self) -> Dict:
        """Get orchestrator statistics."""
        return {
            "rl_agent": self.rl_agent.get_stats(),
            "initialized": self._initialized
        }


# Global orchestrator instance
orchestrator = SQLOrchestrator()
