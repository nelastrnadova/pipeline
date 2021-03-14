import json


class File:
    def __init__(self, filename: str):
        self.filename = filename

    def get_content(self):
        return open(self.filename, "r").read()

    def get_as_json(self):
        return json.loads(self.get_content())
