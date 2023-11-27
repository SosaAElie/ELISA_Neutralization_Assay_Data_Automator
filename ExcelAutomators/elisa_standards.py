from Classes.ExcelWrapper import ExcelWrapper
from Classes.Sample import Sample
from typing import Callable
import statistics
import os

def main(filepath:str, destination:str, samples:list[str], \
        starting_conc:str, suffix:str, dilution_factor:str, dilutions:str = "6",\
        replicates:str = "2", neg_control:str = "IgG1, Kappa Isotype AB", blank:str = "IgG Depleted Serum")->None:
    
    '''User selects whether the samples were run in duplicates or triplicates. The average of the replicates of the samples, standards and any controls are calculated, using
        linear regression the concentration of the samples is determined from the slope of the linear regression calculated from the standards.
        Assumes the standards are always on the right hand side of the plate and the IgG isotype control is on the bottom of the standards, the rest of the wells contain samples.
        Assumes the highest concentration of the standard is 1 ug/mL and the dilution factor is 2x by default
    '''
    DUPLICATES = 2
    TRIPLICATES = 3
    
    
    ewrapper = ExcelWrapper(filepath)
    new_dest = '/'.join([destination,filepath.replace(".txt", ".xlsx").split('/')[-1]])
    
    plate = ewrapper.get_cell_matrix(top_offset=3, left_offset=3, width=12, height=8, val_only=True)
    standard_labels, standard_concentrations = determine_standards(starting_conc, suffix, dilution_factor, dilutions)
    samples:list[Sample] = [Sample(sample) for sample in samples]
    standards:list[Sample] = [Sample(label=label, ab_concentration=concetration) for label, concetration in zip(standard_labels, standard_concentrations)]
    standards.append(Sample(blank))
    standards.append(Sample(neg_control))
    replicates = int(replicates)
    
    if replicates == DUPLICATES: 
        extract_duplicates(plate, samples)
        extract_duplicates(plate, standards, starting_index=len(samples)*2)
    elif replicates == TRIPLICATES:
        extract_triplicates(plate, samples)
        extract_triplicates(plate, standards, starting_index=len(samples)*3)

    lr_equation, r_squared = linear_regression_function([standard.ab_concentration for standard in standards[:-2]], [standard.average for standard in standards[:-2]])
    
    for sample in samples:sample.ab_concentration = lr_equation(sample.average)
    for control in standards[-2:]: control.ab_concentration = lr_equation(control.average)
    
    if replicates == DUPLICATES: write_duplicates(ewrapper, samples, standards, r_squared)
    elif replicates == TRIPLICATES: write_triplicates(ewrapper, samples, standards, r_squared)
   
    ewrapper.write_excel(new_dest)
    os.system(f'start excel "{new_dest}"')

