CREATE TABLE components_master (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    runner VARCHAR(255) NOT NULL,
    pipeline_fk INTEGER NOT NULL,
    FOREIGN KEY(pipeline_fk) REFERENCES pipelines_master(id)
);