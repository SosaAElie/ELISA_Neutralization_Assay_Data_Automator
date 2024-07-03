import PrismAutomators.elisa_prism_automator as epa
from Classes.ExcelWrapper import ExcelWrapper
from Classes.Sample import Sample
from settings import *
import os
import statistics


        
def analyze_data(filepath:str, destination:str, samples:list[Sample],controls:list[Sample], replicates:int = 2) -> tuple[str,dict]:
    '''Creates Excel file out of text file and returns the new filepath and a dictionary to be passed into the prism automator'''

    ewrapper = ExcelWrapper(filepath)
    plate = ewrapper.get_cell_matrix(top_offset=3, left_offset=3, width=12, height=8, val_only=True)
    controls.append(Sample("PosControl"))
    controls.append(Sample("NegControl"))
    controls.append(Sample("Blank"))
    extract_values(plate, samples)
    extract_values(plate, controls, start=len(samples)*2)
    control_ave = group_mean(controls[:-3])
    
    sample_labels = ["Sample Number"]
    sample_od1 = ["Sample Well 1 OD"]
    sample_od2 = ["Sample Well 2 OD"]
    sample_averages = ["Sample Raw OD Averages"]
    control_labels = ["Control Number"]
    control_od1 = ["Control Well 1 OD"]
    control_od2 = ["Control Well 2 OD"]
    control_averages = ["Control Raw OD Averages"]
    sample_normalized_ave = ["Normalized Sample OD Averages"]
    control_normalized_ave = ["Normalized Control OD Averages"]
    
    normalize_values(samples, control_ave)
    normalize_values(controls, control_ave)
    
    raw_cutoff = calculate_cutoff([control.average for control in controls[:-3]])
    normalized_cutoff = calculate_cutoff([control.normalized_average for control in controls[:-3]])
    
    sample_labels.extend([sample.label for sample in samples])
    sample_od1.extend([sample.values[0] for sample in samples])
    sample_od2.extend([sample.values[1] for sample in samples])
    sample_averages.extend([sample.average for sample in samples])
    control_labels.extend([control.label for control in controls])
    control_od1.extend([control.values[0] for control in controls])
    control_od2.extend([control.values[1] for control in controls])
    control_averages.extend([control.average for control in controls])
    sample_normalized_ave.extend([sample.normalized_average for sample in samples])
    control_normalized_ave.extend([control.normalized_average for control in controls])

    ewrapper.add_column("P",sample_labels)
    ewrapper.add_column("Q",sample_od1)
    ewrapper.add_column("R",sample_od2)
    ewrapper.add_column("S", sample_averages)
    ewrapper.add_column("U", control_labels)
    ewrapper.add_column("V", control_od1)
    ewrapper.add_column("W", control_od2)
    ewrapper.add_column("X", control_averages)
    ewrapper.add_column("Y", ["Control Average", control_ave])
    ewrapper.add_column("Z", ["Raw Cutoff", raw_cutoff])
    ewrapper.add_column("AA", sample_labels)
    ewrapper.add_column("AB", sample_normalized_ave)
    ewrapper.add_column("AC", control_labels)
    ewrapper.add_column("AD", control_normalized_ave)
    ewrapper.add_column("AE", ["Normalized Cutoff", normalized_cutoff])

    new_dest = '/'.join([destination,filepath.replace(".txt", ".xlsx").split('/')[-1]])
    ewrapper.write_excel(new_dest)
    
    sample_labels.extend([control.label for control in controls])
    
    return destination, {
        "sample_labels":sample_labels[1:],
        "sample_averages":sample_averages[1:],
        "control_averages":control_averages[1:-3],
        "control_normalized":control_normalized_ave[1:-3],
        "sample_normalized":sample_normalized_ave[1:],
    }
    
def calculate_cutoff(values:list[float|int])->int|float:
    '''Takes in a list if values and returns the cutoff according to the 2021 Bastard paper
        cutoff = 3*stdev(values)+mean(values)
    '''

    return statistics.median(values) + (3*statistics.stdev(values))

def extract_values(plate:list[float],group:list[Sample], start = 0)->None:
    '''Modifies the list of Samples and appends the number of associated values, i.e assumes each sample is run in duplicates and 8 samples per column'''
    ROWS_PER_COL = 8
    count = 0
    for index in range(len(group)):
        if index%ROWS_PER_COL == 0 and index != 0: count+=1
        first = index if count < 1 else index + ROWS_PER_COL*count
        second = first+ROWS_PER_COL
        od1 = float(plate[first+start])
        od2 = float(plate[second+start])
        group[index].values.append(od1)
        group[index].values.append(od2)
        group[index].average = statistics.mean(group[index].values)

def normalize_values(group:list[Sample], normalizer:float|int)->None:
    '''Normalizes a list of Samples by dividing each Sample.average by the normalizer'''
    if normalizer == 0: 
        print("Error normalizer cannot be 0")
        return
    
    for sample in group:sample.normalized_average = sample.average/normalizer

    return

def group_mean(group:list[Sample])->float|int:
    '''Returns the mean of the Sample.average of a list of Samples'''
    return statistics.mean([sample.average for sample in group])
         
def old_main(filepath:str, destination:str, samples:list[int], controls:list[int], sample_col:int = 1, control_col:int = 8):
    '''Analyzes ELISA text file data from optical density machine, assumes the samples always start at column 1 and the controls always start at column 8'''
    print(samples, controls)
    samples  = [Sample(sample) for sample in samples]
    controls = [Sample(control) for control in controls]
    new_file, data = analyze_data(filepath, destination, samples,controls)
    epa.main(data, new_file)
    os.system(f'start excel "{new_file}"')

def main(data_filepath:str, template_filepath:str, destination_filepath:str)->None:
    '''Takes in the template and the raw txt exported by the SoftMax Pro software and determines positivity as the average OD
        of the controls + 3 stdev of the OD of the controls
    '''
    
