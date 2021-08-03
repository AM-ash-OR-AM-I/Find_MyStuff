from kivy import platform
from kivy.lang import Builder
from kivy.properties import ColorProperty, NumericProperty
from kivymd.app import MDApp

from Modules.CustomCard import CardTextField
from kivymd.uix.behaviors import FakeCircularElevationBehavior
from kivymd.uix.behaviors.magic_behavior import MagicBehavior
from kivymd.uix.button import MDFloatingActionButton
from kivy.uix.widget import Widget
from kivy.animation import Animation

Builder.load_string('''
<MicAnimation>
    canvas:
        Color:
            rgba: root.set_color
        Ellipse:
            size: dp(self.rad),dp(self.rad)
            pos:(-dp(self.rad)/2+self.widget_pos/2,-dp(self.rad)/2+self.widget_pos/2)
    
<DarkAnimation@Widget>
    rad : 80
    set_color: [0,0,0,1]
    parent_rad: 20
    opacity:root.opacity
    canvas:
        Color:
            rgba: app.theme_cls.opposite_bg_normal
        Ellipse:
            size: 2*self.rad,2*self.rad
            pos: (self.x + self.parent_rad - self.rad , self.y + self.parent_rad - self.rad)

<CustomMDSpinner>:
    auto_dismiss: False
    background_color: 0, 0, 0, 0
    FloatLayout:
        AKSpinnerDoubleBounce:
            pos_hint: {'center_x': .5, 'center_y': .5}
            spinner_size: dp(30)
            active: True
''')


class MovingTextField(CardTextField):

    def on_focus(self, instance, focus):
        super().on_focus(instance, focus)
        if platform == 'android':
            MDApp.get_running_app().HomeScreen.shift_up(focus)


class FloatingButton(MDFloatingActionButton, FakeCircularElevationBehavior):
    elevation = 15
    rotate = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.bind(primary_hue=self.update_md_bg_color)


class CustomFloatingButton(FloatingButton, MagicBehavior):
    _no_ripple_effect = True
    scale = 1.5
    magic_speed = 1

    def shrink(self):
        Animation(
            scale_x=self.scale, scale_y=self.scale, t="out_quad", d=0.1 / self.magic_speed
        ).start(self)

    def reset(self):
        Animation(scale_x=1, scale_y=1, t='out_quad', d=0.1 / self.magic_speed).start(self)


class MicAnimation(Widget):
    set_color = ColorProperty([0, 0, 0, 1])
    rad = NumericProperty(80)
    widget_pos = NumericProperty(0)
