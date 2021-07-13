import os
import pickle
import random
from time import time
from PIL import Image
from kivy.core.clipboard import Clipboard
from kivy.graphics.context_instructions import PushMatrix, Rotate, PopMatrix
from kivy.uix.image import Image as Kivy_Image
from kivy.animation import Animation
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ListProperty, BooleanProperty, NumericProperty, ColorProperty, Logger
from kivy.uix.widget import Widget
from kivy.factory import Factory
from Modules.dialogs import AKAlertDialog
from kivymd.icon_definitions import md_icons
from kivymd.uix.banner import MDBanner
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import CardTransition, ScreenManager
from kivy.utils import platform
from kivymd.color_definitions import colors, custom_light_color
from kivymd.uix.list import IRightBodyTouch
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.imagelist import SmartTileWithLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.selectioncontrol import MDSwitch
from Modules.taptargetview import MDTapTargetView
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.button import MDFloatingActionButton, MDRoundFlatIconButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp
from kivymd.uix.behaviors import TouchBehavior, FakeCircularElevationBehavior
from kivymd.uix.behaviors.magic_behavior import MagicBehavior
from Modules.picker import MDThemePicker
from Modules.find import find
import threading
import webbrowser

if platform == 'win':
    WIN = True
    ANDROID = False
elif platform == 'android':
    ANDROID = True
    WIN = False
if not os.path.exists('Data/object_dict'):
    FIRST_TIME = True
else:
    FIRST_TIME = False

PREPOSITIONS = ['about', 'above', 'across', 'after', 'against', 'among', 'around', 'at', 'before', 'behind', 'below',
                'beside',
                'between', 'by', 'down', 'during', 'for', 'from', 'in', 'inside', 'into', 'near', 'of', 'off', 'on',
                'out',
                'over', 'through', 'to', 'toward', 'under', 'up', 'with', 'aboard', 'along', 'amid', 'as', 'beneath',
                'beyond',
                'but', 'concerning', 'considering', 'despite', 'except', 'following', 'like', 'minus', 'next', 'onto',
                'opposite', 'outside', 'past', 'per', 'plus', 'regarding', 'round', 'save', 'since', 'than', 'till',
                'underneath', 'unlike', 'until', 'upon', 'versus', 'via', 'within', 'without', ]

if WIN:
    import speech_recognition as sr
    import pyttsx3 as p

    Window.size = (1000 * 9 / 19.5, 1000)

elif ANDROID:
    from plyer import tts
    from Speechrecognizer import stt
    from Modules.JavaAPI import statusbar, keyboard_height, dark_mode
    from android.permissions import request_permissions, Permission

SYSTEM_DARK_MODE = dark_mode() if ANDROID else False


class FloatingButton(MDFloatingActionButton, FakeCircularElevationBehavior):
    elevation = 15
    rotate = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.bind(primary_hue=self.update_md_bg_color)


class RightSwitch(IRightBodyTouch, MDSwitch):
    pass


class CustomCircle(Widget):
    set_color = ColorProperty([0, 0, 0, 1])
    rad = NumericProperty()
    widget_pos = NumericProperty(0)


class CustomDialog(MDDialog):
    radius = ListProperty([dp(25), dp(25), dp(25), dp(25)])


class Setting(MDScreen):
    hide_text = BooleanProperty(True)
    Builder.load_file('KV/Settings.kv')


class CustomMDSpinner(ModalView):
    pass


class StartScreen(MDScreen):
    def on_enter(self, *args):
        Clock.schedule_once(MDApp.get_running_app().add_screens)

    Builder.load_file('KV/StartScreen.kv')


class CameraScreen(MDScreen):
    rotating_angle = NumericProperty(0)
    Builder.load_file('KV/CameraScreen.kv')


class ObjectInfo(MDScreen):
    Builder.load_file('KV/ObjectDetails.kv')


class HomeScreen(MDScreen):
    Builder.load_file('KV/HomeScreen.kv')
    first_use = True
    change_home = False

    def on_enter(self, *args):
        app = MDApp.get_running_app()

        app.fix_back = True
        if self.first_use and FIRST_TIME:
            app.tap_target()
            self.first_use = False

        elif self.change_home:

            app.update_home() if app.add_picture else print('No changes Made')
            app.add_picture = False
            self.change_home = False


