CREATE TABLE pipeline_outputs (
    id INTEGER PRIMARY KEY,
    val VARCHAR(255) NOT NULL,
    pipeline_fk INTEGER,
    pipeline_output_master_fk INTEGER,
    FOREIGN KEY(pipeline_fk) REFERENCES pipelines(id),
    FOREIGN KEY(pipeline_output_master_fk) REFERENCES pipeline_outputs_master(id)
);