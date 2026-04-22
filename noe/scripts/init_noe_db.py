"""
NOE Database Initialization Script
Creates and verifies the Quality Vault database
"""

import sqlite3
import os
from pathlib import Path

def init_database():
    """Initialize the NOE Quality Vault database."""
    
    # Get paths relative to this script
    script_dir = Path(__file__).parent.parent
    db_path = script_dir / "db" / "quality_vault.db"
    sql_path = script_dir / "db" / "init_quality_vault.sql"
    
    print(f"NOE Database Initialization")
    print(f"=" * 40)
    print(f"Database path: {db_path}")
    print(f"Schema path: {sql_path}")
    print()
    
    # Check if schema exists
    if not sql_path.exists():
        print(f"ERROR: Schema file not found at {sql_path}")
        return False
    
    # Create database
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Read and execute schema
        with open(sql_path, 'r') as f:
            schema = f.read()
        
        cursor.executescript(schema)
        conn.commit()
        
        print("Schema executed successfully.")
        print()
        
        # Verify tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"Tables created: {len(tables)}")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  - {table}: {count} rows")
        
        print()
        
        # Verify taste_memory seed data
        cursor.execute("SELECT COUNT(*) FROM taste_memory")
        taste_count = cursor.fetchone()[0]
        
        if taste_count >= 5:
            print(f"✓ Taste memory seeded: {taste_count} entries")
        else:
            print(f"WARNING: Expected 5 taste_memory entries, found {taste_count}")
        
        conn.close()
        
        print()
        print("=" * 40)
        print("NOE Quality Vault initialized successfully!")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False


if __name__ == "__main__":
    init_database()
