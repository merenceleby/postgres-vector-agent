import ollama
from typing import Dict, List
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMOptimizer:
    """LLM-powered query optimization decision maker"""
    
    def __init__(self, model_name: str = 'phi3:mini'):
        """
        Initialize LLM optimizer
        
        Args:
            model_name: Ollama model name
        """
        self.model_name = model_name
        logger.info(f"Initializing LLM Optimizer with model: {model_name}")
        
        # Test connection
        try:
            ollama.list()
            logger.info("✅ Ollama connection successful")
        except Exception as e:
            logger.error(f"❌ Ollama connection failed: {e}")
            logger.error("Make sure Ollama is running: ollama serve")
            raise
    
    def decide_optimization(self, analysis: Dict) -> Dict:
        """
        Use LLM to decide on optimization strategy
        
        Args:
            analysis: Query analysis from QueryAnalyzer
            
        Returns:
            Optimization decision with reasoning
        """
        # Build prompt for LLM
        prompt = self._build_optimization_prompt(analysis)
        
        try:
            # Get LLM response
            response = ollama.chat(
                model=self.model_name,
                messages=[{
                    'role': 'system',
                    'content': 'You are a PostgreSQL database optimization expert. '
                              'Analyze query performance and recommend specific index strategies.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }],
                options={
                    'temperature': 0.3,  # Low temperature for consistent technical responses
                    'num_predict': 500
                }
            )
            
            llm_output = response['message']['content']
            
            # Parse LLM response
            decision = self._parse_llm_response(llm_output, analysis)
            
            logger.info(f"LLM Decision: {decision['action']}")
            
            return decision
            
        except Exception as e:
            logger.error(f"LLM optimization error: {e}")
            # Fallback to rule-based decision
            return self._fallback_decision(analysis)
    
    def _build_optimization_prompt(self, analysis: Dict) -> str:
        """Build prompt for LLM"""
        prompt = f"""
Analyze this PostgreSQL query performance issue:

PERFORMANCE METRICS:
- Execution Time: {analysis['execution_time_ms']:.2f} ms
- Scan Type: {analysis['scan_type']}
- Index Used: {analysis['index_used']}
- Rows Scanned: {analysis.get('rows_scanned', 'N/A')}
- Rows Returned: {analysis.get('rows_returned', 'N/A')}

DETECTED ISSUES:
{chr(10).join(f'- {issue}' for issue in analysis['issues'])}

CONTEXT:
This is a vector similarity search query on a PostgreSQL table with pgvector extension.
The table uses vector(384) embeddings for semantic search.

AVAILABLE INDEX TYPES:
1. HNSW (Hierarchical Navigable Small World)
   - Best for: High recall, low latency
   - Trade-off: Higher memory usage, slower build time
   - Good for: <1M vectors, real-time search

2. IVFFlat (Inverted File with Flat compression)
   - Best for: Large datasets, memory efficiency
   - Trade-off: Lower recall (90-95%)
   - Good for: >1M vectors, batch processing

QUESTION:
Should I create an index? If yes, which type (HNSW or IVFFlat)?

Respond in this EXACT format:
ACTION: [create_hnsw_index | create_ivfflat_index | no_action | optimize_query]
REASONING: [Your technical explanation in 1-2 sentences]
EXPECTED_IMPROVEMENT: [Quantitative estimate, e.g., "10-50x faster"]
"""
        return prompt
    
    def _parse_llm_response(self, llm_output: str, analysis: Dict) -> Dict:
        """Parse LLM response into structured decision"""
        decision = {
            'action': 'no_action',
            'reasoning': llm_output,
            'index_type': None,
            'expected_improvement': 'Unknown',
            'confidence': 'medium'
        }
        
        # Extract action
        llm_lower = llm_output.lower()
        if 'create_hnsw_index' in llm_lower or 'hnsw' in llm_lower:
            decision['action'] = 'create_hnsw_index'
            decision['index_type'] = 'hnsw'
        elif 'create_ivfflat_index' in llm_lower or 'ivfflat' in llm_lower:
            decision['action'] = 'create_ivfflat_index'
            decision['index_type'] = 'ivfflat'
        elif 'optimize_query' in llm_lower:
            decision['action'] = 'optimize_query'
        
        # Extract reasoning (look for REASONING: line)
        for line in llm_output.split('\n'):
            if line.strip().startswith('REASONING:'):
                decision['reasoning'] = line.replace('REASONING:', '').strip()
            elif line.strip().startswith('EXPECTED_IMPROVEMENT:'):
                decision['expected_improvement'] = line.replace('EXPECTED_IMPROVEMENT:', '').strip()
        
        # Set confidence based on analysis
        if analysis['execution_time_ms'] > 200:
            decision['confidence'] = 'high'
        elif analysis['execution_time_ms'] > 100:
            decision['confidence'] = 'medium'
        else:
            decision['confidence'] = 'low'
        
        return decision
    
    def _fallback_decision(self, analysis: Dict) -> Dict:
        """Fallback rule-based decision if LLM fails"""
        decision = {
            'action': 'no_action',
            'reasoning': 'Fallback rule-based decision',
            'index_type': None,
            'expected_improvement': 'Unknown',
            'confidence': 'low'
        }
        
        # Simple rules
        if analysis['execution_time_ms'] > 100 and not analysis['index_used']:
            if analysis['rows_scanned'] < 100000:
                decision['action'] = 'create_hnsw_index'
                decision['index_type'] = 'hnsw'
                decision['reasoning'] = 'Dataset size suitable for HNSW. High performance required.'
                decision['expected_improvement'] = '10-50x faster'
            else:
                decision['action'] = 'create_ivfflat_index'
                decision['index_type'] = 'ivfflat'
                decision['reasoning'] = 'Large dataset. IVFFlat more memory efficient.'
                decision['expected_improvement'] = '20-30x faster'
        
        return decision
    
    def generate_sql(self, decision: Dict, tenant_id: str = 'default') -> str:
        """Generate SQL command for optimization"""
        if decision['action'] == 'create_hnsw_index':
            index_name = f"idx_embedding_hnsw_{tenant_id}"
            sql = f"""
CREATE INDEX IF NOT EXISTS {index_name}
ON rag_system.documents
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
"""
        elif decision['action'] == 'create_ivfflat_index':
            index_name = f"idx_embedding_ivfflat_{tenant_id}"
            sql = f"""
CREATE INDEX IF NOT EXISTS {index_name}
ON rag_system.documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
"""
        else:
            sql = None
        
        return sql