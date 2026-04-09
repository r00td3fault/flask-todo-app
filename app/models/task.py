from dataclasses import asdict, dataclass


@dataclass
class Task:
    id: int
    texto: str
    completada: bool = False

    def to_dict(self):
        return asdict(self)
