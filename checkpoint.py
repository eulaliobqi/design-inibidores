import json
from pathlib import Path

class CheckpointManager:
    def __init__(self, filename):
        self.filename = Path(filename)
        self.data = {}
        if self.filename.exists():
            with open(self.filename) as f:
                self.data = json.load(f)

    def save(self, step, result):
        self.data[step] = result
        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=2)

    def load(self, step):
        return self.data.get(step, {})

    def is_completed(self, step):
        return step in self.data