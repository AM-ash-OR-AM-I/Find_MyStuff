import os
import threading
from random import random
from time import time
from kivy import platform
from kivy.animation import Animation
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.metrics import dp
from kivy.properties import BooleanProperty
from PIL import Image
from kivy.uix.modalview import ModalView
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen

PREPOSITIONS = ['about', 'above', 'across', 'after', 'against', 'among', 'around', 'at', 'before', 'behind', 'below',
                'beside', 'between', 'by', 'down', 'during', 'for', 'from', 'in', 'inside', 'into', 'near', 'of', 'off',
                'on', 'out', 'over', 'through', 'to', 'toward', 'under', 'up', 'with', 'aboard', 'along', 'amid', 'as',
                'beneath', 'beyond', 'but', 'concerning', 'considering', 'despite', 'except', 'following', 'like',
                'minus', 'next', 'onto', 'opposite', 'outside', 'past', 'per', 'plus', 'regarding', 'round', 'save',
                'since', 'than', 'till', 'underneath', 'unlike', 'until', 'upon', 'versus', 'via', 'within', 'without']

if platform == 'win':
    import speech_recognition as sr

    WIN = True
    ANDROID = False

elif platform == 'android':
    from Speechrecognizer import stt

    ANDROID = True
    WIN = False


class CustomMDSpinner(ModalView):
    pass


app = MDApp.get_running_app()
app.load_file('ObjectInfo.kv')


class CustomDialog(MDDialog):
    radius = dp(20), dp(20), dp(20), dp(20)

    def on_dismiss(self):
        super().on_dismiss()
        app.InfoScreen.stop_anim()
        return False