class MyImage(SmartTileWithLabel, TouchBehavior, MagicBehavior):
    _no_ripple_effect = True
    index = NumericProperty(0)
    bg_color = ColorProperty([0, 0, 0, 0])
    check_box_state = BooleanProperty(False)
    canvas = None
    duration_long_touch = .25
    shrink_scale = .85

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # #print(" __init__ of My Image gets called ")
        self.app = MDApp.get_running_app()
        self.light_color = self.app.generate_light_color(0.3)
        self.image_list = self.app.HomeScreen.ids.grid_layout.children
        Clock.schedule_once(self.update_checkbox_color)
        self.theme_cls.bind(primary_palette=self.update_checkbox_color)
        self.theme_cls.bind(primary_hue=self.update_checkbox_color)
        self.magic_speed = .8

    def update_checkbox_color(self, *args):
        self.ids.checkbox.selected_color = [1, 1, 0, 1]

    def shrink(self):
        Animation(
            scale_x=self.shrink_scale, scale_y=self.shrink_scale, t="out_quad", d=0.1 / self.magic_speed
        ).start(self)

    def reset(self):
        Animation(
            scale_x=1, scale_y=1, t="out_quad", d=0.1 / self.magic_speed
        ).start(self)

    def on_long_touch(self, *args):
        self.app.prev_state = self.app.show_text
        self.app.show_text = False
        for image in self.image_list:
            image.ids.checkbox.disabled = False
        self.ids.checkbox.active = True

    def on_check_box_state(self, obj, active):
        self.app.delete_dict[obj.source] = active
        self.app.toolbar_change = True
        # #print('<On_Check_box_event>')
        if active:
            self.shrink()
            self.bg_color = custom_light_color[self.theme_cls.primary_palette]
        else:
            self.reset()
            self.bg_color = [0, 0, 0, 0]

        if True not in self.app.delete_dict.values():  # Deselecting everything
            # #print(f'{self.app.delete_dict.values() = }')
            self.app.ignore_release = True
            self.app.toolbar_change = False
            # #print(f'{self.app.root.ids.setting.ids.switch_item= }')
            if self.app.prev_state:
                self.app.show_text = True
            for image in self.image_list:
                image.ids.checkbox.disabled = True


class CustomFloatingButton(FloatingButton, MagicBehavior):
    _no_ripple_effect = True
    shrink_scale = .88
    magic_speed = 1.2

    def shrink(self):
        Animation(
            scale_x=self.shrink_scale, scale_y=self.shrink_scale, t="out_quad", d=0.1 / self.magic_speed
        ).start(self)

    def reset(self):
        Animation(scale_x=1, scale_y=1, t='out_quad', d=0.1 / self.magic_speed).start(self)


class CustomAnimate(Animation):
    def on_complete(self, widget):
        MDApp.get_running_app().set_mode()


