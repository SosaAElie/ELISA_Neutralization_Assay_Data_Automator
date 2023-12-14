from Classes.ExcelWrapper import ExcelWrapper
from Classes.Sample import Sample
from typing import Callable
import statistics
import math
import os
import matplotlib.pyplot as plt
import scipy.optimize
import numpy as np



def main(data_filepath:str, template_filepath:str, destination:str, regression_type:str = "linear", make_excel:bool = False, figure_num:int = 1)->None:
    
    '''User selects whether the samples were run in duplicates or triplicates. The average of the replicates of the samples, standards and any controls are calculated, using
        linear regression the concentration of the samples is determined from the slope of the linear regression calculated from the standards.
        Assumes the standards are always on the right hand side of the plate and the IgG isotype control is on the bottom of the standards, the rest of the wells contain samples.
        Assumes the highest concentration of the standard is 1 ug/mL and the dilution factor is 2x by default
    '''
   
    ewrapper = ExcelWrapper(data_filepath)
    regression = ""
    if regression_type == "linear":
        regression = "-Linear-"
    elif regression_type == "logarthmic":
        regression = "-Logarthimic-"
    elif regression_type == "5PL":
        regression = "-5PL-"
    
    new_dest = '/'.join([destination,data_filepath.replace(".txt", f"{regression}.xlsx").split('/')[-1]])
    
    plate = ewrapper.get_matrix(top_offset=3, left_offset=3, width=12, height=8, val_only=True)
    template = ExcelWrapper(template_filepath).get_matrix(top_offset=2, left_offset=2, width = 12, height=8, val_only=True)
    samples, standards, units = merge_plate_template(plate, template)
    
    if regression_type == "linear":
        inverse_equation,equation, r_squared = get_linear_regression_function([standard.ab_concentration for standard in standards if standard.sample_type == "standard"], [standard.average for standard in standards if standard.sample_type == "standard"])
    elif regression_type == "logarthmic":
        inverse_equation, equation, r_squared = get_logarithmic_regression_function([standard.ab_concentration for standard in standards if standard.sample_type == "standard"], [standard.average for standard in standards if standard.sample_type == "standard"])
    elif regression_type == "5PL":
        inverse_equation, equation, r_squared  = get_five_parameter_logistic_curve([standard.ab_concentration for standard in standards if standard.sample_type == "standard"], [standard.average for standard in standards if standard.sample_type == "standard"])
       
    # get_five_parameter_logistic_curve([156.25,78.13,39.06,19.53,9.7,4.8,0],[1.586033333,0.9029333333,0.5281,0.2722333333,0.1810333333,0.1235,0.08873333333])
    
    for standard in standards: 
        standard.calculated_ab = inverse_equation(standard.average)
        print(standard.calculated_ab)
    for sample in samples:
        sample.calculated_ab = inverse_equation(sample.average)
        print(sample.calculated_ab)
    
    write_to_excel(ewrapper, samples, standards, r_squared)

    if make_excel:
        ewrapper.write_excel(new_dest)
        os.system(f'start excel "{new_dest}"')
    
    regression_plot(equation,[standard for standard in standards if standard.sample_type == "standard"], samples, r_squared, units, regression_type, figure_name = new_dest.split("/")[-1])

def write_to_excel(ewrapper:ExcelWrapper, samples:list[Sample], standards:list[Sample], r_squared:float)->None: 
    '''Writes the label, values, average(std), ab_concentration stored in the Sample instance horizontally'''
    sample_headers = ["Samples"]
    standard_headers = ["Standards"]

    sample_wells = max([len(sample.values) for sample in samples])
    standard_wells = max([len(standard.values) for standard in standards])

    for num in range(1, sample_wells+1):sample_headers.append(f"Well {num}")
    for num in range(1, standard_wells+1):standard_headers.append(f"Well {num}")
    sample_headers.append("OD Average (std)")
    sample_headers.append("Calculated Ab")
    standard_headers.append("OD Average (std)")
    standard_headers.append("Calculated Ab")

    sample_data_length = len(sample_headers)
    standard_data_length = len(standard_headers)

    ewrapper.add_row(row=1, data=standard_headers, start_col="Q")
    
    for row, standard in zip(range(2, len(standards)+2), standards):
        standard_data = standard.get_all_values()

        if len(standard_data) != standard_data_length:
            while len(standard_data) != standard_data_length:
                standard_data.insert(-2, "")

        last_col = ewrapper.add_row(row=row, data=standard_data, start_col="Q")
            
    ewrapper.add_column(last_col+1, ["R-Squared", r_squared], start_row=1)

    ewrapper.add_row(row=1, data=sample_headers, start_col=last_col+3)
    for row, sample in zip(range(2, len(samples)+2),samples):
        sample_data = sample.get_all_values()
        if len(sample_data) != sample_data_length:
            while len(sample_data) != sample_data_length:
                sample_data.insert(-2, "")
        ewrapper.add_row(row=row, data=sample_data, start_col=last_col+3)
    
    return None

