
"""MDLA VPN - Простая версия для Android"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput


class MDLAApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Заголовок
        title = Label(
            text='MDLA VPN Manager',
            font_size='24sp',
            size_hint_y=None,
            height='60dp'
        )
        layout.add_widget(title)
        
        # Статус
        self.status_label = Label(
            text='Disconnected',
            font_size='18sp',
            size_hint_y=None,
            height='40dp'
        )
        layout.add_widget(self.status_label)
        
        # Поле для сервера
        server_label = Label(
            text='Server URL:',
            font_size='16sp',
            size_hint_y=None,
            height='30dp'
        )
        layout.add_widget(server_label)
        
        self.server_input = TextInput(
            hint_text='vmess://... or vless://...',
            multiline=False,
            size_hint_y=None,
            height='40dp'
        )
        layout.add_widget(self.server_input)
        
        # Кнопка подключения
        self.connect_btn = Button(
            text='Connect',
            font_size='18sp',
            size_hint_y=None,
            height='50dp'
        )
        self.connect_btn.bind(on_press=self.toggle_connection)
        layout.add_widget(self.connect_btn)
        
        # Информация
        info = Label(
            text='MDLA VPN v0.1.0\nSupports: VMess, VLESS, Trojan, Shadowsocks',
            font_size='12sp',
            halign='center'
        )
        layout.add_widget(info)
        
        return layout
    
    def toggle_connection(self, instance):
        if self.connect_btn.text == 'Connect':
            # Симуляция подключения
            server_url = self.server_input.text.strip()
            if server_url:
                self.status_label.text = 'Connecting...'
                self.connect_btn.text = 'Disconnect'
                # Здесь был бы реальный код подключения
                self.status_label.text = 'Connected'
            else:
                self.status_label.text = 'Enter server URL'
        else:
            # Отключение
            self.status_label.text = 'Disconnected'
            self.connect_btn.text = 'Connect'


if __name__ == '__main__':
    MDLAApp().run()
