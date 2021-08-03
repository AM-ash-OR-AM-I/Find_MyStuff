from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import OptionProperty, get_color_from_hex
from Modules.dialogs import AKAlertDialog
from kivymd.color_definitions import colors, palette
from kivymd.uix import SpecificBackgroundColorBehavior
from kivymd.uix.button import MDIconButton

PICKER = '''
#: import custom_light_color kivymd.color_definitions.custom_light_color
#: import colors kivymd.color_definitions.colors
<ColorSelector>
    canvas:
        Color:
            rgba: root.rgb_hex(root.color_name)
        Ellipse:
            size: self.size
            pos: self.pos
    theme_text_color:'Custom'
    text_color: [0,0,0,0]
            
<PrimaryColorSelector@ColorSelector>
    on_release: 
        self.theme_cls.primary_palette = root.color_name
        self.theme_cls.primary_hue='500' if not app.dark_mode else '300'
        app.extra_light_color = app.generate_light_color(0.1)
        app.light_color=app.generate_light_color(app.light_alpha)
    
<ColorGrid@MDGridLayout>
    cols: 5
    rows: 4
    adaptive_size: True
    spacing: "8dp"
    padding: (dp(20),20,dp(20),20)
    pos_hint: {"center_x": .5, "top": 1}

'''
Builder.load_string(PICKER)


class ColorSelector(MDIconButton):
    color_name = OptionProperty("Indigo", options=palette)

    def rgb_hex(self, col):
        return get_color_from_hex(colors[col][self.theme_cls.primary_hue])


class MDThemePicker(AKAlertDialog, SpecificBackgroundColorBehavior):
    header_text_type = 'text'
    header_text = 'COLORS'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.bind(theme_style=self.update_selector)
        self.content_cls = Factory.ColorGrid()
        self.header_font_size = '40dp'
        self.size_portrait = ['320dp', '380dp']

    def update_selector(self, *args):
        self.content_cls.clear_widgets()

    def on_open(self):
        if not self.content_cls.children:
            for name_palette in palette:
                self.content_cls.add_widget(
                    Factory.PrimaryColorSelector(color_name=name_palette))
