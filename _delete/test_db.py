import psycopg2
import json

try:
    dsn = 'postgresql://narrative:shadow_secret@127.0.0.1:25433/narrative_shadow'
    conn = psycopg2.connect(dsn)
    cur = conn.cursor()
    
    print('=== ALL RECENT EXTRACTIONS ===')
    cur.execute('''
        SELECT q.raw_headline, e.geopolitical_extraction 
        FROM llm_retry_queue q
        LEFT JOIN events e ON q.article_hash = e.content_hash
        WHERE q.status = 'COMPLETED'
        ORDER BY q.completed_at DESC NULLS LAST
        LIMIT 5
    ''')
    for row in cur.fetchall():
        print(f'H: {row[0]}')
        print(f'J: {json.dumps(row[1]) if row[1] else "NONE"}')
        print('-'*40)
        
    print('=== QUEUE COUNTS ===')
    cur.execute('SELECT status, COUNT(*) FROM llm_retry_queue GROUP BY status')
    for row in cur.fetchall():
        print(f'{row[0]}: {row[1]}')
        
    cur.close()
    conn.close()
except Exception as err:
    print('Error:', err)
