import os, threading, webbrowser
from time import time
from kivy.animation import Animation
from kivy.clock import Clock, mainthread
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.graphics.context_instructions import PushMatrix, Rotate, PopMatrix
from kivy.lang import Builder
from kivy.properties import BooleanProperty, NumericProperty, ColorProperty
from kivy.uix.screenmanager import CardTransition, ScreenManager, NoTransition
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.color_definitions import colors
from kivymd.icon_definitions import md_icons
from kivymd.toast import toast
from kivymd.uix.banner import MDBanner
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen
from Modules.dialogs import AKAlertDialog
from Modules.picker import MDThemePicker

if platform == 'win':
    WIN, ANDROID = True, False
    device_x, device_y = (1080, 2240)
    device_dpi = 400
    desktop_dpi = 157
    scale_factor = desktop_dpi / device_dpi
    Window.size = (scale_factor * device_x, scale_factor * device_y)

elif platform == 'android':
    ANDROID, WIN = True, False
    from Modules.JavaAPI import statusbar, dark_mode
    from android.permissions import request_permissions, Permission

SYSTEM_DARK_MODE = dark_mode() if ANDROID else False


class FindStuff(MDApp):
    dark_mode = BooleanProperty(False)
    circle_color = ColorProperty([0, 0, 0, .1])
    light_color = ColorProperty()
    extra_light_color = ColorProperty()
    light_alpha = .6
    dark_hex = colors['Dark']['Background']
    start_call, resize_in_progress = True, False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from configure import Config
        self.configuration = Config()
        if self.configuration.restore_variables():
            self.variables_restored = True
        else:
            self.variables_restored = False
            self.configuration.set_variables({'self.theme_cls.primary_palette': 'Purple', 'text_size': 15,
                                              'optimise': False, 'avail_preview_size': [], 'set_preview_index': 2,
                                              'show_optimise': True, 'dark_mode': False, 'grid_cols': 2,
                                              'show_text': True})

        self.extra_light_color = self.generate_light_color(0.1)
        self.light_color = self.generate_light_color(self.light_alpha)
        self.toolbar_color = self.theme_cls.primary_color

    def check_camera(self, *args) -> "Checks if camera is running and turns it off":
        if self.sm.current != 'camera':
            self.camera.ids.xcamera.play = False

    def reduce_preview_size(self):
        self.optimise = True
        if self.avail_preview_size[self.set_preview_index][1] > 480:
            self.set_preview_index += 1

    def load_screen(self, *args):
        @mainthread
        def add_cam():
            self.sm.add_widget(self.camera)
            Clock.schedule_once(self.check_camera, 0.5)

        @mainthread
        def initialise_stuff(*args):
            if self.variables_restored:
                self.dark_mode = self.configuration.get_variable(
                    'dark_mode') if not SYSTEM_DARK_MODE else SYSTEM_DARK_MODE
                if ANDROID:
                    if not self.dark_mode:
                        statusbar(theme='white')
                    self.start_call = False
            elif ANDROID:
                if not SYSTEM_DARK_MODE:
                    statusbar(theme='white')
                else:
                    self.dark_mode = True
            self.start_call = False
            self.change_screen('HomeScreen')
            self.sm.transition = CardTransition(mode='push', direction='left', duration=0.2)
            self.HomeScreen.add_images()
            if self.time_taken > 3:
                if self.show_optimise:
                    if self.optimise:
                        self.reduce_preview_size()
                    else:
                        if self.time_taken > 4:
                            widget = self.HomeScreen.ids.grid_layout if self.variables_restored else self.HomeScreen.NoImage
                            self.banner = MDBanner(type='three-line', text=[
                                '[b]Decrease Loading Time',
                                'It will result in lower camera preview',
                                'quality, but loading time will be less.'],
                                                   left_action=[
                                                       f"Make it Fast [font=Icons] {md_icons['lightning-bolt']}[/font]",
                                                       lambda x: self.reduce_preview_size()],
                                                   right_action=[
                                                       "Don't show again",
                                                       lambda x: exec("self.show_optimise = False",
                                                                      {'self': self})],
                                                   over_widget=widget)
                            self.HomeScreen.add_widget(self.banner)
                            self.banner.show()

        def load_cam(*args):
            initial = time()
            if ANDROID:
                self.camera = CameraScreen(name='camera')
                self.sm.add_widget(self.camera)
                self.time_taken = time() - initial
                initialise_stuff()
            else:
                threading.Thread(target=initialise_stuff, daemon=True).start()
                self.time_taken = time() - initial
                self.camera = CameraScreen(name='camera')
                add_cam()

        from Screens.ObjectInfo.ObjectInfo import ObjectInfo
        from Screens.HomeScreen import HomeScreen
        self.HomeScreen = HomeScreen.HomeScreen(name='HomeScreen')
        self.SettingScreen = Setting(name='setting')
        self.InfoScreen = ObjectInfo(name='ObjectInfo')
        self.sm.add_widget(self.HomeScreen)
        self.sm.add_widget(self.SettingScreen)
        self.sm.add_widget(self.InfoScreen)
        if ANDROID:
            Clock.schedule_once(load_cam)
        else:
            threading.Thread(target=load_cam, daemon=True).start()

    def add_screens(self, *args):
        if ANDROID:
            statusbar(status_color='5433fe', nav_color='a4fdcb')
        Clock.schedule_once(self.load_screen)
        Window.bind(on_keyboard=self.go_back)
        self.screen_history = []

    def build(self):

        self.sm = ScreenManager()
        self.theme_cls.theme_style = 'Dark' if (self.variables_restored and self.configuration.get_variable(
            'dark_mode')) or SYSTEM_DARK_MODE else 'Light'
        print(f'{self.theme_cls.theme_style = }')
        self.StartScreen = StartScreen()
        self.sm.add_widget(self.StartScreen)
        self.sm.transition = NoTransition()
        if ANDROID:
            request_permissions([Permission.RECORD_AUDIO, Permission.CAMERA])
        return self.sm

    def on_dark_mode(self, inst, active):

        if self.start_call:
            self.set_mode()
        else:
            radius = 1.3 * max(Window.size)
            self.SettingScreen.ids.circle_mode.opacity = 1
            self.anim = Animation(rad=radius, duration=.8, t='in_quad')
            self.anim.start(self.SettingScreen.ids.circle_mode)
            self.anim.on_complete = self.set_mode

    def set_mode(self, *args):
        dark_mode = self.dark_mode
        print(dark_mode)
        if dark_mode:
            if ANDROID:
                statusbar(theme='black', status_color=self.dark_hex)
            self.theme_cls.theme_style = 'Dark'
            self.theme_cls.primary_hue = '300'
        else:
            if ANDROID:
                statusbar(theme='white')
            self.theme_cls.theme_style = 'Light'
            self.theme_cls.primary_hue = '500'

        self.SettingScreen.ids.circle_mode.rad = 0.1
        for im in self.HomeScreen.ids.grid_layout.children:
            im.tile_text_color = [0.5, 0.5, 0.5, 1]
            im.tile_text_color = self.theme_cls.accent_color if self.SettingScreen.ids.switch.active else [0, 0, 0, 0]
            im.ids.checkbox.disabled_color = [0, 0, 0, 0]

    def back_button(self, home_screen=False, *args):
        if not home_screen:
            self.screen_history.pop()
        else:
            self.screen_history = ['HomeScreen']
        self.sm.transition.mode = 'pop'
        self.sm.transition.direction = 'right'
        self.sm.current = self.screen_history[-1]

    def change_screen(self, screen_name, *args):
        self.sm.transition.mode = 'push'
        self.sm.transition.direction = 'left'
        self.sm.current = screen_name
        self.screen_history.append(screen_name)
        print(f'{self.screen_history = }')

    def go_back(self, instance, key, *a):
        def check_process_finished(*args):
            if not self.resize_in_progress:
                self.interval.cancel()
                self.stop()
            else:
                self.exit_dialog.text = 'Exiting...'

        def check_bg_process(*args):
            if not self.resize_in_progress:
                self.stop()
            else:
                self.exit_dialog.text = 'Saving Stuff...'
                self.interval = Clock.schedule_once(check_process_finished, .05)

        if key in (27, 1001):
            self.screen_history.pop()
            if self.screen_history != []:
                self.sm.transition.mode = 'pop'
                self.sm.transition.direction = 'right'
                self.sm.current = self.screen_history[-1]

            else:
                self.exit_dialog = MDDialog(title='Exit', text='Do you want to exit?',
                                            buttons=[MDRaisedButton(text='YES', on_release=check_bg_process),
                                                     MDFlatButton(text='NO',
                                                                  on_release=lambda x: self.exit_dialog.dismiss())])
                self.exit_dialog.open()
                self.screen_history = ['HomeScreen']
        return True

    def on_stop(self):
        self.configuration.save_variables()

    def on_pause(self):
        try:
            if self.sm.current != 'Start':
                if self.sm.current == 'ObjectInfo':
                    self.HomeScreen.on_enter()
                self.configuration.save_variables()
        except AttributeError as e:
            print(e)
        return True

    def generate_light_color(self, factor):
        color = self.theme_cls.primary_color
        color[-1] = factor * color[-1]
        return color

    def darker(self, factor):
        r, g, b, a = self.theme_cls.primary_color
        r *= factor
        g *= factor
        b *= factor
        return r, g, b, a

    @staticmethod
    def load_file(filename):
        file = os.path.join('Screens', filename[:-3], filename)
        Builder.load_file(file)


