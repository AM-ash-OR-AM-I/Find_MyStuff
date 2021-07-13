from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import OptionProperty, get_color_from_hex
from kivymd.color_definitions import colors, palette
from kivymd.uix import SpecificBackgroundColorBehavior
from kivymd.uix.behaviors import FakeRectangularElevationBehavior
from kivymd.uix.button import MDIconButton
from kivymd.uix.dialog import BaseDialog

PICKER = '''
#: import custom_light_color kivymd.color_definitions.custom_light_color
#: import colors kivymd.color_definitions.colors
#: import Statusbar Modules.JavaAPI
<ColorSelector>
    canvas:
        Color:
            rgba: root.rgb_hex(root.color_name)
        Ellipse:
            size: self.size
            pos: self.pos
            
<PrimaryColorSelector@ColorSelector>
    on_release: 
        self.theme_cls.primary_palette = root.color_name
        self.theme_cls.primary_hue='500' if not app.dark_mode else '300'
        app.extra_light_color = app.generate_light_color(0.1)
        app.light_color=app.generate_light_color(app.light_alpha)
        '' if app.dark_mode or platform=='win' else Statusbar.statusbar(colors[self.theme_cls.primary_palette]['500']) 
    
<MDThemePicker>
    size_hint: None, None
    size: "300dp", "400dp"
    canvas:
        Color:
            rgb: app.theme_cls.primary_color
        RoundedRectangle:
            size: self.width, dp(100)
            pos: root.pos[0], root.pos[1] + root.height - dp(120)
            radius: [dp(15), dp(15), dp(0), dp(0)]
        Color:
            rgb: app.theme_cls.bg_normal
        RoundedRectangle:
            size: self.width, dp(290)
            pos: root.pos[0], root.pos[1] + root.height - (dp(120) + dp(290))
            radius: [dp(0), dp(0), dp(15), dp(15)]
            
    MDBoxLayout:
        orientation: "vertical"

        MDLabel:
            font_style: "H5"
            markup: True
            text: "[b]COLORS"
            halign:'center'
            size_hint: (None, None)
            size: dp(160), dp(110)
            pos_hint: {"center_x": .5, "center_y": .9}
            theme_text_color: "Custom"
            text_color: root.specific_text_color


        MDGridLayout:
            id: primary_box
            cols: 5
            rows: 4
            adaptive_size: True
            spacing: "8dp"
            padding: (dp(40),20,dp(40),20)
            pos_hint: {"center_x": .5, "top": 1}
            

        MDRoundFlatButton:
            text: "CLOSE"
            md_bg_color: app.extra_light_color
            size_hint_x:.6
            pos_hint:{'center_x':.5}
            on_release: root.dismiss()

'''
Builder.load_string(PICKER)


class ColorSelector(MDIconButton):
    color_name = OptionProperty("Indigo", options=palette)

    def rgb_hex(self, col):
        return get_color_from_hex(colors[col][self.theme_cls.primary_hue])


class MDThemePicker(
    BaseDialog,
    SpecificBackgroundColorBehavior,
    FakeRectangularElevationBehavior,
):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.theme_cls.bind(theme_style=self.update_selector)

    def update_selector(self,*args):
        self.ids.primary_box.clear_widgets()

    def on_open(self):
        if not self.ids.primary_box.children:
            for name_palette in palette:
                self.ids.primary_box.add_widget(
                    Factory.PrimaryColorSelector(color_name=name_palette))
