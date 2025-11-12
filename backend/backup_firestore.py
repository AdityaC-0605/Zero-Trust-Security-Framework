"""
Firestore backup script for production data protection
Supports automated backups to Google Cloud Storage
"""

import os
import json
from datetime import datetime, timedelta
from firebase_admin import firestore
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FirestoreBackup:
    """Handles Firestore database backups"""
    
    def __init__(self):
        self.db = firestore.client()
        self.project_id = os.getenv('FIREBASE_PROJECT_ID')
        self.backup_bucket = os.getenv('BACKUP_BUCKET', f'{self.project_id}-backups')
    
    def export_collection(self, collection_name, output_dir='./backups'):
        """Export a single collection to JSON"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            collection_ref = self.db.collection(collection_name)
            docs = collection_ref.stream()
            
            data = []
            for doc in docs:
                doc_data = doc.to_dict()
                doc_data['_id'] = doc.id
                data.append(doc_data)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{output_dir}/{collection_name}_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"Exported {len(data)} documents from {collection_name} to {filename}")
            return filename
        
        except Exception as e:
            logger.error(f"Failed to export collection {collection_name}: {str(e)}")
            raise
    
    def export_all_collections(self, output_dir='./backups'):
        """Export all collections"""
        collections = [
            'users',
            'accessRequests',
            'auditLogs',
            'policies',
            'notifications',
            'systemConfig'
        ]
        
        exported_files = []
        for collection in collections:
            try:
                filename = self.export_collection(collection, output_dir)
                exported_files.append(filename)
            except Exception as e:
                logger.error(f"Failed to export {collection}: {str(e)}")
        
        return exported_files
    
    def backup_to_gcs(self):
        """
        Backup Firestore to Google Cloud Storage using managed export
        Requires gcloud CLI and appropriate permissions
        """
        try:
            import subprocess
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_uri = f"gs://{self.backup_bucket}/firestore-backups/{timestamp}"
            
            # Use gcloud firestore export command
            cmd = [
                'gcloud', 'firestore', 'export',
                output_uri,
                '--project', self.project_id
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Firestore backup successful: {output_uri}")
                return output_uri
            else:
                logger.error(f"Firestore backup failed: {result.stderr}")
                raise Exception(result.stderr)
        
        except Exception as e:
            logger.error(f"Failed to backup to GCS: {str(e)}")
            raise
    
    def cleanup_old_backups(self, days=30):
        """Clean up backups older than specified days"""
        try:
            from google.cloud import storage
            
            client = storage.Client()
            bucket = client.bucket(self.backup_bucket)
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            blobs = bucket.list_blobs(prefix='firestore-backups/')
            deleted_count = 0
            
            for blob in blobs:
                if blob.time_created.replace(tzinfo=None) < cutoff_date:
                    blob.delete()
                    deleted_count += 1
                    logger.info(f"Deleted old backup: {blob.name}")
            
            logger.info(f"Cleaned up {deleted_count} old backups")
            return deleted_count
        
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {str(e)}")
            raise
    
    def restore_collection(self, collection_name, backup_file):
        """Restore a collection from backup file"""
        try:
            with open(backup_file, 'r') as f:
                data = json.load(f)
            
            collection_ref = self.db.collection(collection_name)
            restored_count = 0
            
            for doc_data in data:
                doc_id = doc_data.pop('_id')
                collection_ref.document(doc_id).set(doc_data)
                restored_count += 1
            
            logger.info(f"Restored {restored_count} documents to {collection_name}")
            return restored_count
        
        except Exception as e:
            logger.error(f"Failed to restore collection {collection_name}: {str(e)}")
            raise


def scheduled_backup():
    """Function to be called by cron job or Cloud Scheduler"""
    try:
        backup = FirestoreBackup()
        
        # Perform backup to GCS
        output_uri = backup.backup_to_gcs()
        logger.info(f"Scheduled backup completed: {output_uri}")
        
        # Cleanup old backups
        backup.cleanup_old_backups(days=90)
        
        return True
    except Exception as e:
        logger.error(f"Scheduled backup failed: {str(e)}")
        return False


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python backup_firestore.py export [collection_name]")
        print("  python backup_firestore.py backup")
        print("  python backup_firestore.py cleanup [days]")
        print("  python backup_firestore.py restore <collection_name> <backup_file>")
        sys.exit(1)
    
    backup = FirestoreBackup()
    command = sys.argv[1]
    
    if command == 'export':
        if len(sys.argv) > 2:
            backup.export_collection(sys.argv[2])
        else:
            backup.export_all_collections()
    
    elif command == 'backup':
        backup.backup_to_gcs()
    
    elif command == 'cleanup':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        backup.cleanup_old_backups(days)
    
    elif command == 'restore':
        if len(sys.argv) < 4:
            print("Error: restore requires collection_name and backup_file")
            sys.exit(1)
        backup.restore_collection(sys.argv[2], sys.argv[3])
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
