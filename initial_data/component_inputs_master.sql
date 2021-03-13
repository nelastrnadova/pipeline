CREATE TABLE component_inputs_master (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    component_master_fk INTEGER NOT NULL,
    FOREIGN KEY(component_master_fk) REFERENCES components_master(id)
);