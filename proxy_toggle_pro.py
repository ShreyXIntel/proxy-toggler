"""
Windows Desktop Proxy Toggle Widget - Professional Multi-Proxy Edition
Clean, crisp UI with multiple proxy profiles
"""

import tkinter as tk
from tkinter import ttk, messagebox
import winreg
import ctypes
import sys
import json
import os

# Default Proxy Configurations
DEFAULT_PROXIES = [
    {
        "name": "Office Proxy",
        "server": "http://proxy-example.corp.com:912",
        "enabled": False
    },
    {
        "name": "VPN Proxy",
        "server": "http://vpn-proxy.example.com:8080",
        "enabled": False
    }
]

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".proxy_widget_config.json")

# Windows API constants
GWL_EXSTYLE = -20
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TOOLWINDOW = 0x00000080
HWND_BOTTOM = 1
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOACTIVATE = 0x0010


class ProxyConfig:
    """Manage proxy configurations"""
    
    @staticmethod
    def load_proxies():
        """Load proxy configurations from file"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            else:
                # Create default config
                ProxyConfig.save_proxies(DEFAULT_PROXIES)
                return DEFAULT_PROXIES
        except Exception as e:
            print(f"Error loading config: {e}")
            return DEFAULT_PROXIES
    
    @staticmethod
    def save_proxies(proxies):
        """Save proxy configurations to file"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(proxies, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")


