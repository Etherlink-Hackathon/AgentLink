import os
import psycopg2
import json
from datetime import datetime, timedelta

def get_latest_opportunities():
    """
    Fetch the latest 'EXECUTE' decisions from the DipDup database.
    """
    conn_str = f"host={os.getenv('POSTGRES_HOST', 'localhost')} " \
               f"dbname={os.getenv('POSTGRES_DB', 'dipdup')} " \
               f"user={os.getenv('POSTGRES_USER', 'dipdup')} " \
               f"password={os.getenv('POSTGRES_PASSWORD', 'changeme')}"
    
    try:
        conn = psycopg2.connect(conn_str)
        cur = conn.cursor()
        
        # Query for EXECUTE decisions in the last 15 minutes
        since = datetime.utcnow() - timedelta(minutes=15)
        query = """
            SELECT id, vault_id, decision, reason, opportunity_details, timestamp 
            FROM agent_decision 
            WHERE decision = 'EXECUTE' AND timestamp > %s
            ORDER BY timestamp DESC
            LIMIT 5;
        """
        cur.execute(query, (since,))
        rows = cur.fetchall()
        
        opportunities = []
        for row in rows:
            opportunities.append({
                "id": row[0],
                "vault": row[1],
                "decision": row[2],
                "reason": row[3],
                "details": row[4],
                "timestamp": row[5].isoformat()
            })
            
        print(json.dumps(opportunities, indent=2))
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    get_latest_opportunities()
