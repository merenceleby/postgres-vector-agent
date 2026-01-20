"""
Load Wikipedia data into PostgreSQL
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.database import DatabaseManager
from agent.embeddings import EmbeddingGenerator
from datasets import load_dataset
from tqdm import tqdm
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_wikipedia_data(num_documents: int = 5000):
    """
    Load Wikipedia articles and embed them
    
    Args:
        num_documents: Number of documents to load
    """
    logger.info(f"📚 Loading {num_documents} Wikipedia articles...")
    
    # Initialize components
    db = DatabaseManager()
    db.connect()
    embedder = EmbeddingGenerator()
    
    try:
        # Load Wikipedia dataset (using 20220301.simple subset - smaller articles)
        logger.info("Downloading dataset...")
        dataset = load_dataset(
            "wikipedia",
            "20220301.simple",
            split="train",
            streaming=True
        )
        
        # Process documents in batches
        batch_size = 100
        documents = []
        batch_num = 0
        
        logger.info("Processing documents...")
        
        for i, item in enumerate(tqdm(dataset, total=num_documents)):
            if i >= num_documents:
                break
            
            # Extract text
            text = item['text'][:1000]  # First 1000 chars
            
            if len(text) < 100:  # Skip very short texts
                continue
            
            documents.append({
                'tenant_id': 'wikipedia',
                'content': text,
                'metadata': {
                    'title': item['title'],
                    'url': item['url'],
                    'source': 'wikipedia'
                }
            })
            
            # Process batch when ready
            if len(documents) >= batch_size:
                batch_num += 1
                logger.info(f"Processing batch {batch_num} ({len(documents)} docs)...")
                
                # Generate embeddings
                texts = [doc['content'] for doc in documents]
                embeddings = embedder.encode_documents(texts)
                
                # Add embeddings to documents
                for doc, emb in zip(documents, embeddings):
                    doc['embedding'] = emb
                
                # Insert to database
                db.insert_documents(documents)
                
                logger.info(f"✅ Batch {batch_num} inserted")
                documents = []
        
        # Insert remaining documents
        if documents:
            logger.info("Processing final batch...")
            texts = [doc['content'] for doc in documents]
            embeddings = embedder.encode_documents(texts)
            
            for doc, emb in zip(documents, embeddings):
                doc['embedding'] = emb
            
            db.insert_documents(documents)
        
        logger.info(f"✅ Successfully loaded {num_documents} documents!")
        
        # Print statistics
        result = db.execute_query("SELECT COUNT(*) as count FROM rag_system.documents")
        total_count = result[0]['count']
        logger.info(f"📊 Total documents in database: {total_count}")
        
    except Exception as e:
        logger.error(f"❌ Error loading data: {e}")
        raise
    finally:
        db.close()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Load Wikipedia data')
    parser.add_argument('--num-docs', type=int, default=5000,
                       help='Number of documents to load (default: 5000)')
    
    args = parser.parse_args()
    
    load_wikipedia_data(args.num_docs)