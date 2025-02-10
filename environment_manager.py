import os
import argparse
from colorama import init, Fore, Style
import textwrap
from shutil import get_terminal_size
import platform
import winreg
from enum import Enum
from typing import Dict, List, Optional

# Constants for the application
class Constants:
    # Registry paths
    SYSTEM_ENV_PATH = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
    USER_ENV_PATH = r'Environment'
    
    # UI Constants
    SEPARATOR_LENGTH = 50
    SEPARATOR_CHAR = "="
    SUBSEPARATOR_CHAR = "-"
    
    # Terminal display
    MIN_TERMINAL_WIDTH = 80
    VALUE_COLUMN_RATIO = 0.5
    INDEX_COLUMN_WIDTH = 3
    SPACING_WIDTH = 15
    
    # Menu options
    MENU_OPTIONS = {
        '1': 'Update variable',
        '2': 'Add new variable',
        '3': 'Refresh',
        '4': 'Exit'
    }
    
    # Colors
    class Colors:
        TITLE = Fore.YELLOW
        VALUE = Fore.WHITE
        SUCCESS = Fore.GREEN
        ERROR = Fore.RED
        INDEX = Fore.CYAN
        KEY = Fore.GREEN

class VariableType(Enum):
    SYSTEM = "system"
    USER = "user"

