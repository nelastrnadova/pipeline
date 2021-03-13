CREATE TABLE component_outputs (
    id INTEGER PRIMARY KEY,
    val VARCHAR(255) NOT NULL,
    component_fk INTEGER,
    component_output_master_fk INTEGER,
    FOREIGN KEY(component_fk) REFERENCES components(id),
    FOREIGN KEY(component_output_master_fk) REFERENCES component_outputs_master(id)
);