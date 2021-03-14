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
        # TODO: get inputs, start component, set state to running, save output to component outputs, set state to finished
        pass

    def can_component_run(self, component_id: int) -> bool:
        component_master_id, pipeline_id = self.db.single_select('components', ['component_master_fk', 'pipeline_fk'], ['id'], [component_id])
        depends_on = self.db.select('dependencies', ['depends_on'], ['component_fk'], [component_master_id])
        if not len(depends_on):
            return True
        for dependency in depends_on:
            if self.db.single_select('components', ['state'], ['component_master_fk', 'pipeline_fk'], [dependency, pipeline_id])[0] != 2:
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
                self.run_component(component_id)  # async

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
                self.db.update('pipelines', ['state'], [2], ['id'], [pipeline_id])
                # TODO: set pipeline outputs


if __name__ == '__main__':
    Core().main()
