from .database import DatabaseManager
from .query_analyzer import QueryAnalyzer
from .optimizer import LLMOptimizer
from .embeddings import EmbeddingGenerator
import time
import logging
from typing import Dict, List
from colorama import Fore, Style, init

init(autoreset=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AutoTuningAgent:
    """Autonomous PostgreSQL Vector Store Optimization Agent"""
    
    def __init__(self):
        """Initialize the agent"""
        logger.info(f"{Fore.CYAN}🤖 Initializing Auto-Tuning Agent...{Style.RESET_ALL}")
        
        self.db = DatabaseManager()
        self.db.connect()
        
        self.analyzer = QueryAnalyzer()
        self.optimizer = LLMOptimizer()
        self.embedder = EmbeddingGenerator()
        
        self.optimization_count = 0
        self.total_improvement = 0
        
        logger.info(f"{Fore.GREEN}✅ Agent initialized successfully{Style.RESET_ALL}")
    
   
    def observe(self, query_embedding: List[float], tenant_id: str = 'default') -> Dict:
        """
        Observe query performance using the new database analyzer
        """
        logger.info(f"{Fore.YELLOW}👁️  OBSERVE: Analyzing query performance...{Style.RESET_ALL}")
        
        # Yeni database metodunu kullan (SQL oluşturma işini database.py hallediyor)
        analysis = self.db.analyze_query("Vector Similarity Search", embedding=query_embedding)
        
        # Sorunları tespit et (Eskiden QueryAnalyzer yapıyordu, şimdi burada basitçe yapıyoruz)
        analysis['issues'] = []
        
        # 1. Performans kontrolü (Örn: 20ms üzeri yavaş kabul edilir)
        if analysis['execution_time_ms'] > 20:
            analysis['issues'].append('high_latency')
        
        # 2. İndeks kontrolü
        if not analysis['index_used']:
            analysis['issues'].append('missing_index')
        
        # Metrikleri kaydet
        self.db.log_query_metric({
            'query_type': 'vector_similarity_search',
            'execution_time_ms': analysis['execution_time_ms'],
            'index_used': analysis['index_used'],
            'rows_scanned': 0,  # EXPLAIN JSON'dan çekmek karmaşık olabilir, şimdilik 0
            'query_plan': {'scan_type': analysis['scan_type']}
        })
        
        logger.info(f"{Fore.CYAN}📊 Execution Time: {analysis['execution_time_ms']:.2f} ms{Style.RESET_ALL}")
        logger.info(f"{Fore.CYAN}📊 Scan Type: {analysis['scan_type']}{Style.RESET_ALL}")
        logger.info(f"{Fore.CYAN}📊 Index Used: {analysis['index_used']}{Style.RESET_ALL}")
        
        return analysis
    def reason(self, analysis: Dict) -> Dict:
        """
        Reason about optimization using LLM
        
        Args:
            analysis: Query analysis results
            
        Returns:
            Optimization decision
        """
        logger.info(f"{Fore.YELLOW}🧠 REASON: Consulting LLM for optimization strategy...{Style.RESET_ALL}")
        
        # Check if optimization is needed
        if not analysis['issues']:
            logger.info(f"{Fore.GREEN}✅ No optimization needed. Performance is acceptable.{Style.RESET_ALL}")
            return {'action': 'no_action', 'reasoning': 'Performance is acceptable'}
        
        # Get LLM decision
        decision = self.optimizer.decide_optimization(analysis)
        
        logger.info(f"{Fore.MAGENTA}💭 Decision: {decision['action']}{Style.RESET_ALL}")
        logger.info(f"{Fore.MAGENTA}💭 Reasoning: {decision['reasoning']}{Style.RESET_ALL}")
        
        return decision
    
    def act(self, decision: Dict, tenant_id: str = 'default') -> Dict:
        """
        Execute optimization action
        
        Args:
            decision: Optimization decision from LLM
            tenant_id: Tenant identifier
            
        Returns:
            Action results
        """
        if decision['action'] == 'no_action':
            return {'success': True, 'message': 'No action taken'}
        
        logger.info(f"{Fore.YELLOW}⚡ ACT: Executing optimization...{Style.RESET_ALL}")
        
        result = {
            'action': decision['action'],
            'success': False,
            'sql_executed': None,
            'error': None
        }
        
        try:
            # Generate SQL
            sql = self.optimizer.generate_sql(decision, tenant_id)
            
            if not sql:
                result['error'] = 'No SQL generated'
                return result
            
            result['sql_executed'] = sql
            
            # Execute optimization
            if 'create_' in decision['action'] and 'index' in decision['action']:
                index_type = decision['index_type']
                index_name = f"idx_embedding_{index_type}_{tenant_id}"
                
                logger.info(f"{Fore.CYAN}🔨 Creating {index_type.upper()} index: {index_name}{Style.RESET_ALL}")
                
                self.db.create_index(index_name, index_type)
                result['success'] = True
                
                logger.info(f"{Fore.GREEN}✅ Index created successfully{Style.RESET_ALL}")
            
            # Log action
            self.db.log_agent_action({
                'action_type': decision['action'],
                'reasoning': decision['reasoning'],
                'sql_executed': sql,
                'success': result['success'],
                'impact_metrics': {
                    'expected_improvement': decision.get('expected_improvement'),
                    'confidence': decision.get('confidence')
                }
            })
            
            self.optimization_count += 1
            
        except Exception as e:
            logger.error(f"{Fore.RED}❌ Action failed: {e}{Style.RESET_ALL}")
            result['error'] = str(e)
            result['success'] = False
        
        return result
    
    def run_optimization_cycle(self, query_text: str, tenant_id: str = 'default') -> Dict:
        """
        Run complete optimization cycle: Observe → Reason → Act
        
        Args:
            query_text: Text query for similarity search
            tenant_id: Tenant identifier
            
        Returns:
            Complete cycle results
        """
        logger.info(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        logger.info(f"{Fore.CYAN}🚀 OPTIMIZATION CYCLE START{Style.RESET_ALL}")
        logger.info(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        cycle_start = time.time()
        
        # Generate query embedding
        query_embedding = self.embedder.encode_query(query_text)
        
        # OBSERVE
        analysis_before = self.observe(query_embedding, tenant_id)
        
        # REASON
        decision = self.reason(analysis_before)
        
        # ACT
        action_result = self.act(decision, tenant_id)
        
        # VERIFY (observe again after optimization)
        analysis_after = None
        improvement = None
        
        if action_result['success'] and 'create_' in decision['action']:
            logger.info(f"\n{Fore.YELLOW}🔍 Verifying optimization impact...{Style.RESET_ALL}")
            time.sleep(2)  # Wait for index to be ready
            analysis_after = self.observe(query_embedding, tenant_id)
            
            # Calculate improvement
            time_before = analysis_before['execution_time_ms']
            time_after = analysis_after['execution_time_ms']
            improvement = ((time_before - time_after) / time_before) * 100
            
            logger.info(f"\n{Fore.GREEN}📈 IMPROVEMENT: {improvement:.1f}%{Style.RESET_ALL}")
            logger.info(f"{Fore.GREEN}   Before: {time_before:.2f} ms → After: {time_after:.2f} ms{Style.RESET_ALL}")
            
            self.total_improvement += improvement
        
        cycle_time = (time.time() - cycle_start)
        
        logger.info(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        logger.info(f"{Fore.CYAN}✅ CYCLE COMPLETE ({cycle_time:.2f}s){Style.RESET_ALL}")
        logger.info(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        return {
            'analysis_before': analysis_before,
            'decision': decision,
            'action_result': action_result,
            'analysis_after': analysis_after,
            'improvement_percentage': improvement,
            'cycle_time_seconds': cycle_time
        }
    
    def get_statistics(self) -> Dict:
        """Get agent statistics"""
        return {
            'optimizations_performed': self.optimization_count,
            'average_improvement': self.total_improvement / max(self.optimization_count, 1),
            'total_improvement': self.total_improvement
        }
    
    def close(self):
        """Cleanup resources"""
        self.db.close()
        logger.info(f"{Fore.CYAN}👋 Agent shutdown complete{Style.RESET_ALL}")