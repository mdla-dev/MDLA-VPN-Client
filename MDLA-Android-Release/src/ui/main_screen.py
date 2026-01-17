"""MDLA Android Main Screen"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.metrics import dp
from typing import Optional, List, Callable, Any

from .components import ServerCard, ConnectionButton, StatsPanel, AddServerDialog
from .theme import apply_theme
from ..core.core_manager import AndroidCoreManager, ConnectionState
from ..core.subscription import SubscriptionManager
from ..core.speed_test import SpeedTester
from ..core.protocol_parser import ServerConfig


class MainScreen(Screen):
    """Main application screen"""
    
    def __init__(self, core_manager: AndroidCoreManager, 
                 subscription_manager: SubscriptionManager,
                 async_runner: Callable, **kwargs):
        super().__init__(**kwargs)
        
        # Core components
        self.core_manager = core_manager
        self.subscription_manager = subscription_manager
        self.async_runner = async_runner
        
        # State
        self.selected_server: Optional[ServerConfig] = None
        self.server_cards: List[ServerCard] = []
        self.current_view = "home"
        
        # Setup callbacks
        self.core_manager.set_status_callback(self._on_status_change)
        self.core_manager.set_traffic_callback(self._on_traffic_update)
        
        # Build UI
        self._build_ui()
        
        # Load servers
        self._refresh_servers()
    
    def _build_ui(self):
        """Build the main UI"""
        # Main container
        main_layout = BoxLayout(orientation='vertical')
        
        # Header with connection status
        self._build_header(main_layout)
        
        # Navigation tabs
        self._build_navigation(main_layout)
        
        # Content area
        self.content_area = BoxLayout(orientation='vertical')
        main_layout.add_widget(self.content_area)
        
        # Stats panel at bottom
        self.stats_panel = StatsPanel()
        main_layout.add_widget(self.stats_panel)
        
        # Apply theme
        apply_theme(main_layout)
        
        self.add_widget(main_layout)
        
        # Show initial view
        self._show_home()
    
    def _build_header(self, parent):
        """Build header with connection button and status"""
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(80))
        
        # Logo and title section
        logo_section = BoxLayout(orientation='horizontal', size_hint_x=0.3)
        
        # Try to load logo
        try:
            from ..config.settings import get_logo_path
            from kivy.uix.image import Image
            
            logo_path = get_logo_path()
            if logo_path.exists():
                logo_img = Image(
                    source=str(logo_path),
                    size_hint=(None, None),
                    size=(dp(40), dp(40))
                )
                logo_section.add_widget(logo_img)
        except Exception as e:
            print(f"Could not load logo: {e}")
        
        # Title
        title_layout = BoxLayout(orientation='vertical')
        title_label = Label(
            text="MDLA",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(25),
            halign='left'
        )
        title_label.bind(size=title_label.setter('text_size'))
        title_layout.add_widget(title_label)
        
        subtitle_label = Label(
            text="VPN Manager",
            font_size=dp(10),
            size_hint_y=None,
            height=dp(15),
            halign='left'
        )
        subtitle_label.bind(size=subtitle_label.setter('text_size'))
        title_layout.add_widget(subtitle_label)
        
        logo_section.add_widget(title_layout)
        header.add_widget(logo_section)
        
        # Connection button
        self.connect_btn = ConnectionButton(on_toggle=self._on_connect_toggle)
        header.add_widget(self.connect_btn)
        
        # Server info
        info_layout = BoxLayout(orientation='vertical')
        
        server_name = self.selected_server.name if self.selected_server else "No server selected"
        server_addr = f"{self.selected_server.address}:{self.selected_server.port}" if self.selected_server else "Select a server to connect"
        
        self.selected_name = Label(
            text=server_name,
            font_size=dp(14),
            size_hint_y=None,
            height=dp(25),
            halign='left'
        )
        self.selected_name.bind(size=self.selected_name.setter('text_size'))
        info_layout.add_widget(self.selected_name)
        
        self.selected_address = Label(
            text=server_addr,
            font_size=dp(11),
            size_hint_y=None,
            height=dp(20),
            halign='left'
        )
        self.selected_address.bind(size=self.selected_address.setter('text_size'))
        info_layout.add_widget(self.selected_address)
        
        # Status
        self.status_label = Label(
            text="● Disconnected",
            font_size=dp(12),
            size_hint_y=None,
            height=dp(25)
        )
        info_layout.add_widget(self.status_label)
        
        header.add_widget(info_layout)
        parent.add_widget(header)
    
    def _build_navigation(self, parent):
        """Build navigation tabs"""
        nav_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        nav_buttons = [
            ("Home", self._show_home),
            ("Servers", self._show_servers),
            ("Stats", self._show_stats),
            ("Settings", self._show_settings),
        ]
        
        self.nav_buttons = {}
        for text, command in nav_buttons:
            btn = Button(
                text=text,
                font_size=dp(14),
                size_hint_x=1
            )
            btn.bind(on_press=lambda x, cmd=command: cmd())
            nav_layout.add_widget(btn)
            self.nav_buttons[text.lower()] = btn
        
        parent.add_widget(nav_layout)
    
    def _show_home(self):
        """Show home view"""
        self._set_active_nav("home")
        self._clear_content()
        
        # Server list with quick actions
        content = BoxLayout(orientation='vertical')
        
        # Quick actions
        actions = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        add_btn = Button(text="+ Add Server", size_hint_x=0.3)
        add_btn.bind(on_press=self._show_add_dialog)
        actions.add_widget(add_btn)
        
        refresh_btn = Button(text="🔄 Refresh", size_hint_x=0.3)
        refresh_btn.bind(on_press=lambda x: self._refresh_subscriptions())
        actions.add_widget(refresh_btn)
        
        ping_btn = Button(text="📶 Ping All", size_hint_x=0.4)
        ping_btn.bind(on_press=lambda x: self._ping_all_servers())
        actions.add_widget(ping_btn)
        
        content.add_widget(actions)
        
        # Server list
        self._build_server_list(content)
        
        self.content_area.add_widget(content)
    
    def _show_servers(self):
        """Show servers management view"""
        self._set_active_nav("servers")
        self._clear_content()
        
        content = BoxLayout(orientation='vertical')
        
        # Title
        title = Label(
            text="Server Management",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(title)
        
        # Actions
        actions = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        add_btn = Button(text="+ Add Server")
        add_btn.bind(on_press=self._show_add_dialog)
        actions.add_widget(add_btn)
        
        update_btn = Button(text="🔄 Update Subscriptions")
        update_btn.bind(on_press=lambda x: self._refresh_subscriptions())
        actions.add_widget(update_btn)
        
        content.add_widget(actions)
        
        # Subscriptions list
        subs = self.subscription_manager.get_subscriptions()
        if subs:
            sub_label = Label(
                text="Subscriptions",
                font_size=dp(16),
                size_hint_y=None,
                height=dp(30)
            )
            content.add_widget(sub_label)
            
            for sub in subs:
                sub_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
                
                sub_info = Label(
                    text=f"📁 {sub.name} ({len(sub.servers)} servers)",
                    font_size=dp(14)
                )
                sub_layout.add_widget(sub_info)
                
                delete_btn = Button(
                    text="🗑",
                    size_hint_x=None,
                    width=dp(40)
                )
                delete_btn.bind(on_press=lambda x, s=sub: self._delete_subscription(s.id))
                sub_layout.add_widget(delete_btn)
                
                content.add_widget(sub_layout)
        
        # Server list
        self._build_server_list(content)
        
        self.content_area.add_widget(content)
    
    def _show_stats(self):
        """Show statistics view"""
        self._set_active_nav("stats")
        self._clear_content()
        
        content = BoxLayout(orientation='vertical')
        
        title = Label(
            text="Traffic Statistics",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(title)
        
        # Stats cards
        stats_grid = GridLayout(cols=2, size_hint_y=None, height=dp(120))
        
        # Upload card
        upload_layout = BoxLayout(orientation='vertical')
        upload_layout.add_widget(Label(text="↑ Upload", font_size=dp(12)))
        self.upload_label = Label(text="0 B/s", font_size=dp(16))
        upload_layout.add_widget(self.upload_label)
        stats_grid.add_widget(upload_layout)
        
        # Download card
        download_layout = BoxLayout(orientation='vertical')
        download_layout.add_widget(Label(text="↓ Download", font_size=dp(12)))
        self.download_label = Label(text="0 B/s", font_size=dp(16))
        download_layout.add_widget(self.download_label)
        stats_grid.add_widget(download_layout)
        
        content.add_widget(stats_grid)
        
        # Connection info
        status = self.core_manager.status
        status_text = "Connected" if status.state == ConnectionState.CONNECTED else "Disconnected"
        
        info_label = Label(
            text=f"Status: {status_text}",
            font_size=dp(14),
            size_hint_y=None,
            height=dp(30)
        )
        content.add_widget(info_label)
        
        if self.selected_server:
            server_label = Label(
                text=f"Server: {self.selected_server.name}",
                font_size=dp(12),
                size_hint_y=None,
                height=dp(25)
            )
            content.add_widget(server_label)
        
        self.content_area.add_widget(content)
    
    def _show_settings(self):
        """Show settings view"""
        self._set_active_nav("settings")
        self._clear_content()
        
        content = BoxLayout(orientation='vertical')
        
        title = Label(
            text="Settings",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(title)
        
        # VPN Mode settings
        mode_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100))
        
        mode_label = Label(
            text="VPN Mode",
            font_size=dp(16),
            size_hint_y=None,
            height=dp(30)
        )
        mode_layout.add_widget(mode_label)
        
        # TUN mode (default for Android)
        tun_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(35))
        tun_layout.add_widget(Label(text="TUN Mode (Recommended)", font_size=dp(14)))
        
        self.tun_switch = Switch(active=True)
        self.tun_switch.bind(active=self._on_tun_toggle)
        tun_layout.add_widget(self.tun_switch)
        
        mode_layout.add_widget(tun_layout)
        content.add_widget(mode_layout)
        
        # Proxy settings
        proxy_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120))
        
        proxy_label = Label(
            text="Local Proxy",
            font_size=dp(16),
            size_hint_y=None,
            height=dp(30)
        )
        proxy_layout.add_widget(proxy_label)
        
        http_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(35))
        http_layout.add_widget(Label(text="HTTP:", font_size=dp(12), size_hint_x=0.3))
        http_input = TextInput(text="127.0.0.1:10809", font_size=dp(12), size_hint_x=0.7)
        http_layout.add_widget(http_input)
        proxy_layout.add_widget(http_layout)
        
        socks_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(35))
        socks_layout.add_widget(Label(text="SOCKS5:", font_size=dp(12), size_hint_x=0.3))
        socks_input = TextInput(text="127.0.0.1:10808", font_size=dp(12), size_hint_x=0.7)
        socks_layout.add_widget(socks_input)
        proxy_layout.add_widget(socks_layout)
        
        content.add_widget(proxy_layout)
        
        # About
        about_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80))
        
        about_title = Label(
            text="MDLA v0.1.0",
            font_size=dp(16),
            size_hint_y=None,
            height=dp(30)
        )
        about_layout.add_widget(about_title)
        
        about_desc = Label(
            text="VPN Manager for Android",
            font_size=dp(12),
            size_hint_y=None,
            height=dp(25)
        )
        about_layout.add_widget(about_desc)
        
        content.add_widget(about_layout)
        
        self.content_area.add_widget(content)
    
    def _build_server_list(self, parent):
        """Build server list component"""
        # Server list header
        list_header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
        
        servers_label = Label(
            text="Servers",
            font_size=dp(16),
            size_hint_x=0.7
        )
        list_header.add_widget(servers_label)
        
        parent.add_widget(list_header)
        
        # Scrollable server list
        scroll = ScrollView()
        server_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        server_layout.bind(minimum_height=server_layout.setter('height'))
        
        self.server_container = server_layout
        scroll.add_widget(server_layout)
        parent.add_widget(scroll)
        
        self._populate_server_list()
    
    def _populate_server_list(self):
        """Populate server list with cards"""
        # Clear existing cards
        if hasattr(self, 'server_container'):
            self.server_container.clear_widgets()
        self.server_cards.clear()
        
        # Get all servers
        servers = self.subscription_manager.get_all_servers()
        
        # Create cards
        for i, server in enumerate(servers):
            card = ServerCard(
                server_name=server.name,
                server_address=f"{server.address}:{server.port}",
                protocol=server.protocol.value,
                on_select=lambda c, s=server: self._on_server_select(c, s)
            )
            
            if hasattr(self, 'server_container'):
                self.server_container.add_widget(card)
            self.server_cards.append(card)
            
            # Restore selection
            if self.selected_server and server.address == self.selected_server.address:
                card.set_selected(True)
        
        # Show empty state if no servers
        if not servers and hasattr(self, 'server_container'):
            empty_label = Label(
                text="No servers yet.\nTap '+ Add Server' to add servers or subscriptions.",
                font_size=dp(14),
                size_hint_y=None,
                height=dp(60)
            )
            self.server_container.add_widget(empty_label)
    
    def _set_active_nav(self, view_name: str):
        """Update navigation button states"""
        self.current_view = view_name
        # TODO: Update button appearance for active state
    
    def _clear_content(self):
        """Clear content area"""
        self.content_area.clear_widgets()
    
    def _refresh_servers(self):
        """Refresh server list"""
        self._populate_server_list()
    
    def _on_server_select(self, card: ServerCard, server: ServerConfig):
        """Handle server selection"""
        # Deselect all
        for c in self.server_cards:
            c.set_selected(False)
        
        # Select this one
        card.set_selected(True)
        self.selected_server = server
        
        # Update info
        self.selected_name.text = server.name
        self.selected_address.text = f"{server.address}:{server.port} • {server.protocol.value.upper()}"
    
    def _on_connect_toggle(self, connect: bool):
        """Handle connect/disconnect"""
        if connect:
            if not self.selected_server:
                return
            
            self.connect_btn.set_state(False, connecting=True)
            self.async_runner(self._connect())
        else:
            self.connect_btn.set_state(True, connecting=False)
            self.async_runner(self._disconnect())
    
    async def _connect(self):
        """Connect to selected server"""
        if not self.selected_server:
            return
        
        success = await self.core_manager.start(
            self.selected_server.to_dict(),
            use_tun=True  # Always use TUN on Android
        )
        
        # Update UI in main thread
        Clock.schedule_once(lambda dt: self._update_connection_ui(success))
    
    async def _disconnect(self):
        """Disconnect from server"""
        await self.core_manager.stop()
        Clock.schedule_once(lambda dt: self._update_connection_ui(False))
    
    def _update_connection_ui(self, connected: bool):
        """Update UI after connection change"""
        self.connect_btn.set_state(connected)
        
        if connected:
            self.status_label.text = "● Connected"
        else:
            self.status_label.text = "● Disconnected"
    
    def _on_status_change(self, status):
        """Handle core status change"""
        def update(dt):
            if status.state == ConnectionState.CONNECTED:
                self.status_label.text = "● Connected"
                self.connect_btn.set_state(True)
            elif status.state == ConnectionState.CONNECTING:
                self.status_label.text = "● Connecting..."
            elif status.state == ConnectionState.ERROR:
                self.status_label.text = f"● Error"
                self.connect_btn.set_state(False)
            else:
                self.status_label.text = "● Disconnected"
                self.connect_btn.set_state(False)
        
        Clock.schedule_once(update)
    
    def _on_traffic_update(self, stats):
        """Handle traffic stats update"""
        def update(dt):
            from ..core.traffic_monitor import TrafficMonitor
            upload_speed = TrafficMonitor.format_speed(stats.upload_speed)
            download_speed = TrafficMonitor.format_speed(stats.download_speed)
            
            self.stats_panel.update_stats(upload_speed, download_speed)
            
            # Update stats view if visible
            if hasattr(self, 'upload_label'):
                self.upload_label.text = upload_speed
            if hasattr(self, 'download_label'):
                self.download_label.text = download_speed
        
        Clock.schedule_once(update)
    
    def _show_add_dialog(self, instance=None):
        """Show add server dialog"""
        dialog = AddServerDialog(on_add=self._on_add_server)
        dialog.open()
    
    def _on_add_server(self, add_type: str, data):
        """Handle adding server/subscription"""
        if add_type == "url":
            servers = self.subscription_manager.add_server_from_clipboard(data)
            if servers:
                self._refresh_servers()
        elif add_type == "subscription":
            sub = self.subscription_manager.add_subscription(data["name"], data["url"])
            self.async_runner(self._update_and_refresh(sub.id))
    
    async def _update_and_refresh(self, sub_id: str):
        """Update subscription and refresh UI"""
        await self.subscription_manager.update_subscription(sub_id)
        Clock.schedule_once(lambda dt: self._refresh_servers())
    
    def _refresh_subscriptions(self):
        """Refresh all subscriptions"""
        self.async_runner(self._do_refresh_subscriptions())
    
    async def _do_refresh_subscriptions(self):
        """Actually refresh subscriptions"""
        await self.subscription_manager.update_all_subscriptions()
        Clock.schedule_once(lambda dt: self._refresh_servers())
    
    def _ping_all_servers(self):
        """Ping all servers"""
        self.async_runner(self._do_ping_all())
    
    async def _do_ping_all(self):
        """Actually ping all servers"""
        servers = self.subscription_manager.get_all_servers()
        if not servers:
            return
        
        results = await SpeedTester.batch_ping([s.to_dict() for s in servers])
        
        def update_ui(dt):
            for idx, latency in results:
                if idx < len(self.server_cards):
                    lat_str = f"{latency:.0f} ms" if latency > 0 else "Timeout"
                    self.server_cards[idx].update_latency(lat_str)
        
        Clock.schedule_once(update_ui)
    
    def _delete_subscription(self, sub_id: str):
        """Delete a subscription"""
        self.subscription_manager.remove_subscription(sub_id)
        self._show_servers()  # Refresh view
    
    def _on_tun_toggle(self, instance, value):
        """Handle TUN mode toggle"""
        print(f"TUN mode: {'enabled' if value else 'disabled'}")