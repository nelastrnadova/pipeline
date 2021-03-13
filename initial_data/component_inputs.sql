CREATE TABLE component_inputs (
    id INTEGER PRIMARY KEY,
    val VARCHAR(255) NOT NULL,
    component_fk INTEGER,
    component_input_master_fk INTEGER,
    FOREIGN KEY(component_fk) REFERENCES components(id),
    FOREIGN KEY(component_input_master_fk) REFERENCES component_inputs_master(id)
);