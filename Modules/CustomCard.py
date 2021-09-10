from kivy import platform, Logger
from kivy.lang import Builder
from kivy.properties import ColorProperty, StringProperty, BooleanProperty, NumericProperty, ListProperty
from kivymd.app import MDApp
from kivymd.theming import ThemableBehavior
from kivymd.uix.button import MDIconButton
from kivymd.uix.relativelayout import MDRelativeLayout

Builder.load_string('''

<CustomMDCard@MDCard+RectangularElevationBehavior>:

<CardTextField>
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
	MDBoxLayout:
		orientation:'vertical'
		padding:(dp(20),0,0,dp(6)) if not root.icon_left_action or root.label_text else (dp(6),0,0,0)
		MDLabel:
		    id: lbl
		    text: root.label_text
		    font_size: root.label_height if self.text else dp(0)
		    theme_text_color:'Custom'
		    text_color:root.border_color if root.focus else [.5,.5,.5,.8]
			x: textfield.x
        MDBoxLayout:
            id: card_box
            TextInput:
                id: textfield
                size_hint_y:None
                hint_text:root.hint_text
                height: card.height - lbl.height if root.label_text else card.height
                background_color:[0,0,0,0]
                font_size:'18sp'
                padding:[0,(self.height-self.font_size)/2,0,dp(0)] if not root.label_text\
                 else [0,(self.height-self.font_size)/2,0,dp(6)]
                foreground_color: app.theme_cls.primary_dark if app.theme_cls.theme_style=='Light'\
                 else app.theme_cls.primary_light
                hint_text_color: root.hint_text_color if root.hint_text_color is not None else [.5,.5,.5,.8]
                cursor_color: app.theme_cls.primary_color
                multiline: root.multiline
                text: root.text
                on_text:
                    root.text = self.text
                on_focus:
                    root.focus = self.focus
                y: card.y
                center_x: card.center_x
''')


class CardTextField(MDRelativeLayout, ThemableBehavior):
    inactive_color = ColorProperty([.5, .5, .5, .1])
    border_color = ColorProperty([.5, .5, .5, .1])
    active_color = [0, 0, 1, .3]
    focus = BooleanProperty(False)
    hint_text_color = ColorProperty(None)
    text = StringProperty('')
    thickness = NumericProperty(2)
    hint_text = StringProperty('')
    label_height = StringProperty('15dp')
    label_text = StringProperty('')
    icon_left_action = ListProperty(None)
    multiline = BooleanProperty(False)
    icon_color = ColorProperty([.5, .5, .5, 1])
    icon_right_action = ListProperty(None)
    win = True if platform == 'win' else False
    app = None
    c = 0

    def on_icon_left_action(self, instance, value: 'List containing icon name and function'):
        if not self.label_text:
            if len(value) == 1:
                self.icon_left = MDIconButton(icon=self.icon_left_action[0], theme_text_color='Custom',
                                              text_color=self.icon_color,
                                              pos_hint={'center_y': 1})

            else:
                self.icon_left = MDIconButton(icon=self.icon_left_action[0], theme_text_color='Custom',
                                              text_color=self.icon_color,
                                              pos_hint={'center_y': 1}, on_release=self.icon_left_action[1])
            self.ids.card_box.add_widget(self.icon_left, index=1)

        else:
            Logger.warning("CardTextField: Doesn't support icon-left for Top label")

    def on_icon_right_action(self, instance, value):
        if len(value) == 1:
            self.icon_right = MDIconButton(icon=self.icon_right_action[0], theme_text_color='Custom',
                                           text_color=self.icon_color,
                                           pos_hint={'center_y': 1})

        else:
            self.icon_right = MDIconButton(icon=self.icon_right_action[0], theme_text_color='Custom',
                                           text_color=self.icon_color,
                                           pos_hint={'center_y': 1}, on_release=self.icon_right_action[1])
        self.ids.card_box.add_widget(self.icon_right)

    def on_icon_color(self, instance, color):
        if self.icon_left_action is not None:
            self.icon_left.text_color = color
        if self.icon_right_action is not None:
            self.icon_right.text_color = color

    def on_inactive_color(self, *args):
        self.border_color = self.inactive_color

    def on_text(self, instance, text):
        """Use this to do what you want"""

    def on_focus(self, instance, focus):
        print('event:<on_focus> is_called')
        if self.app is None:
            self.app = MDApp.get_running_app()
        if platform == "android":
            from Modules.JavaAPI import fix_back_button
            if not focus:
                fix_back_button()

        if focus:
            self.border_color = self.active_color
        else:
            self.border_color = self.inactive_color


if __name__ == '__main__':
    class TestCard(MDApp):
        def build(self):
            return Builder.load_string('''
Screen:
    CardTextField:
        size_hint_x:.7
        pos_hint:{'center_x':.5,'center_y':.5}
        radius:'25dp'
		hint_text:''
		label_text:'Object'
		thickness: 1.5
		active_color:app.theme_cls.primary_light
        icon_color: app.theme_cls.primary_light
		icon_left_action:['magnify',lambda x: print('Call any function you want like this.')]
        icon_right_action:['microphone']
        on_text:
            print(self.text)
        height: '80dp'
            ''')

    TestCard().run()
