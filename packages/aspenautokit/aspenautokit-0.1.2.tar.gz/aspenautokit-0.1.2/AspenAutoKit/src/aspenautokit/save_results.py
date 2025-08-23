# This file is intended to hold the logic to save the results
# from the Aspen Plus simulations.

# will need to parse in result_df and output_df.

import pandas as pd
import os
import numpy as np

class ResultsSaver:
    """
    Handles all logic for saving and collating simulation results.
    """
    def __init__(self, results_dir: str):
        """
        Initializes the ResultsSaver with the base directory for saving results.
        """
        self.results_dir = results_dir
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)


    def save_simulation_results(self, case_id: str, sim_id: str, user_values: dict, variables_df: pd.DataFrame, result_df: pd.DataFrame, aspen_conn):
        """
        Saves the results of a single simulation to a unique Excel file,
        using the result_df as the template and organizing by CASE ID.

        Args:
            case_id (str): The unique identifier for the case (e.g., 'Test1').
            sim_id (str): A unique identifier for the simulation.
            user_values (dict): A dictionary of the input values used for the simulation.
            variables_df (pd.DataFrame): DataFrame containing both input and output variable definitions.
            result_df (pd.DataFrame): DataFrame containing the template for the results.
            aspen_conn: An instance of the AspenConnection class.
        """
        print(f"[{sim_id}] Starting to save results...")
        
        # 1. Prepare a new DataFrame based on the structure of result_df
        results_to_save_df = result_df.copy()
        
        # 2. Map variable identifiers to their paths and values
        variable_definitions = {row['Variable Name']: {'path': str(row['Aspen Tree Path']).strip().strip('"')} for _, row in variables_df.iterrows()}
        
        values = []
        for var_id in results_to_save_df['Value']:
            if var_id in user_values:
                values.append(user_values[var_id])
            elif var_id in variable_definitions:
                node_path = variable_definitions[var_id]['path']
                try:
                    node = aspen_conn._node(node_path)
                    values.append(node.Value if node else "Node Not Found")
                except Exception as e:
                    print(f"[{sim_id}] Error reading output node '{var_id}': {e}")
                    values.append(f"Error: {str(e)}")
            else:
                values.append("N/A")
        
        results_to_save_df['Value'] = values

        # 3. Generate a unique filename and file path
        independent_var_name = list(user_values.keys())[0]
        independent_var_value = user_values[independent_var_name]

        # Construct the new results subdirectory path
        sim_result_subdir = os.path.join(self.results_dir, case_id, f"{sim_id}_{independent_var_name}")
        if not os.path.exists(sim_result_subdir):
            os.makedirs(sim_result_subdir)
        
        filename = f"{sim_id}_{independent_var_name}_{independent_var_value:.2f}.xlsx"
        file_path = os.path.join(sim_result_subdir, filename)

        # 4. Save the DataFrame to an Excel file
        results_to_save_df.to_excel(file_path, index=False)
        print(f"[{sim_id}] Results saved to {file_path}")

    def collate_results(self):
        """
        Combines all individual results files from all subdirectories into separate Excel files.
        """
        print("Collating all results into separate files per CASE ID...")
        
        for case_id in os.listdir(self.results_dir):
            case_id_dir = os.path.join(self.results_dir, case_id)
            if os.path.isdir(case_id_dir):
                collated_df = pd.DataFrame()
                
                # Recursively find all Excel files within the CASE ID directory
                for root, dirs, files in os.walk(case_id_dir):
                    for file_name in files:
                        if file_name.endswith('.xlsx'):
                            file_path = os.path.join(root, file_name)
                            df = pd.read_excel(file_path)
                            
                            column_name = os.path.splitext(file_name)[0]
                            
                            if 'Variable' in df.columns and 'Value' in df.columns:
                                df_to_add = df[['Variable', 'Value']].set_index('Variable')
                                df_to_add = df_to_add.rename(columns={'Value': column_name})
                                
                                if collated_df.empty:
                                    collated_df = df_to_add
                                else:
                                    collated_df = pd.concat([collated_df, df_to_add], axis=1)

                if not collated_df.empty:
                    collated_file_path = os.path.join(self.results_dir, f"{case_id}_Collated_Results.xlsx")
                    collated_df.to_excel(collated_file_path)
                    print(f"All results for {case_id} collated into: {collated_file_path}")
                else:
                    print(f"No results files found for {case_id} to collate.")