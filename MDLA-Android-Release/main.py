"""MDLA Android - Main Application Entry Point"""
import asyncio
import threading
from pathlib import Path

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.clock import Clock
from kivy.logger import Logger

from src.ui.main_screen import MainScreen
from src.core.core_manager import AndroidCoreManager
from src.core.subscription import SubscriptionManager
from src.config.settings import setup_android_paths


class MDLAApp(App):
    """Main MDLA Android Application"""
    
    def __init__(self):
        super().__init__()
        self.title = "MDLA VPN"
        
        # Setup Android paths
        setup_android_paths()
        
        # Core components
        self.core_manager = AndroidCoreManager()
        self.subscription_manager = SubscriptionManager()
        
        # Async loop for background tasks
        self._loop = asyncio.new_event_loop()
        self._async_thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self._async_thread.start()
    
    def build(self):
        """Build the main UI"""
        # Screen manager
        sm = ScreenManager()
        
        # Main screen
        main_screen = MainScreen(
            name='main',
            core_manager=self.core_manager,
            subscription_manager=self.subscription_manager,
            async_runner=self._run_async
        )
        sm.add_widget(main_screen)
        
        return sm
    
    def _run_async_loop(self):
        """Run async event loop in background thread"""
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()
    
    def _run_async(self, coro):
        """Run coroutine in background thread"""
        return asyncio.run_coroutine_threadsafe(coro, self._loop)
    
    def on_stop(self):
        """Called when app is closing"""
        # Stop VPN if running
        if hasattr(self, 'core_manager'):
            self._run_async(self.core_manager.stop())
        
        # Stop async loop
        if hasattr(self, '_loop'):
            self._loop.call_soon_threadsafe(self._loop.stop)


if __name__ == '__main__':
    MDLAApp().run()