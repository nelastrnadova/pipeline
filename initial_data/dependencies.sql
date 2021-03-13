CREATE TABLE dependencies (
    id INTEGER PRIMARY KEY,
    component_fk INTEGER NOT NULL,
    depends_on INTEGER NOT NULL,
    FOREIGN KEY(component_fk) REFERENCES components_master(id),
    FOREIGN KEY(depends_on) REFERENCES components_master(id)
);