def get_linear_regression_function(x_values:list[float], y_values:list[float])->tuple[Callable[[float], float], Callable[[float], float], float]:
    '''Returns the inverse linear regression function, linear regression function and R-squared value that are derived from standards, 
    the inverse linear function is used to calculate the concentration of AB relative to the OD values of the standards'''
    slope, intercept = statistics.linear_regression(x_values, y_values)
    
    r_squared = statistics.correlation(x_values, y_values)**2 #The sqaure of the pearson coeffecient is the coefficient of determination
    print("The slope of the linear regression line is: ", slope, "\nThe intercept is: ", intercept, "\nThe R-squared value is: ", r_squared)
    return lambda y: (y-intercept)/slope, lambda x:slope*x+intercept, r_squared

def get_logarithmic_regression_function(x_values:list[float], y_values:list[float])->tuple[Callable[[float], float], Callable[[float], float], float]:
    '''Returns the inverse logarithmic regression function, logarithmic regression function and R-squared value that are derived from standards, 
    the inverse logarithmic function is used to calculate the concentration of AB relative to the OD values of the standards'''
  
    ln_x_values = [math.log(x) for x in x_values if x != 0]
    filtered_y_values = [y for y,x in zip(y_values, x_values) if x != 0]
    print(x_values, y_values)
    print(ln_x_values, filtered_y_values)
    slope, intercept = statistics.linear_regression(ln_x_values, filtered_y_values)
    r_squared = statistics.correlation(ln_x_values, filtered_y_values)**2
    print("The slope of the logarithmic regression line is: ", slope, "\nThe intercept is: ", intercept, "\nThe R-squared value is: ", r_squared)
    return lambda y: math.exp((y-intercept)/slope), lambda x: slope*math.log(x)+intercept, r_squared

def get_five_parameter_logistic_curve(x_values:list[float], y_values:list[float])->tuple[Callable[[float], float], Callable[[float], float]]:
    '''Returns the inverse 5 parameter logistic curve function and 5 parameter logistic curve function that are derived from standards, 
    the inverse function is used to calculate the concentration of AB relative to the OD values of the standards'''

    A = min(y_values) #The lower asymptote -> Assumes that the lowest measured y value is the lowest asymptote
    B = max(y_values) #The upper asymptote -> Assumes that the highest measured y value is the lowest asymptote
    C = max(x_values)/2 #Inflection point -> Assumes that the inflection point is the middle value of the measured concentrations
    D = (B-A)/(max(x_values)-min(x_values)) #Slope at the inflection point
    E = 1 #Asymmetry factor, assumes the sigmodial curve is symmetrical indicated by the value 1
    
    five_pl = lambda x, a,b,c,d,e: d + (a - d) / ((1 + (x / c) ** b) ** e)
    
    
    optimal_params, _ = scipy.optimize.curve_fit(f = five_pl, xdata=x_values, ydata=y_values, maxfev=10000, p0=[A,B,C,D,E])
    A,B,C,D,E = optimal_params
    return  lambda y: C * ((B - A) / (y - A))**(1/D) * math.exp(E * ((y - A)/(B - A))**(1/D)) - C, lambda x: D + (A - D) / ((1 + (x / C) ** B) ** E), 1

def determine_standards(starting_conc:str, suffix:str, dilution_factor:str, dilutions:str = "6")->tuple[list[str], list[float], str]:
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
    return (labels, concentrations, suffix)

