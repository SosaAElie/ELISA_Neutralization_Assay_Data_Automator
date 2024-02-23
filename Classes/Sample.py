from dataclasses import dataclass, field

@dataclass
class Sample:

    label:int|str
    values:list[float] = field(default_factory=list)
    average:float = 0
    normalized_average:float = 0
    std:float = 0
    ab_concentration:float = 0
    calculated_ab:float = 0
    sample_type:str=""
    closest_conc:float|int = 0
    firefly_lum:list[float|int] = field(default_factory=list)
    renilla_lum:list[float|int] = field(default_factory=list)
    ff_r_ratio:list[float|int] = field(default_factory=list)
    
    def get_all_values(self)->list:
        '''Returns a list that contains all the property values
            formatted in a way that is expected.
        '''
        return [self.label, *self.values, f"{self.average} ({self.std})", self.calculated_ab]
    def get_neutralization_assay_values(self)->list:
        return [self.label, *self.ff_r_ratio, f"{self.average} ({self.std})"]