def write_duplicates(ewrapper:ExcelWrapper, samples:list[Sample], standards:list[Sample], r_squared:float)->None:
    '''Contains the logic to write the values to an excel file assuming duplicates'''
    standard_labels = ["Standards"]
    standard_well1 = ["Well 1 OD"]
    standard_well2 = ["Well 2 OD"]
    standard_od_average_std = ["OD Average (OD Std)"]
    
    control_labels = ["Controls"]
    control_well1 = ["Well 1 OD"]
    control_well2 = ["Well 2 OD"]
    control_od_average_std = ["OD Average (OD Std)"]
    control_ab_concentration = ["Calculated AB"]
    
    sample_labels = ["Samples"]
    sample_well1 = ["Well 1 OD"]
    sample_well2 = ["Well 2 OD"]
    sample_od_average_std = ["OD Average (OD Std)"]
    sample_ab_concentration = ["Calculated AB"]
    
    standard_labels.extend([standard.label for standard in standards[:-2]])
    standard_well1.extend([standard.values[0] for standard in standards[:-2]])
    standard_well2.extend([standard.values[1] for standard in standards[:-2]])
    standard_od_average_std.extend([f"{standard.average} ({standard.std})" for standard in standards[:-2]])
    
    control_labels.extend([control.label for control in standards[-2:]])
    control_well1.extend([control.values[0] for control in standards[-2:]])
    control_well2.extend([control.values[1] for control in standards[-2:]])
    control_od_average_std.extend([f"{control.average} ({control.std})" for control in standards[-2:]])
    control_ab_concentration.extend([control.ab_concentration for control in standards[-2:]])
    
    sample_labels.extend([sample.label for sample in samples])
    sample_well1.extend([sample.values[0] for sample in samples])
    sample_well2.extend([sample.values[1] for sample in samples])
    sample_od_average_std.extend([f"{sample.average} ({sample.std})" for sample in samples])
    sample_ab_concentration.extend([sample.ab_concentration for sample in samples])
    
    
    
    ewrapper.add_column("Q", standard_labels)
    ewrapper.add_column("R", standard_well1)
    ewrapper.add_column("S", standard_well2)
    ewrapper.add_column("T", standard_od_average_std)
    ewrapper.add_column("U", ["R-Squared", r_squared])
    
    ewrapper.add_column("W", control_labels)
    ewrapper.add_column("X", control_well1)
    ewrapper.add_column("Y", control_well2)
    ewrapper.add_column("Z", control_od_average_std)
    ewrapper.add_column("AA", control_ab_concentration)
    
    ewrapper.add_column("AC", sample_labels)
    ewrapper.add_column("AD", sample_well1)
    ewrapper.add_column("AE", sample_well2)
    ewrapper.add_column("AF", sample_od_average_std)
    ewrapper.add_column("AG", sample_ab_concentration)

def write_triplicates(ewrapper:ExcelWrapper, samples:list[Sample], standards:list[Sample], r_squared:float)->None:
    '''Contains the logic to write values to an excel file assuming triplicates'''
    '''Contains the logic to write the values to an excel file assuming duplicates'''
    standard_labels = ["Standards"]
    standard_well1 = ["Well 1 OD"]
    standard_well2 = ["Well 2 OD"]
    standard_well3 = ["Well 3 OD"]
    standard_od_average_std = ["OD Average (OD Std)"]
    
    control_labels = ["Controls"]
    control_well1 = ["Well 1 OD"]
    control_well2 = ["Well 2 OD"]
    control_well3 = ["Well 3 OD"]
    control_od_average_std = ["OD Average (OD Std)"]
    control_ab_concentration = ["Calculated AB"]
    
    sample_labels = ["Samples"]
    sample_well1 = ["Well 1 OD"]
    sample_well2 = ["Well 2 OD"]
    sample_well3 = ["Well 3 OD"]
    sample_od_average_std = ["OD Average (OD Std)"]
    sample_ab_concentration = ["Calculated AB"]
    
    standard_labels.extend([standard.label for standard in standards[:-2]])
    standard_well1.extend([standard.values[0] for standard in standards[:-2]])
    standard_well2.extend([standard.values[1] for standard in standards[:-2]])
    standard_well3.extend([standard.values[2] for standard in standards[:-2]])
    standard_od_average_std.extend([f"{standard.average} ({standard.std})" for standard in standards[:-2]])
    
    control_labels.extend([control.label for control in standards[-2:]])
    control_well1.extend([control.values[0] for control in standards[-2:]])
    control_well2.extend([control.values[1] for control in standards[-2:]])
    control_well3.extend([control.values[2] for control in standards[-2:]])
    control_od_average_std.extend([f"{control.average} ({control.std})" for control in standards[-2:]])
    control_ab_concentration.extend([control.ab_concentration for control in standards[-2:]])
    
    sample_labels.extend([sample.label for sample in samples])
    sample_well1.extend([sample.values[0] for sample in samples])
    sample_well2.extend([sample.values[1] for sample in samples])
    sample_well3.extend([sample.values[2] for sample in samples])
    sample_od_average_std.extend([f"{sample.average} ({sample.std})" for sample in samples])
    sample_ab_concentration.extend([sample.ab_concentration for sample in samples])
    
    
    ewrapper.add_column("Q", standard_labels)
    ewrapper.add_column("R", standard_well1)
    ewrapper.add_column("S", standard_well2)
    ewrapper.add_column("T", standard_well3)
    ewrapper.add_column("U", standard_od_average_std)
    ewrapper.add_column("V", ["R-Squared", r_squared])
    
    ewrapper.add_column("X", control_labels)
    ewrapper.add_column("Y", control_well1)
    ewrapper.add_column("Z", control_well2)
    ewrapper.add_column("AA", control_well3)
    ewrapper.add_column("AB", control_od_average_std)
    ewrapper.add_column("AC", control_ab_concentration)
    
    ewrapper.add_column("AE", sample_labels)
    ewrapper.add_column("AF", sample_well1)
    ewrapper.add_column("AG", sample_well2)
    ewrapper.add_column("AH", sample_well3)
    ewrapper.add_column("AI", sample_od_average_std)
    ewrapper.add_column("AJ", sample_ab_concentration)

