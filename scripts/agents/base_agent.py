import logging
import sys
from pathlib import Path
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Agente base: logging estruturado, workdir, checkpoint integrado."""

    def __init__(self, name: str, config: dict, workdir: str | Path):
        self.name = name
        self.config = config
        self.workdir = Path(workdir)
        self.workdir.mkdir(parents=True, exist_ok=True)
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(self.name)
        if logger.handlers:
            return logger
        logger.setLevel(logging.INFO)
        fmt = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s — %(message)s",
                                datefmt="%Y-%m-%d %H:%M:%S")
        # Handler arquivo
        fh = logging.FileHandler(self.workdir / f"{self.name}.log")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
        # Handler terminal
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(fmt)
        logger.addHandler(ch)
        return logger

    @abstractmethod
    def run(self, **kwargs):
        pass

    def _warn_missing_tool(self, tool: str, install_hint: str = ""):
        self.logger.warning(f"⚠  Ferramenta '{tool}' não encontrada. {install_hint}")
        self.logger.warning(f"   Etapa '{self.name}' será pulada.")
