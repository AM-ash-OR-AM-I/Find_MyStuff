__all__ = ('CardTextField')

from kivy import platform
from kivy.animation import Animation
from kivy.lang import Builder
from kivy.properties import ColorProperty, StringProperty, BooleanProperty
from kivy.uix.textinput import TextInput
from kivymd.app import MDApp

from kivymd.uix.behaviors import RectangularElevationBehavior
from kivymd.uix.card import MDCard
from kivymd.uix.relativelayout import MDRelativeLayout

KV = '''
<CardTextField>
    thickness:2
    height: '40dp'
    size_hint_y:None
    size_hint_x:None
    radius: dp(8)
    set_elevation: 8
    CustomMDCard:
        id: card
        height: root.height
        size_hint_y: None
        radius: root.radius
        elevation: root.set_elevation
        canvas:
            Color:
                rgba: root.border_color
            Line:
                width:root.thickness
                rounded_rectangle:
                    (self.x,self.y,self.width,self.height,self.radius[0])
    BoxLayout:
        MDIconButton:
            icon: root.left_icon
            pos_hint:{'center_y':.5}
            theme_text_color:'Custom'
            text_color: app.theme_cls.primary_color
            on_release:
        CustomInput:
            id: textfield
            size_hint_y:None
            hint_text:root.hint_text
            height: card.height
            background_color:[0,0,0,0]
            padding:[6,(self.height-self.font_size)/2,6,6]
            font_size:'18sp'
            foreground_color: app.theme_cls.primary_dark if app.theme_cls.theme_style=='Light' else app.theme_cls.primary_light
            hint_text_color: root.hint_text_color if root.hint_text_color is not None else [.5,.5,.5,.8]
            cursor_color: app.theme_cls.primary_color
            _on_focus: root.animate(self.focus)
            multiline: root.multiline
            on_text : root.on_card_text(self.text)
            y: card.y
            center_x: card.center_x
'''


class CustomMDCard(MDCard, RectangularElevationBehavior):
    pass


class CustomInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(text=self.on_text)

    def on_text(self, *args):
        pass


class CardTextField(MDRelativeLayout):
    inactive_color = ColorProperty([.5, .5, .5, .1])
    border_color = ColorProperty()
    active_color = [0, 0, 1, .3]
    hint_text_color = ColorProperty(None)
    hint_text = StringProperty('')
    left_icon = StringProperty('magnify')
    multiline = BooleanProperty(False)
    Builder.load_string(KV)
    first_call = 1
    win = True if platform == 'win' else False
    app = None
    c = 0

    def on_inactive_color(self, *args):
        self.border_color = self.inactive_color

    def on_card_text(self, text):
        if not __name__ == '__main__':
            try:
                self.app.find_image(text)  # Custom method made to find text, remove it for yourself.
            except AttributeError:
                pass

    def animate(self, focus):

        if platform == "android":
            if platform == 'win':
                from JavaAPI import fix_back_button
            else:
                from Modules.JavaAPI import fix_back_button

            if not focus and MDApp.get_running_app().fix_back:
                fix_back_button()

        if self.app is None:
            self.app = MDApp.get_running_app()
        if not self.first_call:
            print('called')
            if not __name__ == '__main__' and platform=='android':
                try:

                    self.app.shift_up(focus)
                    # Custom method made to move up textfield when keyboard covers it, remove it for yourself.

                except AttributeError:
                    pass

            if focus:

                if self.win:

                    Animation(border_color=self.active_color, duration=.2).start(self)
                else:
                    self.border_color = self.active_color
            else:

                if self.win:
                    Animation(border_color=self.inactive_color, duration=.1).start(self)
                else:
                    self.border_color = self.inactive_color
        self.first_call = 0


if __name__ == '__main__':
    class TestCard(MDApp):
        def build(self):
            return Builder.load_string('''
Screen:
    CardTextField:
        size_hint_x:.7
        pos_hint:{'center_x':.5,'center_y':.5}
        hint_text:'Search'
        radius:'25dp'
        height: '60dp'
            ''')


    TestCard().run()
