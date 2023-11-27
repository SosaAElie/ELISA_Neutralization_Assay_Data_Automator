from xml.dom import minidom
from settings import *

def set_sample_numbers(*elements:minidom.Element, data:dict[str, list[str|int]])->None:
    elements1 = elements[0].getElementsByTagName('d')
    elements2 = elements[1].getElementsByTagName('d')
    data_values = data
    data_len = len(data_values)
    elements_len = elements1.length
    
    for ele1, ele2, val in zip(elements1, elements2, data_values):
        ele1.firstChild.nodeValue = val
        ele2.firstChild.nodeValue = val
        
    if elements_len != data_len:
        for index in range(data_len, elements_len):
            child1 = elements1[index].firstChild
            child2 = elements2[index].firstChild
            elements1[index].removeChild(child1)
            elements2[index].removeChild(child2)
    
    return None

def set_ctrl_ods(element:minidom.Element, data:dict[str, list[str|int]])->None:
    elements = element.getElementsByTagName('d')
    data_values = data
    data_len = len(data_values)
    elements_len = elements.length
    
    for ele, val in zip(elements, data_values):
        ele.firstChild.nodeValue = val
        
    if elements_len != data_len:
        for index in range(data_len, elements_len):
            child = elements[index].firstChild
            elements[index].removeChild(child)
    return None

def set_sample_ods(element:minidom.Element, data:dict[str, list[str|int]])->None:
    elements = element.getElementsByTagName('d')
    data_values = data
    data_len = len(data_values)
    elements_len = elements.length
    
    for ele, val in zip(elements, data_values):
        ele.firstChild.nodeValue = val
        
    if elements_len != data_len:
        for index in range(data_len, elements_len):
            child = elements[index].firstChild
            elements[index].removeChild(child)
    return None

def set_norm_ctrl_ods(element:minidom.Element, data:dict[str, list[str|int]])->None:
    elements = element.getElementsByTagName('d')
    data_values = data
    data_len = len(data_values)
    elements_len = elements.length
    
    for ele, val in zip(elements, data_values):
        ele.firstChild.nodeValue = val
        
    if elements_len != data_len:
        for index in range(data_len, elements_len):
            child = elements[index].firstChild
            elements[index].removeChild(child)
    return None

def set_norm_sample_ods(element:minidom.Element, data:dict[str, list[str|int]])->None:
    elements = element.getElementsByTagName('d')
    data_values = data
    data_len = len(data_values)
    elements_len = elements.length
    
    for ele, val in zip(elements, data_values):
        ele.firstChild.nodeValue = val
        
    if elements_len != data_len:
        for index in range(data_len, elements_len):
            child = elements[index].firstChild
            elements[index].removeChild(child)
    return None

def create_prism_file(filename:str, dom:minidom.Document)->None:
    filename = filename.replace(EXCEL_EXT,PRISM_EXT)
    with open(filename, 'w') as prism:
        dom.writexml(prism)
    return None

def create_dom()->minidom.Document:
    template = 'Templates/elisa_template.pzfx'
    dom = minidom.parse(template)
    return dom

def main(data:dict[str,dict], filename:str)->None:
    '''Uses the prism file called template.pzfx to create a new prism file with the data from the optical plate reader
        Only creates the prism file that we make for the normalized and non-normalized data
    '''
    dom = create_dom()
    sample_nums, sample_ods, ctrl_ods,norm_ctrl_ods,norm_samp_ods,= data.values()
    samples_element, ctrlODs_element, samplesODs_elements, samples_element_again, norm_ctrlODs_element, norm_sampleODs_elements = dom.getElementsByTagName('Subcolumn')
    
    set_sample_numbers(samples_element, samples_element_again, data=sample_nums)
    set_ctrl_ods(ctrlODs_element, ctrl_ods)
    set_sample_ods(samplesODs_elements, sample_ods)
    set_norm_ctrl_ods(norm_ctrlODs_element, norm_ctrl_ods)
    set_norm_sample_ods(norm_sampleODs_elements, norm_samp_ods)
    create_prism_file(filename, dom)
    
    

