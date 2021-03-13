CREATE TABLE components (
    id INTEGER PRIMARY KEY,
    state INTEGER DEFAULT 0,
    component_master_fk INTEGER,
    FOREIGN KEY(component_master_fk) REFERENCES components_master(id)
);