import time
import logging
from firebase_admin import firestore

logger = logging.getLogger(__name__)

class FirestoreWrapper:
    def __init__(self, db_client):
        self._db = db_client

    def __getattr__(self, name):
        return getattr(self._db, name)
        
    def stream_with_logging(self, query, description="Firestore_Query"):
        start = time.time()
        results = list(query.stream())
        duration = time.time() - start
        
        if duration > 1.0:
            logger.warning(f"SLOW QUERY: {description} took {duration:.2f}s")
            
        return results

    def paginate_query(self, query, limit=100, start_after_doc=None):
        if start_after_doc:
            query = query.start_after(start_after_doc)
        
        query = query.limit(limit)
        return self.stream_with_logging(query, description="Paginated Query")

def get_wrapped_db():
    return FirestoreWrapper(firestore.client())
