from Classes.ExcelWrapper import ExcelWrapper
import PrismAutomators.neutralization_assay_prism_automator as npa
import statistics
import sqlite3
import os

cur = sqlite3.connect("Databases/NeutralizationAssayDB.sqlite").cursor()

def flatten_list(lists:list)->list:
    '''flattens inner lists into 1 list, goes 1 level deep only'''
    flattened = []
    for item in lists:
        if type(item) == list:
            for inner_item in item: flattened.append(inner_item)
        else:
            flattened.append(item)
        
    return flattened

def calculate_cutoff(values:list[int|float])->int|float:
    '''Calculates the cutoff according to the Bastard et al 2021 paper, 0.15(median(controls))'''
    return statistics.median(values)*0.15

def calculate_averages(*values:list[int|float])->list[int|float]:
    '''Averages the values between the lists passed within the same index, 
    i.e the average of list_one[i] and list_two[i]'''

    rows = len(values)
    cols = len(values[0])
    averages = []
    for col in range(cols):
        current_index = []
        for row in range(rows):
            current_index.append(float(values[row][col]))
        averages.append(statistics.mean(current_index))
        current_index.clear()
    return averages

def get_patient_serum(half:dict[str, list])->list:
    '''Returns the first 4 columns from a plate half as a list'''
    return flatten_list([half[key] for index, key in enumerate(half.keys()) if index < 4])

def get_mir_serum(half:dict[str, list])->list:
    return flatten_list([half[key] for index, key in enumerate(half.keys()) if index >= 4 and index < 6])

def get_controls(half:dict[str, list])->list:
    return flatten_list([half[key] for index, key in enumerate(half.keys()) if index >= 6])