class ProxyManager:
    """Handle Windows proxy settings"""
    
    @staticmethod
    def get_current_proxy():
        """Get currently enabled proxy from Windows"""
        try:
            registry_key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
                0,
                winreg.KEY_READ
            )
            
            proxy_enable, _ = winreg.QueryValueEx(registry_key, "ProxyEnable")
            
            if proxy_enable:
                proxy_server, _ = winreg.QueryValueEx(registry_key, "ProxyServer")
                winreg.CloseKey(registry_key)
                return proxy_server
            
            winreg.CloseKey(registry_key)
            return None
            
        except Exception as e:
            print(f"Error reading proxy: {e}")
            return None
    
    @staticmethod
    def set_proxy(proxy_server):
        """Enable specific proxy"""
        try:
            registry_key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
                0,
                winreg.KEY_WRITE
            )
            
            if proxy_server:
                winreg.SetValueEx(registry_key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(registry_key, "ProxyServer", 0, winreg.REG_SZ, proxy_server)
            else:
                winreg.SetValueEx(registry_key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(registry_key, "ProxyServer", 0, winreg.REG_SZ, "")
            
            winreg.CloseKey(registry_key)
            
            # Notify system
            INTERNET_OPTION_SETTINGS_CHANGED = 39
            INTERNET_OPTION_REFRESH = 37
            internet_set_option = ctypes.windll.Wininet.InternetSetOptionW
            internet_set_option(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)
            internet_set_option(0, INTERNET_OPTION_REFRESH, 0, 0)
            
            return True
        except Exception as e:
            print(f"Error setting proxy: {e}")
            return False


class ModernToggle(tk.Canvas):
    """Modern toggle switch with smooth animation"""
    
    def __init__(self, parent, width=56, height=28, command=None):
        super().__init__(parent, width=width, height=height, 
                        bg='white', highlightthickness=0, cursor='hand2', bd=0)
        
        self.width = width
        self.height = height
        self.command = command
        self.is_on = False
        
        self.bind('<Button-1>', lambda e: self.toggle())
        self.draw()
    
    def draw(self):
        """Draw toggle with crisp rendering"""
        self.delete('all')
        
        if self.is_on:
            track_color = '#10b981'  # Modern green
            knob_x = self.width - self.height/2 - 3
        else:
            track_color = '#d1d5db'  # Light gray
            knob_x = self.height/2 + 3
        
        # Draw track
        radius = self.height / 2
        self.create_oval(2, 2, self.height-2, self.height-2, 
                        fill=track_color, outline='', width=0)
        self.create_oval(self.width-self.height+2, 2, 
                        self.width-2, self.height-2,
                        fill=track_color, outline='', width=0)
        self.create_rectangle(self.height/2, 2, 
                             self.width-self.height/2, self.height-2,
                             fill=track_color, outline='', width=0)
        
        # Draw knob
        knob_radius = (self.height - 8) / 2
        self.create_oval(knob_x - knob_radius, self.height/2 - knob_radius,
                        knob_x + knob_radius, self.height/2 + knob_radius,
                        fill='white', outline='#e5e7eb', width=1)
    
    def toggle(self):
        """Toggle state"""
        self.is_on = not self.is_on
        self.draw()
        if self.command:
            self.command()
    
    def set_state(self, state):
        """Set state programmatically"""
        if self.is_on != state:
            self.is_on = state
            self.draw()


class ProxyToggleWidget:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("")
        
        # Window setup
        self.root.overrideredirect(True)
        
        # Load proxy configurations
        self.proxies = ProxyConfig.load_proxies()
        self.proxy_toggles = {}
        
        # Dynamic height based on number of proxies
        window_width = 300
        base_height = 90
        proxy_item_height = 50
        window_height = base_height + (len(self.proxies) * proxy_item_height)
        
        # Position
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width - window_width - 20
        y = screen_height - window_height - 60
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Styling
        self.root.configure(bg='white')
        
        # Create a border frame
        self.border_frame = tk.Frame(
            self.root,
            bg='white',
            highlightbackground='#e5e7eb',
            highlightthickness=1,
            bd=0
        )
        self.border_frame.place(x=0, y=0, width=window_width, height=window_height)
        
        # Add subtle shadow effect (inner border)
        self.inner_frame = tk.Frame(
            self.border_frame,
            bg='white',
            bd=0
        )
        self.inner_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        self.setup_ui()
        self.root.after(50, self.set_window_style)
        self.update_ui()
        
    def set_window_style(self):
        """Set window to stay at desktop level"""
        try:
            hwnd = self.root.winfo_id()
            user32 = ctypes.windll.user32
            
            ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            new_style = ex_style | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
            
            user32.SetWindowPos(hwnd, HWND_BOTTOM, 0, 0, 0, 0,
                               SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)
            
            self.root.after(100, lambda: user32.SetWindowPos(
                hwnd, HWND_BOTTOM, 0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE
            ))
        except Exception as e:
            print(f"Error setting window style: {e}")
    
    def start_move(self, event):
        self.x = event.x
        self.y = event.y
    
    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.inner_frame, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)
        
        main_frame.bind('<Button-1>', self.start_move)
        main_frame.bind('<B1-Motion>', self.do_move)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='white')
        header_frame.pack(fill=tk.X, pady=(0, 12))
        header_frame.bind('<Button-1>', self.start_move)
        header_frame.bind('<B1-Motion>', self.do_move)
        
        title_label = tk.Label(
            header_frame,
            text="Proxy Settings",
            font=('Segoe UI', 11, 'bold'),
            bg='white',
            fg='#111827'
        )
        title_label.pack(side=tk.LEFT)
        title_label.bind('<Button-1>', self.start_move)
        title_label.bind('<B1-Motion>', self.do_move)
        
        # Button container for close and settings
        btn_container = tk.Frame(header_frame, bg='white')
        btn_container.pack(side=tk.RIGHT)
        
        # Settings button
        settings_btn = tk.Label(
            btn_container,
            text="⚙",
            font=('Segoe UI', 11),
            bg='white',
            fg='#6b7280',
            cursor='hand2',
            padx=4
        )
        settings_btn.pack(side=tk.LEFT, padx=(0, 4))
        settings_btn.bind('<Button-1>', lambda e: self.show_settings())
        settings_btn.bind('<Enter>', lambda e: settings_btn.config(fg='#111827'))
        settings_btn.bind('<Leave>', lambda e: settings_btn.config(fg='#6b7280'))
        
        # Close button
        close_btn = tk.Label(
            btn_container,
            text="✕",
            font=('Segoe UI', 11),
            bg='white',
            fg='#6b7280',
            cursor='hand2',
            padx=4
        )
        close_btn.pack(side=tk.LEFT)
        close_btn.bind('<Button-1>', lambda e: self.root.quit())
        close_btn.bind('<Enter>', lambda e: close_btn.config(fg='#ef4444'))
        close_btn.bind('<Leave>', lambda e: close_btn.config(fg='#6b7280'))
        
        # Separator
        sep = tk.Frame(main_frame, bg='#f3f4f6', height=1)
        sep.pack(fill=tk.X, pady=(0, 12))
        
        # Proxy list container with scrollable frame
        list_container = tk.Frame(main_frame, bg='white')
        list_container.pack(fill=tk.BOTH, expand=True)
        
        # Create proxy items
        for i, proxy in enumerate(self.proxies):
            self.create_proxy_item(list_container, proxy, i)
    
    def create_proxy_item(self, parent, proxy, index):
        """Create a proxy toggle item"""
        item_frame = tk.Frame(parent, bg='white')
        item_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Left side - Info
        info_frame = tk.Frame(item_frame, bg='white')
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Proxy name
        name_label = tk.Label(
            info_frame,
            text=proxy['name'],
            font=('Segoe UI', 10, 'bold'),
            bg='white',
            fg='#111827',
            anchor='w'
        )
        name_label.pack(anchor='w')
        
        # Proxy server (smaller, gray)
        server_label = tk.Label(
            info_frame,
            text=proxy['server'],
            font=('Segoe UI', 8),
            bg='white',
            fg='#6b7280',
            anchor='w'
        )
        server_label.pack(anchor='w', pady=(2, 0))
        
        # Right side - Toggle
        toggle = ModernToggle(
            item_frame,
            width=52,
            height=26,
            command=lambda idx=index: self.toggle_proxy(idx)
        )
        toggle.pack(side=tk.RIGHT)
        
        self.proxy_toggles[index] = toggle
    
    def toggle_proxy(self, index):
        """Toggle specific proxy on/off"""
        # Turn off all other proxies
        for i in range(len(self.proxies)):
            if i != index:
                self.proxies[i]['enabled'] = False
                self.proxy_toggles[i].set_state(False)
        
        # Toggle selected proxy
        self.proxies[index]['enabled'] = not self.proxies[index]['enabled']
        
        # Apply to Windows
        if self.proxies[index]['enabled']:
            ProxyManager.set_proxy(self.proxies[index]['server'])
        else:
            ProxyManager.set_proxy(None)
        
        # Save config
        ProxyConfig.save_proxies(self.proxies)
        
        self.update_ui()
    
    def update_ui(self):
        """Update UI based on current Windows proxy state"""
        current_proxy = ProxyManager.get_current_proxy()
        
        # Update all toggles based on current Windows proxy
        for i, proxy in enumerate(self.proxies):
            is_active = (current_proxy == proxy['server']) if current_proxy else False
            self.proxy_toggles[i].set_state(is_active)
            self.proxies[i]['enabled'] = is_active
    
    def show_settings(self):
        """Show settings dialog for managing proxies"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Proxy Settings")
        settings_window.geometry("480x520")
        settings_window.configure(bg='white')
        
        # Title
        title = tk.Label(
            settings_window,
            text="Manage Proxy Configurations",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg='#111827'
        )
        title.pack(pady=20)
        
        # Instructions
        instructions = tk.Label(
            settings_window,
            text="Click the buttons below to manage your proxy configurations.\nAdd, edit, or remove proxies from the config file.",
            font=('Segoe UI', 9),
            bg='white',
            fg='#6b7280',
            justify=tk.CENTER
        )
        instructions.pack(pady=10)
        
        # Example format - more concise
        example_frame = tk.Frame(settings_window, bg='#f9fafb', bd=1, relief=tk.SOLID)
        example_frame.pack(padx=30, pady=10, fill=tk.BOTH, expand=True)
        
        example_text = '''Config File Format (JSON):

[
  {
    "name": "Office Proxy",
    "server": "http://proxy.company.com:912",
    "enabled": false
  },
  {
    "name": "VPN Proxy", 
    "server": "http://vpn.company.com:8080",
    "enabled": false
  }
]

Tips:
• Always use "enabled": false (widget manages this)
• Include http:// and port number
• Use descriptive names'''
        
        example_label = tk.Label(
            example_frame,
            text=example_text,
            font=('Consolas', 9),
            bg='#f9fafb',
            fg='#374151',
            justify=tk.LEFT
        )
        example_label.pack(padx=15, pady=15, anchor='w')
        
        # Buttons
        btn_frame = tk.Frame(settings_window, bg='white')
        btn_frame.pack(pady=20)
        
        # Open folder button
        folder_btn = tk.Button(
            btn_frame,
            text="📁 Open Config Folder",
            font=('Segoe UI', 9, 'bold'),
            bg='#3b82f6',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2',
            command=lambda: os.startfile(os.path.dirname(CONFIG_FILE))
        )
        folder_btn.pack(pady=5, fill=tk.X, padx=50)
        
        open_btn = tk.Button(
            btn_frame,
            text="📝 Edit Config File",
            font=('Segoe UI', 9),
            bg='#10b981',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2',
            command=lambda: os.startfile(CONFIG_FILE)
        )
        open_btn.pack(pady=5, fill=tk.X, padx=50)
        
        reload_btn = tk.Button(
            btn_frame,
            text="🔄 Reload & Restart",
            font=('Segoe UI', 9),
            bg='#f59e0b',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2',
            command=lambda: self.reload_config(settings_window)
        )
        reload_btn.pack(pady=5, fill=tk.X, padx=50)
        
        # Separator
        sep = tk.Frame(settings_window, bg='#e5e7eb', height=1)
        sep.pack(fill=tk.X, pady=15, padx=50)
        
        close_btn = tk.Button(
            btn_frame,
            text="Close",
            font=('Segoe UI', 9),
            bg='#6b7280',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2',
            command=settings_window.destroy
        )
        close_btn.pack(pady=5, fill=tk.X, padx=50)
    
    def reload_config(self, settings_window):
        """Reload configuration and restart widget"""
        settings_window.destroy()
        self.root.destroy()
        # Restart
        os.execl(sys.executable, sys.executable, *sys.argv)
    
    def run(self):
        """Start the widget"""
        self.root.mainloop()


if __name__ == "__main__":
    if sys.platform != "win32":
        print("This tool only works on Windows.")
        sys.exit(1)
    
    app = ProxyToggleWidget()
    app.run()
