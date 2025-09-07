import os
import subprocess
import shutil
import logging
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("/var/log/crd_setup.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def run_command(cmd, check=True, shell=False):
    """Run a command and return the result"""
    try:
        if shell:
            result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        else:
            result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {cmd}, Error: {e}")
        if check:
            raise
        return e.returncode, "", str(e)

def main():
    # Get user input
    CRD_SSH_Code = input("Google CRD SSH Code: ").strip()
    username = "user"  # Default username
    password = input("Set password for user (default: 'root'): ").strip() or "root"
    Pin = input("Set CRD PIN (6 digits, default: 123456): ").strip() or "123456"
    
    # Validate inputs
    if not CRD_SSH_Code:
        logger.error("Please enter authcode from the given link")
        sys.exit(1)
    
    if len(Pin) < 6:
        logger.error("Enter a pin with at least 6 digits")
        sys.exit(1)
    
    try:
        Pin = int(Pin)  # Ensure PIN is integer
    except ValueError:
        logger.error("PIN must be a number")
        sys.exit(1)
    
    Autostart = True  # Default to autostart
    
    logger.info("Starting CRD setup process...")
    
    # Create user
    try:
        logger.info(f"Creating user: {username}")
        run_command(["sudo", "useradd", "-m", "-s", "/bin/bash", username])
        run_command(["sudo", "usermod", "-aG", "sudo", username])
        run_command(["sudo", "chpasswd"], input=f"{username}:{password}", shell=False)
        logger.info(f"User {username} created successfully")
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        sys.exit(1)
    
    class CRDSetup:
        def __init__(self, user):
            self.user = user
            self.install_dependencies()
            self.installCRD()
            self.installDesktopEnvironment()
            self.changewall()
            self.installGoogleChrome()
            self.installTelegram()
            self.installQbit()
            self.finish(user)
        
        def install_dependencies(self):
            """Install necessary dependencies"""
            logger.info("Installing dependencies...")
            run_command(["sudo", "apt", "update"])
            run_command(["sudo", "apt", "install", "-y", "wget", "curl", "xfce4", "xfce4-terminal", "xfce4-goodies", "dbus-x11", "xscreensaver"])
            logger.info("Dependencies installed successfully")
        
        def installCRD(self):
            logger.info("Installing Chrome Remote Desktop...")
            run_command(["wget", "https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb"])
            run_command(["sudo", "dpkg", "-i", "chrome-remote-desktop_current_amd64.deb"])
            run_command(["sudo", "apt", "install", "-f", "-y"])
            logger.info("Chrome Remote Desktop installed successfully")
        
        def installDesktopEnvironment(self):
            logger.info("Setting up XFCE4 Desktop Environment...")
            # Configure Chrome Remote Desktop session
            run_command(["bash", "-c", 'echo "exec /etc/X11/Xsession /usr/bin/xfce4-session" | sudo tee /etc/chrome-remote-desktop-session'])
            
            # Ensure DBus is running
            run_command(["sudo", "systemctl", "enable", "dbus"])
            run_command(["sudo", "systemctl", "start", "dbus"])
            
            logger.info("XFCE4 Desktop Environment configured successfully")
        
        def installGoogleChrome(self):
            logger.info("Installing Google Chrome...")
            run_command(["wget", "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"])
            run_command(["sudo", "dpkg", "-i", "google-chrome-stable_current_amd64.deb"])
            run_command(["sudo", "apt", "install", "-f", "-y"])
            logger.info("Google Chrome installed successfully")
        
        def installTelegram(self):
            logger.info("Installing Telegram Desktop...")
            run_command(["sudo", "apt", "install", "-y", "telegram-desktop"])
            logger.info("Telegram Desktop installed successfully")
        
        def changewall(self):
            logger.info("Downloading wallpapers...")
            wallpapers = {
                "1280x1024.svg": "https://gitlab.com/chamod12/gcrd_deb_codesandbox.io_rdp/-/raw/main/walls/1280x1024.svg",
                "1280x800.svg": "https://gitlab.com/chamod12/gcrd_deb_codesandbox.io_rdp/-/raw/main/walls/1280x800.svg",
                "1600x1200.svg": "https://gitlab.com/chamod12/gcrd_deb_codesandbox.io_rdp/-/raw/main/walls/1600x1200.svg",
                "1920x1080.svg": "https://gitlab.com/chamod12/gcrd_deb_codesandbox.io_rdp/-/raw/main/walls/1920x1080.svg",
                "1920x1200.svg": "https://gitlab.com/chamod12/gcrd_deb_codesandbox.io_rdp/-/raw/main/walls/1920x1200.svg",
                "2560x1440.svg": "https://gitlab.com/chamod12/gcrd_deb_codesandbox.io_rdp/-/raw/main/walls/2560x1440.svg",
                "2560x1600.svg": "https://gitlab.com/chamod12/gcrd_deb_codesandbox.io_rdp/-/raw/main/walls/2560x1600.svg",
                "3200x1800.svg": "https://gitlab.com/chamod12/gcrd_deb_codesandbox.io_rdp/-/raw/main/walls/3200x1800.svg",
                "3200x2000.svg": "https://gitlab.com/chamod12/gcrd_deb_codesandbox.io_rdp/-/raw/main/walls/3200x2000.svg",
                "3840x2160.svg": "https://gitlab.com/chamod12/gcrd_deb_codesandbox.io_rdp/-/raw/main/walls/3840x2160.svg",
                "5120x2880.svg": "https://gitlab.com/chamod12/gcrd_deb_codesandbox.io_rdp/-/raw/main/walls/5120x2880.svg"
            }
            
            # Create wallpaper directory if it doesn't exist
            wallpaper_dir = "/usr/share/backgrounds/xfce"
            run_command(["sudo", "mkdir", "-p", wallpaper_dir])
            
            for filename, url in wallpapers.items():
                try:
                    run_command(["sudo", "curl", "-s", "-L", "-o", f"{wallpaper_dir}/{filename}", url])
                    logger.info(f"Downloaded {filename}")
                except Exception as e:
                    logger.warning(f"Failed to download {filename}: {e}")
            
            logger.info("Wallpapers downloaded successfully")
        
        def installQbit(self):
            logger.info("Installing qBittorrent...")
            run_command(["sudo", "apt", "install", "-y", "qbittorrent"])
            logger.info("qBittorrent installed successfully")
        
        def finish(self, user):
            logger.info("Finalizing setup...")
            
            if Autostart:
                autostart_dir = f"/home/{user}/.config/autostart"
                run_command(["sudo", "mkdir", "-p", autostart_dir])
                
                link = "https://www.youtube.com/@The_Disala"
                colab_autostart = f"""[Desktop Entry]
Type=Application
Name=Colab
Exec=sensible-browser {link}
Icon=
Comment=Open a predefined notebook at session signin.
X-GNOME-Autostart-enabled=true"""
                
                with open("/tmp/colab.desktop", "w") as f:
                    f.write(colab_autostart)
                
                run_command(["sudo", "mv", "/tmp/colab.desktop", f"{autostart_dir}/colab.desktop"])
                run_command(["sudo", "chown", "-R", f"{user}:{user}", f"/home/{user}/.config"])
                run_command(["sudo", "chmod", "+x", f"{autostart_dir}/colab.desktop"])
            
            # Add user to chrome-remote-desktop group
            run_command(["sudo", "usermod", "-aG", "chrome-remote-desktop", user])
            
            # Set up CRD with the provided code
            command = f"{CRD_SSH_Code} --pin={Pin}"
            run_command(["sudo", "-u", user, "bash", "-c", command])
            
            # Enable and start the service
            run_command(["sudo", "systemctl", "enable", "chrome-remote-desktop"])
            run_command(["sudo", "systemctl", "start", "chrome-remote-desktop"])
            
            # Display completion message
            print("\n" + "="*60)
            print("SETUP COMPLETED SUCCESSFULLY!")
            print("="*60)
            print(f"Username: {username}")
            print(f"Password: {password}")
            print(f"CRD PIN: {Pin}")
            print("="*60)
            print("Telegram Channel: https://t.me/TheDisala4U")
            print("YouTube Channel: https://www.youtube.com/@The_Disala")
            print("="*60)
            logger.info("CRD setup completed successfully")
    
    # Run the setup
    try:
        CRDSetup(username)
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()