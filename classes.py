from kivy import platform
from kivy.lang import Builder
from kivy.properties import ColorProperty, NumericProperty
from kivymd.app import MDApp

from Modules.CustomCard import CardTextField
from kivymd.uix.behaviors import FakeCircularElevationBehavior
from kivymd.uix.behaviors.magic_behavior import MagicBehavior
from kivymd.uix.button import MDFloatingActionButton, MDRoundFlatIconButton
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


class React(MagicBehavior):
    shrink_scale = .9
    grow_scale = 1.2

    def react(self, option='reset'):
        if option == 'shrink':
            Animation(scale_x=self.shrink_scale, scale_y=self.shrink_scale, t="out_quad", d=0.05).start(self)
        elif option == 'grow':
            Animation(scale_x=self.grow_scale, scale_y=self.grow_scale, t='out_quad', d=.01).start(self)
        else:
            Animation(scale_x=1, scale_y=1, t='out_quad', d=.05).start(self)


class FloatingButton(MDFloatingActionButton, FakeCircularElevationBehavior):
    rotate = shrunk = 0
    elevation = 10

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.bind(primary_hue=self.update_md_bg_color)


class CustomFloatingButton(FloatingButton, React):
    _no_ripple_effect = True

    def on_press(self):
        super().on_press()
        self.shrunk = True
        self.react('shrink')

    def on_touch_up(self, touch):
        super().on_touch_up(touch)
        if self.shrunk:
            self.react()
        self.shrunk=False


class MicAnimation(Widget):
    set_color = ColorProperty([0, 0, 0, 1])
    rad = NumericProperty(80)
    widget_pos = NumericProperty(0)