def linear_regression_function(x_values:list[float], y_values:list[float])->tuple[Callable[[float], float], float]:
    '''Returns a function that is derived from the values of the standards, the function is used to calculate the concentration of AB relative to the OD values of the standards'''
    slope, intercept = statistics.linear_regression(x_values, y_values)
    r_squared = statistics.correlation(x_values, y_values)**2 #The sqaure of the pearson coeffecient is the coefficient of determination
    print("The slope of the linear regression line is: ", slope, "\nThe intercept is: ", intercept, "\nThe R-squared value is: ", r_squared)
    return lambda x:slope*x+intercept, r_squared

def determine_standards(starting_conc:str, suffix:str, dilution_factor:str, dilutions:str = "6")->tuple[list[str], list[float]]:
    '''Returns a list of strings containing the labels used for the standards based of the starting concentration and the dilution factor, assumes the starting
        concentration is diluted 6 times.
    '''
    labels = []
    concentrations = []
    prv = 0
    nxt = float(starting_conc)
    dilution_factor = float(dilution_factor)
    for _ in range(int(dilutions)):
        prv = nxt
        nxt = prv/dilution_factor
        label = f"{prv}{suffix}"
        labels.append(label)
        concentrations.append(prv)
    return (labels, concentrations)

def extract_duplicates(plate:list[float],group:list[Sample], starting_index = 0)->None:
    '''Modifies the list of Samples and appends the number of associated values, i.e assumes each sample is run in duplicates and 8 samples per column,
        The starting index refers to the point at which the values from the plate should be extracted
    '''
    ROWS_PER_COL = 8
    AMOUNT_OF_COLUMNS_TO_SKIP_OVER = 1
    count = 0
    for index in range(len(group)):
        if index%ROWS_PER_COL == 0 and index != 0: count+=1
        first = index if count < 1 else index + ROWS_PER_COL*count*AMOUNT_OF_COLUMNS_TO_SKIP_OVER
        second = first+ROWS_PER_COL
        od1 = float(plate[first+starting_index])
        od2 = float(plate[second+starting_index])
        group[index].values.append(od1)
        group[index].values.append(od2)
        group[index].average = round(statistics.mean(group[index].values), 4) 
        group[index].std = round(statistics.stdev(group[index].values), 4)
        
def extract_triplicates(plate:list[float],group:list[Sample], starting_index = 0)->None:
    '''Modifies the list of Samples and appends the number of associated values, i.e assumes each sample is run in duplicates and 8 samples per column,
        The starting index refers to the point at which the values from the plate should be extracted
    '''
    ROWS_PER_COL = 8
    AMOUNT_OF_COLUMNS_TO_SKIP_OVER = 2
    count = 0
    for index in range(len(group)):
        if index%ROWS_PER_COL == 0 and index != 0: count+=1
        first = index if count < 1 else index + ROWS_PER_COL*count*AMOUNT_OF_COLUMNS_TO_SKIP_OVER
        second = first+ROWS_PER_COL
        third = second+ROWS_PER_COL
        od1 = float(plate[first+starting_index])
        od2 = float(plate[second+starting_index])
        od3 = float(plate[third+starting_index])
        group[index].values.append(od1)
        group[index].values.append(od2)
        group[index].values.append(od3)
        group[index].average = round(statistics.mean(group[index].values), 4)
        group[index].std = round(statistics.stdev(group[index].values, xbar=1),4)
