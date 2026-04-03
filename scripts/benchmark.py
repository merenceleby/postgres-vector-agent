"""
Run benchmarks and demonstrate agent optimization (3-Phase Baseline Testing)
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
    """Run the complete 3-phase benchmark"""
    
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
        baseline_times = []
        optimized_times = []

        # ==========================================
        # PHASE 1: BASELINE (Test without Index)
        # ==========================================
        print(f"\n{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}PHASE 1: BASELINE PERFORMANCE TEST (No Index){Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}")
        
        for i, query in enumerate(test_queries, 1):
            # Generate embedding
            query_embedding = agent.embedder.encode_query(query)
            
            # Observe only, no optimization triggered
            analysis = agent.observe(query_embedding, tenant_id='wikipedia')
            baseline_times.append(analysis['execution_time_ms'])
            
            print(f"Query {i} (Baseline): {analysis['execution_time_ms']:.2f} ms | Index Used: {analysis['index_used']}")

        # ==========================================
        # PHASE 2: AGENT OPTIMIZATION
        # ==========================================
        print(f"\n{Fore.YELLOW}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}PHASE 2: AGENT TAKES ACTION (Triggered by Query 1){Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'='*70}{Style.RESET_ALL}")
        
        # The agent will detect poor performance on the first query and create an index
        agent.run_optimization_cycle(test_queries[0], tenant_id='wikipedia')
        
        # Short delay to ensure the index is fully ready and registered
        time.sleep(2)

        # ==========================================
        # PHASE 3: VERIFICATION (Test with Index)
        # ==========================================
        print(f"\n{Fore.GREEN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}PHASE 3: POST-OPTIMIZATION VERIFICATION (All Queries){Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*70}{Style.RESET_ALL}")
        
        for i, query in enumerate(test_queries, 1):
            # Generate embedding
            query_embedding = agent.embedder.encode_query(query)
            
            # Observe again to see the impact of the newly created index
            analysis = agent.observe(query_embedding, tenant_id='wikipedia')
            optimized_times.append(analysis['execution_time_ms'])
            
            print(f"Query {i} (Optimized): {analysis['execution_time_ms']:.2f} ms | Index Used: {analysis['index_used']}")

        # ==========================================
        # FINAL RESULTS & SUMMARY
        # ==========================================
        print(f"\n\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📊 BENCHMARK COMPARISON SUMMARY{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
        
        for i, query in enumerate(test_queries):
            t_before = baseline_times[i]
            t_after = optimized_times[i]
            
            # Calculate improvement percentage safely
            if t_before > 0:
                improvement = ((t_before - t_after) / t_before) * 100
            else:
                improvement = 0.0

            print(f"Query {i+1}: '{query[:35]}...'")
            print(f"  Before: {Fore.RED}{t_before:.2f} ms{Style.RESET_ALL} -> After: {Fore.GREEN}{t_after:.2f} ms{Style.RESET_ALL} (Improvement: {improvement:.1f}%)\n")

        print(f"\n{Fore.GREEN}✅ Benchmark complete!{Style.RESET_ALL}\n")
        
        # Display the overall project summary
        display_summary()
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️  Benchmark interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        logger.error(f"{Fore.RED}❌ Benchmark failed: {e}{Style.RESET_ALL}")
        raise
    finally:
        agent.close()

if __name__ == '__main__':
    main()