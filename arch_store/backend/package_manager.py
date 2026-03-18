import subprocess
import os
import shutil

class PackageManager:
    def __init__(self):
        pass

    def is_installed(self, package_name):
        """Check if a package is installed."""
        try:
            subprocess.run(
                ['pacman', '-Qi', package_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def get_installed_version(self, package_name):
        """Get the installed version of a package."""
        try:
            result = subprocess.run(
                ['pacman', '-Q', package_name],
                capture_output=True,
                text=True,
                check=True
            )
            # Output format: package_name version
            return result.stdout.split()[1]
        except (subprocess.CalledProcessError, IndexError):
            return None

    def list_installed(self):
        """List all installed packages."""
        try:
            result = subprocess.run(
                ['pacman', '-Q'],
                capture_output=True,
                text=True,
                check=True
            )
            packages = []
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    packages.append({'name': parts[0], 'version': parts[1]})
            return packages
        except subprocess.CalledProcessError:
            return []

    def remove_package(self, package_name):
        """
        Remove a package using pkexec.
        """
        cmd = ['pkexec', 'pacman', '-Rns', package_name, '--noconfirm']
        try:
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def is_official_package(self, package_name):
        """Check if a package exists in the official repositories."""
        try:
            # pacman -Ss ^package_name$ searches for exact match in sync dbs
            result = subprocess.run(
                ['pacman', '-Ss', f'^{package_name}$'],
                capture_output=True,
                text=True,
                check=False # Don't raise on non-zero, just return False
            )
            return result.returncode == 0
        except Exception:
            return False

    def install_package_in_terminal(self, package_name):
        """
        Install a package by opening a terminal window.
        Handles both official packages (pacman -S) and AUR (makepkg).
        """
        
        # Find a suitable terminal
        terminals = ['konsole', 'gnome-terminal', 'xfce4-terminal', 'xterm', 'kitty', 'alacritty']
        terminal = None
        for t in terminals:
            if shutil.which(t):
                terminal = t
                break
        
        if not terminal:
            print("No supported terminal found.")
            return False

        if self.is_official_package(package_name):
            # Official Package Installation
            script = f"""
            echo "Installing {package_name} from official repositories..."
            sudo pacman -S {package_name}
            echo "Press Enter to close..."
            read
            """
        else:
            # AUR Installation
            build_dir = os.path.expanduser("~/arch_store_build")
            os.makedirs(build_dir, exist_ok=True)
            
            script = f"""
            echo "Installing {package_name} from AUR..."
            mkdir -p {build_dir}
            cd {build_dir}
            rm -rf {package_name}
            git clone https://aur.archlinux.org/{package_name}.git
            cd {package_name}
            if [ -f PKGBUILD ]; then
                makepkg -si
            else
                echo "Error: PKGBUILD not found. This might be an official package or the AUR repo is empty."
            fi
            echo "Press Enter to close..."
            read
            """

        if terminal == 'gnome-terminal':
            cmd = [terminal, '--wait', '--', 'bash', '-c', script]
        elif terminal == 'konsole':
            cmd = [terminal, '--nofork', '-e', 'bash', '-c', script]
        elif terminal == 'xfce4-terminal':
            cmd = [terminal, '--disable-server', '-x', 'bash', '-c', script]
        elif terminal == 'xterm':
            cmd = [terminal, '-e', 'bash', '-c', script]
        else:
            # Fallback for others that usually take -e
            cmd = [terminal, '-e', 'bash', '-c', script]
            
        return subprocess.Popen(cmd)

    def update_system_in_terminal(self):
        """
        Run a full system update (pacman -Syu) in a terminal.
        """
        terminals = ['konsole', 'gnome-terminal', 'xfce4-terminal', 'xterm', 'kitty', 'alacritty']
        terminal = None
        for t in terminals:
            if shutil.which(t):
                terminal = t
                break
        
        if not terminal:
            return None

        script = """
        echo "Updating System (pacman -Syu)..."
        sudo pacman -Syu
        echo "Press Enter to close..."
        read
        """
        
        if terminal == 'gnome-terminal':
            cmd = [terminal, '--wait', '--', 'bash', '-c', script]
        elif terminal == 'konsole':
            cmd = [terminal, '--nofork', '-e', 'bash', '-c', script]
        elif terminal == 'xfce4-terminal':
            cmd = [terminal, '--disable-server', '-x', 'bash', '-c', script]
        elif terminal == 'xterm':
            cmd = [terminal, '-e', 'bash', '-c', script]
        else:
            cmd = [terminal, '-e', 'bash', '-c', script]
            
        return subprocess.Popen(cmd)


    def check_updates(self):
        """
        Check for updates by comparing installed versions with AUR versions.
        Returns a list of dicts with package info.
        """
        # 1. Get all installed packages (foreign) - usually AUR packages are 'foreign'
        # pacman -Qm lists foreign packages
        try:
            result = subprocess.run(['pacman', '-Qm'], capture_output=True, text=True, check=True)
            foreign_pkgs = [line.split()[0] for line in result.stdout.splitlines()]
        except subprocess.CalledProcessError:
            return []

        if not foreign_pkgs:
            return []

        # 2. Get AUR info for these packages
        # We need to import AurApi here or pass it in. 
        # Better to keep PackageManager independent? 
        # But checking updates requires AUR info.
        # Let's assume we pass the AUR info or use a helper.
        # For simplicity, let's import AurApi inside the method to avoid circular imports if any
        from .aur_api import AurApi
        api = AurApi()
        
        updates = []

        # Check Official Updates (pacman -Qu)
        try:
            result = subprocess.run(['pacman', '-Qu'], capture_output=True, text=True, check=False)
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    # Format: package old_ver -> new_ver
                    # Example: "bash 5.1.0-1 -> 5.1.8-1"
                    parts = line.split()
                    if len(parts) >= 4 and parts[2] == '->':
                        name = parts[0]
                        old_ver = parts[1]
                        new_ver = parts[3]
                        
                        updates.append({
                            'Name': name,
                            'Version': new_ver,
                            'CurrentVersion': old_ver,
                            'Description': f'Official Update: {old_ver} -> {new_ver}',
                            'IsOfficial': True
                        })
                    elif len(parts) >= 2:
                        # Fallback if format is different
                        name = parts[0]
                        version = parts[1]
                        updates.append({
                            'Name': name,
                            'Version': version,
                            'CurrentVersion': 'Unknown',
                            'Description': 'Official Repository Update',
                            'IsOfficial': True
                        })
        except Exception as e:
            print(f"Error checking official updates: {e}")

        # Check AUR Updates
        # AUR RPC supports multiple args
        # We might need to chunk this if too many packages
        chunk_size = 100
        
        for i in range(0, len(foreign_pkgs), chunk_size):
            chunk = foreign_pkgs[i:i+chunk_size]
            aur_info = api.get_info(chunk)
            
            for pkg in aur_info:
                name = pkg['Name']
                aur_version = pkg['Version']
                current_version = self.get_installed_version(name)
                
                # Simple string comparison is not enough for versions (e.g. 1.10 > 1.9)
                # We can use 'vercmp' tool from pacman
                if current_version and self.compare_versions(current_version, aur_version) < 0:
                    pkg['CurrentVersion'] = current_version
                    pkg['IsOfficial'] = False
                    updates.append(pkg)
                    
        return updates

    def compare_versions(self, v1, v2):
        """
        Compare two versions using vercmp.
        Returns < 0 if v1 < v2, 0 if equal, > 0 if v1 > v2
        """
        try:
            result = subprocess.run(['vercmp', v1, v2], capture_output=True, text=True, check=True)
            return int(result.stdout.strip())
        except (subprocess.CalledProcessError, ValueError):
            return 0


