"""MDLA Android UI Components"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.metrics import dp
from typing import Callable, Optional, Any

from ..config.settings import COLORS


class ServerCard(BoxLayout):
    """Server card component"""
    
    def __init__(self, server_name: str, server_address: str, protocol: str,
                 on_select: Callable[['ServerCard'], None], **kwargs):
        super().__init__(orientation='vertical', size_hint_y=None, height=dp(80), **kwargs)
        
        self.on_select = on_select
        self.selected = False
        
        # Main info
        info_layout = BoxLayout(orientation='horizontal')
        
        # Server details
        details_layout = BoxLayout(orientation='vertical')
        
        self.name_label = Label(
            text=server_name,
            font_size=dp(14),
            size_hint_y=None,
            height=dp(25),
            halign='left'
        )
        self.name_label.bind(size=self.name_label.setter('text_size'))
        details_layout.add_widget(self.name_label)
        
        self.address_label = Label(
            text=f"{server_address} • {protocol.upper()}",
            font_size=dp(11),
            size_hint_y=None,
            height=dp(20),
            halign='left'
        )
        self.address_label.bind(size=self.address_label.setter('text_size'))
        details_layout.add_widget(self.address_label)
        
        info_layout.add_widget(details_layout)
        
        # Latency
        self.latency_label = Label(
            text="",
            font_size=dp(12),
            size_hint_x=None,
            width=dp(80),
            halign='right'
        )
        info_layout.add_widget(self.latency_label)
        
        self.add_widget(info_layout)
        
        # Make clickable
        self.bind(on_touch_down=self._on_touch)
    
    def _on_touch(self, instance, touch):
        """Handle touch events"""
        if self.collide_point(*touch.pos):
            self.on_select(self)
            return True
        return False
    
    def set_selected(self, selected: bool):
        """Set selection state"""
        self.selected = selected
        # TODO: Update visual appearance
    
    def update_latency(self, latency: str):
        """Update latency display"""
        self.latency_label.text = latency


class ConnectionButton(Button):
    """Connection toggle button"""
    
    def __init__(self, on_toggle: Callable[[bool], None], **kwargs):
        super().__init__(
            text="Connect",
            font_size=dp(16),
            size_hint=(None, None),
            size=(dp(120), dp(50)),
            **kwargs
        )
        
        self.on_toggle = on_toggle
        self.connected = False
        self.connecting = False
        
        self.bind(on_press=self._on_press)
    
    def _on_press(self, instance):
        """Handle button press"""
        if self.connecting:
            return
        
        self.on_toggle(not self.connected)
    
    def set_state(self, connected: bool, connecting: bool = False):
        """Set button state"""
        self.connected = connected
        self.connecting = connecting
        
        if connecting:
            self.text = "Connecting..."
            self.disabled = True
        elif connected:
            self.text = "Disconnect"
            self.disabled = False
        else:
            self.text = "Connect"
            self.disabled = False


class StatsPanel(BoxLayout):
    """Traffic statistics panel"""
    
    def __init__(self, **kwargs):
        super().__init__(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            **kwargs
        )
        
        # Upload
        upload_layout = BoxLayout(orientation='horizontal')
        upload_layout.add_widget(Label(text="↑", font_size=dp(12), size_hint_x=None, width=dp(20)))
        self.upload_label = Label(text="0 B/s", font_size=dp(11))
        upload_layout.add_widget(self.upload_label)
        self.add_widget(upload_layout)
        
        # Download
        download_layout = BoxLayout(orientation='horizontal')
        download_layout.add_widget(Label(text="↓", font_size=dp(12), size_hint_x=None, width=dp(20)))
        self.download_label = Label(text="0 B/s", font_size=dp(11))
        download_layout.add_widget(self.download_label)
        self.add_widget(download_layout)
    
    def update_stats(self, upload_speed: str, download_speed: str):
        """Update traffic statistics"""
        self.upload_label.text = upload_speed
        self.download_label.text = download_speed


class AddServerDialog(Popup):
    """Dialog for adding servers or subscriptions"""
    
    def __init__(self, on_add: Callable[[str, Any], None], **kwargs):
        super().__init__(
            title="Add Server",
            size_hint=(0.9, 0.7),
            **kwargs
        )
        
        self.on_add = on_add
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', spacing=dp(10))
        
        # Tabs
        tabs = TabbedPanel(do_default_tab=False)
        
        # URL tab
        url_tab = TabbedPanelItem(text='Server URL')
        url_layout = BoxLayout(orientation='vertical', spacing=dp(10))
        
        url_layout.add_widget(Label(
            text="Paste server URL or multiple URLs (one per line):",
            font_size=dp(12),
            size_hint_y=None,
            height=dp(30)
        ))
        
        self.url_input = TextInput(
            multiline=True,
            hint_text="vmess://...\nvless://...\ntrojan://...",
            font_size=dp(12)
        )
        url_layout.add_widget(self.url_input)
        
        url_btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        
        url_add_btn = Button(text="Add Servers", font_size=dp(14))
        url_add_btn.bind(on_press=self._add_from_url)
        url_btn_layout.add_widget(url_add_btn)
        
        url_layout.add_widget(url_btn_layout)
        url_tab.add_widget(url_layout)
        tabs.add_widget(url_tab)
        
        # Subscription tab
        sub_tab = TabbedPanelItem(text='Subscription')
        sub_layout = BoxLayout(orientation='vertical', spacing=dp(10))
        
        sub_layout.add_widget(Label(
            text="Add subscription URL:",
            font_size=dp(12),
            size_hint_y=None,
            height=dp(30)
        ))
        
        # Name input
        name_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        name_layout.add_widget(Label(text="Name:", font_size=dp(12), size_hint_x=0.3))
        self.name_input = TextInput(
            hint_text="My Subscription",
            font_size=dp(12),
            size_hint_x=0.7
        )
        name_layout.add_widget(self.name_input)
        sub_layout.add_widget(name_layout)
        
        # URL input
        url_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        url_layout.add_widget(Label(text="URL:", font_size=dp(12), size_hint_x=0.3))
        self.sub_url_input = TextInput(
            hint_text="https://...",
            font_size=dp(12),
            size_hint_x=0.7
        )
        url_layout.add_widget(self.sub_url_input)
        sub_layout.add_widget(url_layout)
        
        sub_btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        
        sub_add_btn = Button(text="Add Subscription", font_size=dp(14))
        sub_add_btn.bind(on_press=self._add_subscription)
        sub_btn_layout.add_widget(sub_add_btn)
        
        sub_layout.add_widget(sub_btn_layout)
        sub_tab.add_widget(sub_layout)
        tabs.add_widget(sub_tab)
        
        main_layout.add_widget(tabs)
        
        # Close button
        close_btn = Button(
            text="Close",
            font_size=dp(14),
            size_hint_y=None,
            height=dp(40)
        )
        close_btn.bind(on_press=self.dismiss)
        main_layout.add_widget(close_btn)
        
        self.content = main_layout
    
    def _add_from_url(self, instance):
        """Add servers from URL input"""
        url_text = self.url_input.text.strip()
        if url_text:
            self.on_add("url", url_text)
            self.dismiss()
    
    def _add_subscription(self, instance):
        """Add subscription"""
        name = self.name_input.text.strip()
        url = self.sub_url_input.text.strip()
        
        if name and url:
            self.on_add("subscription", {"name": name, "url": url})
            self.dismiss()