class MainApp(MDApp):
    ignore_release = False
    fix_back = False
    prev_list = []
    toolbar_change = BooleanProperty(False)
    show_text = BooleanProperty(True)
    dark_mode = BooleanProperty(False)
    image_exists = BooleanProperty(True)
    restore_normal_color = BooleanProperty(False)
    circle_color = ColorProperty([0, 0, 0, .1])
    key_height = 0
    drop2 = None
    theme_picker = None
    button_pressed = False
    add_picture = False
    uniform_color = False
    NoImage = None
    optimise = False
    list = []
    index = 0
    active = True
    delete_dict = {}
    preview_size = None
    light_color = ColorProperty()
    extra_light_color = ColorProperty()
    dialog = None
    camera = None
    text_size = 15
    n_col = 2
    light_alpha = .6
    InfoDict = {}
    text_list = []
    prev_scale = 1
    avail_preview_size = []
    show_optimise = True
    set_preview_index = 0
    landscape = BooleanProperty(False) if ANDROID else BooleanProperty(True)
    source_list = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # #print('__init__ of MainAPP')
        if os.path.exists('Data/theme_details.txt'):
            with open('Data/theme_details.txt', 'r')as f:
                string = f.read()
            self.InfoDict = eval(string)
            for info in self.InfoDict:
                if info == 'PRIMARY_PALETTE':
                    self.theme_cls.primary_palette = self.InfoDict[info]
                elif info == 'TEXT_SIZE':
                    self.text_size = self.InfoDict[info]
                elif info == 'OPTIMISE':
                    self.optimise = self.InfoDict[info]
                elif info == 'PREVIEW_SIZE':
                    self.avail_preview_size = self.InfoDict[info]
                elif info == 'PREVIEW_INDEX':
                    self.set_preview_index = self.InfoDict[info]
                elif info == 'SHOW_OPTIMISE':
                    self.show_optimise = self.InfoDict[info]
            self.n_col = self.InfoDict['GRID_SIZE']
        else:
            self.theme_cls.primary_palette = 'Purple'

        ##print(f'{self.InfoDict = }')
        self.drop = None
        self.extra_light_color = self.generate_light_color(0.1)
        self.light_color = self.generate_light_color(self.light_alpha)
        self.dark_hex = colors['Dark']['CardsDialogs']
        self.toolbar_color = self.theme_cls.primary_color

    def check_camera(self, *args) -> "Checks if camera is running and turns it off":
        self.camera.ids.xcamera.play = False

    def reduce_preview_size(self):
        self.optimise = True
        self.set_preview_index += 1

    def add_screens(self, *args):

        @mainthread
        def add_cam():
            sm.add_widget(self.camera)
            Clock.schedule_once(self.check_camera, .5)

        def load_cam(*args):
            self.camera = CameraScreen(name='camera')
            add_cam()

        def load_screen(*args):
            initial = time()
            self.HomeScreen = HomeScreen(name='HomeScreen')

            self.SettingScreen = Setting(name='setting')
            self.InfoScreen = ObjectInfo(name='ObjectInfo')
            sm.add_widget(self.HomeScreen)
            sm.add_widget(self.SettingScreen)
            sm.add_widget(self.InfoScreen)
            if WIN:
                threading.Thread(target=load_cam, daemon=True).start()


            else:
                self.camera = CameraScreen(name='camera')
                sm.add_widget(self.camera)
            self.time_taken = time() - initial
            ##print(f'{self.time_taken = }')
            self.StartScreen.ids.progress_percent.anim_speed= .4
            self.StartScreen.ids.progress_percent.current_percent = 100
            if self.InfoDict != {}:

                self.start_call = True
                self.dark_mode = self.InfoDict['DARK_MODE'] if not SYSTEM_DARK_MODE else SYSTEM_DARK_MODE
                if ANDROID:
                    if not self.dark_mode:
                        statusbar(colors[self.theme_cls.primary_palette]['500'], nav_color='white')
                    ##print(f'{self.dark_mode = }')
                    self.start_call = False

            else:
                if ANDROID: statusbar('5433fe', nav_color='white')
            self.start_call = False
            self.add_card()
            if self.time_taken > 9.5 and self.show_optimise:
                if self.optimise:
                    self.reduce_preview_size()
                else:
                    if self.time_taken > 12:
                        widget = self.HomeScreen.ids.grid_layout if self.InfoDict != {} else self.NoImage
                        self.banner = MDBanner(type='three-line',
                                               text=['[b]Decrease Loading Time',
                                                     'It will result in lower camera preview',
                                                     'quality, but loading time will be less.'],
                                               left_action=[
                                                   f"Make it Fast [font=Icons] {md_icons['lightning-bolt']}[/font]",
                                                   lambda x: self.reduce_preview_size()],
                                               right_action=["Don't show again",
                                                             lambda x: exec("self.InfoDict['SHOW_OPTIMISE']=False",
                                                                            {'self': self})],
                                               over_widget=widget)
                        self.HomeScreen.add_widget(self.banner)
                        self.banner.show()

        if ANDROID:
            statusbar('5433fe', nav_color='a4fdcb')

        Clock.schedule_once(load_screen)
        self.content_cls = self.Voicereco()
        self.dialog = CustomDialog(type="custom", content_cls=self.content_cls,
                                   size_hint=(0.9, dp(380) / Window.size[1]), pos_hint={'center_y': .55},
                                   buttons=[
                                       MDFlatButton(text='CLOSE', on_release=self.dismiss_dialog),
                                       MDRoundFlatIconButton(text='[font=Poppins]Take Picture[/font]',
                                                             icon='camera', disabled=True, on_release=self.save)],
                                   on_dismiss=self.check_dismiss)
        Window.bind(on_keyboard=self.go_back)
        self.screen_history = []

    def build(self):
        Builder.load_file('classes.kv')
        self.theme_cls.theme_style = 'Dark' if (self.InfoDict != {} and self.InfoDict[
            'DARK_MODE']) or SYSTEM_DARK_MODE else 'Light'
        #print(f'{self.theme_cls.theme_style = }')
        self.StartScreen = StartScreen()
        sm.add_widget(self.StartScreen)
        sm.transition = CardTransition(mode='push', direction="left", duration=.2)
        if ANDROID:
            request_permissions([Permission.RECORD_AUDIO, Permission.CAMERA])
        return sm

    def on_dark_mode(self, inst, active):

        if self.start_call:
            self.set_mode()
        else:
            radius = 1.3 * max(Window.size)
            self.SettingScreen.ids.circle_mode.opacity = 1
            self.anim = CustomAnimate(rad=radius, duration=.8, t='in_quad')
            self.anim.start(self.SettingScreen.ids.circle_mode)

    def set_mode(self):

        dark_mode = self.dark_mode
        #print(dark_mode)
        if dark_mode:
            statusbar(self.dark_hex, nav_color='black') if ANDROID else ''
            self.theme_cls.theme_style = 'Dark'
            self.theme_cls.primary_hue = '300'
        else:
            statusbar(colors[self.theme_cls.primary_palette]['500'], nav_color='white') if ANDROID else ''
            self.theme_cls.theme_style = 'Light'
            self.theme_cls.primary_hue = '500'

        self.SettingScreen.ids.circle_mode.rad = 0.1
        for im in self.HomeScreen.ids.grid_layout.children:
            im.tile_text_color = [0.5, 0.5, 0.5, 1]
            im.tile_text_color = self.theme_cls.accent_color if self.SettingScreen.ids.switch.active else [0, 0, 0,
                                                                                                           0]
            im.ids.checkbox.disabled_color = [0, 0, 0, 0]

    def check_height(self, dt):
        self.key_height = keyboard_height()
        if self.key_height > 0:
            self.HomeScreen.ids.textbox.y = self.key_height
            self.check_keyboard.cancel()

    def set_active(self):
        self.active = True

    def open_about(self):
        content = Factory.AboutClass()
        self.about_dialog = AKAlertDialog(header_icon='heart-circle')
        self.about_dialog.size_portrait=['300dp','380dp']
        self.about_dialog.auto_dismiss = True
        self.about_dialog.content_cls = content
        self.about_dialog.open()

    def open_web(self,github=False,youtube=False,email=False):
        if github:
            webbrowser.open('https://github.com/AM-ash-OR-AM-I/Find_MyStuff')
            toast('Star my repository if you like it :)')
        elif youtube:
            webbrowser.open('https://youtu.be/l2OCr50ifIw')
        elif email:
            webbrowser.open('https://mail.google.com/mail/u/0/#inbox?compose=new')
            Clipboard.copy('ashutoshmaha2909@gmail.com')
            toast('Email address Copied, Paste Email address to send email.')

    def shift_up(self, active):
        textbox = self.HomeScreen.ids.textbox
        if active:
            textbox.icon = 'close'
            if not self.key_height:
                self.check_keyboard = Clock.schedule_interval(self.check_height, .05)
            else:
                textbox.y = self.key_height
        else:
            self.active = active
            textbox.y = 0
            textbox.icon = 'plus'

    "Following methods are for dialog screen"

    def open_dialog(self):
        self.dialog.open()
        self.dialog.buttons[0].disabled = True if ANDROID else False

        if not self.content_cls.listening:
            self.content_cls.start_listening()

    def check_screen_exists(self, *args) -> "Waits to change the screen till the camera widget is loaded.":
        if 'camera' in sm.screen_names:
            self.spinner.dismiss()
            sm.current = 'camera'
            self.interval.cancel()

    def save(self, *args):
        if ANDROID:
            self.camera.ids.xcamera._camera._android_camera.startPreview()

        self.content_cls.say_again, self.content_cls.tell_place = False, False
        self.dict = {}
        self.object = self.content_cls.ids.object.text
        first = self.object[0].upper()
        self.object = first + self.object[1:]
        self.place = self.content_cls.ids.place.text

        if ANDROID:
            sm.current = 'camera'
        else:
            if 'camera' in sm.screen_names:
                sm.current = 'camera'
                self.camera.ids.xcamera.play = True
            else:
                self.spinner = CustomMDSpinner()
                self.spinner.open()
                self.interval = Clock.schedule_interval(self.check_screen_exists, .1)

        self.dismiss_dialog(self)
        # self.change_screen('camera')
        self.dict[self.object] = self.place
        self.filename = self.object + '.png'

    class Voicereco(MDBoxLayout):
        Builder.load_file('KV/DialogBox.kv')
        stop = BooleanProperty(False)
        say_again, tell_place, listening, animate = False, False, False, None
        win_listen = False
        if WIN:
            tts = p.init()
            tts.setProperty('rate', 135)
        dict = {}
        object, place = '', ''

        def animate_it(self, widget, *args) -> "Used to animate microphone.":
            widget.opacity = 0.15
            self.ids.instant.text = 'Listening'
            self.widget = widget
            self.rad = widget.rad
            self.animate = Animation(rad=self.rad * 1.8, duration=0.2)
            for i in range(15):
                self.animate += Animation(rad=self.rad * (1 + random.random()), duration=0.3)
            self.animate.start(self.widget)
            self.animate.repeat = True

        def stop_anim(self, *args):
            if ANDROID:
                if stt.listening:
                    stt.stop()
                self.checking_clock.cancel()
            Animation(rad=self.rad, opacity=0, duration=.1).start(self.widget)
            #print('animation cancelled')
            MDApp.get_running_app().dialog.buttons[0].disabled = False
            self.listening = False
            self.animate.stop(self.widget)
            self.ids.microphone.md_bg_color = [0.5, 0.5, 0.5, 1]

        def start_listening(self, *args):

            self.listening = True
            self.animate_it(self.ids.ellipse)
            self.ids.microphone.md_bg_color = MDApp.get_running_app().theme_cls.primary_color
            if ANDROID:

                if stt.listening:
                    stt.stop()
                    # #print('stt is started while it was listening stopping it...')
                    return
                stt.start()
                self.stop = False
                self.checking_clock = Clock.schedule_interval(self.check_state, 1 / 5)

            elif WIN:
                def voicethread():
                    #print('Voice Thread Starts')
                    r = sr.Recognizer()
                    try:
                        self.win_listen = True
                        with sr.Microphone() as source:
                            r.adjust_for_ambient_noise(source, duration=.5)
                            audio = r.listen(source, timeout=4)

                        #print('Stops Listening')
                        self.recognized_text = r.recognize_google(audio)
                        #print('Recognized audio', self.recognized_text)
                        self.win_listen = False
                        self.stop_listening()
                    except sr.UnknownValueError:
                        self.stop_anim()
                        self.win_listen = False
                        toast("Google Speech Recognition could not understand audio")

                    except sr.RequestError as e:
                        self.stop_anim()
                        self.win_listen = False
                        toast("Could not request results from Google Speech Recognition service; {0}".format(e))

                    except sr.WaitTimeoutError:
                        self.stop_anim()
                        self.win_listen = False
                        toast("Something Went Wrong.")

                if not self.win_listen:
                    threading.Thread(target=voicethread, daemon=True).start()

        def stop_listening(self, *args):
            self.ids.object.disabled = False
            self.ids.place.disabled = False
            self.stop_anim()
            if ANDROID:
                #print(f'{stt.results=}')
                if stt.results != []:
                    self.recognized_text = stt.results[0]
                    self.ids.instant.text = self.recognized_text

                else:
                    self.recognized_text = ''
                    self.ids.instant.text = "Can't understand, try again :("
                    toast("Can't Recognize speech")
                    threading.Thread(target=tts.speak, args=("Sorry Couldn't recognize",), daemon=True).start()

            #print(f'{self.recognized_text = }')
            if self.recognized_text != '':

                "Gets rid of part that serves no information."

                separator = False
                word_list = self.recognized_text.split(' ')
                for i in ['is', 'does', 'are', 'has', 'have', 'a', 'the']:
                    if i in word_list:
                        word_list.remove(i)

                self.recognized_text = ' '.join(word_list)

                "Tries to separate sentence using PREPOSITIONS unless, tell_place is True"
                if not self.tell_place:
                    self.object, self.place = '', ''
                    for prep in PREPOSITIONS:
                        if prep in word_list:
                            #print(f'{prep = }')
                            ind = word_list.index(prep)
                            self.object = ' '.join(word_list[:ind])
                            self.place = ' '.join(word_list[ind + 1:])
                            break
                    if (self.object, self.place) != ('', ''):
                        separator = True
                #print(f'{(self.object, self.place) = }')

                if separator and not self.tell_place:
                    "If it is able to separate"

                    if ANDROID:
                        say = f'Okay, saving info about {self.object}'
                        threading.Thread(target=tts.speak, args=(say,), daemon=True).start()

                    elif WIN:
                        self.tts.say(f'Okay, saving info about {self.object}')
                        self.tts.runAndWait()
                    self.ids.object.text = self.object
                    self.ids.place.text = self.place


                elif not self.say_again:
                    "Couldn't separate object & place thus Asks for object to user."

                    self.ids.instant.text = "Can't understand, please tell the object :("
                    self.say_again = True
                    if WIN:
                        self.tts.say("Sorry what's the object please?")
                        self.tts.runAndWait()
                    elif ANDROID:
                        say = "Sorry what's the object please?"
                        threading.Thread(target=tts.speak, args=(say,), daemon=True).start()
                    Clock.schedule_once(self.start_listening, 2.3)

                else:
                    "Saves object & Asks for place"

                    if not self.tell_place:
                        self.ids.instant.text = "Got it! Now, tell me the place"
                        self.tell_place = True
                        self.object = self.recognized_text
                        if ANDROID:
                            say = 'Okay, Can you please tell the place?'
                            threading.Thread(target=tts.speak, args=(say,), daemon=True).start()
                        elif WIN:
                            self.tts.say('Okay, Can you please tell the place?')
                            self.tts.runAndWait()
                        self.ids.object.text = self.recognized_text

                        Clock.schedule_once(self.start_listening, 2.3)

                    else:
                        # Saves object & place
                        self.tell_place = False
                        self.say_again = False
                        if ANDROID:
                            say = 'Edit object if you want'
                            threading.Thread(target=tts.speak, args=(say,), daemon=True).start()
                        elif WIN:
                            self.tts.say('Edit object if you want')
                            self.tts.runAndWait()
                        self.ids.place.text = self.recognized_text
                        self.dict[self.ids.object.text] = self.recognized_text

            else:
                self.tell_place, self.say_again = False, False

        def on_stop(self, *args):
            if not stt.listening and self.stop:
                self.stop_listening()

        def check_state(self, dt):
            # Updates text every 1/5th sec. also checks whether stt is listening or not.
            if stt.listening:
                try:
                    if stt.partial_results != []:
                        self.ids.instant.text = stt.partial_results[len(stt.partial_results) - 1]
                    else:
                        self.ids.instant.text = 'Recognizing...'
                except AttributeError as e:
                    toast(f'Some Error occurred, error Code = {e}')
            if not stt.listening and not self.stop:
                self.stop = True

    def open_theme(self):
        if self.theme_picker is None:
            self.theme_picker = MDThemePicker()
        self.theme_picker.open()

    def save_info(self):
        #print('Saving Stuff')
        self.InfoDict['PREVIEW_SIZE'] = self.avail_preview_size
        self.InfoDict['PREVIEW_INDEX'] = self.set_preview_index
        self.InfoDict['OPTIMISE'] = self.optimise
        self.InfoDict['DARK_MODE'] = self.dark_mode
        self.InfoDict['PRIMARY_PALETTE'] = self.theme_cls.primary_palette
        self.InfoDict['TEXT_SIZE'] = self.text_size
        self.InfoDict['GRID_SIZE'] = self.grid.cols
        self.InfoDict['SHOW_TEXT'] = self.SettingScreen.ids.switch.active
        with open('Data/theme_details.txt', 'w')as f:
            f.write(str(self.InfoDict))

    def on_stop(self):
        self.save_info()

    def on_pause(self):
        try:
            self.save_info() if sm.current != 'Start' else ''
        except AttributeError as e:
            print(e)
        return True

    def dismiss_dialog(self, obj):
        self.button_pressed = True
        try:
            self.content_cls.stop_anim(None)
            self.dialog.dismiss() if not self.content_cls.listening else None

        except AttributeError:
            pass

        self.button_pressed = False

    def change_tool(self, *args):
        self.show_text = True if self.prev_state else False
        for image in self.grid.children:
            image.ids.checkbox.disabled = True
            image.ids.checkbox.active = False
        self.ignore_release = False
        self.toolbar_change = False

    def find_image(self, text: 'Text From TextField'):
        if len(text) >= 3 or text == '':
            image_list = find(key=text, data=self.list)
            if self.prev_list != image_list:
                self.prev_list = image_list
                self.grid.clear_widgets()
                self.index = 0
                tile_text_color = self.theme_cls.accent_color if self.show_text else [0, 0, 0, 0]
                box_color = [0, 0, 0, 0.3] if self.show_text else [0, 0, 0, 0]
                for i in image_list:
                    for d in self.list:
                        if i in d:
                            self.index = self.list.index(d)
                            break

                    self.grid.add_widget(
                        MyImage(source=f'{i}.png',
                                text=f'[font=Poppins][size={int(dp(self.text_size))}]{i}[/size][/font]',
                                tile_text_color=tile_text_color, box_color=box_color, index=self.index))
                    self.source_list.append(i)

    def update_index(self, image):
        for index in range(len(self.list)):
            # #print(f'{image.source[:-4] = }, {self.list[index] = }\n{image.source[:-4] in self.list[index] =}')
            if image.source[:-4] in self.list[index]:
                image.index = index
                break
            self.index = index + 1

    def remove_tile(self, *args):
        lst = list(self.grid.children)  # Stored in another list so that we can remove widget
        for image in lst:
            self.update_index(image)
            if image.source in self.delete_dict:
                if self.delete_dict[image.source]:
                    self.grid.remove_widget(image)
                    del self.delete_dict[image.source]

    def delete_object(self, *args):
        c = 0
        for d in self.list:
            if d != {}:
                image_source = list(d.keys())[0] + '.png'
                #print(f'{self.list = }{self.delete_dict=}{d=}')
                if image_source in self.delete_dict:

                    if self.delete_dict[image_source]:
                        # #print('gets Deleted')
                        if os.path.exists(image_source):
                            os.remove(image_source)  # Deletes the image file
                        del d[image_source[:-4]]

        # # #print(f'{c = }')
        self.list.remove({})
        self.remove_tile()
        threading.Thread(target=self.write_file, args=(self,), daemon=True).start()
        self.change_tool()
        if self.list == []:
            self.image_exists = False
        else:
            for item in self.list:
                if item != {}:
                    break
                else:
                    c += 1
            if c == len(self.list):
                self.image_exists = False

        #print(f'{self.list=}')

    def write_file(self, *args):
        c = 0
        with open('Data/object_dict', 'wb')as f:
            for d in self.list:
                c += 1
                if d != {}:
                    pickle.dump(d, f)

    def on_toolbar_change(self, obj, delete=False):
        #print('Toolbar_changed', f'{delete = } , {obj = }')
        toolbar = self.HomeScreen.ids.toolbar
        if delete:
            factor = .7 if not self.dark_mode else 1.5
            md_bg_color = [factor * value for value in toolbar.md_bg_color[:-1]] + [1]
            self.prev_color = list(toolbar.md_bg_color)
            self.prev_left_items = toolbar.left_action_items
            self.prev_right_items = toolbar.right_action_items  # Selecting and unselecting the picture changes toolbar
            self.prev_title = toolbar.title
            toolbar.left_action_items = [['close', lambda x: self.change_tool()]]
            toolbar.right_action_items = [['trash-can', lambda x: self.delete_object()]]
            toolbar.title = 'Delete selected'
            Animation(md_bg_color=md_bg_color, d=.15).start(toolbar)

        else:

            toolbar.md_bg_color = self.prev_color
            toolbar.left_action_items = self.prev_left_items
            toolbar.right_action_items = self.prev_right_items
            toolbar.title = self.prev_title

    def check_dismiss(self, obj):
        return True if not self.button_pressed else False

    def call(self, icon):
        if self.drop is None:
            self.drop = MDDropdownMenu(
                caller=icon,
                items=[{
                    "text": f"Cols = {i}",
                    "height": dp(66),
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x=f"{i}": self.change_grid(x),
                } for i in range(1, 6)],
                width_mult=2, )
        self.drop.open()

    def change_grid(self, x: int(n_col)):
        image_list = self.grid.children
        new_grid = int(x)
        if image_list[0].tile_text_color != [0, 0, 0, 0]:
            # #print('Changing text size')
            prev_grid = self.grid.cols
            old_text_size = self.text_size
            self.text_size = old_text_size * prev_grid / new_grid
            # #print(f'{self.text_size = } , {old_text_size = }')

            for im in image_list:
                if im.tile_text_color != [0, 0, 0, 0]:
                    text = im.text
                    text = text.replace('%d' % dp(old_text_size), '%d' % dp(self.text_size))
                    im.text = text
                else:
                    break
        self.grid.cols = new_grid

    def on_show_text(self, instance, show_text):

        right_list = self.HomeScreen.ids.toolbar.right_action_items
        if not show_text:
            if len(right_list) == 3:
                right_list.pop(1)
        else:
            if len(right_list) != 3:
                right_list.insert(1, ['format-font-size-increase', lambda x: self.open_dropdown(x),
                                      'Change Image Text Size'])
        image_list = self.grid.children
        for im in image_list:
            if not show_text:
                im.tile_text_color = [0, 0, 0, 0]
                im.box_color = [0, 0, 0, 0]

            else:
                im.tile_text_color = self.theme_cls.accent_color
                im.box_color = [0, 0, 0, 0.3]

    def darker(self, factor):
        r, g, b, a = self.theme_cls.primary_color
        r *= factor
        g *= factor
        b *= factor
        return r, g, b, a

    def on_landscape(self, instance, landscape):
        if ANDROID:
            self.landscape = landscape
            if not landscape:
                self.angle = 90
            else:
                self.angle = -90
            lst = self.camera.ids
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

    def change_scale(self, scaling):
        image_list = self.grid.children
        if image_list[0].text != '':
            # #print('Changing text size')
            old_text_size = self.text_size
            if self.prev_scale != scaling:
                self.text_size = self.text_size * scaling / self.prev_scale
                # #print(f'{self.text_size = }')
                for im in image_list:
                    if im.text != '':
                        text = im.text
                        text = text.replace('%d' % dp(old_text_size), '%d' % dp(self.text_size))
                        im.text = text
                    else:
                        break
            self.prev_scale = scaling

    def open_dropdown(self, icon):
        if self.drop2 is None:
            self.drop2 = MDDropdownMenu(caller=icon,
                                        items=[{
                                            "text": f"{i / 10}",
                                            "height": dp(46),
                                            "viewclass": "OneLineListItem",
                                            "on_release": lambda x=f"{i / 10}": self.change_scale(float(x)),
                                        } for i in range(6, 16, 2)],
                                        width_mult=1, )
        self.drop2.open()

    def back_button(self, home_screen=False, *args):
        if not home_screen:
            self.screen_history.pop()
        else:
            self.screen_history = ['HomeScreen']
        sm.transition.mode = 'pop'
        sm.transition.direction = 'right'
        sm.current = self.screen_history[-1]

    def add_card(self, *args):
        self.grid = self.HomeScreen.ids.grid_layout
        self.NoImage = Kivy_Image(source='Data/NoImage_grey_small.png', opacity=.5,
                                  pos_hint={'center_y': .7, 'center_x': .5},
                                  size_hint=(0.5, 0.5))
        if not FIRST_TIME:
            self.list = []
            with open('Data/object_dict', 'rb')as f:
                try:
                    while True:
                        self.list.append(pickle.load(f))
                except EOFError:
                    if self.list != []:
                        self.index = 0
                        for d in self.list:
                            for i in d:
                                self.grid.add_widget(
                                    MyImage(source=f'{i}.png',
                                            text=f'[font=Poppins][size={int(dp(self.text_size))}]{i}[/size][/font]',
                                            tile_text_color=self.theme_cls.accent_color, index=self.index))
                                self.source_list.append(i)
                            self.index += 1
                    else:
                        self.image_exists = False

        else:
            self.image_exists = False

        def call_change(*args):

            self.change_screen('HomeScreen')
            if 'SHOW_TEXT' in self.InfoDict:
                self.show_text = self.InfoDict['SHOW_TEXT']


        Clock.schedule_once(call_change,.8)

    def on_image_exists(self, instance, exists):
        setting = self.SettingScreen
        right_items = self.HomeScreen.ids.toolbar.right_action_items
        # #print(f'{setting.ids.switch_item = }\n{exists = }')

        if not exists:
            self.HomeScreen.add_widget(self.NoImage)
            setting.ids.switch.disabled = True
            setting.ids.image_text.md_bg_color_disabled = [0, 0, 0, 0]
            setting.ids.switch_item.disabled = True
            remove_list = []

            for icon_list in right_items:
                if icon_list[0] in ('format-font-size-increase', 'view-grid'):
                    remove_list.append(icon_list)

            for icon in remove_list:
                right_items.remove(icon)

        else:
            self.HomeScreen.remove_widget(self.NoImage)
            setting.ids.switch.disabled = False
            setting.ids.switch_item.disabled = False

            if len(right_items) == 1:
                right_items.insert(0, ['format-font-size-increase', lambda x: self.open_dropdown(x),
                                       'Change Image Text Size'])
                right_items.insert(0, ["view-grid", lambda x: self.call(x), "Change grid size"])

    def update_info(self, object, place):
        def write_stuff(object, place):
            ind = 0
            if self.add_picture:  # Creating new object

                self.list.append({object: place})
                with open('Data/object_dict', 'ab')as f:
                    pickle.dump({object: place}, f)

            else:
                for dict in self.list:  # Updating existing info
                    ind += 1
                    if object in dict:
                        dict[object] = place
                    with open('Data/object_dict', 'wb')as f:
                        for d in self.list:
                            pickle.dump(d, f)
                    return
            # #print('Stuff Updated')

        threading.Thread(target=write_stuff, args=(object, place)).start()

    def update_home(self):
        if not self.image_exists:  # Removing Sad face
            self.image_exists = True
        self.grid.add_widget(
            MyImage(source='%s.png' % self.InfoScreen.ids.heading.text,
                    text=f'[font=Poppins][size={int(dp(self.text_size))}]{self.InfoScreen.ids.heading.text}[/size][/font]',
                    tile_text_color=self.theme_cls.accent_color if self.show_text else [0, 0, 0, 0],
                    box_color=[0, 0, 0, 0.3] if self.show_text else [0, 0, 0, 0],
                    index=self.index))
        self.source_list.append(self.InfoScreen.ids.heading.text)
        self.index += 1

    def tap_target(self, *args):
        if FIRST_TIME:
            self.tap_plus = MDTapTargetView(widget=self.HomeScreen.ids.plus, title_text="Add Object",
                                            title_text_size="20sp", outer_radius=dp(150),
                                            description_text="Tap this to add\n objects and their info.",
                                            description_text_bold=True,
                                            widget_position="right_bottom")

            Clock.schedule_once(self.tap_state, .3)

    c = 0

    def tap_state(self, *args):
        if self.tap_plus.state == "close":
            self.tap_plus.start()
        else:
            self.tap_plus.stop()

    def add_info_object(self, *args):
        @mainthread
        def add_pic(*args):
            self.InfoScreen.ids.im.source = self.filename
            self.InfoScreen.ids.circle_bounce.active = False
            self.InfoScreen.ids.check.disabled = False
            self.InfoScreen.ids.im.opacity = 1
            #print('Image added')

        def rotate_resize():
            i = time()
            img = Image.open(self.filename)
            ratio = img.size[0] / img.size[1]
            #print(ratio)
            resize = img.resize((int(ratio * 900), 900))
            if not self.landscape:
                rot_img = resize.transpose(Image.ROTATE_270)
                #print(f'{rot_img.size = }')
            else:
                rot_img = resize
            rot_img.save(self.filename)
            #print(f'Time taken = {time() - i}')
            Clock.schedule_once(add_pic)

        self.InfoScreen.ids.im.opacity = 0
        self.InfoScreen.ids.check.disabled = True
        self.InfoScreen.ids.heading.text = self.object
        self.InfoScreen.ids.place.text = self.place
        self.change_screen('ObjectInfo')
        self.InfoScreen.ids.circle_bounce.active = True
        self.add_picture = True
        if ANDROID:
            threading.Thread(target=rotate_resize).start()
        else:
            self.camera.ids.xcamera.play = False
            threading.Thread(target=rotate_resize).start()

    def image_clicked(self, image):
        self.change_screen('ObjectInfo')
        self.InfoScreen.ids.heading.text = image.source[:len(image.source) - 4]
        self.InfoScreen.ids.place.text = self.list[image.index][image.source[:len(image.source) - 4]]
        self.InfoScreen.ids.im.source = image.source[:len(image.source) - 4] + '.png'

    def crop_image(self, *args):
        img = Image.open(self.filename)
        height, width = img.size[1], img.size[0]
        crop_left, crop_top = (width - height) // 2, 0
        img_crop = img.crop((crop_left, crop_top, width - crop_left, height))
        img_crop.resize((1000, 1000))
        img_crop.save(self.filename)

    def change_screen(self, screen_name, *args):
        sm.transition.mode = 'push'
        sm.transition.direction = 'left'
        sm.current = screen_name
        self.screen_history.append(screen_name)
        # #print(self.screen_history)

    def go_back(self, instance, key, *a):

        if key in (27, 1001):
            self.screen_history.pop()
            if self.screen_history != []:
                sm.transition.mode = 'pop'
                sm.transition.direction = 'right'
                sm.current = self.screen_history[-1]

            else:
                self.stop()
        return True

    def generate_light_color(self, factor):
        color = self.theme_cls.primary_color
        color[-1] = factor * color[-1]
        return color

    def get_toolbar_icon(self, toolbar: object, icon_name: str):
        parent = toolbar.children[0].children  # List of multiple icons in Toolbar
        for icon_obj in parent:
            if icon_obj.icon == icon_name:
                return icon_obj
        Logger.warning(f"get_toolbar_icon: Couldn't find icon {icon_name}")


sm: ScreenManager = ScreenManager()
MainApp().run()
