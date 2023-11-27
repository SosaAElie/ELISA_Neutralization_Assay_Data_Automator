from pandas.io.formats import excel
import PrismAutomators.elisa_prism_automator as epa
from Classes.Sample import Sample
from settings import *
import pandas as pd
import numpy as np
import os

        
def analyze_data(filepath:str, destination:str, samples:list[Sample], samp_loc:list[tuple], controls:list[Sample], cont_loc:list[tuple]) -> tuple[str,dict]:
    '''Creates a Pandas Dataframe out of the filepath passed in and returns the relative file path and a Dataframe that contains the normalized OD values of the samples and controls and the cutoff OD value'''

    df = pd.read_csv(filepath, encoding=FILE_ENCODING, delimiter=FILE_DELIMITER, skiprows=ROWS_SKIPPED)
    
    sample_data = sample_averages(samples, df, samp_loc)
    ctrl_data = control_averages(controls, df, cont_loc)
    
    ctrl_ave = {'Ctrl Avg':[np.mean([control.average for control in controls])]}
    ctrl_median = {'Ctrl Median':[np.median([control.average for control in controls])]}
    ctrl_sd = {'Ctrl SD':[np.std([control.average for control in controls], ddof=1)]}
    cutoff_val = ((ctrl_sd['Ctrl SD'][0])*3)+ctrl_median['Ctrl Median'][0]
    cutoff_dict = {'Cutoff':[cutoff_val]}
    norm_ave = {
        'Sample Numbers': sample_data['Samp Numbers'],
        'Normalized Sample OD':[sample.average/ctrl_ave['Ctrl Avg'][0] for sample in samples]
        }
    norm_ctrl = {
        'Control Numbers': ctrl_data['Ctrl Numbers'],
        'Normalized Ctrl OD':[control.average/ctrl_ave['Ctrl Avg'][0] for control in controls]
        }
    norm_sd = {'Normalized SD':[np.std(norm_ctrl['Normalized Ctrl OD'], ddof=1)]}
    norm_ctrl_median = np.median(norm_ctrl['Normalized Ctrl OD'])
    norm_cutoff_val = ((norm_sd['Normalized SD'][0])*3)+norm_ctrl_median
    norm_cutoff = {'Normalized Cutoff':[norm_cutoff_val]}


    all_data_sets = [df, sample_data, ctrl_data, ctrl_ave, ctrl_sd, cutoff_dict, norm_ave, norm_ctrl, norm_sd,norm_cutoff]
    normalized_data_sets = [sample_data, ctrl_data, cutoff_dict, norm_ctrl, norm_ave, norm_cutoff]
    
    
    combined_df = pd.concat([pd.DataFrame.from_dict(data) for data in all_data_sets], axis=1)
    norm_dict = pd.concat([pd.DataFrame.from_dict(n_data) for n_data in normalized_data_sets], axis=1).to_dict()  

    new_dest = '/'.join([destination,filepath.replace(TEXT_EXT, EXCEL_EXT).split('/')[-1]])

    combined_df.to_excel(new_dest, index=False)
    return new_dest, norm_dict

def sample_averages(samples:list[Sample], df:pd.DataFrame, locations: list[tuple])->dict[str,list]:
    '''Modifies the dataframe and the Sample objects in the samples list'''
    for sample, location in zip(samples, locations):
        od_value1 = df.at[location[0], location[1]]
        od_value2 = df.at[location[0], location[2]]
        average = np.mean([np.float32(od_value1), np.float32(od_value2)])
        sample.values.append(od_value1)
        sample.values.append(od_value2)
        sample.average = average
        df.at[location[0], location[1]] = f'{sample.label} - {od_value1}'
        df.at[location[0], location[2]] = f'{sample.label} - {od_value2}'

    data = {
        'Samp Numbers' :[sample.label for sample in samples],
        'Samp OD Averages':[sample.average for sample in samples],
    }
    
    return data

def control_averages(controls:list[Sample], df:pd.DataFrame, locations: list[tuple])->dict[str,list]:
    
    for control, location in zip(controls, locations):
        od_value1 = df.at[location[0], location[1]]
        od_value2 = df.at[location[0], location[2]]
        average = np.mean([np.float32(od_value1), np.float32(od_value2)])
        control.values.append(od_value1)
        control.values.append(od_value2)
        control.average = average
        df.at[location[0], location[1]] = f'{control.label} - {od_value1}'
        df.at[location[0], location[2]] = f'{control.label} - {od_value2}'

    data = {
        'Ctrl Numbers' :[control.label for control in controls],
        'Ctrl OD Averages':[control.average for control in controls],
    }
    
    return data
         
def check_samples(samples:list[Sample], locations:list[tuple[int,int,int]])->str:
    '''Checks the size of the sample cohort and the locations for them'''
    LOC = len(locations)
    AMT = len(samples)
    
    if AMT != LOC:
        message = f'ERROR! More samples than locations: {AMT} samples and {LOC} locations.' if AMT > LOC else f'WARNING! Less samples than locations: {AMT} samples and {LOC} locations.'
    else:
        message = f'Success! {AMT} samples and {LOC} locations.' 
        
    return message 
        
def check_controls(controls:list[Sample], locations:list[tuple[int,int,int]])->str:
    '''Checks size of the control cohort and the locations for them'''
    LOC = len(locations)
    AMT = len(controls)
    
    if AMT != LOC:
        message = f'ERROR! More controls than locations: {AMT} controls and {LOC} locations.' if AMT > LOC else f'WARNING! Less controls than locations: {AMT} controls and {LOC} locations.'
    else:
        message = f'Success! {AMT} controls and {LOC} locations.' 
        
    return message 

def locations(start:int, end:int)->list[tuple[int,int,int]]:
    '''Creates a list of tuples with each tuple being the location for each sample, i.e the first tuple has both locations for the first sample'''
    STEP = 2
    ROWS = 8
    loca = []
    for column in range(start, end, STEP):
        for row in range(ROWS):
            first = str(column)
            second = str(column+1)
            loca.append((row, first, second))
    
    return loca

def check_columns(col1, col2):
    if col1 and col2:
        return int(col1), int(col2)
    if col1 and not col2:
        return int(col1), DEFAULT_CONTROL_COLUMN
    if not col1 and col2:
        return DEFAULT_SAMPLE_COLUMN, int(col2)
    if not col1 and not col2:
        return DEFAULT_SAMPLE_COLUMN,DEFAULT_CONTROL_COLUMN
  
def main(filepath:str, destination:str, samples:list[int], controls:list[int], sample_col:str, control_col:str):
    '''Analyzes raw data from optical density machine'''
    excel.ExcelFormatter.header_style = None
    samples  = [Sample(sample) for sample in samples]
    controls = [Sample(control) for control in controls]
    sample_locations = locations(sample_col, control_col)
    control_locations = locations(control_col, DEFAULT_LAST_COLUMN)
    print(check_samples(samples, sample_locations), check_controls(controls, control_locations), sep='\n')
    new_file, data_df = analyze_data(filepath, destination, samples, sample_locations, controls, control_locations)
    epa.main(data_df, new_file)
    os.system(f'start excel "{new_file}"')