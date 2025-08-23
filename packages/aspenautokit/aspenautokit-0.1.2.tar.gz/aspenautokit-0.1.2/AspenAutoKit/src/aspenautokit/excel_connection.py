import pandas as pd
import os
import re

class ExcelReader:
    '''
    The aim of this class is to be hold all the code required to collect the required information
    from the excel controller. 
    '''

    def __init__(self, file_path: str):
        '''
        Initializes ExcelReader class from excel controller
        '''
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The specified file was not found: {file_path}")
        self.file_path = file_path

    def get_specific_str(self, sheet_name: str, row: int, col: int) -> str:
        '''
        Retrieves a str value from excel controller from specific box
        '''
        try:
            df = pd.read_excel(self.file_path, sheet_name=sheet_name)
            value = df.iloc[row, col]
            cleaned_value = str(value).strip().replace('"', '')

            return cleaned_value
        
        except FileNotFoundError:
            print(f"Error: file {self.file_path} not found.")
            return None
        except KeyError:
            print(f"Error: Sheet '{sheet_name}' not found in the Excel file.")
            return None
        except IndexError:
            print(f"Error: Row or column index ({row}, {col}) is out of bounds for the sheet '{sheet_name}'.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None
        
    def get_specific_int(self, sheet_name: str, row: int, col: int) -> int:
        '''
        Retrieves a int value from excel controller from specific box
        '''
        try:
            df = pd.read_excel(self.file_path, sheet_name=sheet_name)
            value = df.iloc[row, col]
            integer_value = int(value)

            return integer_value
        
        except FileNotFoundError:
            print(f"Error: The file '{self.file_path}' was not found.")
            return None
        except KeyError:
            print(f"Error: Sheet '{sheet_name}' not found in the Excel file.")
            return None
        except IndexError:
            print(f"Error: Row or column index ({row}, {col}) is out of bounds for the sheet '{sheet_name}'.")
            return None
        except ValueError:
            print(f"Error: The value '{value}' at ({row}, {col}) could not be converted to an integer.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None
        
    def read_simulations_sheet(self) -> pd.DataFrame:
        '''
        Reads the "Simulations" sheet and stores the data in a DataFrame.
        '''
        try:
            df = pd.read_excel(
                self.file_path,
                sheet_name="Simulations",
                header=1
            )
            
            df.dropna(how='all', axis=1, inplace=True)
            df.dropna(how='all', axis=0, inplace=True)
            
            return df
        
        except FileNotFoundError:
            print(f"Error: The file '{self.file_path}' was not found.")
        except KeyError:
            print(f"Error: The sheet 'Simulations' was not found in the Excel file.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            
        # Return an empty DataFrame on any error
        return pd.DataFrame()
    
    def read_inputs_and_outputs(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        sheet_name = "IO Variables"
        print(f"Reading 'Inputs' and 'Outputs' from the '{sheet_name}' sheet...")
        try:
            df = pd.read_excel(self.file_path, sheet_name=sheet_name, header=None)

            input_headers = df.iloc[1, 0:5].values
            input_data = df.iloc[2:, 0:5]
            input_df = pd.DataFrame(input_data.values, columns=input_headers)
            
            output_headers = df.iloc[1, 5:11].values
            output_data = df.iloc[2:, 5:11]
            output_df = pd.DataFrame(output_data.values, columns=output_headers)

            input_df.dropna(how='all', axis=0, inplace=True)
            output_df.dropna(how='all', axis=0, inplace=True)

            int_cols = ['Lower Range', 'Upper Range']
            
            # CRITICAL FIX: Loop to process both DataFrames
            for df_to_process in [input_df, output_df]:
                for col in df_to_process.columns:
                    if col in int_cols:
                        df_to_process[col] = pd.to_numeric(df_to_process[col], errors='coerce').astype('Int64')
                    else:
                        df_to_process[col] = df_to_process[col].astype(str)
                
                # Apply the string formatting logic to the current DataFrame
                if 'Aspen Tree Path' in df_to_process.columns:
                    def extract_and_format_path(full_string):
                        match = re.search(r'"(.*?)"', full_string)
                        if match:
                            return '"' + match.group(1) + '"'
                        return full_string

                    df_to_process['Aspen Tree Path'] = df_to_process['Aspen Tree Path'].apply(extract_and_format_path)

            print(f"Successfully separated inputs and outputs into two DataFrames.")
            return input_df, output_df
        
        except FileNotFoundError:
            print(f"Error: The file '{self.file_path}' was not found.")
        except KeyError:
            print(f"Error: The sheet '{sheet_name}' was not found in the Excel file.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        
        return pd.DataFrame(), pd.DataFrame()
    
    def read_results_sheet(self) -> pd.DataFrame:
        '''
        Reads the "Result File" sheet into a DataFrame.
        The function uses the first row as the header and converts all
        values to strings.
        
        Returns:
            pd.DataFrame: A pandas DataFrame containing the data from the "Result File" sheet.
                          Returns an empty DataFrame if an error occurs.
        '''
        sheet_name = "Result File"
        print(f"Reading '{sheet_name}' sheet...")
        try:
            # Read the entire sheet using the first row as the header (header=0)
            df = pd.read_excel(
                self.file_path,
                sheet_name=sheet_name,
                header=0
            )

            # Drop any entirely empty columns and rows
            df.dropna(how='all', axis=1, inplace=True)
            df.dropna(how='all', axis=0, inplace=True)

            # Convert all columns to string type
            for col in df.columns:
                df[col] = df[col].astype(str)
                
            print(f"Successfully read '{sheet_name}' sheet into a DataFrame.")
            return df
        
        except FileNotFoundError:
            print(f"Error: The file '{self.file_path}' was not found.")
        except KeyError:
            print(f"Error: The sheet '{sheet_name}' was not found in the Excel file.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            
        return pd.DataFrame()