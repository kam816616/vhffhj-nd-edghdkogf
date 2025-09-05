import os
import subprocess
import socket

# Configuration
username = "user"  # @param {type:"string"}
password = "root"  # @param {type:"string"}
rdp_port = 3389  # @param {type:"integer"}

# Create user and set password
os.system(f"useradd -m {username}")
os.system(f"adduser {username} sudo")
os.system(f"echo '{username}:{password}' | sudo chpasswd")
os.system("sed -i 's/\/bin\/sh/\/bin\/bash/g' /etc/passwd")

class XRDPSetup:
    def __init__(self, user):
        print("Starting XRDP Remote Desktop Setup...")
        os.system("apt update")
        self.installDesktopEnvironment()
        self.installXRDP()
        self.configureXRDP(user)
        self.installGoogleChrome()
        self.installQbit()
        self.configureFirewall()
        self.finish(user)

    @staticmethod
    def installDesktopEnvironment():
        print("Installing XFCE4 Desktop Environment...")
        os.system("export DEBIAN_FRONTEND=noninteractive")
        os.system("apt install --assume-yes xfce4 xfce4-goodies desktop-base xfce4-terminal")
        os.system("apt install --assume-yes dbus-x11")
        
        # Remove conflicting packages
        os.system("apt remove --assume-yes gnome-terminal")
        os.system("sudo service lightdm stop")
        os.system("service dbus start")
        print("XFCE4 Desktop Environment installed successfully!")

    @staticmethod
    def installXRDP():
        print("Installing XRDP...")
        os.system("apt install --assume-yes xrdp")
        os.system("apt install --assume-yes xorgxrdp")
        
        # Enable XRDP service
        os.system("systemctl enable xrdp")
        print("XRDP installed successfully!")

    @staticmethod
    def configureXRDP(user):
        print("Configuring XRDP...")
        
        # Configure XRDP to use XFCE4
        xrdp_startwm_content = """#!/bin/sh
# xrdp X session start script (c) 2015, 2017 mirabilos
# published under The MirOS Licence

if test -r /etc/profile; then
        . /etc/profile
fi

if test -r /etc/default/locale; then
        . /etc/default/locale
        test -z "${LANG+x}" || export LANG
        test -z "${LANGUAGE+x}" || export LANGUAGE
        test -z "${LC_ADDRESS+x}" || export LC_ADDRESS
        test -z "${LC_ALL+x}" || export LC_ALL
        test -z "${LC_COLLATE+x}" || export LC_COLLATE
        test -z "${LC_CTYPE+x}" || export LC_CTYPE
        test -z "${LC_IDENTIFICATION+x}" || export LC_IDENTIFICATION
        test -z "${LC_MEASUREMENT+x}" || export LC_MEASUREMENT
        test -z "${LC_MESSAGES+x}" || export LC_MESSAGES
        test -z "${LC_MONETARY+x}" || export LC_MONETARY
        test -z "${LC_NAME+x}" || export LC_NAME
        test -z "${LC_NUMERIC+x}" || export LC_NUMERIC
        test -z "${LC_PAPER+x}" || export LC_PAPER
        test -z "${LC_TELEPHONE+x}" || export LC_TELEPHONE
        test -z "${LC_TIME+x}" || export LC_TIME
fi

if test -r /etc/profile; then
        . /etc/profile
fi

xfce4-session
"""
        
        # Write startwm.sh configuration
        with open("/etc/xrdp/startwm.sh", "w") as f:
            f.write(xrdp_startwm_content)
        os.system("chmod +x /etc/xrdp/startwm.sh")
        
        # Create .xsession for user
        with open(f"/home/{user}/.xsession", "w") as f:
            f.write("xfce4-session\n")
        os.system(f"chown {user}:{user} /home/{user}/.xsession")
        os.system(f"chmod +x /home/{user}/.xsession")
        
        # Configure xrdp.ini for better performance
        os.system("cp /etc/xrdp/xrdp.ini /etc/xrdp/xrdp.ini.bak")
        
        xrdp_ini_additions = """
# Performance optimizations
tcp_keepalive=true
tcp_send_buffer_bytes=32768
tcp_recv_buffer_bytes=32768
"""
        
        with open("/etc/xrdp/xrdp.ini", "a") as f:
            f.write(xrdp_ini_additions)
            
        print("XRDP configured successfully!")

    @staticmethod
    def installGoogleChrome():
        print("Installing Google Chrome...")
        subprocess.run(["wget", "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"])
        subprocess.run(["dpkg", "--install", "google-chrome-stable_current_amd64.deb"])
        subprocess.run(['apt', 'install', '--assume-yes', '--fix-broken'])
        print("Google Chrome installed successfully!")

    @staticmethod
    def changeWallpaper():
        print("Setting up wallpapers...")
        # Create wallpaper directory
        os.system("mkdir -p /usr/share/pixmaps/wallpapers")
        
        # Download wallpapers
        wallpaper_urls = [
            "https://gitlab.com/chamod12/gcrd_deb_codesandbox.io_rdp/-/raw/main/walls/1920x1080.svg",
            "https://gitlab.com/chamod12/gcrd_deb_codesandbox.io_rdp/-/raw/main/walls/1920x1200.svg"
        ]
        
        for i, url in enumerate(wallpaper_urls):
            os.system(f"curl -s -L -o /usr/share/pixmaps/wallpapers/wallpaper_{i+1}.svg {url}")
            
        print("Wallpapers downloaded successfully!")

    @staticmethod
    def installQbit():
        print("Installing qBittorrent...")
        subprocess.run(["sudo", "apt", "update"])
        subprocess.run(["sudo", "apt", "install", "-y", "qbittorrent"])
        print("qBittorrent installed successfully!")

    @staticmethod
    def configureFirewall():
        print("Configuring firewall for RDP...")
        # Install ufw if not present
        os.system("apt install --assume-yes ufw")
        
        # Allow RDP port
        os.system(f"ufw allow {rdp_port}/tcp")
        
        # Enable firewall
        os.system("ufw --force enable")
        print("Firewall configured for RDP access!")

    @staticmethod
    def getServerIP():
        try:
            # Get server IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "localhost"

    def finish(self, user):
        print("Finalizing setup...")
        
        # Add user to ssl-cert group (required for XRDP)
        os.system(f"adduser {user} ssl-cert")
        
        # Restart XRDP service
        os.system("systemctl restart xrdp")
        os.system("systemctl start xrdp")
        
        # Get server IP
        server_ip = self.getServerIP()
        
        print("\n" + "="*60)
        print("🎉 XRDP REMOTE DESKTOP SETUP COMPLETED! 🎉")
        print("="*60)
        print(f"Server IP Address: {server_ip}")
        print(f"RDP Port: {rdp_port}")
        print(f"Username: {user}")
        print(f"Password: {password}")
        print("="*60)
        print("\n📋 CONNECTION INSTRUCTIONS:")
        print("1. Open Remote Desktop Connection on Windows")
        print(f"2. Enter computer: {server_ip}:{rdp_port}")
        print(f"3. Username: {user}")
        print(f"4. Password: {password}")
        print("\n🐧 For Linux clients:")
        print(f"   rdesktop -u {user} -p {password} {server_ip}:{rdp_port}")
        print("\n🍎 For Mac clients:")
        print("   Use Microsoft Remote Desktop app from App Store")
        print("\n⚠️  SECURITY NOTES:")
        print("- Change the default password immediately")
        print("- Consider using key-based authentication")
        print("- Restrict RDP access to trusted IP ranges")
        print("="*60)
        print("\n🔧 Troubleshooting:")
        print("- Check XRDP status: sudo systemctl status xrdp")
        print("- Restart XRDP: sudo systemctl restart xrdp")
        print("- Check logs: sudo journalctl -u xrdp")
        print("="*60)
        
        # Keep the script running to show status
        print("\n✅ XRDP service is running. You can now connect remotely!")
        print("Press Ctrl+C to exit this script (XRDP will continue running)")
        
        try:
            while True:
                import time
                time.sleep(60)
                # Check if XRDP is still running
                result = subprocess.run(["systemctl", "is-active", "xrdp"], 
                                      capture_output=True, text=True)
                if result.stdout.strip() != "active":
                    print("⚠️  XRDP service stopped. Restarting...")
                    os.system("systemctl start xrdp")
        except KeyboardInterrupt:
            print("\n👋 Setup script ended. XRDP service continues running in background.")

# Main execution
try:
    if len(password) < 4:
        print("❌ Please use a password with at least 4 characters")
    else:
        XRDPSetup(username)
except Exception as e:
    print(f"❌ Setup failed with error: {e}")
    print("Please check the logs and try again.")