def regression_plot(equation:Callable[[float], float], standards:list[Sample], samples:list[Sample], r_squared:float, unit:str, regression_type:str = "linear", figure_name:str = "")->None:
    '''Adds a set of data points to the matplotlib graph instance to show later'''
    
    #Create a large set of x_values between the max and the min of the standards to give the appearance of a smooth line
    filler = np.linspace(0, 5, 100)

    plt.figure(figure_name)
    plt.ylim(top = 2)
    plt.plot([standard.ab_concentration for standard in standards], [standard.average for standard in standards], "go")
    for standard in standards:plt.text(standard.ab_concentration, standard.average, standard.label)
    
    if regression_type == "linear":
        plt.plot([standard.ab_concentration for standard in standards],[equation(standard.ab_concentration) for standard in standards], label = f"R-squared: {round(r_squared, 3)}")
        plt.legend(loc = "upper center")
    elif regression_type == "logarthmic":
        plt.plot([x for x in filler if x > 0], [equation(x) for x in filler if x > 0], label = f"R-squared: {round(r_squared, 3)}")
        plt.legend(loc = "upper center")
    elif regression_type == "5PL":
        plt.plot(filler, [equation(x) for x in filler], label = "5PL")
        plt.legend(loc = "upper center")
        
    
    plt.plot([sample.calculated_ab for sample in samples], [sample.average for sample in samples], "ro")
    for sample in samples: plt.text(sample.calculated_ab, sample.average, sample.label)

    plt.title(figure_name)
    plt.xlabel(f"Ab Concentration ({unit})")
    plt.ylabel("Optical Density")
    plt.draw()
    plt.show()

def process_standards(standard_args:list[str])->tuple[list[str], list[float], str]:
    '''Takes in the args passed in by the front end and determines if they came from the
        InconsistentDilution or ConsistentDilution page and returns a tuple with the concentrations as strings
        and the concentrations as floats to be used to create instances of the Sample class
    '''
    if len(standard_args) == 2:
        values, unit = standard_args
        return [f"{value}{unit}" for value in values], [float(value) for value in values], unit
    elif len(standard_args) == 4:
        return determine_standards(*standard_args)

def merge_plate_template(plate:list[str], template:list[str])->tuple[list[Sample], list[Sample]]:
    '''Iterates through each list and creates two lists that contains only unique values from the template list, Sample and Standards.
    The lists are seperated based on the prefix given to the name of the sample/standard/control, i.e 'Unknown', 'Standards', 'Control'. '''
    STANDARD = "standard"
    CONTROL = "control"
    SAMPLE = "sample"
    
    samples:dict[str, Sample] = {}
    standards:dict[str, Sample] = {}
    units = ""
    prefixes = get_prefixes(template)
    labels = remove_prefixes(template)

    for prefix, label, od in zip(prefixes, labels, plate):
        od = float(od) #if float(od) >= 0 else 0 -> Need to ask HuiTing whether or not convert negative OD values into 0
        if prefix == STANDARD:
            conc = float(remove_unit(label))
            units = get_unit(label)
            check_and_append(standards, label, od, prefix, conc)
        elif prefix == CONTROL:
            check_and_append(standards, label, od, prefix)
        elif prefix == SAMPLE:
            check_and_append(samples, label, od, prefix)

    s = []
    s2 = []

    for sample in samples.values():
        sample.average = round(statistics.mean(sample.values), 4)
        sample.std = round(statistics.stdev(sample.values),4) if len(sample.values) > 1 else 0
        s.append(sample)

    for standard in standards.values():
        standard.average = round(statistics.mean(standard.values), 4)
        standard.std = round(statistics.stdev(standard.values),4) if len(standard.values) > 1 else 0
        s2.append(standard)

    return s, s2, units

def check_and_append(storage:dict[str, Sample], label:str, od:float, sample_type:str, conc:float = None)->None:
    if current := storage.get(label,False):
        current.values.append(od)
    else:
        current = Sample(label, ab_concentration=conc, sample_type=sample_type) if conc != None else Sample(label)
        current.values.append(od)
        storage[label] = current

def remove_prefixes(vals:list[str], sep:str = "-")->list[str]:
    '''Removes the prefix from the rest of the string using the 'seperator' as the barrier between both of them'''
    return [val.split(sep)[-1] for val in vals]

def get_prefixes(vals:list[str], seperator:str = "-")->list[str]:
    '''Returns a list of prefixes from the rest of the string using the 'seperator' as the barrier between both of them'''
    return [val.split(sep=seperator)[0].lower() for val in vals]

def remove_unit(val:str)->str:
    '''Assumes the units are 4 characters and are located at the end of the string'''
    return val[:-5]

def get_unit(val:str)->str:
    '''Assumes the units are 4 characters and are located at the end of the string'''
    return val[-5:]

def get_template(filepath:str)->list[str]:
    '''Opens the filepath passed in from the frontend for a .csv file that contains a 12 by 8, 96 well plate layout
        The layout corresponds to the layout of the data, i.e the sample label in the upper left corner matches the
        optical plate reader data in that corner as well.
    '''
    return ExcelWrapper(filepath).get_cell_matrix(top_offset=2, left_offset=2, width = 12, height=8, val_only=True)