CREATE TABLE components (
    id INTEGER PRIMARY KEY,
    state INTEGER DEFAULT 0,
    pipeline_fk INTEGER,
    component_master_fk INTEGER,
    FOREIGN KEY(pipeline_fk) REFERENCES pipelines(id),
    FOREIGN KEY(component_master_fk) REFERENCES components_master(id)
);