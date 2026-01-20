import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
import json
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages PostgreSQL connections and operations"""
    
    def __init__(self):
        self.conn_params = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'database': os.getenv('POSTGRES_DB', 'vector_store'),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'postgres123')
        }
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.conn_params)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            logger.info("✅ Database connected successfully")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("Database connection closed")
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute a query and return results"""
        try:
            self.cursor.execute(query, params)
            if self.cursor.description:
                return self.cursor.fetchall()
            return []
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            self.conn.rollback()
            raise
    
    def analyze_query(self, query_text: str, embedding: List[float] = None) -> Dict:
        """Analyze vector query performance with EXPLAIN ANALYZE"""
        try:
            if not embedding:
                logger.warning("No embedding provided")
                return {
                    "execution_time_ms": 100.0,
                    "scan_type": "ERROR",
                    "index_used": False,
                    "planning_time_ms": 0.0
                }
            
            # Convert embedding to PostgreSQL array format
            embedding_str = f"[{','.join(map(str, embedding))}]"
            
            # SQL query with proper vector syntax
            sql = """
            EXPLAIN (ANALYZE, FORMAT JSON)
            SELECT content, metadata
            FROM rag_system.documents
            ORDER BY embedding <-> %s::vector
            LIMIT 5
            """
            
            # Execute EXPLAIN ANALYZE
            #logger.info(f"Executing EXPLAIN with embedding length: {len(embedding)}")
            #logger.info(f"SQL: {sql}")
            #logger.info(f"Param (first 50 chars): {embedding_str[:50]}...")
            self.cursor.execute(sql, (embedding_str,))
            result = self.cursor.fetchone()

            if not result:
                raise Exception("Empty EXPLAIN result")

            # result is a RealDictRow, get first column value
            # Column name is 'QUERY PLAN'
            explain_data = result.get('QUERY PLAN') or list(result.values())[0]
            if isinstance(explain_data, str):
                explain_data = json.loads(explain_data)
            
            # Extract first element if it's a list
            if isinstance(explain_data, list):
                if len(explain_data) > 0:
                    explain_data = explain_data[0]
                else:
                    raise Exception("Empty EXPLAIN plan")
            
            # Extract performance metrics
            plan = explain_data.get('Plan', {})
            execution_time = float(explain_data.get('Execution Time', 0.0))
            planning_time = float(explain_data.get('Planning Time', 0.0))
            
            # Detect scan type and index usage
            scan_type = plan.get('Node Type', 'Unknown')
            index_used = 'Index Scan' in str(plan) or 'Bitmap' in str(plan)
            
            return {
                "execution_time_ms": execution_time,
                "scan_type": scan_type,
                "index_used": index_used,
                "planning_time_ms": planning_time
            }
            
        except Exception as e:
            import traceback
            logger.error(f"EXPLAIN ANALYZE error in analyze_query: {e}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            self.conn.rollback()
            # Return fallback values to trigger optimization
            return {
                "execution_time_ms": 100.0,
                "scan_type": "ERROR",
                "index_used": False,
                "planning_time_ms": 0.0,
                "error": str(e)
            }
    
    def execute_explain(self, query: str, params: tuple = None) -> Dict:
        """Legacy method - calls analyze_query"""
        return self.analyze_query(query)
    
    def insert_documents(self, documents: List[Dict[str, Any]]):
        """Bulk insert documents with embeddings"""
        insert_query = """
            INSERT INTO rag_system.documents (tenant_id, content, embedding, metadata)
            VALUES %s
        """
        try:
            values = [
                (
                    doc['tenant_id'],
                    doc['content'],
                    doc['embedding'],
                    json.dumps(doc.get('metadata', {}))
                )
                for doc in documents
            ]
            execute_values(self.cursor, insert_query, values)
            self.conn.commit()
            logger.info(f"✅ Inserted {len(documents)} documents")
        except Exception as e:
            logger.error(f"Insert error: {e}")
            self.conn.rollback()
            raise
    
    def search_similar(self, query_embedding: List[float], tenant_id: str, limit: int = 10) -> List[Dict]:
        """Vector similarity search"""
        search_query = """
            SELECT id, content, metadata,
                   embedding <-> %s::vector AS distance
            FROM rag_system.documents
            WHERE tenant_id = %s
            ORDER BY embedding <-> %s::vector
            LIMIT %s
        """
        embedding_str = f"[{','.join(map(str, query_embedding))}]"
        return self.execute_query(search_query, (embedding_str, tenant_id, embedding_str, limit))
    
    def get_query_stats(self) -> List[Dict]:
        """Get statistics from pg_stat_statements"""
        stats_query = """
            SELECT 
                query,
                calls,
                mean_exec_time,
                max_exec_time,
                stddev_exec_time
            FROM pg_stat_statements
            WHERE query LIKE '%rag_system.documents%'
            ORDER BY mean_exec_time DESC
            LIMIT 10
        """
        try:
            return self.execute_query(stats_query)
        except Exception:
            return []
    
    def create_index2(self, index_name: str, index_type: str = 'hnsw'):
        """Create vector index"""
        logger.info(f"🔨 Creating index: {index_name} type: {index_type}...")
        
        # Drop existing index first
        drop_query = f"DROP INDEX IF EXISTS {index_name};"
        
        if index_type == 'hnsw':
            create_query = f"""
                CREATE INDEX {index_name}
                ON rag_system.documents
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64)
            """
        elif index_type == 'ivfflat':
            create_query = f"""
                CREATE INDEX {index_name}
                ON rag_system.documents
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100)
            """
        else:
            raise ValueError(f"Unknown index type: {index_type}")
        
        try:
            self.cursor.execute(drop_query)
            self.cursor.execute(create_query)
            self.conn.commit()
            
            # Register index
            self.cursor.execute("""
                INSERT INTO rag_system.index_registry (index_name, table_name, index_type, metadata)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (index_name) 
                DO UPDATE SET created_at = CURRENT_TIMESTAMP
            """, (index_name, 'documents', index_type, json.dumps({'auto_created': True})))
            self.conn.commit()
            
            logger.info(f"✅ Successfully created {index_type} index: {index_name}")
        except Exception as e:
            logger.error(f"Index creation error: {e}")
            self.conn.rollback()
            raise
    def create_index(self, index_name: str, index_type: str = 'hnsw'):
        """Create vector index"""
        logger.info(f"🔨 Creating index: {index_name} type: {index_type}...")
        
        # Check if index exists - if yes, skip creation
        check_query = """
            SELECT COUNT(*) as count 
            FROM pg_indexes 
            WHERE schemaname = 'rag_system' AND indexname = %s
        """
        result = self.execute_query(check_query, (index_name,))
        
        if result and result[0]['count'] > 0:
            logger.info(f"ℹ️  Index {index_name} already exists, skipping creation")
            return
        
        # Drop existing index first (safety)
        drop_query = f"DROP INDEX IF EXISTS rag_system.{index_name};"
    def log_query_metric(self, metric_data: Dict):
        """Log query performance metrics"""
        insert_query = """
            INSERT INTO rag_system.query_metrics 
            (query_type, execution_time_ms, index_used, rows_scanned, query_plan)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            self.cursor.execute(insert_query, (
                metric_data.get('query_type'),
                metric_data.get('execution_time_ms'),
                metric_data.get('index_used'),
                metric_data.get('rows_scanned', 0),
                json.dumps(metric_data.get('query_plan', {}))
            ))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Metric logging error: {e}")
            self.conn.rollback()
    
    def log_agent_action(self, action_data: Dict):
        """Log agent optimization actions"""
        insert_query = """
            INSERT INTO rag_system.agent_actions
            (action_type, reasoning, sql_executed, success, impact_metrics)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            self.cursor.execute(insert_query, (
                action_data.get('action_type'),
                action_data.get('reasoning'),
                action_data.get('sql_executed'),
                action_data.get('success'),
                json.dumps(action_data.get('impact_metrics', {}))
            ))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Action logging error: {e}")
            self.conn.rollback()