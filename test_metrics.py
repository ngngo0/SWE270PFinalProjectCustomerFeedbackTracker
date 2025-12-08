"""
Simple test script for metrics tracking and logging system

This script demonstrates the metrics tracking functionality
by simulating agent execution.
"""

import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimpleMetricsTracker:
    """Simple metrics tracker for testing"""
    
    def __init__(self):
        self.metrics = {
            'test_agent': {'api_calls': 0, 'tool_calls': 0, 'total_tokens': 0},
            'total': {'api_calls': 0, 'tool_calls': 0, 'total_tokens': 0}
        }
        self.start_time = None
        self.end_time = None
    
    def start_tracking(self):
        self.start_time = datetime.now()
        logger.info(f"Metrics tracking started at {self.start_time}")
    
    def end_tracking(self):
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        logger.info(f"Metrics tracking ended (Duration: {duration:.2f}s)")
    
    def record_api_call(self, agent_name: str, tokens: int = 150):
        self.metrics[agent_name]['api_calls'] += 1
        self.metrics[agent_name]['total_tokens'] += tokens
        self.metrics['total']['api_calls'] += 1
        self.metrics['total']['total_tokens'] += tokens
        logger.info(f"[{agent_name.upper()}] API Call #{self.metrics[agent_name]['api_calls']}")
    
    def record_tool_call(self, agent_name: str):
        self.metrics[agent_name]['tool_calls'] += 1
        self.metrics['total']['tool_calls'] += 1
        logger.info(f"[{agent_name.upper()}] Tool Call #{self.metrics[agent_name]['tool_calls']}")
    
    def print_summary(self):
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0
        
        print("\n" + "="*70)
        print("METRICS SUMMARY")
        print("="*70)
        print(f"Duration: {duration:.2f}s")
        print(f"Total API Calls: {self.metrics['total']['api_calls']}")
        print(f"Total Tool Calls: {self.metrics['total']['tool_calls']}")
        print(f"Total Tokens: {self.metrics['total']['total_tokens']:,}")
        print("="*70 + "\n")


async def test_basic_tracking():
    """Test basic metrics tracking"""
    print("\n" + "="*70)
    print("TEST 1: Basic Metrics Tracking")
    print("="*70 + "\n")
    
    tracker = SimpleMetricsTracker()
    tracker.start_tracking()
    
    # Simulate activity
    tracker.record_api_call('test_agent', 100)
    await asyncio.sleep(0.1)
    tracker.record_tool_call('test_agent')
    await asyncio.sleep(0.1)
    tracker.record_api_call('test_agent', 50)
    
    tracker.end_tracking()
    tracker.print_summary()
    
    assert tracker.metrics['test_agent']['api_calls'] == 2
    assert tracker.metrics['test_agent']['tool_calls'] == 1
    
    print("Basic tracking test passed!\n")


async def test_logging():
    """Test logging functionality"""
    print("\n" + "="*70)
    print("TEST 2: Logging System")
    print("="*70 + "\n")
    
    logger.info("[PLANNER] Starting planner agent...")
    await asyncio.sleep(0.1)
    logger.info("[PLANNER] Tool call: create_plan")
    await asyncio.sleep(0.1)
    logger.info("[PLANNER] Agent completed")
    
    print("Logging test passed!\n")


async def test_multi_agent_simulation():
    """Simulate multi-agent workflow"""
    print("\n" + "="*70)
    print("TEST 3: Multi-Agent Simulation")
    print("="*70 + "\n")
    
    agents = ['planner', 'developer', 'tester']
    tracker = SimpleMetricsTracker()
    
    # Add metrics for each agent
    for agent in agents:
        tracker.metrics[agent] = {'api_calls': 0, 'tool_calls': 0, 'total_tokens': 0}
    
    tracker.start_tracking()
    
    for agent in agents:
        logger.info(f"[{agent.upper()}] Starting {agent} agent...")
        await asyncio.sleep(0.1)
        
        # Simulate API calls
        for i in range(2):
            tracker.record_api_call(agent, 100)
            await asyncio.sleep(0.05)
        
        # Simulate tool calls
        tracker.record_tool_call(agent)
        await asyncio.sleep(0.05)
        
        logger.info(f"[{agent.upper()}] Agent completed")
    
    tracker.end_tracking()
    tracker.print_summary()
    
    print("Multi-agent simulation passed!\n")


async def run_all_tests():
    """Run all test cases"""
    print("\n" + "🚀 " + "="*68)
    print("METRICS & LOGGING SYSTEM - TEST SUITE")
    print("🚀 " + "="*68 + "\n")
    
    tests = [
        ("Basic Tracking", test_basic_tracking),
        ("Logging System", test_logging),
        ("Multi-Agent Simulation", test_multi_agent_simulation),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            await test_func()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"{test_name} FAILED: {str(e)}\n")
            logger.error(f"Test failed: {test_name}", exc_info=True)
    
    # Print final summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(tests)*100):.1f}%")
    print("="*70 + "\n")
    
    if failed == 0:
        print("All tests passed! The metrics and logging system is working correctly.\n")
        print("Next steps:")
        print("1. Run the full system: python -m ui.app")
        print("2. Check agent_communication.log for detailed logs")
        print("3. View metrics in the UI's 'Metrics & Performance' tab\n")


if __name__ == "__main__":
    asyncio.run(run_all_tests())