def neutralization_assay_singlets(file:str, destination:str, cohort:str=None, sample_numbers:list[str]= None, mir_controls:list[str]=None)->None:
    '''Analyzes the text file produced from the Optical Plate reader assumptions:
        - Half the 96 well plate is used for 0.1ng/mL, other half for 10ng/mL protein stimulation
        - Same cohort is tested on both halves of the 96 well plate
        - Only 13 MIR Controls are used
        - 1 Pos Control (1ug/mL of human Anti-IFNa2)
        - 1 Neg Control (1ug/mL of non-specific IgG)
        - Last well in both halves has no stimulation(No recombinant protein added)
        See layout here: "Neutralization_Assay_Procedure_for_IFNa2_and_IFNw Singlets.docx"
    '''

    ewrapper = ExcelWrapper(file)
    
    if cohort:
        sample_numbers = [[sample][0][0] for sample in cur.execute(f"SELECT label FROM {cohort} WHERE label NOT LIKE 'MIR%' AND NOT excluded ORDER BY rowid").fetchall()]
        mir_controls = [[control][0][0] for control in cur.execute(f"SELECT label FROM {cohort} WHERE label LIKE 'MIR%' AND NOT excluded ORDER BY rowid").fetchall()]
    
   
    first_half = {
        "first_col": ewrapper.get_column("C", 14, 22, True),
        "second_col":ewrapper.get_column("D", 14, 22, True),
        "third_col":ewrapper.get_column("E", 14, 22, True),
        "fourth_col":ewrapper.get_column("F", 14, 22, True),
        "fifth_col":ewrapper.get_column("G", 14, 22, True),
        "sixth_col":ewrapper.get_column("H", 14, 19, True),
        "pos_control":ewrapper.get_column("H", 19, 20, True),
        "neg_control":ewrapper.get_column("H", 20, 21, True),
        "no_stimulation":ewrapper.get_column("H", 21, 22, True),
    }
    
    second_half = {
        "first_col": ewrapper.get_column("I", 14, 22, True),
        "second_col":ewrapper.get_column("J", 14, 22, True),
        "third_col":ewrapper.get_column("K", 14, 22, True),
        "fourth_col":ewrapper.get_column("L", 14, 22, True),
        "fifth_col":ewrapper.get_column("M", 14, 22, True),
        "sixth_col":ewrapper.get_column("N", 14, 19, True),
        "pos_control":ewrapper.get_column("N", 19, 20, True),
        "neg_control":ewrapper.get_column("N", 20, 21, True),
        "no_stimulation":ewrapper.get_column("N", 21, 22, True),
    }
    
    first_half_mirs_flus_rlus = get_mir_serum(first_half)
    second_half_mirs_flus_rlus = get_mir_serum(second_half)
    first_half_patient_flus_rlus = get_patient_serum(first_half)
    second_half_patient_flus_rlus = get_patient_serum(second_half)
    
    ewrapper.add_column("Q", ["Patient Sample Number"])
    ewrapper.add_column("Q", sample_numbers, 2)
    ewrapper.add_column("R", ["0.1ng/mL Patient FLU/RLU"])
    ewrapper.add_column("R", first_half_patient_flus_rlus, 2)
    ewrapper.add_column("S", ["MIR Control Number"])
    ewrapper.add_column("S", mir_controls, 2)
    ewrapper.add_column("S", ["hAnti-IFNa"],len(mir_controls)+2)
    ewrapper.add_column("S", ["hIgG"],len(mir_controls)+3)
    ewrapper.add_column("S", ["Not Stimulated"],len(mir_controls)+4)
    ewrapper.add_column("T", ["0.1ng/mL Control FLU/RLU"])
    ewrapper.add_column("T", first_half_mirs_flus_rlus, 2)
    ewrapper.add_column("T", get_controls(first_half),len(first_half_mirs_flus_rlus)+2) # + length of the mirs list 
    ewrapper.add_column("U", ["Cutoff", calculate_cutoff([float(mir) for mir in first_half_mirs_flus_rlus])]) #need to convert 'str' in mirs list to 'float'
    
    ewrapper.add_column("W", ["Patient Sample Number"])
    ewrapper.add_column("W", sample_numbers, 2)
    ewrapper.add_column("X", ["10ng/mL Patient FLU/RLU"])
    ewrapper.add_column("X", second_half_patient_flus_rlus, 2)
    ewrapper.add_column("Y", ["MIR Control Number"])
    ewrapper.add_column("Y", mir_controls, 2)
    ewrapper.add_column("Y", ["hAnti-IFNa"],len(mir_controls)+2)
    ewrapper.add_column("Y", ["hIgG1, kappa"],len(mir_controls)+3)
    ewrapper.add_column("Y", ["Not Stimulated"],len(mir_controls)+4)
    ewrapper.add_column("Z", ["10ng/mL Control FLU/RLU"])
    ewrapper.add_column("Z", second_half_mirs_flus_rlus, 2)
    ewrapper.add_column("Z", get_controls(second_half),len(second_half_mirs_flus_rlus)+2) # +2 is used since the column and the mir serum takes up more rows that just the length of the mirs list 
    ewrapper.add_column("AA", ["Cutoff", calculate_cutoff([float(mir) for mir in second_half_mirs_flus_rlus])]) #need to convert 'str' in mirs list to 'float'
    
    new_dest = '/'.join([destination,file.replace(".txt", ".xlsx").split('/')[-1]])
    ewrapper.write_excel(new_dest)
    os.system(f'start excel "{new_dest}"')
    npa.main(file, destination,cohort,{
        "sample_numbers":sample_numbers,
        "mir_numbers":mir_controls,
        "sample_flus_rlus":first_half_patient_flus_rlus,
        "mirs_flus_rlus":first_half_mirs_flus_rlus,
        "pos":first_half["pos_control"],
        "neg":first_half["neg_control"],
        "ns":first_half["no_stimulation"],
    }, {
        "sample_numbers":sample_numbers,
        "mir_numbers":mir_controls,
        "sample_flus_rlus":second_half_patient_flus_rlus,
        "mirs_flus_rlus":second_half_mirs_flus_rlus,
        "pos":second_half["pos_control"],
        "neg":second_half["neg_control"],
        "ns":second_half["no_stimulation"],
    })
    
    
#The code below is a "unit test" to verify that the script works, need to create mure unit tests in the future
# neutralization_assay_singlets("test.txt", ['74','75','76','77','78','79',
#                                            '80','81','82','83','84','85', '86','87','88',
#                                            '89', '90', '91','92','93','94', '95','96',
#                                            '97','98', '99','100', '102', '103', '104', '105',
#                                            '106'
#                                            ], ["MIR001", "MIR002", "MIR003", "MIR004", "MIR005",
#                                                "MIR010", "MIR012", "MIR013", "MIR023", 
#                                                 "MIR024", "MIR025", "MIR026", "MIR028" ])