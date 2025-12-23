CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    raw_path TEXT NOT NULL,
    extracted_text TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
