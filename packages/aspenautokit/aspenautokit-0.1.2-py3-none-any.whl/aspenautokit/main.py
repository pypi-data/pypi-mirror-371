'''
Code methodology developed by Vincent Bailey Ladd @ University of Sheffield.

This code is open source and available for edits by any and all individuals, it is requested
that anyone using this code for research purposes reference the original publication regarding
the development of the automation methodology.

AI was used to develop some parts of this architecture but not the methodology

'''

from .aspen_connection import AspenConnection
from .excel_connection import ExcelReader
from .save_results import ResultsSaver

import pandas as pd
from joblib import Parallel, delayed
import os
import shutil
import numpy as np
import pythoncom
import uuid
import sys

def parallel_run(worker_id: str, sim_file: str, user_values: dict, inputs_df: pd.DataFrame, output_df: pd.DataFrame, result_df: pd.DataFrame, results_saver: ResultsSaver, case_id: str):
    """
    Runs a single simulation and saves results for a parallel worker.
    """
    aspen_conn = None
    try:
        # Aspen Initialization
        try:
            pythoncom.CoInitialize()
        except pythoncom.com_error:
            print(f"[{worker_id}] COM initialization failed.")
            return

        aspen_conn = AspenConnection(sim_file=sim_file)
        app = aspen_conn.initialize_aspen(visible=True, suppress_dialogs=True)
        
        if app:
            should_quit_aspen = True
            aspen_conn.set_simulation_nodes(user_values, inputs_df)
            print(f"[{worker_id}] Successfully set nodes.")
            aspen_conn.run_Application()
            hasError = aspen_conn.check_error_status()
            variables_df = pd.concat([inputs_df, output_df], ignore_index=True)

            if not hasError:
                print(f"[{worker_id}] Completed without errors: {os.path.basename(sim_file)}")
                results_saver.save_simulation_results(case_id=case_id, sim_id=worker_id, user_values=user_values, variables_df=variables_df, result_df=result_df, aspen_conn=aspen_conn)
            else:
                print(f"[{worker_id}] Completed with errors: {os.path.basename(sim_file)}")
    
    except Exception as e:
        print(f"[{worker_id}] A fatal error occurred: {e}")
    finally:
        if aspen_conn:
            aspen_conn.quit()
        try:
            pythoncom.CoUninitialize()
        except pythoncom.com_error:
            pass

def linear_run(worker_id: str, sim_file: str, list_of_user_values: list, inputs_df: pd.DataFrame, output_df: pd.DataFrame, result_df: pd.DataFrame, results_saver: ResultsSaver, case_id: str):
    """
    Runs a series of simulations linearly in a single Aspen instance.
    """
    aspen_conn = None
    try:
        # Aspen Initialization (once per linear run)
        try:
            pythoncom.CoInitialize()
        except pythoncom.com_error:
            print(f"[{worker_id}] COM initialization failed.")
            return

        aspen_conn = AspenConnection(sim_file=sim_file)
        app = aspen_conn.initialize_aspen(visible=True, suppress_dialogs=True)
        
        if app:
            for user_values in list_of_user_values:
                print(f"[{worker_id}] Setting nodes for values: {user_values}")
                aspen_conn.set_simulation_nodes(user_values, inputs_df)
                
                print(f"[{worker_id}] Successfully set nodes. Starting run.")
                aspen_conn.run_Application()
                hasError = aspen_conn.check_error_status()
                variables_df = pd.concat([inputs_df, output_df], ignore_index=True)
                
                if not hasError:
                    print(f"[{worker_id}] Completed without errors: {os.path.basename(sim_file)}")
                    results_saver.save_simulation_results(case_id=case_id, sim_id=worker_id, user_values=user_values, variables_df=variables_df, result_df=result_df, aspen_conn=aspen_conn)
                else:
                    print(f"[{worker_id}] Completed with errors. Breaking out of linear run.")
                    break

    except Exception as e:
        print(f"[{worker_id}] A fatal error occurred: {e}")
    finally:
        if aspen_conn and aspen_conn.Application:
            aspen_conn.quit()
        try:
            pythoncom.CoUninitialize()
        except pythoncom.com_error:
            pass

import pandas as pd
import os
import shutil
import sys
import uuid

