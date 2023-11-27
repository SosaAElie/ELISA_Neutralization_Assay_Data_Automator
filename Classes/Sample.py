from dataclasses import dataclass, field

@dataclass
class Sample:
    label:int|str
    values:list[str] = field(default_factory=list)
    average:float = 0
    normalized_average:float = 0
    std:float = 0
    ab_concentration:float = 0
