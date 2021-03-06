import argparse
from glob import glob

from database import Database
from file import File
from yaml import Yaml

parser = argparse.ArgumentParser()
parser.add_argument("json", type=str, help="Path to yaml file")
parser.add_argument("-db", type=str, help="Path to db file", default="database.db")
args = parser.parse_args()

db = Database(args.db)

import_json = File(args.json).get_as_json()
for pipeline in import_json:
    pipeline_json = import_json[pipeline]
    pipeline_id = db.insert('pipelines_master', ['name', 'description'], [pipeline, pipeline_json['name']])

    if 'inputs' in pipeline_json:
        for pipeline_input in pipeline_json['inputs']:
            db.insert('pipeline_inputs_master', ['name', 'pipeline_master_fk'], [pipeline_input, pipeline_id])

    if 'outputs' in pipeline_json:
        for pipeline_output in pipeline_json['outputs']:
            db.insert('pipeline_outputs_master', ['name', 'pipeline_master_fk'], [pipeline_output, pipeline_id])

    for component in pipeline_json['components']:
        component_json = pipeline_json['components'][component]
        component_id = db.insert('components_master', ['name', 'runner', 'pipeline_master_fk'], [component, component_json['runner'], pipeline_id])

        if 'inputs' in component_json:
            for component_input in component_json['inputs']:
                if '.' in component_input:
                    dep = component_input.split('.')[0]
                    if 'dependencies' not in component_json:
                        component_json['dependencies'] = []
                    if dep not in component_json['dependencies']:
                        component_json['dependencies'].append(dep)
                db.insert('component_inputs_master', ['name', 'component_master_fk'], [component_input, component_id])

        if 'outputs' in component_json:
            for component_output in component_json['outputs']:
                db.insert('component_outputs_master', ['name', 'component_master_fk'], [component_output, component_id])

    for component in pipeline_json['components']:
        component_json = pipeline_json['components'][component]
        if 'dependencies' in component_json:
            component_id = db.single_select('components_master', ['id'], ['name', 'pipeline_master_fk'], [component, str(pipeline_id)])[0]
            for component_dependency in component_json['dependencies']:
                depends_on_id = db.single_select('components_master', ['id'], ['name', 'pipeline_master_fk'], [component_dependency, str(pipeline_id)])[0]
                db.insert('dependencies', ['component_fk', 'depends_on'], [component_id, depends_on_id])