def simulation_worker(task: dict, working_dir: str):
    """
    Manages the full lifecycle for a single simulation run.
    This function is executed by a separate process.
    """
    aspen_conn = None
    temp_dir_path = None
    log_file = None
    original_stdout = sys.stdout
    should_quit_aspen = False

    try:
        worker_id = uuid.uuid4().hex[:6]
        
        # Unpack the task dictionary
        sim_file = task['sim_file']
        user_values = task['user_values']
        inputs_df = task['inputs_df']
        output_df = task['output_df']
        result_df = task['result_df']
        results_saver = task['results_saver']
        case_id = task['case_id']
        run_type = task['run_type']

        # Define all paths relative to the working_dir passed in
        log_dir = os.path.join(working_dir, "logs")
        temp_dir_base = os.path.join(working_dir, "tmp")

        # Create log and tmp directories if they don't exist
        os.makedirs(log_dir, exist_ok=True)
        os.makedirs(temp_dir_base, exist_ok=True)
        
        log_file_path = os.path.join(log_dir, f"worker_log_{worker_id}.txt")
        temp_dir_name = f"{os.path.basename(os.path.dirname(sim_file))}_{uuid.uuid4().hex}"
        temp_dir_path = os.path.join(temp_dir_base, temp_dir_name)
        
        # Redirect output to log file
        log_file = open(log_file_path, "w")
        sys.stdout = log_file

        print(f"[{worker_id}] Starting worker...")
        print(f"[{worker_id}] Using unique temporary folder: {temp_dir_path}")

        # Copy original folder
        shutil.copytree(os.path.dirname(sim_file), temp_dir_path)
        sim_prefix = os.path.splitext(os.path.basename(sim_file))[0]
        temp_sim_file = os.path.join(temp_dir_path, f"{sim_prefix}.apw")

        if run_type.lower() == 'parallel':
            single_user_values = task['user_values'][0]
            parallel_run(worker_id, temp_sim_file, single_user_values, inputs_df, output_df, result_df, results_saver, case_id)
        elif run_type.lower() == 'linear':
            list_of_user_values = task['user_values']
            linear_run(worker_id, temp_sim_file, list_of_user_values, inputs_df, output_df, result_df, results_saver, case_id)
        else:
            print(f"[{worker_id}] Invalid run type: {run_type}")
        
    except Exception as e:
        print(f"[{worker_id}] A fatal error occurred: {e}")
    finally:
        # Restore stdout
        if log_file:
            log_file.close()
            sys.stdout = original_stdout
        
        # The temp directory is cleaned up here
        if temp_dir_path and os.path.exists(temp_dir_path):
            shutil.rmtree(temp_dir_path, ignore_errors=True)
   

def main():
    """Main entry point for the AspenAutoKit command line interface."""
    if len(sys.argv) > 1:
        test_excel_file_path = sys.argv[1]
        print(f"Excel file path detected: {test_excel_file_path}")
    else:
        print(f"Warning: No excel file path detected!")
        print("Usage: aspenautokit <excel_file_path>")
        return

    excel_reader = ExcelReader(test_excel_file_path)

    parallel_instances = excel_reader.get_specific_str(sheet_name="Settings", row=0, col=7)
    sim_file = excel_reader.get_specific_str(sheet_name="Settings", row=3, col=7)
    working_dir = excel_reader.get_specific_str(sheet_name="Settings", row=6, col=7)
    print(working_dir)

    results_dir = os.path.join(working_dir, 'Results')
    log_dir = os.path.join(working_dir, 'logs')
    tmp_dir = os.path.join(working_dir, 'tmp')
    
    os.makedirs(results_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(tmp_dir, exist_ok=True)

    try:
        parallel_instances = int(parallel_instances)
    except (ValueError, TypeError):
        parallel_instances = 1
        print("Could not parse parallel instances from Excel, defaulting to 1.")

    sim_df = excel_reader.read_simulations_sheet()
    input_df, output_df = excel_reader.read_inputs_and_outputs()
    result_df = excel_reader.read_results_sheet()

    # print(f"res_dir: {res_dir}")
    # print(sim_df)
    # print(input_df)
    # print(output_df)
    # print(result_df)

    simulation_tasks = []
    results_saver = ResultsSaver(results_dir)

    for index, row in sim_df.iterrows():
        case_id = row['CASE ID']
        run_type = row['Linear/Parallel']
        variable_name = row['VARIABLE']
        lower_lim = row['LOWER LIM']
        upper_lim = row['UPPER LIM']
        steps = int(row['STEPS'])
        
        independent_values = np.linspace(lower_lim, upper_lim, steps)
        dependent_variable_name = sim_df.columns[6]

        if run_type.lower() == 'parallel':
            # For parallel runs, each user_values dictionary is a separate task
            for val in independent_values:
                user_values = {
                    variable_name: val,
                    dependent_variable_name: row[dependent_variable_name]
                }
                simulation_tasks.append({
                    'sim_file': sim_file,
                    'user_values': [user_values], # Pass as a single-item list
                    'inputs_df': input_df,
                    'output_df': output_df,
                    'result_df': result_df,
                    'results_saver': results_saver,
                    'case_id': case_id,
                    'run_type': run_type
                })
        elif run_type.lower() == 'linear':
            # For linear runs, the entire list of user_values is a single task
            user_values_list = []
            for val in independent_values:
                user_values = {
                    variable_name: val,
                    dependent_variable_name: row[dependent_variable_name]
                }
                user_values_list.append(user_values)
            simulation_tasks.append({
                'sim_file': sim_file,
                'user_values': user_values_list,
                'inputs_df': input_df,
                'output_df': output_df,
                'result_df': result_df,
                'results_saver': results_saver,
                'case_id': case_id,
                'run_type': run_type
            })
        else:
            print(f"Invalid run type for CASE ID: {case_id}. Skipping.")

    print(f"Starting {len(simulation_tasks)} simulations across {parallel_instances} parallel jobs.")
    
    Parallel(n_jobs=parallel_instances)(
        delayed(simulation_worker)(task=task, working_dir=working_dir) for task in simulation_tasks
    )

    print("All simulation initialization tasks have been started.")
    results_saver.collate_results()


if __name__ == "__main__":
    main()