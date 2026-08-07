import sqlite3
import json
import os
import networkx as nx
from typing import List, Dict, Any

class StorageManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, "platform.db")
        self.db_path = db_path
        self._init_db()
        self.graph = nx.DiGraph()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Index Plein Texte FTS5 pour recherche instantanée
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
                    title,
                    source_url,
                    content,
                    entity_type,
                    tokenize = 'porter ascii'
                );
            """)
            # Table de stockage du Graphe d'Entités
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entity_relations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_entity TEXT NOT NULL,
                    relation TEXT NOT NULL,
                    target_entity TEXT NOT NULL,
                    metadata JSON
                );
            """)
            conn.commit()

    def add_document(self, title: str, source_url: str, content: str, entity_type: str = "general"):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO documents_fts (title, source_url, content, entity_type) VALUES (?, ?, ?, ?)",
                (title, source_url, content, entity_type)
            )
            conn.commit()

    def search_fts(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT title, source_url, snippet(documents_fts, 2, '<b>', '</b>', '...', 20) as snippet "
                "FROM documents_fts WHERE documents_fts MATCH ? ORDER BY rank LIMIT ?",
                (query, limit)
            )
            return [dict(row) for row in cursor.fetchall()]

    def add_relation(self, source: str, relation: str, target: str, meta: Dict = None):
        self.graph.add_edge(source, target, relation=relation, **(meta or {}))
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO entity_relations (source_entity, relation, target_entity, metadata) VALUES (?, ?, ?, ?)",
                (source, relation, target, json.dumps(meta or {}))
            )
            conn.commit()

    def get_graph_json(self) -> Dict[str, Any]:
        return nx.node_link_data(self.graph)
