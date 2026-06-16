# backend/services/memory_service.py
"""
MEMORY LAYER - Your Copilot never forgets!
Stores conversations, decisions, and learns from interactions.
"""

import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
import hashlib

class MemoryService:
    """The brain that remembers everything!"""
    
    def __init__(self):
        self.db_path = Path("./data/memory.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        print("✅ Memory service initialized!")
    
    def _init_database(self):
        """Initialize SQLite database with all tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                project_id TEXT,
                messages TEXT,
                summary TEXT,
                timestamp TEXT,
                role TEXT,
                metadata TEXT
            )
        ''')
        
        # Decisions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS decisions (
                id TEXT PRIMARY KEY,
                conversation_id TEXT,
                context TEXT,
                decision TEXT,
                rationale TEXT,
                alternatives TEXT,
                timestamp TEXT,
                status TEXT
            )
        ''')
        
        # Code context table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS code_context (
                id TEXT PRIMARY KEY,
                file_path TEXT,
                code_snippet TEXT,
                embedding TEXT,
                timestamp TEXT,
                metadata TEXT
            )
        ''')
        
        # Learning table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learnings (
                id TEXT PRIMARY KEY,
                topic TEXT,
                insight TEXT,
                source TEXT,
                timestamp TEXT,
                confidence REAL,
                tags TEXT
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                key TEXT,
                value TEXT,
                timestamp TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _generate_id(self) -> str:
        """Generate unique ID"""
        import uuid
        return str(uuid.uuid4())
    
    # ============================================
    # CONVERSATION MEMORY
    # ============================================
    
    def save_conversation(self, messages: List[Dict], role: str = "architect", project_id: str = None) -> Dict:
        """Save a conversation to memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        conv_id = self._generate_id()
        timestamp = datetime.now().isoformat()
        
        # Generate summary
        summary = self._summarize_conversation(messages)
        
        cursor.execute('''
            INSERT INTO conversations (id, project_id, messages, summary, timestamp, role, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            conv_id,
            project_id or "default",
            json.dumps(messages),
            summary,
            timestamp,
            role,
            json.dumps({"total_messages": len(messages)})
        ))
        
        conn.commit()
        conn.close()
        
        return {
            "id": conv_id,
            "summary": summary,
            "timestamp": timestamp,
            "messages_count": len(messages)
        }
    
    def get_conversation(self, conv_id: str) -> Optional[Dict]:
        """Get a specific conversation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM conversations WHERE id = ?', (conv_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "project_id": row[1],
                "messages": json.loads(row[2]),
                "summary": row[3],
                "timestamp": row[4],
                "role": row[5],
                "metadata": json.loads(row[6]) if row[6] else {}
            }
        return None
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """Get recent conversations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, summary, timestamp, role, metadata 
            FROM conversations 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            "id": row[0],
            "summary": row[1],
            "timestamp": row[2],
            "role": row[3],
            "metadata": json.loads(row[4]) if row[4] else {}
        } for row in rows]
    
    def search_conversations(self, query: str) -> List[Dict]:
        """Search through conversations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, summary, timestamp, role, messages 
            FROM conversations 
            WHERE summary LIKE ? OR messages LIKE ?
            ORDER BY timestamp DESC
        ''', (f'%{query}%', f'%{query}%'))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            "id": row[0],
            "summary": row[1],
            "timestamp": row[2],
            "role": row[3],
            "messages": json.loads(row[4]) if len(row) > 4 else []
        } for row in rows]
    
    def _summarize_conversation(self, messages: List[Dict]) -> str:
        """Generate a summary of the conversation"""
        if not messages:
            return "Empty conversation"
        
        # Get first and last messages
        first = messages[0].get('message', '')[:50]
        last = messages[-1].get('message', '')[:50]
        
        return f"Started with: {first}... Ended with: {last}..."
    
    # ============================================
    # DECISION MEMORY
    # ============================================
    
    def save_decision(self, context: str, decision: str, rationale: str, alternatives: List[str] = None) -> Dict:
        """Save an important decision"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        dec_id = self._generate_id()
        timestamp = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO decisions (id, context, decision, rationale, alternatives, timestamp, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            dec_id,
            context,
            decision,
            rationale,
            json.dumps(alternatives or []),
            timestamp,
            "active"
        ))
        
        conn.commit()
        conn.close()
        
        return {
            "id": dec_id,
            "decision": decision,
            "timestamp": timestamp
        }
    
    def get_decisions(self, limit: int = 20) -> List[Dict]:
        """Get all decisions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, context, decision, rationale, timestamp, status
            FROM decisions
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            "id": row[0],
            "context": row[1],
            "decision": row[2],
            "rationale": row[3],
            "timestamp": row[4],
            "status": row[5]
        } for row in rows]
    
    # ============================================
    # LEARNING MEMORY
    # ============================================
    
    def learn(self, topic: str, insight: str, source: str = "conversation") -> Dict:
        """Store a learning/insight"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        learn_id = self._generate_id()
        timestamp = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO learnings (id, topic, insight, source, timestamp, confidence, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            learn_id,
            topic,
            insight,
            source,
            timestamp,
            0.8,  # default confidence
            json.dumps([topic.lower()])
        ))
        
        conn.commit()
        conn.close()
        
        return {
            "id": learn_id,
            "topic": topic,
            "insight": insight,
            "timestamp": timestamp
        }
    
    def get_learnings(self, topic: str = None, limit: int = 20) -> List[Dict]:
        """Get learnings, optionally filtered by topic"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if topic:
            cursor.execute('''
                SELECT id, topic, insight, source, timestamp, confidence
                FROM learnings
                WHERE topic LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (f'%{topic}%', limit))
        else:
            cursor.execute('''
                SELECT id, topic, insight, source, timestamp, confidence
                FROM learnings
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            "id": row[0],
            "topic": row[1],
            "insight": row[2],
            "source": row[3],
            "timestamp": row[4],
            "confidence": row[5]
        } for row in rows]
    
    # ============================================
    # PREFERENCES
    # ============================================
    
    def set_preference(self, key: str, value: str, user_id: str = "default") -> Dict:
        """Set user preference"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        pref_id = self._generate_id()
        timestamp = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO preferences (id, user_id, key, value, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (pref_id, user_id, key, value, timestamp))
        
        conn.commit()
        conn.close()
        
        return {"key": key, "value": value}
    
    def get_preference(self, key: str, user_id: str = "default") -> Optional[str]:
        """Get user preference"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT value FROM preferences
            WHERE user_id = ? AND key = ?
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (user_id, key))
        
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else None
    
    # ============================================
    # CONTEXT BUILDING
    # ============================================
    
    def build_context(self, limit: int = 5) -> Dict:
        """Build rich context from memory"""
        return {
            "recent_conversations": self.get_recent_conversations(limit),
            "recent_decisions": self.get_decisions(limit),
            "learnings": self.get_learnings(limit=limit),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_memory_stats(self) -> Dict:
        """Get memory statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        for table in ['conversations', 'decisions', 'learnings', 'preferences']:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            stats[table] = count
        
        conn.close()
        return stats

# Create global instance
memory = MemoryService()