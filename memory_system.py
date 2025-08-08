# AI Memory System - The Brain of the Copilot
# Stores, learns, and recalls design patterns

import json
import sqlite3
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional
import hashlib
from pathlib import Path

class CADMemorySystem:
    """Intelligent memory for CAD operations"""
    
    def __init__(self, db_path: Optional[str] = None):
        # Store in user's FreeCAD config directory
        if not db_path:
            import FreeCAD
            config_dir = Path(FreeCAD.getUserAppDataDir()) / "AICopilot"
            config_dir.mkdir(exist_ok=True)
            db_path = config_dir / "memory.db"
            
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
        self._init_database()
        
    def _init_database(self):
        """Initialize database schema"""
        cursor = self.conn.cursor()
        
        # Design sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS design_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                description TEXT,
                created_at TIMESTAMP,
                last_accessed TIMESTAMP,
                tags TEXT,
                embeddings BLOB
            )
        """)
        
        # Operations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                operation_type TEXT,
                parameters TEXT,
                context TEXT,
                timestamp TIMESTAMP,
                was_successful BOOLEAN,
                was_undone BOOLEAN,
                time_taken REAL,
                FOREIGN KEY (session_id) REFERENCES design_sessions(session_id)
            )
        """)
        
        # Patterns table - learned patterns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_name TEXT,
                operation_sequence TEXT,
                frequency INTEGER,
                success_rate REAL,
                avg_time REAL,
                last_used TIMESTAMP
            )
        """)
        
        # User preferences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                preference_type TEXT,
                preference_value TEXT,
                confidence REAL,
                learned_at TIMESTAMP
            )
        """)
        
        self.conn.commit()
        
    def start_session(self, description: str = "") -> str:
        """Start a new design session"""
        session_id = hashlib.md5(
            f"{datetime.now().isoformat()}{description}".encode()
        ).hexdigest()[:12]
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO design_sessions (session_id, description, created_at, last_accessed)
            VALUES (?, ?, ?, ?)
        """, (session_id, description, datetime.now(), datetime.now()))
        
        self.conn.commit()
        self.current_session = session_id
        return session_id
        
    def store_operation(self, op_type: str, parameters: Dict, context: Dict):
        """Store an operation with full context"""
        if not hasattr(self, 'current_session'):
            self.start_session("Auto-generated session")
            
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO operations 
            (session_id, operation_type, parameters, context, timestamp, was_successful, time_taken)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            self.current_session,
            op_type,
            json.dumps(parameters),
            json.dumps(context),
            datetime.now(),
            True,  # Assume successful unless marked otherwise
            context.get("duration", 0)
        ))
        
        self.conn.commit()
        
        # Check for patterns
        self._detect_and_store_patterns()
        
    def mark_operation_failed(self, operation_id: int):
        """Mark an operation as failed/undone"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE operations 
            SET was_undone = TRUE, was_successful = FALSE
            WHERE id = ?
        """, (operation_id,))
        self.conn.commit()
        
    def recall_similar_designs(self, query: str, limit: int = 5) -> List[Dict]:
        """Find similar previous designs"""
        # Simple keyword matching for now
        # TODO: Add vector embeddings for semantic search
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT s.*, GROUP_CONCAT(o.operation_type) as operations
            FROM design_sessions s
            LEFT JOIN operations o ON s.session_id = o.session_id
            WHERE s.description LIKE ? OR s.tags LIKE ?
            GROUP BY s.session_id
            ORDER BY s.last_accessed DESC
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "session_id": row[1],
                "description": row[2],
                "created": row[3],
                "operations": row[-1].split(",") if row[-1] else []
            })
            
        return results
        
    def get_operation_sequence(self, session_id: str) -> List[Dict]:
        """Get full operation sequence for a session"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT operation_type, parameters, context, timestamp
            FROM operations
            WHERE session_id = ? AND was_successful = TRUE
            ORDER BY timestamp
        """, (session_id,))
        
        operations = []
        for row in cursor.fetchall():
            operations.append({
                "type": row[0],
                "parameters": json.loads(row[1]),
                "context": json.loads(row[2]),
                "timestamp": row[3]
            })
            
        return operations
        
    def _detect_and_store_patterns(self):
        """Detect patterns in recent operations"""
        cursor = self.conn.cursor()
        
        # Get last 20 operations
        cursor.execute("""
            SELECT operation_type, parameters, time_taken, was_successful
            FROM operations
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT 20
        """, (self.current_session,))
        
        recent_ops = cursor.fetchall()
        
        if len(recent_ops) >= 3:
            # Check for sequences of 3 operations
            for i in range(len(recent_ops) - 2):
                sequence = [recent_ops[i][0], recent_ops[i+1][0], recent_ops[i+2][0]]
                sequence_str = "->".join(sequence)
                
                # Check if pattern exists
                cursor.execute("""
                    SELECT id, frequency FROM patterns
                    WHERE pattern_name = ?
                """, (sequence_str,))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Update frequency
                    cursor.execute("""
                        UPDATE patterns
                        SET frequency = frequency + 1, last_used = ?
                        WHERE id = ?
                    """, (datetime.now(), existing[0]))
                else:
                    # Store new pattern
                    avg_time = sum(op[2] for op in recent_ops[i:i+3]) / 3
                    success_rate = sum(1 for op in recent_ops[i:i+3] if op[3]) / 3
                    
                    cursor.execute("""
                        INSERT INTO patterns (pattern_name, operation_sequence, frequency, success_rate, avg_time, last_used)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (sequence_str, json.dumps(sequence), 1, success_rate, avg_time, datetime.now()))
                    
        self.conn.commit()
        
    def get_common_patterns(self, min_frequency: int = 3) -> List[Dict]:
        """Get commonly used patterns"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT pattern_name, operation_sequence, frequency, success_rate, avg_time
            FROM patterns
            WHERE frequency >= ?
            ORDER BY frequency DESC
        """, (min_frequency,))
        
        patterns = []
        for row in cursor.fetchall():
            patterns.append({
                "name": row[0],
                "sequence": json.loads(row[1]),
                "frequency": row[2],
                "success_rate": row[3],
                "avg_time": row[4]
            })
            
        return patterns
        
    def learn_preference(self, pref_type: str, pref_value: str, confidence: float = 1.0):
        """Learn a user preference"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO preferences (preference_type, preference_value, confidence, learned_at)
            VALUES (?, ?, ?, ?)
        """, (pref_type, pref_value, confidence, datetime.now()))
        self.conn.commit()
        
    def get_preferences(self) -> Dict[str, str]:
        """Get learned preferences"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT preference_type, preference_value, confidence
            FROM preferences
            WHERE confidence > 0.5
            ORDER BY confidence DESC
        """)
        
        prefs = {}
        for row in cursor.fetchall():
            prefs[row[0]] = row[1]
            
        return prefs
        
    def suggest_next_operation(self, current_context: Dict) -> Optional[Dict]:
        """Suggest next operation based on patterns"""
        # Get recent operations
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT operation_type
            FROM operations
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT 2
        """, (self.current_session,))
        
        recent = [row[0] for row in cursor.fetchall()]
        
        if len(recent) >= 2:
            # Look for matching pattern
            pattern_start = f"{recent[1]}->{recent[0]}->"
            
            cursor.execute("""
                SELECT pattern_name, success_rate, avg_time
                FROM patterns
                WHERE pattern_name LIKE ?
                ORDER BY frequency DESC
                LIMIT 1
            """, (f"{pattern_start}%",))
            
            match = cursor.fetchone()
            if match:
                next_op = match[0].split("->")[-1]
                return {
                    "operation": next_op,
                    "confidence": match[1],
                    "expected_time": match[2]
                }
                
        return None