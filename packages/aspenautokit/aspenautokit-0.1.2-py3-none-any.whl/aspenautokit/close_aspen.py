import os

class AspenProcessManager:
    '''
    This class will allow the user to manually kill aspen plus processes as if they were closing them in the task manager.
    '''

    def __init__(self):
        '''
        Print statement to see when this is initialized for development purposes.
        '''
        print("Python: Aspen Process Manager initialized")

    def close_all_instances(self):
        '''
        Forcefully closes all running Aspen processes by using the os task kill command.
        '''
        os.system("taskkill /IM apmain.exe /F")
        os.system("taskkill /IM AspenPlus.exe /F")

def main():
    """
    Main function for the aspenautokit-close command.
    """
    manager = AspenProcessManager()
    manager.close_all_instances()
    print("Python: All Aspen Plus instances closed")

if __name__ == "__main__":
    # This block of code runs only when the script is executed directly.
    main()