CREATE TABLE components_master (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    runner VARCHAR(255) NOT NULL,
    pipeline_master_fk INTEGER NOT NULL,
    FOREIGN KEY(pipeline_master_fk) REFERENCES pipelines_master(id)
);