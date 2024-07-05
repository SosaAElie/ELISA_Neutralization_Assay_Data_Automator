from Classes.ExcelWrapper import ExcelWrapper
from xml.dom import minidom
from typing import Any
import sqlite3

cur = sqlite3.connect("Databases/NeutralizationAssayDB.sqlite").cursor()

def main(file:str, dest:str, cohort:str|None, first_half:dict, second_half:dict)->None:
    pzfx_dom = minidom.parse("Templates/neutralization_assay_singlets_template.pzfx")
    new_dest = '/'.join([dest,file.replace(".txt", ".pzfx").split('/')[-1]])
    lower_conc, higher_conc, lower_conc_elisa, higher_conc_elisa = pzfx_dom.getElementsByTagName("Table")
    update_tables_without_elisa(lower_conc, first_half)
    update_tables_without_elisa(higher_conc, second_half)
    elisa = find_related_elisa(cohort, first_half)
    update_tables_with_elisa(lower_conc_elisa, first_half, elisa)
    update_tables_with_elisa(higher_conc_elisa, second_half, elisa)
    create_prism_file(new_dest,pzfx_dom)

def update_tables_without_elisa(table:minidom.Element, half:dict)->None:
    sample_numbers, control_flus_rlus, patient_flus_rlus, pos, neg, ns = table.getElementsByTagName("Subcolumn")
    update_values(sample_numbers, half["sample_numbers"])
    update_values(control_flus_rlus, half["mirs_flus_rlus"])
    update_values(patient_flus_rlus, half["sample_flus_rlus"])
    update_values(pos, half["pos"])
    update_values(neg, half["neg"])
    update_values(ns, half["ns"])

def update_tables_with_elisa(table:minidom.Element, half:dict, elisa:dict)->None:
    cohort_nums, cohort_ods, cohorts_ods_again, sample_flus_rlus, mir_flus_rlus = table.getElementsByTagName("Subcolumn")
    new_cohort_nums = half["sample_numbers"].copy()
    new_cohort_nums.extend(half["mir_numbers"])
    ods = elisa["sample_ods"].copy()
    ods.extend(elisa["mir_ods"])
    update_values(cohort_nums, new_cohort_nums)
    update_values(cohort_ods, ods)
    update_values(cohorts_ods_again, ods)
    update_values(sample_flus_rlus, half["sample_flus_rlus"])
    update_values(mir_flus_rlus, half["mirs_flus_rlus"])

def update_values(subcolumn:minidom.Element, new_values:list)->None:
    '''Iterates throught the subcolumn element, assumes that there are "d" child elements and replaces the node value of
     those elements with the new values in the list. Both the list and the number of "d" child elements should be the same.'''
    d_elements = subcolumn.getElementsByTagName('d')
    print(len(d_elements), len(new_values))
    filtered = []
    if len(d_elements) != len(new_values):
        print("The number of values is not the same in the subcolumn and in the new values list creating a filtered list to use instead")
        for child in d_elements:
            found_text_node = False
            base_node = child
            current_node = child  
            while not found_text_node:
                try:
                    if current_node.nodeType == current_node.TEXT_NODE:
                        filtered.append(base_node)
                        found_text_node = True
                    else:
                        current_node = current_node.firstChild
                except AttributeError:
                    break

    for child, val in zip(filtered if len(filtered) != 0 else d_elements, new_values):
        found_text_node = False
        current_node = child  
        while not found_text_node:
            try:
                if current_node.nodeType == current_node.TEXT_NODE:
                    current_node.nodeValue = val
                    found_text_node = True
                else:
                    current_node = current_node.firstChild
            except AttributeError:
                break

def create_prism_file(filename:str, dom:minidom.Document)->None:
    with open(filename, 'w') as prism: dom.writexml(prism)
    return None

def remove_prefix(mir:str|None)->int|None:
    return int(mir.lstrip("MIR")) if mir is not None else mir

def is_present(values:list, target:Any)->bool:
    '''Return True if the value is present in the list else returns False by handling a ValueError'''
    try:
        values.index(target)
        return True
    except ValueError:
        return False

def find_related_elisa(cohort:str|None, half:dict)->dict[str, float]:
    '''Finds the related normalized ELISA OD values based off the first sample number and the last sample number that was tested in the neutralization assay
        Uses the sheet named Compiled Normalized ELISA OD (patients).xlsx to find the ELISA OD values
    '''
    
    if cohort:
        sample_ods = [[sample][0][0] for sample in cur.execute(f"SELECT normalizedod FROM {cohort} WHERE label NOT LIKE 'MIR%' AND NOT excluded ORDER BY rowid").fetchall()]
        cohort_mir_ods = [[mir][0][0] for mir in cur.execute(f"SELECT normalizedod FROM {cohort} WHERE label LIKE 'MIR%' AND NOT excluded ORDER BY rowid").fetchall()]
        print(len(sample_ods), len(cohort_mir_ods))
    # cohort_sample_nums = [int(num) for num in half["sample_numbers"]]
    # cohort_mir_nums = [remove_prefix(mir) for mir in half["mir_numbers"]]
    
    # first = cohort_sample_nums[0]
    # last = cohort_sample_nums[-1]

    # ewrapper = ExcelWrapper("Databases/Compiled Normalized ELISA OD (patients).xlsx")
    # sample_numbers = ewrapper.get_column('A', values_only = True)
    
    # first_index = sample_numbers.index(first)
    # last_index = sample_numbers.index(last)

    # sample_ods = ewrapper.get_column('B', values_only=True)[first_index:last_index+1]
    # mir_numbers =[remove_prefix(mir) for mir in ewrapper.get_column('C', values_only=True)[first_index:last_index+1]]
    # mir_ods = ewrapper.get_column('D', values_only=True)[first_index:last_index+1]
    
    # cohort_mir_ods = [od for mir, od in zip(mir_numbers, mir_ods) if is_present(cohort_mir_nums, mir)]

    return {
        "sample_ods":sample_ods,
        "mir_ods":cohort_mir_ods
    }
    
def find_cohort(first_sample:str):
    '''Finds the related cohort in the sqlite3 database using the first sample number tested'''
    pass
