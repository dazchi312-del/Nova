-- NOE Quality Vault Schema
-- Session 1: Foundation Tables

-- Outputs table: stores every generation attempt
CREATE TABLE IF NOT EXISTS outputs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    score REAL,
    accepted INTEGER DEFAULT 0,
    refinement_count INTEGER DEFAULT 0,
    metadata TEXT
);

-- Taste memory: learned quality preferences
CREATE TABLE IF NOT EXISTS taste_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    pattern TEXT NOT NULL,
    weight REAL DEFAULT 1.0,
    created TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Refinement history: tracks improvement attempts
CREATE TABLE IF NOT EXISTS refinement_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    output_id INTEGER,
    attempt_number INTEGER,
    previous_score REAL,
    new_score REAL,
    temperature_used REAL,
    feedback TEXT,
    FOREIGN KEY (output_id) REFERENCES outputs(id)
);

-- Quality stats: aggregate metrics
CREATE TABLE IF NOT EXISTS quality_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    total_outputs INTEGER,
    accepted_count INTEGER,
    average_score REAL,
    refinement_success_rate REAL
);

-- Seed taste memory with Nova identity markers
INSERT INTO taste_memory (category, pattern, weight) VALUES
    ('voice', 'Use precise technical language', 1.2),
    ('voice', 'Avoid corporate buzzwords', 1.1),
    ('structure', 'Lead with context before details', 1.0),
    ('structure', 'Use hierarchical organization', 1.0),
    ('identity', 'Reference Nova ecosystem when relevant', 0.9);
