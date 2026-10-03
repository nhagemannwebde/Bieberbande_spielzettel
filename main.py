import json
import os

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.graphics import Rectangle, Color

# Tastatur-Verhalten
Window.softinput_mode = 'below_target'

# Farbschema mit 50 % Transparenz (Hex '80' am Ende)
COLOR_BG_INPUT = get_color_from_hex('#31324480')
COLOR_TEXT = get_color_from_hex('#000000')
COLOR_PRIMARY = get_color_from_hex('#89b4fa80')
COLOR_SUCCESS = get_color_from_hex('#a6e3a180')
COLOR_SECONDARY = get_color_from_hex('#45475a')
COLOR_DANGER = get_color_from_hex('#f38ba880')
COLOR_TEXT_DARK = get_color_from_hex('#000000')

DATA_FILE = 'bieberbande_data.json'
BG_IMAGE = 'bieberbande_bg.png'


def load_game_data():
    """Lädt die Einstellungen oder startet mit leeren Werten."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "last_count": 3,
        "known_players": []
    }


def save_game_data(count, current_players):
    """Speichert die Anzahl und ergänzt neue Spielernamen."""
    data = load_game_data()
    data["last_count"] = count

    known_set = set(data.get("known_players", []))
    for name in current_players:
        if name.strip():
            known_set.add(name.strip())

    data["known_players"] = sorted(list(known_set))

    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Fehler beim Speichern: {e}")


class DarkSpinnerOption(SpinnerOption):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = COLOR_SECONDARY
        self.color = COLOR_TEXT
        self.bold = True  # SpinnerOption ist ein Button und unterstützt bold=True


class CenteredTextInput(TextInput):
    def __init__(self, **kwargs):
        kwargs.setdefault('background_normal', '')
        kwargs.setdefault('background_color', COLOR_BG_INPUT)
        kwargs.setdefault('foreground_color', COLOR_TEXT)
        kwargs.setdefault('cursor_color', COLOR_TEXT)
        # Fette Schrift für TextInput über Kivys integrierte Schriftart:
        kwargs.setdefault('font_name', 'Roboto-Bold')
        super().__init__(**kwargs)
        self.bind(size=self._update_padding, line_height=self._update_padding)

    def _update_padding(self, *args):
        padding_top = (self.height - self.line_height) / 2
        self.padding_y = [max(0, padding_top), 0]


class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Hintergrundbild mit Absicherung
        with self.canvas.before:
            Color(1, 1, 1, 1)
            if os.path.exists(BG_IMAGE):
                self.bg_rect = Rectangle(source=BG_IMAGE, pos=self.pos, size=self.size)
            else:
                self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.data = load_game_data()

        layout = BoxLayout(orientation='vertical', padding=20, spacing=12)

        # 1. Überschrift
        layout.add_widget(Label(
            text="Bieberbande - Einstellungen",
            font_size='24sp',
            color=COLOR_TEXT,
            bold=True,
            size_hint_y=None,
            height='50dp'
        ))

        # 2. Auswahl der Spieleranzahl über Spinner (feste Höhe 48dp)
        count_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='48dp', spacing=10)
        count_layout.add_widget(Label(text="Anzahl Spieler:", color=COLOR_TEXT, bold=True))

        last_count = self.data.get("last_count", 3)
        last_count_str = str(max(2, min(6, last_count)))

        self.count_spinner = Spinner(
            text=last_count_str,
            values=["2", "3", "4", "5", "6"],
            size_hint_x=0.5,
            background_normal='',
            background_color=COLOR_SECONDARY,
            color=COLOR_TEXT,
            font_size='18sp',
            bold=True,
            option_cls=DarkSpinnerOption
        )
        self.count_spinner.bind(text=self.generate_name_inputs)
        
        count_layout.add_widget(self.count_spinner)
        layout.add_widget(count_layout)

        # 3. Dynamischer Container für Namensfelder
        self.names_container = BoxLayout(
            orientation='vertical',
            spacing=8,
            size_hint_y=None
        )
        self.names_container.bind(minimum_height=self.names_container.setter('height'))
        layout.add_widget(self.names_container)

        # 4. Platzhalter: Nimmt den übrigen Raum ein
        layout.add_widget(Widget(size_hint_y=1))

        # 5. Bottom-Buttons (feste Höhe 50dp)
        bottom_buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp', spacing=10)

        start_btn = Button(
            text="Spiel starten",
            size_hint_x=0.7,
            background_normal='',
            background_color=COLOR_SUCCESS,
            color=COLOR_TEXT_DARK,
            font_size='18sp',
            bold=True
        )
        start_btn.bind(on_press=self.start_game)

        exit_btn = Button(
            text="Beenden",
            size_hint_x=0.3,
            background_normal='',
            background_color=COLOR_DANGER,
            color=COLOR_TEXT_DARK,
            font_size='16sp',
            bold=True
        )
        exit_btn.bind(on_press=lambda x: App.get_running_app().stop())

        bottom_buttons.add_widget(start_btn)
        bottom_buttons.add_widget(exit_btn)
        layout.add_widget(bottom_buttons)

        self.add_widget(layout)
        self.generate_name_inputs(None)

    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def generate_name_inputs(self, instance, *args):
        self.names_container.clear_widgets()
        self.data = load_game_data()
        known_players = self.data.get("known_players", [])

        try:
            count = int(self.count_spinner.text)
            count = max(2, min(6, count))
        except ValueError:
            count = 3

        self.name_inputs = []

        for i in range(count):
            row = BoxLayout(orientation='horizontal', spacing=8, size_hint_y=None, height='48dp')

            row.add_widget(Label(text=f"S{i + 1}:", size_hint_x=0.2, color=COLOR_TEXT, bold=True))

            ti = CenteredTextInput(
                hint_text=f"Spieler {i + 1}",
                multiline=False,
                font_size='16sp',
                halign='center',
                size_hint_x=0.45
            )
            self.name_inputs.append(ti)

            spinner_values = known_players if known_players else ["(Keine Namen)"]

            spinner = Spinner(
                text="Name wählen",
                values=spinner_values,
                size_hint_x=0.35,
                background_normal='',
                background_color=COLOR_SECONDARY,
                color=COLOR_TEXT,
                bold=True,
                option_cls=DarkSpinnerOption
            )

            def on_spinner_select(spinner_instance, selected_text, input_field=ti):
                if selected_text in known_players:
                    input_field.text = selected_text
                    spinner_instance.text = "Name wählen"

            spinner.bind(text=on_spinner_select)

            row.add_widget(spinner)
            row.add_widget(ti)
            self.names_container.add_widget(row)

    def start_game(self, instance):
        player_names = [ti.text.strip() or f"Spieler {i+1}" for i, ti in enumerate(self.name_inputs)]
        count = len(player_names)

        save_game_data(count, player_names)

        score_screen = self.manager.get_screen('score')
        score_screen.setup_board(player_names)
        self.manager.current = 'score'


class ScoreScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(1, 1, 1, 1)
            if os.path.exists(BG_IMAGE):
                self.bg_rect = Rectangle(source=BG_IMAGE, pos=self.pos, size=self.size)
            else:
                self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def setup_board(self, player_names):
        self.clear_widgets()

        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=6)

        # Header
        header_row = BoxLayout(orientation='horizontal', size_hint_y=0.25)
        header_btn = Button(
            text="Bieberbande",
            background_normal='',
            background_color=COLOR_SECONDARY,
            color=COLOR_TEXT,
            font_size='20sp',
            bold=True
        )
        header_row.add_widget(header_btn)
        main_layout.add_widget(header_row)

        spieler_anzahl = len(player_names)

        # Kopfzeile mit Spielernamen & Zurück-Button
        title_row = BoxLayout(orientation='horizontal', spacing=4)

        exit_btn = Button(
            text='<',
            size_hint_x=0.8,
            background_normal='',
            background_color=COLOR_DANGER,
            color=COLOR_TEXT_DARK,
            bold=True
        )
        exit_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'start'))
        title_row.add_widget(exit_btn)

        for name in player_names:
            btn = Button(
                text=name,
                background_normal='',
                background_color=COLOR_PRIMARY,
                color=COLOR_TEXT_DARK,
                bold=True
            )
            title_row.add_widget(btn)
        main_layout.add_widget(title_row)

        self.player_inputs = [[] for _ in range(spieler_anzahl)]
        self.result_buttons = []

        # Runden-Zeilen
        for runde in range(6):
            row_layout = BoxLayout(orientation='horizontal', spacing=4)

            round_btn = Button(
                text=f'Runde {runde + 1}',
                size_hint_x=0.8,
                background_normal='',
                background_color=COLOR_SECONDARY,
                color=COLOR_TEXT,
                bold=True
            )
            row_layout.add_widget(round_btn)

            for s in range(spieler_anzahl):
                ti = CenteredTextInput(
                    input_filter='int',
                    multiline=False,
                    font_size='20sp',
                    halign='center'
                )
                self.player_inputs[s].append(ti)
                row_layout.add_widget(ti)

            main_layout.add_widget(row_layout)

        # Ergebniszeile
        result_row = BoxLayout(orientation='horizontal', spacing=4)

        calc_btn = Button(
            text='Ergebnis',
            size_hint_x=0.8,
            background_normal='',
            background_color=COLOR_SUCCESS,
            color=COLOR_TEXT_DARK,
            bold=True
        )
        calc_btn.bind(on_press=self.berechne_ergebnis)
        result_row.add_widget(calc_btn)

        for _ in range(spieler_anzahl):
            res_btn = Button(
                text='0',
                background_normal='',
                background_color=COLOR_PRIMARY,
                color=COLOR_TEXT_DARK,
                bold=True,
                font_size='18sp'
            )
            self.result_buttons.append(res_btn)
            result_row.add_widget(res_btn)

        main_layout.add_widget(result_row)
        self.add_widget(main_layout)

    def berechne_ergebnis(self, instance):
        for spieler_index, inputs in enumerate(self.player_inputs):
            summe = 0
            for ti in inputs:
                try:
                    summe += int(ti.text)
                except ValueError:
                    pass
            self.result_buttons[spieler_index].text = str(summe)


class MainApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(ScoreScreen(name='score'))
        return sm


if __name__ == '__main__':
    MainApp().run()
