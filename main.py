import asyncio
import threading
import websockets
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import mainthread, Clock

from main_websocket import main_socket

SERVER_URI = "ws://localhost:8765"

class AsyncApp(App):

    def build(self):
        main_layout = BoxLayout(orientation='horizontal')
        self.menu_layout = BoxLayout(orientation='vertical', size_hint=(0.2, 1))
        self.menu_buttons = [
            ('Создать задачу', self.show_create_task),
            ('Мои задачи', self.show_tasks),
            ('Настройки', self.show_settings),
            ('Личный кабинет', self.show_profile),
            ('Помощь', self.show_help)
        ]

        for text, func in self.menu_buttons:
            button = Button(text=text, size_hint_y=None, height=40)
            button.bind(on_press=func)
            self.menu_layout.add_widget(button)

        self.display_frame = BoxLayout(orientation='vertical', size_hint=(0.8, 1))
        self.label = Label(text="Waiting for async task...")
        self.display_frame.add_widget(self.label)

        main_layout.add_widget(self.menu_layout)
        main_layout.add_widget(self.display_frame)

        self.ws = None
        self.task_text = ""
        self.is_connected = False

        self.loop = asyncio.new_event_loop() # Создаем новый поток
        threading.Thread(target=self.start_async_loop, daemon=True).start() # Запускаем асинхронный поток

        return main_layout

    def start_async_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.initialize_websocket())

    async def initialize_websocket(self):
        try:
            self.ws = await websockets.connect(SERVER_URI)
            self.is_connected = True
            await self.listen_for_messages()
        except Exception as e:
            print(f"Ошибка подключения к WebSocket: {e}")

    async def listen_for_messages(self):
        try:
            async for message in self.ws:
                self.update_label(message)
        except websockets.ConnectionClosed as e:
            print(f"Соединение закрыто: {e}")
            self.is_connected = False
            await self.initialize_websocket()


    async def send_message(self, message):
        if self.is_connected and self.ws:
            try:
                await self.ws.send(message)
            except websockets.ConnectionClosedError as e:
                print(f"Ошибка отправки сообщения: Соединение было закрыто {e.code}: {e.reason}")
                self.is_connected = False
            except Exception as e:
                print(f"Ошибка отправки сообщения: {e}")
        else:
            print('WebSocket не подключен или соединение было закрыто')


    @mainthread
    def update_label(self, message):
        self.label.text = message


    def show_create_task(self, instance):
        self.display_frame.clear_widgets()

        task_name_label = Label(text="Название задачи:", font_size='20sp')
        self.task_name_input = TextInput(multiline=False, size_hint_y=None, height=40)

        create_button = Button(text="Создать задачу", size_hint_y=None, height=40)
        create_button.bind(on_press=self.create_task)

        self.display_frame.add_widget(task_name_label)
        self.display_frame.add_widget(self.task_name_input)
        self.display_frame.add_widget(create_button)


    def create_task(self, instance):
        self.task_text = self.task_name_input.text
        if self.task_text:
            asyncio.run_coroutine_threadsafe(self.send_message(self.task_text), self.loop)
            self.show_tasks(None)
        else:
            print('Введите текст задачи')


    def show_tasks(self, instance):
        self.display_frame.clear_widgets()
        self.label = Label(text=f"Текст задачи: {self.task_text}", font_size='20sp')
        self.display_frame.add_widget(self.label)

    def show_settings(self, instance):
        self.display_frame.clear_widgets()
        self.label = Label(text="Settings Screen", font_size='20sp')
        self.display_frame.add_widget(self.label)

    def show_profile(self, instance):
        self.display_frame.clear_widgets()
        self.label = Label(text="Profile Screen", font_size='20sp')
        self.display_frame.add_widget(self.label)

    def show_help(self, instance):
        self.display_frame.clear_widgets()
        self.label = Label(text="Help Screen", font_size='20sp')
        self.display_frame.add_widget(self.label)


if __name__ == '__main__':
    # Запуск WebSocket сервера в отдельном потоке
    def start_websocket():
        asyncio.run(main_socket())

    websocket_thread = threading.Thread(target=start_websocket, daemon=True)
    websocket_thread.start()

    # Запуск Kivy приложения
    AsyncApp().run()