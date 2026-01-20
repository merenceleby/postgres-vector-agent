"""
Display project summary and metrics
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.database import DatabaseManager
from colorama import Fore, Style, init

init(autoreset=True)


def display_summary():
    """Display comprehensive project summary"""
    
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🎯 AUTO-TUNING POSTGRESQL VECTOR STORE AGENT - PROJECT SUMMARY{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
    
    db = DatabaseManager()
    db.connect()
    
    try:
        # 1. Database Stats
        print(f"{Fore.YELLOW}📊 DATABASE STATISTICS{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'─'*70}{Style.RESET_ALL}")
        
        doc_count = db.execute_query("SELECT COUNT(*) as count FROM rag_system.documents")[0]['count']
        print(f"  Documents Loaded: {doc_count:,}")
        
        index_count = db.execute_query("SELECT COUNT(*) as count FROM rag_system.index_registry")[0]['count']
        print(f"  Indexes Created: {index_count}")
        
        # 2. Agent Performance
        print(f"\n{Fore.YELLOW}🤖 AGENT PERFORMANCE{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'─'*70}{Style.RESET_ALL}")
        
        actions = db.execute_query("""
            SELECT 
                action_type,
                COUNT(*) as count,
                SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful
            FROM rag_system.agent_actions
            GROUP BY action_type
        """)
        
        if actions:
            for action in actions:
                success_rate = (action['successful'] / action['count']) * 100
                print(f"  {action['action_type']}: {action['count']} total, {success_rate:.0f}% success")
        else:
            print(f"  No optimizations performed yet")
        
        # 3. Query Metrics
        print(f"\n{Fore.YELLOW}⚡ QUERY PERFORMANCE{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'─'*70}{Style.RESET_ALL}")
        
        metrics = db.execute_query("""
            SELECT 
                AVG(execution_time_ms) as avg_time,
                MIN(execution_time_ms) as min_time,
                MAX(execution_time_ms) as max_time,
                COUNT(*) as query_count
            FROM rag_system.query_metrics
        """)
        
        if metrics and metrics[0]['query_count'] > 0:
            m = metrics[0]
            print(f"  Total Queries: {m['query_count']}")
            print(f"  Average Time: {m['avg_time']:.2f} ms")
            print(f"  Fastest Query: {m['min_time']:.2f} ms")
            print(f"  Slowest Query: {m['max_time']:.2f} ms")
        else:
            print(f"  No query metrics available")
        
        
        # 4. Recent Agent Actions
        print(f"\n{Fore.YELLOW}📜 RECENT AGENT DECISIONS (Last 5){Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'─'*70}{Style.RESET_ALL}")
        
        recent = db.execute_query("""
            SELECT action_type, reasoning, success, timestamp
            FROM rag_system.agent_actions
            ORDER BY timestamp DESC
            LIMIT 5
        """)
        
        if recent:
            for i, act in enumerate(recent, 1):
                status = f"{Fore.GREEN}✅{Style.RESET_ALL}" if act['success'] else f"{Fore.RED}❌{Style.RESET_ALL}"
                print(f"\n  {i}. {status} {act['action_type']}")
                print(f"     Reasoning: {act['reasoning'][:80]}...")
                #print(f"     Time: {act['timestamp']}")
        else:
            print(f"  No agent actions logged")

        
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
    finally:
        db.close()


#if __name__ == '__main__':
#    display_summary()