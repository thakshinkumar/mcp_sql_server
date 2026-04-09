"""Query cost evaluation and execution plan analysis."""

import logging
import time
import re
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class CostEvaluator:
    """Evaluates SQL query cost and performance."""
    
    def __init__(self, config):
        self.config = config
    
    def evaluate_query(self, conn, query: str) -> Dict:
        """Evaluate query cost and performance."""
        cursor = conn.cursor()
        metrics = {
            "execution_time_ms": 0,
            "logical_reads": 0,
            "physical_reads": 0,
            "cpu_time_ms": 0,
            "estimated_cost": 0,
            "rows_affected": 0,
            "success": False,
            "error": None
        }
        
        # Check if this is a DDL statement
        query_upper = query.strip().upper()
        is_ddl = any(query_upper.startswith(cmd) for cmd in 
                     ['CREATE', 'ALTER', 'DROP', 'TRUNCATE', 'RENAME'])
        
        try:
            # Enable statistics (only for non-DDL)
            if not is_ddl:
                cursor.execute("SET STATISTICS IO ON")
                cursor.execute("SET STATISTICS TIME ON")
            
            # Execute query and measure time
            start_time = time.time()
            cursor.execute(query)
            
            # Fetch results if SELECT
            if query_upper.startswith("SELECT"):
                rows = cursor.fetchall()
                metrics["rows_affected"] = len(rows)
            else:
                metrics["rows_affected"] = cursor.rowcount
                conn.commit()
            
            end_time = time.time()
            metrics["execution_time_ms"] = (end_time - start_time) * 1000
            
            # Get execution plan (only for SELECT queries)
            if query_upper.startswith("SELECT"):
                try:
                    cursor.execute(f"SET SHOWPLAN_TEXT ON")
                    cursor.execute(query)
                    plan = cursor.fetchall()
                    metrics["estimated_cost"] = self._parse_plan_cost(plan)
                    cursor.execute(f"SET SHOWPLAN_TEXT OFF")
                except:
                    # Fallback: use execution time as cost proxy
                    metrics["estimated_cost"] = metrics["execution_time_ms"]
            else:
                # For DDL/DML, use execution time as cost
                metrics["estimated_cost"] = metrics["execution_time_ms"]
            
            # Disable statistics (only if enabled)
            if not is_ddl:
                cursor.execute("SET STATISTICS IO OFF")
                cursor.execute("SET STATISTICS TIME OFF")
            
            metrics["success"] = True
            
        except Exception as e:
            logger.error(f"Query evaluation failed: {e}")
            metrics["error"] = str(e)
            metrics["success"] = False
        
        finally:
            cursor.close()
        
        return metrics
    
    def _parse_plan_cost(self, plan) -> float:
        """Parse execution plan to extract cost."""
        # Simplified cost extraction
        # In production, parse XML execution plan
        try:
            if plan and len(plan) > 0:
                plan_text = str(plan)
                # Look for cost indicators
                cost_match = re.search(r'Cost:\s*(\d+\.?\d*)', plan_text)
                if cost_match:
                    return float(cost_match.group(1))
        except:
            pass
        return 0.0
    
    def calculate_total_cost(self, metrics: Dict) -> float:
        """Calculate weighted total cost."""
        cost_weight = self.config.optimizer.cost_weight
        latency_weight = self.config.optimizer.latency_weight
        
        normalized_cost = metrics.get("estimated_cost", 0) / 100.0
        normalized_latency = metrics.get("execution_time_ms", 0) / 1000.0
        
        total_cost = (cost_weight * normalized_cost + 
                     latency_weight * normalized_latency)
        
        return total_cost
