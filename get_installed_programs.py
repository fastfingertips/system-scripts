import winreg
import sys
import os

class WindowsProgramLister:
    """Class to list installed programs from Windows Registry."""

    def __init__(self):
        """Initialize registry paths for program discovery."""
        self.uninstall_registry_keys = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        ]

    def check_windows_compatibility(self):
        """Check if the script is running on Windows OS."""
        return os.name == 'nt'

    def get_programs_from_registry(self, hive, registry_path):
        """Extract program information from specified registry location."""
        programs = []
        try:
            with winreg.OpenKey(hive, registry_path) as registry_key:
                for index in range(winreg.QueryInfoKey(registry_key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(registry_key, index)
                        with winreg.OpenKey(registry_key, subkey_name) as subkey:
                            try:
                                program_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                                program_guid = subkey_name if subkey_name.startswith("{") else "N/A"
                                programs.append((program_guid, program_name))
                            except FileNotFoundError:
                                continue
                    except (FileNotFoundError, OSError):
                        continue
        except FileNotFoundError:
            pass
        return programs

    def get_user_programs(self):
        """Get programs installed in user profiles."""
        user_programs = []
        try:
            with winreg.OpenKey(winreg.HKEY_USERS, "") as users_key:
                for index in range(winreg.QueryInfoKey(users_key)[0]):
                    try:
                        user_sid = winreg.EnumKey(users_key, index)
                        uninstall_path = rf"{user_sid}\Software\Microsoft\Windows\CurrentVersion\Uninstall"
                        user_programs.extend(self.get_programs_from_registry(winreg.HKEY_USERS, uninstall_path))
                    except (FileNotFoundError, OSError):
                        continue
        except FileNotFoundError:
            pass
        return user_programs

    def write_programs_to_file(self, programs, output_file):
        """Write the collected program information to a file."""
        if not programs:
            print("No programs found.")
            return

        max_guid_length = max(len(program[0]) for program in programs)
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(f"{'GUID'.ljust(max_guid_length)} | {'Program Name'}\n")
            file.write("-" * (max_guid_length + 25) + "\n")
            for guid, name in programs:
                file.write(f"{guid.ljust(max_guid_length)} | {name}\n")

    def run(self):
        """Main execution method to collect and write program information."""
        if not self.check_windows_compatibility():
            print("Error: This script requires Windows OS.")
            sys.exit(1)

        installed_programs = []
        
        # Get machine-wide programs
        for registry_key in self.uninstall_registry_keys:
            installed_programs.extend(self.get_programs_from_registry(
                winreg.HKEY_LOCAL_MACHINE, registry_key))

        # Get user-specific programs
        installed_programs.extend(self.get_user_programs())

        # Sort programs by name
        installed_programs.sort(key=lambda program: program[1].lower())
        
        output_file = "installed_programs_sorted.txt"
        self.write_programs_to_file(installed_programs, output_file)
        print(f"A total of {len(installed_programs)} programs found. Output written to: {output_file}")

if __name__ == "__main__":
    program_lister = WindowsProgramLister()
    program_lister.run()