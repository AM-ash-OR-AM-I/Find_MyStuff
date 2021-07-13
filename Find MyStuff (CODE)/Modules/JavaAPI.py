from kivy.utils import platform

if platform == 'android':
    from android.runnable import run_on_ui_thread
    from jnius import autoclass

    Color = autoclass("android.graphics.Color")
    WindowManager = autoclass('android.view.WindowManager$LayoutParams')
    activity = autoclass('org.kivy.android.PythonActivity').mActivity
    Rect = autoclass('android.graphics.Rect')()
    View = autoclass('android.view.View')
    Configuration = autoclass("android.content.res.Configuration")


    @run_on_ui_thread
    def fix_back_button():
        activity.onWindowFocusChanged(False)
        activity.onWindowFocusChanged(True)


    def keyboard_height():
        try:
            decor_view = activity.getWindow().getDecorView()
            height = activity.getWindowManager().getDefaultDisplay().getHeight()
            decor_view.getWindowVisibleDisplayFrame(Rect)
            return height - Rect.bottom

        except:
            return 0


    @run_on_ui_thread
    def statusbar(color, nav_color=None,text_color=None):
        window = activity.getWindow()
        print('Setting StatusBar Color')  # Updates everytime color is changed
        window.clearFlags(WindowManager.FLAG_TRANSLUCENT_STATUS)
        window.addFlags(WindowManager.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS)
        window.setStatusBarColor(Color.parseColor('#' + color))
        try:
            if nav_color is not None:
                if nav_color == 'black':
                    window.setNavigationBarColor(Color.parseColor('#' + color))
                    window.getDecorView().setSystemUiVisibility(0)
                elif nav_color == 'white':
                    window.setNavigationBarColor(Color.parseColor('#FAFAFA'))
                    window.getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR)
                else:
                    window.setNavigationBarColor(Color.parseColor('#' + nav_color))
        except AttributeError:
            pass
        if text_color is not None:
            if text_color == "black":
                window.getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR)
            elif text_color == "white":
                window.getDecorView().setSystemUiVisibility(0)


    def dark_mode():
        night_mode_flags = activity.getContext().getResources().getConfiguration().uiMode & Configuration.UI_MODE_NIGHT_MASK
        if night_mode_flags == Configuration.UI_MODE_NIGHT_YES:
            return True
        elif night_mode_flags in [
            Configuration.UI_MODE_NIGHT_NO,
            Configuration.UI_MODE_NIGHT_UNDEFINED,
        ]:
            return False


    def orientation():
        config = activity.getResources().getConfiguration()
        if config.orientation == 1:
            return 'Portrait'
        else:
            return 'Landscape'