class EnvironmentManager:
    def __init__(self):
        init()
        self.system_vars: Dict[str, str] = {}
        self.user_vars: Dict[str, str] = {}
        self.all_vars: Dict[int, tuple] = {}  # Store all variables with their types

    def get_windows_variables(self, var_type: VariableType) -> Dict[str, str]:
        """Retrieve environment variables from Windows registry"""
        variables = {}
        try:
            key_path = (Constants.SYSTEM_ENV_PATH if var_type == VariableType.SYSTEM 
                       else Constants.USER_ENV_PATH)
            root_key = (winreg.HKEY_LOCAL_MACHINE if var_type == VariableType.SYSTEM 
                       else winreg.HKEY_CURRENT_USER)
            
            with winreg.OpenKey(root_key, key_path, 0, winreg.KEY_READ) as key:
                index = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, index)
                        variables[name] = value
                        index += 1
                    except WindowsError:
                        break
        except WindowsError as e:
            print(f"{Constants.Colors.ERROR}Registry access error: {e}{Style.RESET_ALL}")
        return variables

    def format_variables(self, vars_dict: Dict[str, str], start_index: int = 0) -> List[str]:
        """Format variables for display"""
        if not vars_dict:
            return []
            
        terminal_width = max(get_terminal_size()[0], Constants.MIN_TERMINAL_WIDTH)
        key_width = max(len(key) for key in vars_dict.keys())
        value_width = int((terminal_width - key_width - Constants.SPACING_WIDTH) * 
                         Constants.VALUE_COLUMN_RATIO)

        formatted_lines = []
        for idx, (key, value) in enumerate(vars_dict.items(), start=start_index):
            value = str(value) if value is not None else ""
            wrapped_value = textwrap.shorten(value, width=value_width, placeholder="...")
            formatted_lines.append(
                f"{Constants.Colors.INDEX}{idx:3d}{Style.RESET_ALL} | "
                f"{Constants.Colors.KEY}{key:<{key_width}}{Style.RESET_ALL} | "
                f"{Constants.Colors.VALUE}{wrapped_value}{Style.RESET_ALL}"
            )
        return formatted_lines

    def modify_variable(self, var_name: str, new_value: str, 
                       var_type: VariableType) -> bool:
        """Modify or create an environment variable"""
        try:
            key_path = (Constants.SYSTEM_ENV_PATH if var_type == VariableType.SYSTEM 
                       else Constants.USER_ENV_PATH)
            root_key = (winreg.HKEY_LOCAL_MACHINE if var_type == VariableType.SYSTEM 
                       else winreg.HKEY_CURRENT_USER)
            
            with winreg.OpenKey(root_key, key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, var_name, 0, winreg.REG_EXPAND_SZ, new_value)
            
            # Make changes permanent using setx command
            command = ('setx {} "{}" /M' if var_type == VariableType.SYSTEM 
                      else 'setx {} "{}"')
            os.system(command.format(var_name, new_value))
            return True
        except Exception as e:
            print(f"{Constants.Colors.ERROR}Error: {e}{Style.RESET_ALL}")
            return False

    def display_variables(self, var_type: VariableType):
        """Display environment variables"""
        title = "SYSTEM VARIABLES" if var_type == VariableType.SYSTEM else "USER VARIABLES"
        vars_dict = self.system_vars if var_type == VariableType.SYSTEM else self.user_vars
        
        print(f"\n{Constants.Colors.TITLE}{title}:{Style.RESET_ALL}")
        print(Constants.SUBSEPARATOR_CHAR * Constants.SEPARATOR_LENGTH)
        
        if vars_dict:
            start_index = 0 if var_type == VariableType.SYSTEM else len(self.system_vars)
            lines = self.format_variables(vars_dict, start_index)
            for line in lines:
                print(line)
        else:
            print(f"{Constants.Colors.ERROR}No {var_type.value} variables found.{Style.RESET_ALL}")

    def update_variables(self):
        """Update both system and user variables and create an indexed mapping"""
        self.system_vars = self.get_windows_variables(VariableType.SYSTEM)
        self.user_vars = self.get_windows_variables(VariableType.USER)
        
        # Reset and rebuild all_vars mapping
        self.all_vars.clear()
        index = 0
        
        # Add system variables to mapping
        for key, value in self.system_vars.items():
            self.all_vars[index] = (key, value, VariableType.SYSTEM)
            index += 1
            
        # Add user variables to mapping
        for key, value in self.user_vars.items():
            self.all_vars[index] = (key, value, VariableType.USER)
            index += 1

    def run(self):
        """Main application loop"""
        if platform.system() != "Windows":
            print(f"{Constants.Colors.ERROR}This program currently only fully supports Windows systems.{Style.RESET_ALL}")
            return

        while True:
            self.update_variables()
            
            print("\n" + Constants.SEPARATOR_CHAR * Constants.SEPARATOR_LENGTH)
            print(f"{Constants.Colors.TITLE}Environment Variable Manager{Style.RESET_ALL}")
            print(Constants.SEPARATOR_CHAR * Constants.SEPARATOR_LENGTH)

            self.display_variables(VariableType.SYSTEM)
            self.display_variables(VariableType.USER)

            print("\n" + Constants.SEPARATOR_CHAR * Constants.SEPARATOR_LENGTH)
            print(f"{Constants.Colors.TITLE}OPERATIONS:{Style.RESET_ALL}")
            for key, value in Constants.MENU_OPTIONS.items():
                print(f"{key}. {value}")

            choice = input("\nSelect an option (1-4): ")

            if choice == '1':
                self.handle_update_variable()
            elif choice == '2':
                self.handle_add_variable()
            elif choice == '3':
                continue
            elif choice == '4':
                print(f"{Constants.Colors.TITLE}Exiting program...{Style.RESET_ALL}")
                break
            else:
                print(f"{Constants.Colors.ERROR}Invalid selection{Style.RESET_ALL}")

            input("\nPress Enter to continue...")

    def handle_update_variable(self):
        """Handle variable update operation"""
        print("\nSelect variable type:")
        print("1. System variable")
        print("2. User variable")
        type_choice = input("Select (1-2): ")
        
        var_type = (VariableType.SYSTEM if type_choice == "1" 
                   else VariableType.USER if type_choice == "2" 
                   else None)
        
        if not var_type:
            print(f"{Constants.Colors.ERROR}Invalid selection{Style.RESET_ALL}")
            return

        var_index = input("Enter variable number to modify: ")
        try:
            var_index = int(var_index)
            
            if var_index in self.all_vars:
                var_name, current_value, stored_type = self.all_vars[var_index]
                
                # Check if the selected type matches the variable's actual type
                if stored_type != var_type:
                    print(f"{Constants.Colors.ERROR}Selected variable is not a {var_type.value} variable{Style.RESET_ALL}")
                    return
                
                print(f"Current value: {current_value}")
                new_value = input(f"Enter new value for '{var_name}': ")
                
                if self.modify_variable(var_name, new_value, var_type):
                    print(f"{Constants.Colors.SUCCESS}✓ Variable updated successfully{Style.RESET_ALL}")
                    print(f"{Constants.Colors.TITLE}Note: Some changes may require a system restart.{Style.RESET_ALL}")
                else:
                    print(f"{Constants.Colors.ERROR}✗ Failed to update variable{Style.RESET_ALL}")
            else:
                print(f"{Constants.Colors.ERROR}✗ Invalid index{Style.RESET_ALL}")
        except ValueError:
            print(f"{Constants.Colors.ERROR}✗ Invalid number{Style.RESET_ALL}")

    def handle_add_variable(self):
        """Handle add new variable operation"""
        print("\nSelect variable type:")
        print("1. System variable")
        print("2. User variable")
        var_type = input("Select (1-2): ")
        
        var_type = (VariableType.SYSTEM if var_type == "1" 
                   else VariableType.USER if var_type == "2" 
                   else None)
        
        if not var_type:
            print(f"{Constants.Colors.ERROR}Invalid selection{Style.RESET_ALL}")
            return

        var_name = input("Enter new variable name: ")
        var_value = input("Enter variable value: ")
        
        if self.modify_variable(var_name, var_value, var_type):
            print(f"{Constants.Colors.SUCCESS}✓ New variable added successfully{Style.RESET_ALL}")
            print(f"{Constants.Colors.TITLE}Note: Some changes may require a system restart.{Style.RESET_ALL}")
        else:
            print(f"{Constants.Colors.ERROR}✗ Failed to add variable{Style.RESET_ALL}")

def main():
    manager = EnvironmentManager()
    manager.run()

if __name__ == "__main__":
    main()
