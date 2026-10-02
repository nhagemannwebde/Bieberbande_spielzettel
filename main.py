from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen

class CenteredTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Aktualisiert das Padding automatisch, sobald sich die Größe ändert
        self.bind(size=self._update_padding, line_height=self._update_padding)

    def _update_padding(self, *args):
        # Berechnet den Abstand nach oben, damit der Text mittig sitzt
        padding_top = (self.height - self.line_height) / 2
        self.padding_y = [padding_top, 0]

class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        layout.add_widget(Label(text="Bieberbande - Einstellungen", font_size='24sp', size_hint_y=0.2))

        # 1. Eingabe der Spieleranzahl
        count_layout = BoxLayout(orientation='horizontal', size_hint_y=0.15)
        count_layout.add_widget(Label(text="Anzahl Spieler (2-6):"))
        self.count_input = TextInput(text='3', input_filter='int', multiline=False, font_size='18sp', halign='center')
        count_layout.add_widget(self.count_input)
        layout.add_widget(count_layout)

        # Button zum Aktualisieren der Namensfelder
        btn_update = Button(text="Namensfelder anpassen", size_hint_y=0.15)
        btn_update.bind(on_press=self.generate_name_inputs)
        layout.add_widget(btn_update)

        # Container für die dynamischen Namensfelder
        self.names_container = BoxLayout(orientation='vertical', spacing=5)
        layout.add_widget(self.names_container)

        # Start-Button
        start_btn = Button(text="Spiel starten", size_hint_y=0.15)
        start_btn.bind(on_press=self.start_game)
        layout.add_widget(start_btn)

        self.add_widget(layout)
        
        # Erzeuge beim Start direkt Standard-Namensfelder
        self.generate_name_inputs(None)

    def generate_name_inputs(self, instance):
        """Erstellt je nach Zahl im Eingabefeld die passenden Name-TextInputs."""
        self.names_container.clear_widgets()
        try:
            count = int(self.count_input.text)
            count = max(2, min(6, count))  # Begrenzung auf 1-6 Spieler
        except ValueError:
            count = 3

        self.name_inputs = []
        for i in range(count):
            row = BoxLayout(orientation='horizontal')
            row.add_widget(Label(text=f"Spieler {i + 1}:"))
            ti = CenteredTextInput(text="", multiline=False, font_size='16sp', halign='center')
            self.name_inputs.append(ti)
            row.add_widget(ti)
            self.names_container.add_widget(row)

    def start_game(self, instance):
        """Liest die Spielernamen aus und wechselt zum Punktebogen."""
        player_names = [ti.text.strip() or f"Spieler {i+1}" for i, ti in enumerate(self.name_inputs)]
        
        # Gehe zum ScoreScreen und erstelle das Spielfeld
        score_screen = self.manager.get_screen('score')
        score_screen.setup_board(player_names)
        self.manager.current = 'score'


class ScoreScreen(Screen):
    def setup_board(self, player_names):
        """Baut die Tabelle dynamisch basierend auf den eingegebenen Namen auf."""
        self.clear_widgets()  # Altes Layout entfernen (bei Neustart)

        main_layout = BoxLayout(orientation='vertical')

        # 1. Überschrift
        header_row = BoxLayout(orientation='horizontal', size_hint_y=0.3)
        header_row.add_widget(Button(text="Bieberbande"))
        main_layout.add_widget(header_row)

        spieler_anzahl = len(player_names)

        # 2. Kopfzeile mit den echten Spielernamen
        title_row = BoxLayout(orientation='horizontal')
        exit_btn = Button(text='x')
        exit_btn.bind(on_press=exit)
        title_row.add_widget(exit_btn)
        for name in player_names:
            title_row.add_widget(Button(text=name))
        main_layout.add_widget(title_row)

        # Datenstrukturen für Auswertung
        self.player_inputs = [[] for _ in range(spieler_anzahl)]
        self.result_buttons = []

        # 3. Runden-Zeilen
        for runde in range(6):
            row_layout = BoxLayout(orientation='horizontal')
            row_layout.add_widget(Button(text=f'Runde {runde + 1}'))

            for s in range(spieler_anzahl):
                ti = TextInput(
                    input_filter='int',
                    multiline=False,
                    font_size='20sp',
                    halign='center',
                    padding_y=(10, 10)
                )
                self.player_inputs[s].append(ti)
                row_layout.add_widget(ti)

            main_layout.add_widget(row_layout)

        # 4. Ergebniszeile
        result_row = BoxLayout(orientation='horizontal')

        calc_btn = Button(text='Ergebnis')
        calc_btn.bind(on_press=self.berechne_ergebnis)
        result_row.add_widget(calc_btn)

        for _ in range(spieler_anzahl):
            res_btn = Button(text='0')
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
