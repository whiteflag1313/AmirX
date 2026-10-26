#!/usr/bin/env python3
# AmirX - Advanced MSP Engine & Controller

import ctypes
import os
import urllib.request
import ssl
import random
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.core.clipboard import Clipboard
from kivy.metrics import dp

Window.clearcolor = get_color_from_hex("#0d0d0d")

CORE_LOADED = False
amirx_core = None
possible_paths = [
    os.path.join(os.path.dirname(__file__), "libs", "arm64-v8a", "libcore.so"),
    os.path.join(os.path.dirname(__file__), "libcore.so")
]

for path in possible_paths:
    if os.path.exists(path):
        try:
            amirx_core = ctypes.CDLL(path)
            amirx_core.StartCore.argtypes = [ctypes.c_char_p, ctypes.c_int]
            amirx_core.StartCore.restype = ctypes.c_int
            CORE_LOADED = True
            break
        except Exception:
            pass

FALLBACK_ARVAN_IPS = ["185.215.232.10", "194.5.192.92", "91.216.13.15", "185.204.168.20"]

class AmirXApp(App):
    def build(self):
        self.title = "AmirX - RKh-MSP Advanced Controller"

        root = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))

        header = Label(
            text="[b][color=00ccff]AmirX[/color] RKh-MSP Engine Control[/b]",
            markup=True, size_hint_y=None, height=dp(32), font_size="16sp"
        )
        root.add_widget(header)

        core_status_text = "Go Core (.so): Loaded Successfully" if CORE_LOADED else "Go Core (.so): Python Fallback Mode"
        core_color = "#00ff88" if CORE_LOADED else "#ffcc00"
        self.lbl_core = Label(
            text=core_status_text, color=get_color_from_hex(core_color),
            size_hint_y=None, height=dp(20), font_size="11sp"
        )
        root.add_widget(self.lbl_core)

        source_box = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(6))
        source_box.add_widget(Label(text="IP Pool:", size_hint_x=0.25, color=get_color_from_hex("#aaaaaa"), font_size="12sp"))
        self.spin_source = Spinner(
            text="Arvan Clean IPs (Smart Pool)",
            values=["Arvan Clean IPs (Smart Pool)", "Cloudflare Clean IPs"],
            size_hint_x=0.75,
            background_color=get_color_from_hex("#1a1a2e"), color=(1,1,1,1), font_size="12sp"
        )
        source_box.add_widget(self.spin_source)
        root.add_widget(source_box)

        config_layout = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(70), spacing=dp(2))
        config_layout.add_widget(Label(text="Base Worker Config (VLESS / WS / TLS):", size_hint_y=None, height=dp(16), color=get_color_from_hex("#00ccff"), font_size="11sp"))
        self.txt_config = TextInput(
            text="vless://your-uuid-here@194.5.192.92:443?encryption=none&security=tls&sni=long-morning-7443.amirsanaei1313.workers.dev&type=ws&host=long-morning-7443.amirsanaei1313.workers.dev&path=%2F#AmirX-MSP",
            multiline=True, size_hint_y=None, height=dp(50), font_size="10sp",
            background_color=get_color_from_hex("#1a1a2e"), foreground_color=(1,1,1,1)
        )
        config_layout.add_widget(self.txt_config)
        root.add_widget(config_layout)

        btn_box = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(8))
        self.btn_run = Button(
            text="START MSP CORE & MAP",
            background_color=get_color_from_hex("#005500"),
            color=get_color_from_hex("#00ff88"), bold=True, font_size="13sp"
        )
        self.btn_run.bind(on_press=self.start_msp_engine)
        btn_box.add_widget(self.btn_run)
        root.add_widget(btn_box)

        self.lbl_status = Label(
            text="Ready to initialize AmirX Tunnel...",
            color=get_color_from_hex("#888888"), size_hint_y=None, height=dp(25), font_size="11sp"
        )
        root.add_widget(self.lbl_status)

        output_layout = BoxLayout(orientation="vertical", spacing=dp(2))
        output_layout.add_widget(Label(text="Final Mapped Config (For v2rayNG / TUN):", size_hint_y=None, height=dp(18), color=get_color_from_hex("#00ff88"), font_size="11sp", halign="left"))
        
        self.txt_output = TextInput(
            text="", readonly=True, multiline=True, font_size="10sp",
            background_color=get_color_from_hex("#111118"), foreground_color=get_color_from_hex("#00ccff")
        )
        output_layout.add_widget(self.txt_output)
        root.add_widget(output_layout)

        return root

    def start_msp_engine(self, *args):
        raw_config = self.txt_config.text.strip()
        if not raw_config:
            self.show_popup("Error", "Please enter base worker config!")
            return

        self.lbl_status.text = "Fetching clean IP from pool..."
        self.lbl_status.color = get_color_from_hex("#ffcc00")

        ip_lines = []
        try:
            url = "https://raw.githubusercontent.com/yebekhe/ArvanFilterBypasser/main/ips.txt"
            ctx_ssl = ssl._create_unverified_context()
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx_ssl, timeout=4) as response:
                content = response.read().decode('utf-8')
                ip_lines = [line.strip() for line in content.splitlines() if line.strip() and not line.startswith("#")]
        except Exception:
            pass

        if not ip_lines:
            ip_lines = FALLBACK_ARVAN_IPS

        clean_ip = random.choice(ip_lines)

        try:
            parts = raw_config.split("vless://")[1].split("#")
            main_part = parts[0]
            tag = f"#{parts[1]}" if len(parts) > 1 else "#AmirX-MSP"
            
            user_host_query = main_part.split("@")
            user_info = user_host_query[0]
            host_query = user_host_query[1].split("?")
            
            server_port = host_query[0]
            query_str = host_query[1] if len(host_query) > 1 else ""
            
            port = "443"
            if ":" in server_port:
                port = server_port.split(":")[1]

            new_server_port = f"{clean_ip}:{port}"
            final_config = f"vless://{user_info}@{new_server_port}?{query_str}{tag}"
            
            self.txt_output.text = final_config
            Clipboard.copy(final_config)

            if CORE_LOADED and amirx_core:
                res = amirx_core.StartCore(final_config.encode('utf-8'), 10808)
                if res == 0:
                    self.lbl_status.text = f"AmirX Core Active! IP: {clean_ip} (TUN Ready)"
                else:
                    self.lbl_status.text = f"Mapped OK, Core warning with IP: {clean_ip}"
            else:
                self.lbl_status.text = f"Success! IP Mapped: {clean_ip} (Copied)"

            self.lbl_status.color = get_color_from_hex("#00ff88")
            self.show_popup("Success", f"AmirX RKh-MSP Config Generated!\n\nClean IP: {clean_ip}\n\nCopied to Clipboard!")

        except Exception as e:
            self.show_popup("Error", f"Failed to build config: {str(e)}")

    def show_popup(self, title, msg):
        content = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
        content.add_widget(Label(text=msg, color=(1,1,1,1), font_size="13sp", halign="center"))
        btn = Button(text="OK", size_hint_y=None, height=dp(40), background_color=get_color_from_hex("#005500"))
        content.add_widget(btn)
        popup = Popup(title=title, content=content, size_hint=(0.85, 0.35), background_color=get_color_from_hex("#1a1a2e"))
        btn.bind(on_press=popup.dismiss)
        popup.open()

if __name__ == "__main__":
    AmirXApp().run()

