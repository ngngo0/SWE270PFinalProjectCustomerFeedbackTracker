"""
Metrics Tracking Utility Module for Multi-Agent Systems

This module provides comprehensive tracking of API calls, token usage,
and execution time for multi-agent systems using MCP.

Usage:
    from core.metrics_utils import MetricsTracker, get_global_tracker
    
    tracker = get_global_tracker()
    tracker.start_tracking()
    tracker.record_api_call('agent_name', input_tokens=100, output_tokens=50)
    tracker.end_tracking()
    tracker.print_summary()
"""

import json
import logging
from datetime import datetime
from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class AgentMetrics:
    """Metrics for a single agent"""
    api_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    tool_calls: int = 0
    iterations: int = 0
    errors: int = 0
    
    def add_api_call(self, input_tokens: int = 0, output_tokens: int = 0):
        """Record an API call"""
        self.api_calls += 1
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.total_tokens += (input_tokens + output_tokens)
    
    def add_tool_call(self):
        """Record a tool call"""
        self.tool_calls += 1
    
    def add_iteration(self):
        """Record an iteration"""
        self.iterations += 1
    
    def add_error(self):
        """Record an error"""
        self.errors += 1
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)


class MetricsTracker:
    """
    Comprehensive metrics tracker for multi-agent systems
    
    Tracks:
    - API calls per agent
    - Token usage (input/output/total)
    - Tool calls
    - Execution time
    - Iterations
    - Errors
    """
    
    def __init__(self, agent_names: Optional[list] = None):
        """
        Initialize metrics tracker
        
        Args:
            agent_names: List of agent names to track. If None, uses default agents.
        """
        if agent_names is None:
            agent_names = ['planner', 'developer', 'tester']
        
        self.metrics: Dict[str, AgentMetrics] = {
            name: AgentMetrics() for name in agent_names
        }
        self.metrics['total'] = AgentMetrics()
        
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.session_id: str = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def start_tracking(self):
        """Start tracking execution time"""
        self.start_time = datetime.now()
        logger.info(f"=== Metrics tracking started at {self.start_time} (Session: {self.session_id}) ===")
    
    def end_tracking(self):
        """End tracking and calculate duration"""
        self.end_time = datetime.now()
        duration = self.get_duration()
        logger.info(f"=== Metrics tracking ended at {self.end_time} (Duration: {duration:.2f}s) ===")
    
    def get_duration(self) -> float:
        """Get execution duration in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    def record_api_call(self, agent_name: str, input_tokens: int = 0, output_tokens: int = 0):
        """
        Record an API call with token usage
        
        Args:
            agent_name: Name of the agent making the call
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
        """
        if agent_name not in self.metrics:
            logger.warning(f"Unknown agent: {agent_name}. Creating new metrics entry.")
            self.metrics[agent_name] = AgentMetrics()
        
        self.metrics[agent_name].add_api_call(input_tokens, output_tokens)
        self.metrics['total'].add_api_call(input_tokens, output_tokens)
        
        logger.info(
            f"[{agent_name.upper()}] API Call #{self.metrics[agent_name].api_calls} - "
            f"Input: {input_tokens} tokens, Output: {output_tokens} tokens, "
            f"Total this agent: {self.metrics[agent_name].total_tokens} tokens"
        )
    
    def record_tool_call(self, agent_name: str, tool_name: str = ""):
        """
        Record a tool call
        
        Args:
            agent_name: Name of the agent making the tool call
            tool_name: Name of the tool being called (optional)
        """
        if agent_name not in self.metrics:
            logger.warning(f"Unknown agent: {agent_name}")
            return
        
        self.metrics[agent_name].add_tool_call()
        self.metrics['total'].add_tool_call()
        
        tool_info = f" ({tool_name})" if tool_name else ""
        logger.info(
            f"[{agent_name.upper()}] Tool Call #{self.metrics[agent_name].tool_calls}{tool_info}"
        )
    
    def record_iteration(self, agent_name: str):
        """Record an iteration"""
        if agent_name not in self.metrics:
            return
        
        self.metrics[agent_name].add_iteration()
        self.metrics['total'].add_iteration()
    
    def record_error(self, agent_name: str, error_msg: str = ""):
        """Record an error"""
        if agent_name not in self.metrics:
            return
        
        self.metrics[agent_name].add_error()
        self.metrics['total'].add_error()
        
        logger.error(f"[{agent_name.upper()}] Error recorded: {error_msg}")
    
    def get_summary(self) -> dict:
        """
        Get complete metrics summary
        
        Returns:
            Dictionary containing all metrics and metadata
        """
        return {
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'execution_time_seconds': self.get_duration(),
            'metrics': {
                name: metrics.to_dict() 
                for name, metrics in self.metrics.items()
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def print_summary(self, detailed: bool = True):
        """
        Print formatted metrics summary to console
        
        Args:
            detailed: If True, includes per-agent breakdown
        """
        duration = self.get_duration()
        total = self.metrics['total']
        
        print("\n" + "="*70)
        print("MULTI-AGENT SYSTEM METRICS SUMMARY")
        print("="*70)
        print(f"Session ID: {self.session_id}")
        print(f"Total Execution Time: {duration:.2f} seconds")
        print(f"Total API Calls: {total.api_calls}")
        print(f"Total Tool Calls: {total.tool_calls}")
        print(f"Total Iterations: {total.iterations}")
        print(f"Total Errors: {total.errors}")
        print(f"Total Tokens Used: {total.total_tokens:,}")
        print(f"   - Input Tokens: {total.input_tokens:,}")
        print(f"   - Output Tokens: {total.output_tokens:,}")
        
        if total.api_calls > 0:
            avg_tokens = total.total_tokens / total.api_calls
            print(f"Average Tokens per API Call: {avg_tokens:.1f}")
        
        if detailed:
            print("\n" + "-"*70)
            print("Per-Agent Breakdown:")
            print("-"*70)
            
            for agent_name, metrics in self.metrics.items():
                if agent_name == 'total' or metrics.api_calls == 0:
                    continue
                
                print(f"\n {agent_name.upper()} Agent:")
                print(f"   API Calls: {metrics.api_calls}")
                print(f"   Tool Calls: {metrics.tool_calls}")
                print(f"   Iterations: {metrics.iterations}")
                print(f"   Errors: {metrics.errors}")
                print(f"   Total Tokens: {metrics.total_tokens:,}")
                print(f"   - Input: {metrics.input_tokens:,}")
                print(f"   - Output: {metrics.output_tokens:,}")
                
                if metrics.api_calls > 0:
                    avg = metrics.total_tokens / metrics.api_calls
                    print(f"   Average Tokens/Call: {avg:.1f}")
        
        print("\n" + "="*70 + "\n")
    
    def save_to_file(self, filename: Optional[str] = None, directory: str = "metrics"):
        """
        Save metrics to a JSON file
        
        Args:
            filename: Output filename. If None, uses session_id
            directory: Directory to save metrics (created if doesn't exist)
        """
        # Create directory if it doesn't exist
        metrics_dir = Path(directory)
        metrics_dir.mkdir(exist_ok=True)
        
        # Generate filename if not provided
        if filename is None:
            filename = f"metrics_{self.session_id}.json"
        
        filepath = metrics_dir / filename
        
        # Save metrics
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.get_summary(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"Metrics saved to {filepath}")
        print(f"Metrics saved to: {filepath}")
        
        return str(filepath)
    
    def reset(self):
        """Reset all metrics"""
        for metrics in self.metrics.values():
            metrics.api_calls = 0
            metrics.input_tokens = 0
            metrics.output_tokens = 0
            metrics.total_tokens = 0
            metrics.tool_calls = 0
            metrics.iterations = 0
            metrics.errors = 0
        
        self.start_time = None
        self.end_time = None
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        logger.info("Metrics reset")


# Global tracker instance
_global_tracker: Optional[MetricsTracker] = None


def get_global_tracker() -> MetricsTracker:
    """
    Get or create the global metrics tracker instance
    
    Returns:
        Global MetricsTracker instance
    """
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = MetricsTracker()
    return _global_tracker


def reset_global_tracker():
    """Reset the global metrics tracker"""
    global _global_tracker
    if _global_tracker:
        _global_tracker.reset()
    else:
        _global_tracker = MetricsTracker()


# Convenience functions
def start_tracking():
    """Start tracking with global tracker"""
    get_global_tracker().start_tracking()


def end_tracking():
    """End tracking with global tracker"""
    get_global_tracker().end_tracking()


def record_api_call(agent_name: str, input_tokens: int = 0, output_tokens: int = 0):
    """Record API call with global tracker"""
    get_global_tracker().record_api_call(agent_name, input_tokens, output_tokens)


def record_tool_call(agent_name: str, tool_name: str = ""):
    """Record tool call with global tracker"""
    get_global_tracker().record_tool_call(agent_name, tool_name)


def print_summary(detailed: bool = True):
    """Print summary with global tracker"""
    get_global_tracker().print_summary(detailed)


def save_metrics(filename: Optional[str] = None, directory: str = "metrics"):
    """Save metrics with global tracker"""
    return get_global_tracker().save_to_file(filename, directory)


if __name__ == "__main__":
    # Example usage
    tracker = MetricsTracker(['agent1', 'agent2'])
    
    tracker.start_tracking()
    
    # Simulate some activity
    tracker.record_api_call('agent1', 100, 50)
    tracker.record_tool_call('agent1', 'search_tool')
    tracker.record_iteration('agent1')
    
    tracker.record_api_call('agent2', 200, 100)
    tracker.record_tool_call('agent2', 'write_file')
    tracker.record_iteration('agent2')
    
    tracker.end_tracking()
    
    # Print and save results
    tracker.print_summary()
    tracker.save_to_file()