import datetime
import os

from kivy.core.window import Window
from kivy.logger import Logger
from kivy.clock import mainthread
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.resources import resource_add_path
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.camera import Camera
from kivy.uix.label import Label
from kivy.utils import platform

from kivymd.app import MDApp
from .platform_api import LANDSCAPE, set_orientation, take_picture

ROOT = os.path.dirname(os.path.abspath(__file__))
resource_add_path(ROOT)


def darker(color, factor=0.5):
    r, g, b, a = color
    r *= factor
    g *= factor
    b *= factor
    return r, g, b, a


def is_android():
    return platform == 'android'


def check_camera_permission():
    """
    Android runtime `CAMERA` permission check.
    """
    if not is_android():
        return True
    from android.permissions import Permission, check_permission
    permission = Permission.CAMERA
    return check_permission(permission)


def check_request_camera_permission(callback=None):
    """
    Android runtime `CAMERA` permission check & request.
    """
    had_permission = check_camera_permission()
    if not had_permission:
        from android.permissions import Permission, request_permissions
        permissions = [Permission.CAMERA, Permission.RECORD_AUDIO]
        request_permissions(permissions, callback)
    return had_permission


class XCameraIconButton(ButtonBehavior, Label):
    pass


class XCamera(Camera):
    directory = ObjectProperty(None)
    _previous_orientation = None
    __events__ = ('on_picture_taken', 'on_camera_ready')
    ratio = 16 / 9

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app=MDApp.get_running_app()
        if platform == 'android':
            if not app.optimise:
                avail_preview_size = []
                import time
                i=time.time()
                parameters = self._camera._android_camera.getParameters()
                java_lst = parameters.getSupportedPreviewSizes()

                for preview in java_lst:
                    if preview.height <= Window.width and preview.height!=preview.width:
                        avail_preview_size.append([preview.width, preview.height])

                
                Logger.info(f'CameraPreview:  Available Resolutions are : {avail_preview_size}\n{time.time()-i =}')
                app.avail_preview_size=avail_preview_size
                self.resolution= avail_preview_size[2]
            else:
                self.resolution = app.avail_preview_size[app.set_preview_index]
        else:
            self.resolution = [1280, 720]
        app.preview_size = self.resolution
        self.ratio = self.resolution[0] / self.resolution[1]
        Builder.load_file(os.path.join(ROOT, "xcamera.kv"))
        Logger.info(f'CameraPreview: Preview Size : {self.resolution}')

    def _on_index(self, *largs):
        """
        Overrides `kivy.uix.camera.Camera._on_index()` to make sure
        `camera.open()` is not called unless Android `CAMERA` permission is
        granted, refs #5.
        """

        @mainthread
        def on_permissions_callback(permissions, grant_results):
            """
            On camera permission callback calls parent `_on_index()` method.
            """
            if all(grant_results):
                self._on_index_dispatch(*largs)

        if check_request_camera_permission(callback=on_permissions_callback):
            self._on_index_dispatch(*largs)

    def _on_index_dispatch(self, *largs):
        super()._on_index(*largs)
        self.dispatch('on_camera_ready')

    def on_picture_taken(self, filename):

        """
        This event is fired every time a picture has been taken.
        """
        pass

    def on_camera_ready(self):
        """
        Fired when the camera is ready.
        """
        pass

    def shoot(self, filename='demo'):
        def on_success(filename):
            self.dispatch('on_picture_taken', filename)

        if self.directory:
            filename = os.path.join(self.directory, filename)
        take_picture(self, filename, on_success)

    def force_landscape(self):
        self._previous_orientation = set_orientation(LANDSCAPE)

    def restore_orientation(self):
        if self._previous_orientation is not None:
            set_orientation(self._previous_orientation)
