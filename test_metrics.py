"""
Test script for metrics tracking and logging system

This script demonstrates and tests the metrics tracking functionality
without running the full multi-agent system.
"""

import asyncio
import logging
import time
from core.metrics_utils import MetricsTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def simulate_agent_execution(agent_name: str, tracker: MetricsTracker, 
                                   api_calls: int = 3, tool_calls: int = 2):
    """
    Simulate an agent execution with API and tool calls
    
    Args:
        agent_name: Name of the agent to simulate
        tracker: MetricsTracker instance
        api_calls: Number of API calls to simulate
        tool_calls: Number of tool calls to simulate
    """
    logger.info(f"Starting {agent_name} agent simulation...")
    
    for i in range(api_calls):
        # Simulate processing time
        await asyncio.sleep(0.5)
        
        # Simulate varying token usage
        input_tokens = 100 + (i * 50)
        output_tokens = 50 + (i * 25)
        
        tracker.record_api_call(agent_name, input_tokens, output_tokens)
        tracker.record_iteration(agent_name)
        
        logger.info(f"[{agent_name}] Completed iteration {i+1}/{api_calls}")
    
    for j in range(tool_calls):
        await asyncio.sleep(0.3)
        tool_name = f"tool_{j+1}"
        tracker.record_tool_call(agent_name, tool_name)
        logger.info(f"[{agent_name}] Called {tool_name}")
    
    logger.info(f"{agent_name} agent simulation completed")


async def test_basic_tracking():
    """Test basic metrics tracking functionality"""
    print("\n" + "="*70)
    print("TEST 1: Basic Metrics Tracking")
    print("="*70 + "\n")
    
    tracker = MetricsTracker(['test_agent'])
    tracker.start_tracking()
    
    # Simulate some activity
    tracker.record_api_call('test_agent', 100, 50)
    tracker.record_tool_call('test_agent', 'test_tool')
    tracker.record_iteration('test_agent')
    
    await asyncio.sleep(1)  # Simulate work
    
    tracker.end_tracking()
    tracker.print_summary()
    
    # Verify metrics
    assert tracker.metrics['test_agent'].api_calls == 1
    assert tracker.metrics['test_agent'].tool_calls == 1
    assert tracker.metrics['test_agent'].total_tokens == 150
    
    print("Basic tracking test passed!\n")


async def test_multi_agent_tracking():
    """Test tracking multiple agents"""
    print("\n" + "="*70)
    print("TEST 2: Multi-Agent Tracking")
    print("="*70 + "\n")
    
    tracker = MetricsTracker(['planner', 'developer', 'tester'])
    tracker.start_tracking()
    
    # Simulate all three agents
    await simulate_agent_execution('planner', tracker, api_calls=2, tool_calls=1)
    await simulate_agent_execution('developer', tracker, api_calls=4, tool_calls=3)
    await simulate_agent_execution('tester', tracker, api_calls=3, tool_calls=2)
    
    tracker.end_tracking()
    tracker.print_summary()
    
    # Verify totals
    total_calls = (
        tracker.metrics['planner'].api_calls +
        tracker.metrics['developer'].api_calls +
        tracker.metrics['tester'].api_calls
    )
    assert tracker.metrics['total'].api_calls == total_calls
    
    print("Multi-agent tracking test passed!\n")


async def test_error_tracking():
    """Test error tracking functionality"""
    print("\n" + "="*70)
    print("TEST 3: Error Tracking")
    print("="*70 + "\n")
    
    tracker = MetricsTracker(['error_agent'])
    tracker.start_tracking()
    
    # Simulate normal operations
    tracker.record_api_call('error_agent', 100, 50)
    
    # Simulate errors
    tracker.record_error('error_agent', "Connection timeout")
    tracker.record_error('error_agent', "Invalid response")
    
    tracker.end_tracking()
    tracker.print_summary()
    
    # Verify error count
    assert tracker.metrics['error_agent'].errors == 2
    
    print("Error tracking test passed!\n")


async def test_save_and_load():
    """Test saving metrics to file"""
    print("\n" + "="*70)
    print("TEST 4: Save Metrics to File")
    print("="*70 + "\n")
    
    tracker = MetricsTracker(['save_test_agent'])
    tracker.start_tracking()
    
    # Simulate some activity
    tracker.record_api_call('save_test_agent', 200, 100)
    tracker.record_tool_call('save_test_agent', 'save_tool')
    
    await asyncio.sleep(0.5)
    
    tracker.end_tracking()
    
    # Save to file
    filepath = tracker.save_to_file(filename="test_metrics.json")
    print(f"Metrics saved to: {filepath}")
    
    # Verify file exists
    from pathlib import Path
    assert Path(filepath).exists()
    
    print("Save metrics test passed!\n")