class Setting(MDScreen):
    hide_text = BooleanProperty(True)
    theme_picker = None
    content = None
    Builder.load_file('Screens/Settings.kv')

    def open_about(self):
        if self.content is None:
            content = Factory.AboutClass()
            self.about_dialog = AKAlertDialog(header_icon='heart-circle')
            self.about_dialog.size_portrait = ['300dp', '380dp']
            self.about_dialog.content_cls = content
        self.about_dialog.open()

    def open_web(self, github=False, youtube=False, email=False):
        if github:
            webbrowser.open('https://github.com/AM-ash-OR-AM-I/Find_MyStuff')
            toast('Star my repository if you like it :)')
        elif youtube:
            webbrowser.open('https://www.youtube.com/watch?v=lVz2nCDUoEI&list=PLUdItSprD91zcFG7__KR_0CGsDbCmmbtl')
        elif email:
            webbrowser.open('https://mail.google.com/mail/u/0/#inbox?compose=new')
            Clipboard.copy('ashutoshmaha2909@gmail.com')
            toast('Email address Copied, Paste Email address to send email.')

    def open_theme(self):
        if self.theme_picker is None:
            self.theme_picker = MDThemePicker()
        self.theme_picker.open()


class StartScreen(MDScreen):
    def on_enter(self, *args):
        Clock.schedule_once(MDApp.get_running_app().add_screens)

    Builder.load_file('Screens/StartScreen.kv')


class CameraScreen(MDScreen):
    rotating_angle = NumericProperty(0)
    Builder.load_file('Screens/CameraScreen.kv')
    landscape = BooleanProperty(False if ANDROID else True)

    def on_landscape(self, instance, landscape):
        # if ANDROID:
        self.landscape = landscape
        self.angle = -90 if landscape else 90
        lst = self.ids
        lst.choose_orient.icon = 'phone-rotate-landscape' if not landscape else 'phone-rotate-portrait'
        for id in lst:
            widget = lst[id]
            if id not in ('xcamera', 'show_orient', 'label'):
                with widget.canvas.before:
                    PushMatrix()
                    self.rotation = Rotate(origin=widget.center)
                Animation(angle=self.angle, duration=.2).start(self.rotation)
                with widget.canvas.after:
                    PopMatrix()


FindStuff().run()
