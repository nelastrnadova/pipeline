CREATE TABLE pipelines (
    id INTEGER PRIMARY KEY,
    state INTEGER DEFAULT 0,
    start INTEGER DEFAULT 0,
    pipeline_master_fk INTEGER,
    FOREIGN KEY(pipeline_master_fk) REFERENCES pipelines_master(id)
);