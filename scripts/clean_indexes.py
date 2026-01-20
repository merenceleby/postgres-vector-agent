"""
Clean all vector indexes before benchmark
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.database import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_indexes():
    """Remove all existing indexes"""
    db = DatabaseManager()
    db.connect()
    
    try:
        # Drop all vector indexes
        indexes = [
            'idx_embedding_hnsw_wikipedia',
            'idx_embedding_ivfflat_wikipedia',
            'idx_embedding_hnsw_default',
            'idx_embedding_ivfflat_default'
        ]
        
        for idx in indexes:
            try:
                logger.info(f"Dropping index: {idx}")
                db.cursor.execute(f"DROP INDEX IF EXISTS rag_system.{idx}")
                db.conn.commit()
                logger.info(f"✅ Dropped: {idx}")
            except Exception as e:
                logger.warning(f"Could not drop {idx}: {e}")
                db.conn.rollback()
        
        # Clean registry
        logger.info("Cleaning index registry...")
        db.cursor.execute("DELETE FROM rag_system.index_registry")
        db.conn.commit()
        logger.info("✅ Registry cleaned")
        
        logger.info("\n🎉 All indexes cleaned! Ready for benchmark.")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        db.close()


if __name__ == '__main__':
    clean_indexes()