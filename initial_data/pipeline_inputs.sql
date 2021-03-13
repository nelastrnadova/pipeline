CREATE TABLE pipeline_inputs (
    id INTEGER PRIMARY KEY,
    val VARCHAR(255) NOT NULL,
    pipeline_fk INTEGER,
    pipeline_input_master_fk INTEGER,
    FOREIGN KEY(pipeline_fk) REFERENCES pipelines(id),
    FOREIGN KEY(pipeline_input_master_fk) REFERENCES pipeline_inputs_master(id)
);