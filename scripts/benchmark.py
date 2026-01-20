"""
Run benchmarks and demonstrate agent optimization
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.agent_core import AutoTuningAgent
from colorama import Fore, Style
import time
import logging
from summary import display_summary
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Run the complete benchmark"""
    
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🎯 AUTO-TUNING POSTGRESQL VECTOR STORE AGENT - BENCHMARK{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
    
    # Test queries
    test_queries = [
        "artificial intelligence and machine learning",
        "climate change and global warming",
        "quantum computing and physics",
        "renewable energy sources",
        "space exploration and astronomy"
    ]
    
    # Initialize agent
    logger.info("Initializing agent...")
    agent = AutoTuningAgent()
    
    try:
        # Run optimization cycles
        results = []
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{Fore.YELLOW}{'='*70}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Query {i}/{len(test_queries)}: '{query}'{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{'='*70}{Style.RESET_ALL}\n")
            
            result = agent.run_optimization_cycle(query, tenant_id='wikipedia')
            results.append(result)
            
            # Brief summary
            if result['improvement_percentage']:
                print(f"\n{Fore.GREEN}✅ Optimization Result:{Style.RESET_ALL}")
                print(f"   Action: {result['decision']['action']}")
                print(f"   Improvement: {result['improvement_percentage']:.1f}%")
                print(f"   Before: {result['analysis_before']['execution_time_ms']:.2f} ms")
                print(f"   After: {result['analysis_after']['execution_time_ms']:.2f} ms")
            else:
                print(f"\n{Fore.YELLOW}ℹ️  No optimization performed{Style.RESET_ALL}")
            
            # Small delay between queries
            if i < len(test_queries):
                time.sleep(2)
        
        # Final statistics
        print(f"\n\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📊 BENCHMARK SUMMARY{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
        
        stats = agent.get_statistics()
        print(f"Total Queries: {len(test_queries)}")
        print(f"Optimizations Performed: {stats['optimizations_performed']}")
        print(f"Average Improvement: {stats['average_improvement']:.1f}%")
        
        # Detailed results
        print(f"\n{Fore.CYAN}Detailed Results:{Style.RESET_ALL}\n")
        for i, result in enumerate(results, 1):
            if result['improvement_percentage']:
                print(f"Query {i}: {Fore.GREEN}{result['improvement_percentage']:.1f}% improvement{Style.RESET_ALL}")
            else:
                print(f"Query {i}: {Fore.YELLOW}No optimization needed{Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}✅ Benchmark complete!{Style.RESET_ALL}\n")
        display_summary()

        
        # Suggestions
        print(f"{Fore.CYAN}Next Steps:{Style.RESET_ALL}")
        print("1. Check Grafana dashboard: http://localhost:3000")
        print("2. View query metrics: SELECT * FROM rag_system.query_metrics;")
        print("3. View agent actions: SELECT * FROM rag_system.agent_actions;")
        print("4. Review index registry: SELECT * FROM rag_system.index_registry;")
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️  Benchmark interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        logger.error(f"{Fore.RED}❌ Benchmark failed: {e}{Style.RESET_ALL}")
        raise
    finally:
        agent.close()


if __name__ == '__main__':
    main()