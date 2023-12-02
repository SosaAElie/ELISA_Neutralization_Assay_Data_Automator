from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.cell.cell import Cell
import openpyxl
from typing import Any, Callable
import csv


class ExcelWrapper:

    def __init__(self, filepath:str):
        '''Takes in a text file and produces and excel file or takes a an excel filepath'''
        if filepath.find(".txt") >= 0:
            self.wkbk, self.wkst = self.__create_excel(self.__get_data(filepath, "utf-16", "\t"))
        elif filepath.find(".csv") >= 0:
            self.wkbk, self.wkst = self.__create_excel(self.__get_data(filepath, "utf-8", ","))
        elif filepath.find(".xlsx") >= 0:
            self.wkbk = openpyxl.load_workbook(filepath)
            self.wkst = self.wkbk.active
        else:
            raise ValueError
        self.filepath = filepath

    def __get_data(self, filepath:str, encoding:str, delimiter:str )->list[list]:
        '''Gets the data from a utf-16 encoded text file and returns it as a list of lists'''
        data = []
        
        with open(filepath, "r", encoding=encoding) as raw_file:
            raw_data = csv.DictReader(raw_file, delimiter=delimiter)
            for row_dict in raw_data: data.append([val for val in row_dict.values()])
        print(data)
        return [self.__flatten_list(item) for item in data]
    
    def __create_excel(self,data:list[list], col_limit = 14)->tuple[Workbook, Worksheet]:
        '''Appends each list within the list argument to an excel worksheet, passing in a col_limit means that only
        items until the specified index are appended to the excel worksheet'''
        wkbk = Workbook()
        wkst:Worksheet = wkbk.active
        for row in data: wkst.append(row[:col_limit])
        return wkbk, wkst
    
    def __flatten_list(self, lists:list)->list:
        '''flattens inner lists into 1 list, goes 1 level deep only'''
        flattened = []
        for item in lists:
            if type(item) == list:
                for inner_item in item: flattened.append(inner_item)
            else:
                flattened.append(item)
            
        return flattened
    
    def add_column(self, col:str, data:str|list, start_row:int = 1)->None:
        '''Adds the data passed in to all the cells in the column, if a single value is passed in all cells
        in that column will have that value starting from start_row'''
        col = col.upper()
        col_index = ord(col) - ord("A")+1 if len(col) == 1 else (ord("Z") - ord("A")+1)+ord(col[-1]) - ord("A")+1
        
        limit = len(data) if isinstance(data, list) else self.wkst.max_row
        if not isinstance(data, list): data = [data]*limit

        for row, item in zip(range(start_row,limit+start_row), data): 
            self.wkst.cell(row = row, column=col_index, value=item)
        
        return None  
    
    def get_wkst_size(self, dimensions:str)->dict[str, str|int]:
        '''Parses the wkst.dimensions property and returns a dictionary with the information'''
        start, end = dimensions.split(":")

        return {
            "first_col":start[0],
            "first_index":int(start[1:]),
            "last_col":end[0],
            "last_index":int(end[1:]),
        }
    
    def get_cell_matrix(self, top_offset:int, left_offset:int, width:int, height:int, by_col = True, val_only = False)->list[Cell]:
        '''Returns a list of cells that is width * height beginning from the starting point, if by_col is set to True
        then the list returned are the cells in the order they appear in the excel file vertically, otherwise list returned are 
        the cells horizontally'''
        cells = []
        for col in range(left_offset, width+left_offset):
            for row in range(top_offset, height+top_offset): 
                cells.append(self.wkst.cell(row, col).value if val_only else self.wkst.cell(row, col))

        return cells
    
    def append_to_cell_value(self, cell:Cell, val:str, postion:str = 'prefix')->None:
        '''Adds another value to the current cell value, doesn't replace the cell value'''
        postion = postion.lower()
        if postion == "prefix": cell.value = f"{val}\t{cell.value}"
        elif postion == "suffix": cell.value = f"{cell.value}\t{val}"
        else: raise ValueError("Only 'prefix' or 'suffix' are acceptable arguments")
        return None

    def replace_cell_value(self, cell:Cell, new_val:str)->None:
        '''Replaces the cell value with the new value'''
        cell.value = new_val
        return None

    def get_column(self, col:str, start_row = 1, end_row:int = 0, values_only = False)->list[Cell|Any]:
        '''Gets the cells in a specified column in descending order'''
        col = col.upper()
        col_index = ord(col) - ord("A")+1 if len(col) == 1 else (ord("Z") - ord("A")+1)+ord(col[-1]) - ord("A")+1
        last_row = end_row if end_row > start_row else self.wkst.max_row
        return [self.wkst.cell(row, col_index) if not values_only else self.wkst.cell(row, col_index).value for row in range(start_row,last_row)]

    def apply_to_adj_columns(self, cell_matrix:list[Cell], foo:Callable, col_height = 8)->list[str|int|float]:
        '''Applies the function to each cell value and its adjacent cell value in the cell matrix, its adjacent is calculated
        by adding the col_height to the first index'''
        results = []
        finished_indices = []
        for index in range(len(cell_matrix)):
            if index in finished_indices: continue
            first_col = index
            second_col = index+col_height
            finished_indices.append(first_col)
            finished_indices.append(second_col)
            first_val = float(cell_matrix[first_col].value)
            second_val = float(cell_matrix[second_col].value)
            results.append(foo(first_val, second_val))
        return results
    
    def write_excel(self, destination:str)->None:
        self.wkbk.save(destination)
        return None