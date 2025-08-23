from win32com.client import Dispatch
import time
import os
import pandas as pd
import numpy as np
import shutil
import pythoncom

class AspenConnection:
    '''
    Handles all direct communication and actions with the Aspen Plus application,
    including its initialization.
    '''
    def __init__(self, sim_file: str):
        '''
        Initializes the class with the path to the simulation file.
        '''
        self.sim_file = sim_file
        self.Application = None

# Place this code inside your AspenConnection class
    def initialize_aspen(self, visible: bool, suppress_dialogs: bool):
        '''
        Initializes the Aspen Plus application and loads the simulation file
        from the path it receives. It assumes the file is already prepared
        and located in a unique, process-specific directory.
        '''
        self.Application = None
        try:
            # Step 1: Initialize the COM library
            try:
                pythoncom.CoInitialize()
            except pythoncom.com_error:
                pass
            
            # Step 2: Proceed with the original initialization logic
            self._del_bkp()
            self.Application = Dispatch("Apwn.Document")
            self._del_bkp()
            self.Application.InitFromFile2(self.sim_file)
            self._del_bkp()
            self.Application.Visible = visible
            time.sleep(0.5)
            self.Application.SuppressDialogs = suppress_dialogs
            time.sleep(0.5)
            self._del_bkp()

            wait_time = 0; max_wait_time = 60  # Wait for file to load completely in seconds
            while not self.Application.Tree.FindNode(r"\Data") and wait_time < max_wait_time:
                time.sleep(1)
                wait_time += 1
            if wait_time >= max_wait_time:
                return None

            return self.Application

        except Exception as e:
            print(f"Error initializing Aspen: {e}")
            self.quit()
            return None


    def set_Application_values(self, user_values: dict, inputs_df: pd.DataFrame):
        """
        Sets values in Aspen Plus for defined input nodes.
        """
        if not self.Application:
            print("Aspen application is not initialized. Call initialize_aspen() first.")
            return

        modifiable_nodes = self._get_Application_nodes(inputs_df)

        for var_name, value in user_values.items():
            if var_name in modifiable_nodes:
                node_path = modifiable_nodes[var_name]
                self._present_node(var_name, node_path, user_values)
            else:
                print(f"Warning: {var_name} is not a valid modifiable node.")

    def run_Application(self):
        """Developed using Zihao Wang's code"""
        if not self.Application:
            print("Aspen application is not initialized. Call initialize_aspen() first.")
            return
        
        try:
            self.Application.Engine.Run2(True)
            time_limit = 15 * 60
            elapsed_time = 0
            while self.Application.Engine.IsRunning == 1:
                time.sleep(1)
                elapsed_time += 1
                if elapsed_time >= time_limit:
                    self.Application.Engine.Stop()
                    break
        except Exception as e:
            print(f"Error in aspen run function: {e}")

    def check_error_status(self):
        """
        Check for an error in the Aspen system based on the final cycle data.

        Returns:
            bool: True if an error is detected, False otherwise.
        """
        if not self.Application:
            print("Aspen application is not initialized. Cannot check status.")
            return True
        
        try:
            error_detector_node = self.Application.Tree.FindNode(r"\Data")
            error_status = error_detector_node.AttributeValue(12)
            status = hex(error_status)[2:]
            hasError = not (status[-1] == '1')
            return hasError
        except Exception as e:
            print(f"Error in error detection function: {e}")
            return True

    def quit(self):
        '''
        Quits the Aspen application instance.
        '''
        if self.Application:
            try:
                self.Application.Quit()
                time.sleep(1)
                self.Application = None
            except Exception as e:
                print(f"ERROR DURING ASPEN CLEANUP: {e}")
    
    def _del_bkp(self, retries=3):
        '''
        Attempt to delete temporary backup files with retries (prevents COM overloading).
        '''
        base_sim_name = os.path.splitext(os.path.basename(self.sim_file))[0]
        fold_path = os.path.dirname(self.sim_file)
        
        bkp_file1 = os.path.join(fold_path, f"${base_sim_name.lower()}$backup.bk$")
        bkp_file2 = os.path.join(fold_path, f"${base_sim_name.upper()}$BACKUP$backup.bk$")

        for attempt in range(1, retries + 1):
            try:
                if os.path.exists(bkp_file1):
                    os.remove(bkp_file1)
                if os.path.exists(bkp_file2):
                    os.remove(bkp_file2)
                break
            except Exception as e:
                print(f"Attempt {attempt} to delete backup files failed: {e}")
                if attempt < retries:
                    time.sleep(attempt * 0.5)

    # This is the _node function from your working old code,
    # adapted to the class structure.
    def _node(self, path: str, new_value=None):
        ''' Finds a node in Aspen and provides the option to change its value '''
        if not self.Application:
            print("Aspen application is not initialized. Cannot access nodes.")
            return None
        
        try:
            node = self.Application.Tree.FindNode(path)
            if node is not None:
                if new_value is not None:
                    node.Value = new_value
                    time.sleep(0.1)
                return node
            else:
                print(f"Node not found at path: {path}")
        except Exception as e:
            print(f"Error accessing node {path}: {str(e)}")
        return None

    # This is the _present_node function from your working old code,
    # adapted to the class structure.
    def _present_node(self, key: str, node_path: str, kwargs: dict):
        """Sets an Aspen node only if the value exists and is not NaN."""
        if key in kwargs:
            value = kwargs[key]
            if value is None or (isinstance(value, float) and np.isnan(value)):
                print(f"Skipping {key} (Node: {node_path}) due to NaN or None value.")
                return
            try:
                # This calls the _node method on the same instance
                self._node(node_path, new_value=value)
                print(f"Set {key} (Node: {node_path}) to {value}")
                time.sleep(0.1)
            except Exception as e:
                print(f"Error setting {key} (Node: {node_path}): {str(e)}")
        else:
            print(f"{key} not found in kwargs, skipping.")
    
    def _get_Application_nodes(self, df: pd.DataFrame):
        """
        Extracts Aspen tree paths from a DataFrame and returns a dictionary
        mapping variable names to paths.
        """
        nodes = {}
        if 'Variable Name' in df.columns and 'Aspen Tree Path' in df.columns:
            for _, row in df.iterrows():
                var_name = row['Variable Name']
                path = row['Aspen Tree Path']
                if not pd.isna(var_name) and not pd.isna(path):
                    clean_path = str(path).strip().strip('"')
                    nodes[var_name] = clean_path
        return nodes

    # New method to combine the logic of your old `set_aspen_values` and `node_setter`
    def set_simulation_nodes(self, user_values: dict, inputs_df: pd.DataFrame):
        """
        Sets values in Aspen Plus for defined input nodes from the Excel sheet.
        This method replaces the logic of your old set_aspen_values.
        """
        if not self.Application:
            print("Aspen application is not initialized. Call initialize_aspen() first.")
            return

        # Use the class method to get the node paths from the inputs_df
        modifiable_nodes = self._get_Application_nodes(inputs_df)

        for var_name, value in user_values.items():
            if var_name in modifiable_nodes:
                node_path = modifiable_nodes[var_name]
                # The _present_node method is now called on the instance
                self._present_node(var_name, node_path, user_values)
            else:
                print(f"Warning: {var_name} is not a valid modifiable node.")