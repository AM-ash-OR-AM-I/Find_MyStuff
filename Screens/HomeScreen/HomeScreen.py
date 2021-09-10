import os
import pickle
import threading
from kivy.animation import Animation
from kivy.uix.image import Image
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import BooleanProperty, NumericProperty, ColorProperty
from kivy.clock import Clock
from kivymd.theming import ThemableBehavior
from Modules.taptargetview import MDTapTargetView
from kivymd.uix.menu import MDDropdownMenu
from kivymd.color_definitions import custom_light_color
from kivymd.uix.behaviors import TouchBehavior, MagicBehavior
from kivymd.uix.imagelist import SmartTileWithLabel
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from Modules.find import find

FIRST_TIME = True if not os.path.exists('Data/object_dict') else False
app = MDApp.get_running_app()

app.load_file('HomeScreen.kv')


class HomeScreen(MDScreen, ThemableBehavior):
    toolbar_change = BooleanProperty(False)
    show_text = BooleanProperty(True)
    image_exists = BooleanProperty(True)
    active = first_use = True
    ignore_release = add_picture = change_home = key_height = False
    delete_dict = {}
    drop = drop2 = NoImage = prev_state = None
    list, source_list, prev_list = [], [], []
    index, prev_scale, n_col = 0, 1, 2

    def on_enter(self, *args):
        if self.first_use and FIRST_TIME:
            self.tap_target()
        elif not self.first_use:
            if app.InfoScreen.ids.object.text!='':
                self.update_info(object=app.InfoScreen.ids.object.text, place=app.InfoScreen.ids.place.text)
            if self.add_picture:
                self.update_home()
            else:
                if app.InfoScreen.ids.object.text != ''and app.InfoScreen.previous_object!='':
                    app.InfoScreen.check_object_changed()

            self.add_picture = False
        self.first_use = False

    def on_list(self,*args):
        print(f'{self.list = }')

    def change_tool(self, *args):
        self.toolbar_change = False
        self.show_text = True if self.prev_state else False
        for image in self.grid.children:
            image.ids.checkbox.disabled = True
            image.ids.checkbox.active = False
        self.ignore_release = False

    def on_toolbar_change(self, obj, delete=False):
        print('Toolbar_changed', f'{delete = } , {obj = }')
        toolbar = self.ids.toolbar
        if delete:
            self.prev_color = list(toolbar.md_bg_color)
            self.prev_left_items = toolbar.left_action_items
            self.prev_right_items = toolbar.right_action_items  # Selecting and unselecting the picture changes toolbar
            self.prev_title = toolbar.title
            toolbar.left_action_items = [['close', lambda x: self.change_tool()]]
            toolbar.right_action_items = [['trash-can', lambda x: self.delete_object()]]
            toolbar.title = 'Delete selected'
            if not app.dark_mode:
                if toolbar.md_bg_color != [1, 1, 1, 1]:
                    factor = .7
                else:
                    return
            else:
                factor = 1.5
            md_bg_color = [factor * value for value in toolbar.md_bg_color[:-1]] + [1]

            Animation(md_bg_color=md_bg_color, d=.15).start(toolbar)

        else:

            toolbar.md_bg_color = self.prev_color
            toolbar.left_action_items = self.prev_left_items
            toolbar.right_action_items = self.prev_right_items
            toolbar.title = self.prev_title

    def on_image_exists(self, instance, exists):
        setting = app.SettingScreen
        right_items = self.ids.toolbar.right_action_items
        # #print(f'{setting.ids.switch_item = }\n{exists = }')

        if not exists:
            self.add_widget(self.NoImage)
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
            self.remove_widget(self.NoImage)
            setting.ids.switch.disabled = False
            setting.ids.switch_item.disabled = False

            if len(right_items) == 1:
                right_items.insert(0, ['format-font-size-increase', lambda x: self.open_dropdown(x),
                                       'Change Image Text Size'])
                right_items.insert(0, ["view-grid", lambda x: self.call(x), "Change grid size"])

    def on_show_text(self, instance, show_text):
        app.show_text = show_text
        right_list = self.ids.toolbar.right_action_items
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

    def update_info(self, object, place):
        def write_stuff(object, place):
            ind = 0
            if self.add_picture:  # Creating new object
                self.list.append({object: place})
                with open('Data/object_dict', 'ab') as f:
                    pickle.dump({object: place}, f)

            else:
                for dict in self.list:  # Updating existing info
                    ind += 1
                    if object in dict:
                        dict[object] = place
                    with open('Data/object_dict', 'wb') as f:
                        for d in self.list:
                            pickle.dump(d, f)
                    return
            # #print('Stuff Updated')
        if object not in app.InfoScreen.get_list(self.list, 'object'):
            threading.Thread(target=write_stuff, args=(object, place)).start()

    def update_pic(self, old_info: ('old_object', 'old_place'), new_info: ('new_object', 'new_place')):
        for image in self.grid.children:
            print(f'{image.source = }\n{image.source[:-4] = }\n{old_info[0] = }')
            if image.source[:-4] == old_info[0]:
                image.source = new_info[0]+'.png'
                image.text = f'[font=Poppins][size={int(dp(app.text_size))}]{new_info[0]}[/size][/font]'

    def update_home(self):
        def check_finished(*args):
            if not app.resize_in_progress:
                self.grid.add_widget(
                    MyImage(source=f'{object}.png',
                            text=f'[font=Poppins][size={int(dp(app.text_size))}]{object}[/size][/font]',
                            tile_text_color=self.theme_cls.accent_color if self.show_text else [0, 0, 0, 0],
                            box_color=[0, 0, 0, 0.3] if self.show_text else [0, 0, 0, 0],
                            index=self.index))
                self.source_list.append(object)
                self.index += 1
                self.check_interval.cancel()
        object = app.InfoScreen.ids.object.text
        if object not in self.source_list:
            if not self.image_exists:  # Removing Sad face
                self.image_exists = True
            if not app.resize_in_progress:
                self.grid.add_widget(
                    MyImage(source=f'{object}.png',
                            text=f'[font=Poppins][size={int(dp(app.text_size))}]{object}[/size][/font]',
                            tile_text_color=self.theme_cls.accent_color if self.show_text else [0, 0, 0, 0],
                            box_color=[0, 0, 0, 0.3] if self.show_text else [0, 0, 0, 0],
                            index=self.index))
                self.source_list.append(object)
                self.index += 1
            else:
                self.check_interval = Clock.schedule_interval(check_finished,.1)


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

    def write_file(self, *args):
        def write_file_thread():
            with open('Data/object_dict', 'wb') as f:
                for d in self.list:
                    if d != {}:
                        pickle.dump(d, f)

        threading.Thread(target=write_file_thread, daemon=True).start()

    def delete_object(self, *args):
        c = 0
        for d in self.list:
            if d != {}:
                image_source = list(d.keys())[0] + '.png'
                print(f'{self.list = }{self.delete_dict=}{d=}')
                if image_source in self.delete_dict:

                    if self.delete_dict[image_source]:
                        # #print('gets Deleted')
                        if os.path.exists(image_source):
                            os.remove(image_source)  # Deletes the image file
                        del d[image_source[:-4]]

        # # #print(f'{c = }')
        if {} in self.list:
            self.list.remove({})
        self.remove_tile()
        self.write_file()
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

        print(f'{self.list=}')

    def add_images(self, *args):
        self.grid = self.ids.grid_layout
        self.NoImage = Image(source='Data/NoImage_grey_small.png', opacity=.5,
                             pos_hint={'center_y': .7, 'center_x': .5},
                             size_hint=(0.5, 0.5))
        if not FIRST_TIME:
            self.list = []
            with open('Data/object_dict', 'rb') as f:
                try:
                    while True:
                        self.list.append(pickle.load(f))
                except EOFError:
                    if self.list != []:
                        self.index = 0
                        for di in self.list:
                            for source in di:
                                self.grid.add_widget(
                                    MyImage(source=f'{source}.png',
                                            text=f'[font=Poppins][size={int(dp(app.text_size))}]{source}[/size][/font]',
                                            tile_text_color=self.theme_cls.accent_color, index=self.index))
                                self.source_list.append(source)
                            self.index += 1
                    else:
                        self.image_exists = False

        else:
            self.image_exists = False
        self.show_text = app.configuration.get_variable('show_text')

    def change_grid(self, x: int()):
        image_list = self.grid.children
        new_grid = int(x)
        if image_list[0].tile_text_color != [0, 0, 0, 0]:
            # #print('Changing text size')
            prev_grid = self.grid.cols
            old_text_size = app.text_size
            app.text_size = old_text_size * prev_grid / new_grid
            # #print(f'{app.text_size = } , {old_text_size = }')

            for im in image_list:
                if im.tile_text_color != [0, 0, 0, 0]:
                    text = im.text
                    text = text.replace('%d' % dp(old_text_size), '%d' % dp(app.text_size))
                    im.text = text
                else:
                    break
        self.grid.cols = new_grid
        app.grid_cols = new_grid

    def change_scale(self, scaling):
        image_list = self.grid.children
        if image_list[0].text != '':
            # #print('Changing text size')
            old_text_size = app.text_size
            if self.prev_scale != scaling:
                app.text_size = app.text_size * scaling / self.prev_scale
                # #print(f'{app.text_size = }')
                for im in image_list:
                    if im.text != '':
                        text = im.text
                        text = text.replace('%d' % dp(old_text_size), '%d' % dp(app.text_size))
                        im.text = text
                    else:
                        break
            self.prev_scale = scaling

    def call(self, icon):
        if self.drop is None:
            self.drop = MDDropdownMenu(
                caller=icon,
                items=[{
                    "text": f"Cols = {n}",
                    "height": dp(66),
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x=f"{n}": self.change_grid(x),
                } for n in range(1, 6)],
                width_mult=2, opening_time=0)
        self.drop.open()

    def open_dropdown(self, icon):
        if self.drop2 is None:
            self.drop2 = MDDropdownMenu(caller=icon,
                                        items=[{
                                            "text": f"{i / 10}",
                                            "height": dp(46),
                                            "viewclass": "OneLineListItem",
                                            "on_release": lambda x=f"{i / 10}": self.change_scale(float(x)),
                                        } for i in range(6, 16, 2)],
                                        width_mult=1, opening_time=0)
        self.drop2.open()

    def check_height(self, dt):
        from Modules.JavaAPI import keyboard_height
        self.key_height = keyboard_height()
        if self.key_height > 0:
            self.ids.textbox.y = self.key_height
            self.check_keyboard.cancel()

    def shift_up(self, active):
        textbox = self.ids.textbox
        if active:
            textbox.icon = 'close'
            if not self.key_height:
                self.check_keyboard = Clock.schedule_interval(self.check_height, .1)
            else:
                textbox.y = self.key_height
        else:
            self.active = False
            Clock.schedule_once(lambda x: exec('self.active = True', {'self': self}))
            textbox.y = 0
            textbox.icon = 'plus'

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
                                text=f'[font=Poppins][size={int(dp(app.text_size))}]{i}[/size][/font]',
                                tile_text_color=tile_text_color, box_color=box_color, index=self.index))
                    self.source_list.append(i)

    def tap_target(self, *args):
        if FIRST_TIME:
            self.tap_plus = MDTapTargetView(widget=self.ids.plus, title_text="Add Object",
                                            title_text_size="20sp", outer_radius=dp(150),
                                            description_text="Tap this to add\n objects and their info.",
                                            description_text_bold=True,
                                            widget_position="right_bottom")
            Clock.schedule_once(self.tap_state)

    def tap_state(self, *args):
        if self.tap_plus.state == "close":
            self.tap_plus.start()
        else:
            self.tap_plus.stop()


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

        self.light_color = app.generate_light_color(0.3)
        self.image_list = app.HomeScreen.ids.grid_layout.children
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
        app.HomeScreen.prev_state = app.HomeScreen.show_text
        app.HomeScreen.show_text = False
        for image in self.image_list:
            image.ids.checkbox.disabled = False
        self.ids.checkbox.active = True

    def on_check_box_state(self, obj, active):
        app.HomeScreen.delete_dict[obj.source] = active
        app.HomeScreen.toolbar_change = True
        # #print('<On_Check_box_event>')
        if active:
            self.shrink()
            self.bg_color = custom_light_color[self.theme_cls.primary_palette]
        else:
            self.reset()
            self.bg_color = [0, 0, 0, 0]

        if True not in app.HomeScreen.delete_dict.values():  # Deselecting everything
            # #print(f'{app.HomeScreen.delete_dict.values() = }')
            app.HomeScreen.ignore_release = True
            app.HomeScreen.toolbar_change = False
            # #print(f'{app.root.ids.setting.ids.switch_item= }')
            if app.HomeScreen.prev_state:
                app.HomeScreen.show_text = True
            for image in self.image_list:
                image.ids.checkbox.disabled = True


Builder.load_string('''
<MyImage>:
    index: root.index
    bg_color: root.bg_color
    canvas:
        Color:
            rgba: self.bg_color
        Rectangle:
            size: self.size
            pos: self.pos

    on_press:
        checkbox.active= False if checkbox.disabled or checkbox.active else True
    on_release:
        app.InfoScreen.image_clicked(self) if checkbox.disabled and not app.HomeScreen.ignore_release else ''
        app.HomeScreen.ignore_release=False
    MDCheckbox:
        id: checkbox
        disabled:True
        on_active: root.check_box_state=self.active
        disabled_color:[0,0,0,0]
        selected_color:[1,1,0,1]
        checkbox_icon_normal : "checkbox-blank-circle-outline"
        checkbox_icon_down: 'checkbox-marked-circle'
        size_hint: None,None
        size: "0dp", "0dp"
        pos_hint:{'right':1-dp(48)/Window.size[0],'top':1-dp(48)/Window.size[0]}
''')