async def test_performance_simulation():
    """Simulate a realistic multi-agent workflow"""
    print("\n" + "="*70)
    print("TEST 5: Realistic Multi-Agent Workflow Simulation")
    print("="*70 + "\n")
    
    tracker = MetricsTracker(['planner', 'developer', 'tester'])
    tracker.start_tracking()
    
    # Phase 1: Planning
    print("\n Phase 1: Planning")
    await simulate_agent_execution('planner', tracker, api_calls=3, tool_calls=1)
    
    # Phase 2: Development
    print("\n Phase 2: Development")
    await simulate_agent_execution('developer', tracker, api_calls=5, tool_calls=4)
    
    # Phase 3: Testing
    print("\n Phase 3: Testing")
    await simulate_agent_execution('tester', tracker, api_calls=4, tool_calls=3)
    
    tracker.end_tracking()
    
    # Print detailed summary
    tracker.print_summary(detailed=True)
    
    # Save results
    filepath = tracker.save_to_file(filename="workflow_simulation.json")
    
    # Calculate some statistics
    duration = tracker.get_duration()
    total_tokens = tracker.metrics['total'].total_tokens
    
    print("\n" + "="*70)
    print("Workflow Statistics")
    print("="*70)
    print(f"Total Duration: {duration:.2f} seconds")
    print(f"Tokens per Second: {total_tokens / duration:.1f}")
    print(f"Average API Calls per Agent: {tracker.metrics['total'].api_calls / 3:.1f}")
    print(f"Average Tool Calls per Agent: {tracker.metrics['total'].tool_calls / 3:.1f}")
    print("="*70)
    
    print(f"\nWorkflow simulation completed! Results saved to: {filepath}\n")


async def run_all_tests():
    """Run all test cases"""
    print("\n" + "🚀 " + "="*68)
    print("METRICS TRACKING SYSTEM - TEST SUITE")
    print("🚀" + "="*68 + "\n")
    
    tests = [
        ("Basic Tracking", test_basic_tracking),
        ("Multi-Agent Tracking", test_multi_agent_tracking),
        ("Error Tracking", test_error_tracking),
        ("Save/Load Metrics", test_save_and_load),
        ("Performance Simulation", test_performance_simulation),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            await test_func()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} FAILED: {str(e)}\n")
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


async def interactive_demo():
    """Interactive demonstration of metrics tracking"""
    print("\n" + "="*70)
    print(" INTERACTIVE METRICS TRACKING DEMO")
    print("="*70 + "\n")
    
    print("This demo simulates a simplified multi-agent workflow.")
    print("Watch as each agent executes and metrics are tracked in real-time.\n")
    
    input("Press Enter to start the demo...")
    
    tracker = MetricsTracker(['planner', 'developer', 'tester'])
    tracker.start_tracking()
    
    # Simulate workflow with user prompts
    print("\n Starting Planner Agent...")
    await simulate_agent_execution('planner', tracker, api_calls=2, tool_calls=1)
    input("\nPress Enter to continue to Development phase...")
    
    print("\n Starting Developer Agent...")
    await simulate_agent_execution('developer', tracker, api_calls=3, tool_calls=2)
    input("\nPress Enter to continue to Testing phase...")
    
    print("\n Starting Tester Agent...")
    await simulate_agent_execution('tester', tracker, api_calls=2, tool_calls=1)
    
    tracker.end_tracking()
    
    print("\n🎉 All agents completed!")
    input("\nPress Enter to view final metrics...")
    
    tracker.print_summary()
    
    save = input("\nSave metrics to file? (y/n): ").lower()
    if save == 'y':
        filepath = tracker.save_to_file()
        print(f"\n Metrics saved to: {filepath}")
    
    print("\nDemo completed! Thank you for testing.\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        # Run interactive demo
        asyncio.run(interactive_demo())
    else:
        # Run all automated tests
        asyncio.run(run_all_tests())
        
        print("\nTIP: Run 'python test_metrics.py --demo' for an interactive demonstration\n")