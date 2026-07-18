import json
import os
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
        # Escrita atômica (tmp + replace): evita corrupção quando dois processos
        # gravam o mesmo checkpoint.json quase ao mesmo tempo (colisão real
        # encontrada 2026-07-18 — dois --step concorrentes intercalaram bytes
        # no meio do arquivo, corrompendo o JSON).
        tmp = self.filename.with_suffix(self.filename.suffix + ".tmp")
        with open(tmp, "w") as f:
            json.dump(self.data, f, indent=2)
        os.replace(tmp, self.filename)

    def load(self, step):
        return self.data.get(step, {})

    def is_completed(self, step):
        return step in self.data