import PIL.Image as Image
from pathlib import Path
from Classes.ExcelWrapper import ExcelWrapper
from Classes.Sample import Sample
import matplotlib.pyplot as plt
from random import randint
import statistics
import io
import os

AVE3XSTDEV = "-Ave+3xStdev-"

async def main(data_filepath:Path, template_filepath:Path, make_excel:bool, graph_title:str, xlsx_filename:str, destination_dir:Path)->None:
    '''Takes in the template and the raw txt exported by the SoftMax Pro software and determines positivity as the average OD
        of the controls + 3 stdev of the OD of the controls
    '''
    
    ewrapper = ExcelWrapper(data_filepath)
    xlsx_filename = parse_filename(xlsx_filename)
    if xlsx_filename != data_filepath.stem:
        new_dest = destination_dir/f"{xlsx_filename}{AVE3XSTDEV}.xlsx"
    else:
        new_dest = destination_dir/data_filepath.name.replace(".txt", f"{AVE3XSTDEV}.xlsx")

    plate = ewrapper.get_matrix(top_offset=3, left_offset=3, width=12, height=8, val_only=True)
    template = ExcelWrapper(template_filepath).get_matrix(top_offset=2, left_offset=2, width = 12, height=8, val_only=True)
    samples, controls = merge(plate, template)
    if len(controls) < 1: return None
    cutoff = round(calculate_cutoff(controls),3)
    add_to_excel(controls, samples, cutoff, ewrapper)
    graph_image = scatter_graph(controls, samples, cutoff, new_dest.stem if graph_title == "" else graph_title)
    ewrapper.save_image(graph_image, f"A{ewrapper.get_last_row()}")
    
    if make_excel: 
        ewrapper.save_as_excel(new_dest)    
        if os.name == "nt":
            os.system(f'start excel "{new_dest}"')
        else:
            os.system(f'open "{new_dest}"')

def add_to_excel(controls:list[Sample], samples:list[Sample], cutoff:float, ewrapper:ExcelWrapper)->None:
    '''Adds the data to the ewrapper instance'''
    control_labels = ["Control"]
    control_labels.extend([control.label for control in controls])
    ewrapper.add_column(ewrapper.get_last_col()+1, control_labels)

    control_ods = ["Average (stdev)"]
    control_ods.extend([f"{control.average} ({control.std})" for control in controls])
    ewrapper.add_column(ewrapper.get_last_col()+1, control_ods)

    sample_labels = ["Samples"]
    sample_labels.extend([sample.label for sample in samples])
    ewrapper.add_column(ewrapper.get_last_col()+1, sample_labels)

    sample_ods = ["Average (stdev)"]
    sample_ods.extend([f"{sample.average} ({sample.std})" for sample in samples])
    ewrapper.add_column(ewrapper.get_last_col()+1, sample_ods)

    ewrapper.add_column(ewrapper.get_last_col()+1, ["Cutoff", cutoff])

    postives = ["Above Cutoff"]
    postives.extend([sample.label for sample in samples if sample.average >= cutoff])
    ewrapper.add_column(ewrapper.get_last_col()+1, postives)
    

    postive_ods = ["Average (stdev)"]
    postive_ods.extend([f"{sample.average} ({sample.std})" for sample in samples if sample.average >= cutoff])
    ewrapper.add_column(ewrapper.get_last_col()+1, postive_ods)

def calculate_cutoff(controls:list[Sample])->float:
    '''Returns the cutoff value according to the equation: average(controls) + 3*stdev(controls)'''
    vals = [control.average for control in controls]
    return statistics.mean(vals) + (3*statistics.stdev(vals))
    
def merge(plate:list[str], template:list[str])->tuple[list[Sample], list[Sample]]:
    '''Iterates through each list and creates two lists that contains only unique values from the template list, Sample and Standards.
    The lists are seperated based on the prefix given to the name of the sample/standard/control, i.e 'Unknown', 'Standards', 'Control'. '''    
    CONTROL = "control"
    SAMPLE = "sample"
    
    samples:dict[str, Sample] = {}
    controls:dict[str, Sample] = {}    
    prefixes = get_prefixes(template)
    labels = remove_prefixes(template)

    for prefix, label, od in zip(prefixes, labels, plate):
        od = float(od)
        if prefix == CONTROL:            
            check_and_append(controls, label, od, prefix)        
        elif prefix == SAMPLE:
            check_and_append(samples, label, od, prefix)

    s = []
    s2 = []

    for sample in samples.values():
        sample.average = round(statistics.mean(sample.values), 4)
        sample.std = round(statistics.stdev(sample.values),4) if len(sample.values) > 1 else 0
        s.append(sample)

    for standard in controls.values():
        standard.average = round(statistics.mean(standard.values), 4)
        standard.std = round(statistics.stdev(standard.values),4) if len(standard.values) > 1 else 0
        s2.append(standard)

    return s, s2

def check_and_append(storage:dict[str, Sample], label:str, od:float, sample_type:str, conc:float = None)->None:
    if current := storage.get(label,False):
        current.values.append(od)
    else:
        current = Sample(label, ab_concentration=conc, sample_type=sample_type) if conc != None else Sample(label, sample_type=sample_type)
        current.values.append(od)
        storage[label] = current
    return None

def remove_prefixes(vals:list[str], sep:str = "-")->list[str]:
    '''Removes the prefix from the rest of the string using the 'seperator' as the barrier between both of them'''
    return [val.split(sep)[-1] for val in vals]

def get_prefixes(vals:list[str], seperator:str = "-")->list[str]:
    '''Returns a list of prefixes from the rest of the string using the 'seperator' as the barrier between both of them'''
    return [val.split(sep=seperator)[0].lower() for val in vals]

def scatter_graph(controls:list[Sample], samples:list[Sample], cutoff:float, title:str)->Image.Image:
    '''Creates a graph where each sample and control have the same x value with the y value being the OD average so that they all appear on the same column'''
    plt.figure(title)
    plt.title(title)
    plt.xlabel(f"Samples")
    plt.ylabel("Optical Density")
    
    control_x_postions = [(randint(1,9)/10) for _ in range(len(controls))]    
    sample_x_positions = [(randint(1,9)/10) for _ in range(len(samples))]
    
    plt.plot(control_x_postions, [control.average for control in controls], "bo", label = "Controls")
    plt.plot(sample_x_positions, [sample.average for sample in samples], "ro", label = "Unknowns")
    plt.axhline(cutoff, color = "k", linestyle = "dashed", label = f"Cutoff Average(controls) + 3*Stdev(controls): {cutoff}")
    
    for x, control in zip(control_x_postions, controls):
        plt.annotate(control.label, (x, control.average))
    
    for x, sample in zip(sample_x_positions, samples):
        plt.annotate(sample.label, (x, sample.average))
    
    plt.legend()
    plt.xticks([])
    plt.xlim(0,1)
    plt.ylim(bottom = 0)
    
    plt.show()
    figure_bytes = io.BytesIO()
    plt.savefig(figure_bytes,format = "jpeg")
    return Image.open(figure_bytes)

def parse_filename(filename:str)->str:
    '''Parses the filename passed in by the user to see if there was any extension added to it such as, .xlsx, .txt, .csv, etc
        Returns the filename without the extension
    '''
    if filename.find(".") > -1:
        stem = filename.split(".")[-1]
        return stem
    return filename