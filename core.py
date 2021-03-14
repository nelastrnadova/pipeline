import importlib
import threading
import time

from database import Database


class Core:
    def __init__(self, max_allowed_running_pipelines: int = 10, db_name: str = 'database.db'):
        self.max_allowed_running_pipelines: int = max_allowed_running_pipelines
        self.running: bool = True
        self.db = Database(db_name)

    def main(self) -> None:
        while self.running:
            self.check_components()
            self.check_pipelines()
            time.sleep(0.2)

    def run_component(self, component_id: int) -> None:
        component_master_id, pipeline_id = self.db.single_select('components', ['component_master_fk', 'pipeline_fk'], ['id'], [component_id])
        pipeline_master_id = self.db.single_select('pipelines', ['pipeline_master_fk'], ['id'], [pipeline_id])[0]
        required_inputs = self.db.select('component_inputs_master', ['id', 'name'], ['component_master_fk'], [component_master_id])

        inputs = {}
        for input_master_id, input_name in required_inputs:
            if '.' in input_name:
                component_name = input_name.split('.')[0]
                input_name_processed = input_name.split('.')[1]
                component_dependency_id_master = self.db.single_select('components_master', ['id'], ['name', 'pipeline_master_fk'], [component_name, pipeline_master_id])[0]
                component_dependency_id = self.db.single_select('components', ['id'], ['pipeline_fk', 'component_master_fk'], [pipeline_id, component_dependency_id_master])[0]
                component_dependency_output_id_master = self.db.single_select('component_outputs_master', ['id'], ['name', 'component_master_fk'], [input_name_processed, component_dependency_id_master])[0]
                component_dependency_output_val = self.db.single_select('component_outputs', ['val'], ['component_fk', 'component_output_master_fk'], [component_dependency_id, component_dependency_output_id_master])[0]
                inputs[input_name_processed] = component_dependency_output_val
            else:
                pipeline_input_id = self.db.single_select('pipeline_inputs_master', ['id'], ['pipeline_master_fk', 'name'], [pipeline_master_id, input_name])[0]
                val = self.db.single_select('pipeline_inputs', ['val'], ['pipeline_fk', 'pipeline_input_master_fk'], [pipeline_id, pipeline_input_id])[0]
                inputs[input_name] = val

        self.db.update('components', ['state'], [1], ['id'], [component_id])

        runner = self.db.single_select('components_master', ['runner'], ['id'], [component_master_id])[0]
        module = runner.split('.')[-1]  # TODO: error handling if invalid path (no dot in runner)
        outputs = getattr(
                    importlib.import_module(runner), module
                )().exec(inputs)

        for output in outputs:
            component_output_master_id = self.db.single_select('component_outputs_master', ['id'], ['name', 'component_master_fk'], [output, component_master_id])[0]
            self.db.insert('component_outputs', ['val', 'component_fk', 'component_output_master_fk'], [outputs[output], component_id, component_output_master_id])
        self.db.update('components', ['state'], [2], ['id'], [component_id])  # TODO: check if all outputs filled. if not state 3

    def can_component_run(self, component_id: int) -> bool:
        component_master_id, pipeline_id = self.db.single_select('components', ['component_master_fk', 'pipeline_fk'], ['id'], [component_id])
        depends_on = self.db.select('dependencies', ['depends_on'], ['component_fk'], [component_master_id])
        if not len(depends_on):
            return True
        for dependency in depends_on:
            if self.db.single_select('components', ['state'], ['component_master_fk', 'pipeline_fk'], [dependency[0], pipeline_id])[0] != 2:
                return False
        return True

    def start_pipeline(self, pipeline_id: int) -> None:
        self.db.update('pipelines', ['state', 'start'], [1, int(time.time())], ['id'], [pipeline_id])

    def should_pipeline_timeout(self, pipeline_id: int) -> None:
        master_pipeline_id = self.db.single_select('pipelines', ['pipeline_master_fk'], ['id'], [pipeline_id])[0]
        allowed_runtime = self.db.single_select('pipelines_master', ['max_runtime'], ['id'], [master_pipeline_id])[0]
        start = self.db.single_select('pipelines', ['start'], ['id'], [pipeline_id])[0]
        return not (int(time.time()) - start < allowed_runtime)

    def check_pipeline_should_start(self, pipeline_id: int) -> bool:
        return len(self.db.select('pipelines', ['state'], ['state'], [1])) < self.max_allowed_running_pipelines

    def is_any_pipeline_component_crashed(self, pipeline_id: int) -> bool:
        for component in self.db.select('components', ['state'], ['pipeline_fk'], [pipeline_id]):
            if component[0] == 3:
                return True
        return False

    def are_pipeline_components_finished(self, pipeline_id: int) -> bool:
        for component in self.db.select('components', ['state'], ['pipeline_fk'], [pipeline_id]):
            if component[0] in [0, 1]:
                return False
        return True

    def check_components(self) -> None:
        for component_waiting in self.db.select('components', ['id'], ['state'], [0]):
            component_id = component_waiting[0]
            if self.can_component_run(component_id):
                threading.Thread(target=self.run_component, args=(component_id,)).run()

    def check_pipelines(self) -> None:
        for pipeline_waiting in self.db.select('pipelines', ['id'], ['state'], [0]):
            pipeline_id = pipeline_waiting[0]
            if self.check_pipeline_should_start(pipeline_id):
                self.start_pipeline(pipeline_id)
        for pipeline_running in self.db.select('pipelines', ['id'], ['state'], [1]):
            pipeline_id = pipeline_running[0]
            if self.is_any_pipeline_component_crashed(pipeline_id) or self.should_pipeline_timeout(pipeline_id):
                self.db.update('pipelines', ['state'], [3], ['id'], [pipeline_id])
            elif self.are_pipeline_components_finished(pipeline_id):
                pipeline_master_id = self.db.single_select('pipelines', ['pipeline_master_fk'], ['id'], [pipeline_id])[0]
                output_names = [output_name[0] for output_name in self.db.select('pipeline_outputs_master', ['name'], ['pipeline_master_fk'], [pipeline_master_id])]
                component_children_master_ids = [component_id[0] for component_id in self.db.select('components_master', ['id'], ['pipeline_master_fk'], [pipeline_master_id])]
                component_outputs_master_ids_names = []
                for component_children_master_id in component_children_master_ids:
                    tmp = list(self.db.single_select('component_outputs_master', ['id', 'name'], ['component_master_fk'], [component_children_master_id]))
                    tmp.append(component_children_master_id)
                    component_outputs_master_ids_names.append(tmp)

                output_return_preprocessed = {}
                for output in output_names:
                    for output_master in component_outputs_master_ids_names:
                        if output == output_master[1]:
                            component_id = self.db.single_select('components', ['id'], ['pipeline_fk', 'component_master_fk'], [pipeline_id, output_master[2]])[0]
                            output_return_preprocessed[output] = self.db.single_select('component_outputs', ['val'], ['component_fk', 'component_output_master_fk'], [component_id, output_master[0]])[0]

                output_return = {}
                for output_name in output_return_preprocessed:
                    output_return[self.db.single_select('pipeline_outputs_master', ['id'], ['name', 'pipeline_master_fk'], [output_name, pipeline_master_id])[0]] = output_return_preprocessed[output_name]

                for output_id in output_return:
                    self.db.insert('pipeline_outputs', ['val', 'pipeline_fk', 'pipeline_output_master_fk'], [output_return[output_id], pipeline_id, output_id])

                self.db.insert('pipeline_outputs', [''])
                self.db.update('pipelines', ['state'], [2], ['id'], [pipeline_id])


if __name__ == '__main__':
    Core().main()