class ObjectInfo(MDScreen):
    stop = BooleanProperty(False)
    say_again = tell_place = listening = win_listen = False
    first_call = True
    object = place = previous_object = ''
    dict = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content_cls = Factory.VoiceRecognizer()
        self.spinner = CustomMDSpinner()
        self.dialog = CustomDialog(type='custom', size_hint=(dp(268) / Window.width, dp(268) / Window.height),
                                   content_cls=self.content_cls, overlay_color=[0, 0, 0, .15])

    def open_dialog(self):

        self.ids.im.opacity = 0
        self.ids.object.text = ''
        self.ids.place.text = ''
        self.previous_object = ''
        if not app.sm.current == 'ObjectInfo':
            app.change_screen('ObjectInfo')
        self.dialog.open()
        if not self.listening:
            Clock.schedule_once(self.start_listening)

    def get_list(self, list_of_dictionaries, option):
        new_list = []
        print(list_of_dictionaries)
        if option == 'object':
            for d in list_of_dictionaries:
                for object in d.keys():
                    new_list.append(object)
        else:
            for d in list_of_dictionaries:
                for place in d.values():
                    new_list.append(place)
        return new_list

    def check_object_changed(self, *args):

        new_object = self.ids.object.text
        new_place = self.ids.place.text
        list_dict = app.HomeScreen.list
        if new_object != self.previous_object:  # if object is changed.
            list_objects = self.get_list(list_dict, 'object')
            if self.previous_object in list_objects:
                os.rename(self.previous_object + '.png', new_object + '.png')
                index = list_objects.index(self.previous_object)
                list_dict.pop(index)
                print(f'List after pop {list_objects = }\n{list_dict = }')
                list_dict.insert(index, {new_object: new_place})
                app.HomeScreen.write_file()
                app.HomeScreen.update_pic(old_info=(self.previous_object, self.previous_place),
                                          new_info=(new_object, new_place))
                print(f'{list_dict = }]\n{app.HomeScreen.list = }')

        elif new_place != self.previous_place:
            list_place = self.get_list(list_dict, 'place')
            print(f'{list_place = }')
            if self.previous_place in list_place:
                index = list_place.index(self.previous_place)
                list_dict.pop(index)
                app.HomeScreen.write_file()
                list_dict.insert(index, {new_object: new_place})
                print(f'{list_dict = }]\n{app.HomeScreen.list = }')
            print('Place Changed')

        else:
            print('No change')

    def save(self, *args):
        def check_screen_exists(*args) -> "Waits to change the screen till the camera widget is loaded.":
            if 'camera' in app.sm.screen_names:
                self.spinner.dismiss()
                app.change_screen('camera')
                self.interval.cancel()

        if ANDROID:
            app.camera.ids.xcamera._camera._android_camera.startPreview()

        self.say_again, self.tell_place = False, False
        self.dict = {}
        self.object = self.ids.object.text
        self.place = self.ids.place.text

        if ANDROID:
            app.change_screen('camera')
        else:
            if 'camera' in app.sm.screen_names:
                print(f'{app.sm.screen_names = }')
                app.change_screen('camera')
                app.camera.ids.xcamera.play = True
            else:
                self.spinner.open()
                self.interval = Clock.schedule_interval(check_screen_exists, .1)

        self.dialog.dismiss()
        # self.change_screen('camera')
        self.dict[self.object] = self.place
        self.filename = self.object + '.png'

    def image_clicked(self, image):
        app.change_screen('ObjectInfo')
        self.ids.im.opacity = 1
        self.ids.object.text = image.source[:len(image.source) - 4]
        self.ids.place.text = app.HomeScreen.list[image.index][image.source[:len(image.source) - 4]]
        self.ids.im.source = image.source[:len(image.source) - 4] + '.png'
        self.previous_object = self.ids.object.text
        self.previous_place = self.ids.place.text

    def add_info_object(self, *args):
        @mainthread
        def add_pic(*args):
            for image in app.HomeScreen.grid.children:
                if image.source == self.ids.im.source:
                    image.reload()
                    break
            if self.ids.im.source and self.ids.im.opacity:
                self.ids.im.reload()

            else:
                self.ids.im.source = self.filename
            self.spinner.dismiss()
            self.ids.im.opacity = 1
            app.resize_in_progress = False
            print('Image added')

        def rotate_resize():
            i = time()
            img = Image.open(self.filename)
            ratio = img.size[0] / img.size[1]
            print(ratio)
            resize = img.resize((int(ratio * 900), 900))
            if not app.camera.landscape:
                rot_img = resize.transpose(Image.ROTATE_270)
                print(f'{rot_img.size = }')
            else:
                rot_img = resize
            rot_img.save(self.filename)
            print(f'Time taken = {time() - i}')
            Clock.schedule_once(add_pic)

        self.ids.object.text = self.object
        self.ids.place.text = self.place
        self.spinner.open()
        if ANDROID:
            threading.Thread(target=rotate_resize).start()
        else:
            app.camera.ids.xcamera.play = False
            threading.Thread(target=rotate_resize).start()

        app.resize_in_progress = True
        if not self.ids.im.opacity or not self.ids.im.source:
            app.HomeScreen.add_picture = True
        app.back_button()

    def animate_it(self, widget, *args) -> "Used to animate microphone.":
        widget.opacity = 0.15
        self.content_cls.ids.instant.text = 'Listening..'
        self.widget = widget
        self.rad = widget.rad
        self.animate = Animation(rad=self.rad * 1.8, duration=0.2)
        for i in range(15):
            self.animate += Animation(rad=self.rad * (1 + .6 * random()), duration=0.3)
        self.animate.start(self.widget)
        self.animate.repeat = True

    def stop_anim(self, *args):
        if ANDROID:
            if stt.listening:
                stt.stop()
                self.checking_clock.cancel()
        Animation(rad=self.rad, opacity=0, duration=.1).start(self.widget)
        self.listening = False
        self.animate.stop(self.widget)
        self.content_cls.ids.microphone.md_bg_color = [0.5, 0.5, 0.5, 1]

    def start_listening(self, *args):

        self.listening = True
        self.animate_it(self.content_cls.ids.ellipse)
        self.content_cls.ids.microphone.md_bg_color = app.theme_cls.primary_color
        if ANDROID:
            if stt.listening:
                print('stt is started while it was listening, not doing anything now...')
                return
            stt.start()
            self.stop = False
            self.checking_clock = Clock.schedule_interval(self.check_state, 1 / 6)

        elif WIN:
            def voicethread():
                print('Voice Thread Starts')
                r = sr.Recognizer()
                try:
                    self.win_listen = True
                    with sr.Microphone() as source:
                        r.adjust_for_ambient_noise(source, duration=.2)
                        audio = r.listen(source, timeout=4)

                    print('Stops Listening')
                    self.recognized_text = r.recognize_google(audio)
                    print('Recognized audio', self.recognized_text)
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
        self.stop_anim()
        if ANDROID:
            print(f'{stt.results =}')
            if stt.results != []:
                self.recognized_text = stt.results[0]
                self.content_cls.ids.instant.text = self.recognized_text

            else:
                self.recognized_text = ''
                # TODO: In dark mode there is a grey background in dialog/ box. Still It's not fixed, if u use anim.
                self.dialog.dismiss()

        print(f'{self.recognized_text = }')
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
                        print(f'{prep = }')
                        ind = word_list.index(prep)
                        self.object = ' '.join(word_list[:ind])
                        self.place = ' '.join(word_list[ind + 1:])
                        break
                if (self.object, self.place) != ('', ''):
                    separator = True
            print(f'{(self.object, self.place) = }')

            if separator and not self.tell_place:
                "If it is able to separate"

                self.ids.object.text = self.object
                self.ids.place.text = self.place
                self.dialog.dismiss()

            else:
                "Saves object & Asks for place"

                if not self.tell_place:
                    self.content_cls.ids.instant.text = "Got it! Now, tell me the place"
                    self.tell_place = True
                    self.object = self.recognized_text
                    self.ids.object.text = self.recognized_text

                    Clock.schedule_once(self.start_listening, 1.5)

                else:
                    # Saves object & place
                    self.content_cls.ids.instant.text = "Listening"
                    self.tell_place = False
                    self.ids.place.text = self.recognized_text
                    self.dict[self.ids.object.text] = self.recognized_text
                    self.dialog.dismiss()

        else:
            self.tell_place = False

    def on_stop(self, *args):
        if not stt.listening and self.stop:
            self.stop_listening()

    def check_state(self, dt):
        # Updates text in a interval also checks whether stt is listening or not.
        if stt.listening:
            try:
                if stt.partial_results != []:
                    self.content_cls.ids.instant.text = stt.partial_results[-1]
                else:
                    self.content_cls.ids.instant.text = 'Recognizing...'
            except AttributeError as e:
                toast(f'Some Error occurred, error Code = {e}')
        if not stt.listening and not self.stop:
            self.stop = True
