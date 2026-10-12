#!/usr/bin/python
"""Desktop window and automatic lifecycle for Voicebox 0.5.0."""
import os, sys, json, time, threading, subprocess, urllib.request, signal
from pathlib import Path
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.1')
from gi.repository import Gtk, WebKit2, GLib, Gio, GdkPixbuf
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'source'
DATA = Path(os.environ.get('VOICEBOX_DATA_HOME', str(Path(os.environ.get('XDG_DATA_HOME', str(Path.home()/'.local/share')))/'voicebox-light-meimei')))
PORT = int(os.environ.get('VOICEBOX_PORT', '17494'))
URL = f'http://127.0.0.1:{PORT}'
class Voicebox(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='io.github.segueldev.voiceboxlightmeimei', flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.process = None
        self.log = None
        self.closing = False
        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", lambda *_: self.close())
        self.add_action(action)
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, self.close)
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, self.close)
    def do_activate(self):
        if self.get_active_window():
            self.get_active_window().present()
            return
        DATA.mkdir(parents=True, exist_ok=True)
        self.window = Gtk.ApplicationWindow(application=self, title='Voice Box Edición Light Meimei')
        self.window.set_default_size(1200, 800)
        self.window.set_icon_from_file(str(ROOT / 'linux-light/meimei-icon.svg'))
        context = WebKit2.WebContext.new()
        context.add_path_to_sandbox(str(ROOT), True)
        self.view = WebKit2.WebView(web_context=context, website_policies=WebKit2.WebsitePolicies(autoplay=WebKit2.AutoplayPolicy.ALLOW))
        self.view.get_settings().set_enable_media_stream(True)
        self.view.get_settings().set_media_playback_requires_user_gesture(False)
        preference = """if(!localStorage.getItem('meimei-ui-v1')){localStorage.setItem('voicebox:lang','es');localStorage.setItem('meimei-ui-v1','1')}"""
        self.view.get_user_content_manager().add_script(WebKit2.UserScript.new(preference, WebKit2.UserContentInjectedFrames.TOP_FRAME, WebKit2.UserScriptInjectionTime.START, None, None))

        self.view.connect('permission-request', self.permission)
        self.view.get_context().connect('download-started', self.download)
        self.setup_loading_screen()
        self.window.connect('delete-event', self.close)
        self.set_loading_progress(0.08, 'Preparando la aplicación…')
        self.window.show_all()
        GLib.idle_add(self.logo_reveal.set_reveal_child, True)
        threading.Thread(target=self.start, daemon=True).start()
    def setup_loading_screen(self):
        self.frontend_loading = False
        self.progress_target = 0.0
        self.progress_timer = None
        self.stack = Gtk.Overlay()
        self.stack.set_name('meimei-startup')
        center = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        center.set_halign(Gtk.Align.CENTER)
        center.set_valign(Gtk.Align.CENTER)
        center.set_margin_start(32)
        center.set_margin_end(32)
        center.set_size_request(430, -1)
        self.logo_reveal = Gtk.Revealer(transition_type=Gtk.RevealerTransitionType.CROSSFADE, transition_duration=600)
        logo = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(ROOT/'linux-light/meimei-icon.svg'), 180, 180, True)
        self.logo_reveal.add(Gtk.Image.new_from_pixbuf(logo))
        center.pack_start(self.logo_reveal, False, False, 0)
        title = Gtk.Label(label='Iniciando Voice Box Light Meimei…')
        title.set_name('meimei-loading-title')
        center.pack_start(title, False, False, 4)
        self.loading_bar = Gtk.ProgressBar()
        self.loading_bar.set_size_request(400, 8)
        center.pack_start(self.loading_bar, False, False, 4)
        self.loading_status = Gtk.Label(label='Preparando la aplicación…')
        self.loading_status.set_name('meimei-loading-status')
        center.pack_start(self.loading_status, False, False, 0)
        style = Gtk.CssProvider()
        style.load_from_data(b"""
          #meimei-startup, #meimei-startup-cover { background: #18181b; color: #f4f4f5; }
          #meimei-loading-title { font-size: 20px; font-weight: 600; color: #fafafa; }
          #meimei-loading-status { font-size: 13px; color: #a1a1aa; }
          #meimei-startup progressbar trough { min-height: 8px; border-radius: 8px; background: #303036; border: none; }
          #meimei-startup progressbar progress { min-height: 8px; border-radius: 8px; background: linear-gradient(to right, #ad853f, #dec77c); border: none; }
        """)
        for widget in (self.stack, title, self.loading_status, self.loading_bar):
            widget.get_style_context().add_provider(style, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        cover = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        cover.set_name('meimei-startup-cover')
        cover.set_hexpand(True)
        cover.set_vexpand(True)
        cover.get_style_context().add_provider(style, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        cover.pack_start(center, True, False, 0)
        self.loading_cover = Gtk.Revealer(transition_type=Gtk.RevealerTransitionType.CROSSFADE, transition_duration=350)
        self.loading_cover.add(cover)
        self.loading_cover.set_reveal_child(True)
        # Keep the WebView mapped underneath: WebKit defers hidden stack pages.
        self.stack.add(self.view)
        self.stack.add_overlay(self.loading_cover)
        self.window.add(self.stack)
        self.view.connect('notify::estimated-load-progress', self.page_progress)
        self.view.connect('load-changed', self.page_loaded)
    def set_loading_progress(self, fraction, message):
        self.progress_target = max(self.progress_target, min(fraction, 1.0))
        self.loading_status.set_text(message)
        if self.progress_timer is None:
            self.progress_timer = GLib.timeout_add(16, self.animate_loading_progress)
        return False
    def animate_loading_progress(self):
        current = self.loading_bar.get_fraction()
        difference = self.progress_target-current
        if difference < 0.002:
            self.loading_bar.set_fraction(self.progress_target)
            self.progress_timer = None
            return False
        self.loading_bar.set_fraction(current + difference*0.13)
        return True
    def open_frontend(self):
        self.frontend_loading = True
        self.set_loading_progress(0.72, 'Cargando la interfaz…')
        self.view.load_uri(URL+'/')
        return False
    def page_progress(self, view, unused):
        if self.frontend_loading:
            self.set_loading_progress(0.72+0.27*view.get_estimated_load_progress(), 'Cargando la interfaz…')
    def page_loaded(self, view, event):
        if self.frontend_loading and event == WebKit2.LoadEvent.FINISHED:
            self.set_loading_progress(0.99, 'Preparando la pantalla…')
            self.wait_for_interface()
    def wait_for_interface(self):
        if self.closing or not self.frontend_loading:
            return False
        def checked(view, result, unused):
            try:
                ready = view.evaluate_javascript_finish(result).to_boolean()
            except Exception:
                ready = False
            if ready:
                self.set_loading_progress(1.0, 'Todo listo')
                self.loading_bar.set_fraction(1.0)
                self.loading_cover.set_reveal_child(False)
                self.frontend_loading = False
            elif not self.closing:
                GLib.timeout_add(100, self.wait_for_interface)
        self.view.evaluate_javascript("!!document.querySelector('[data-generation-composer]') || (!document.getElementById('root') && !!document.body?.textContent.trim())", -1, None, None, None, checked, None)
        return False
    def permission(self, view, request):
        if (view.get_uri() or '').startswith(URL+'/') and isinstance(request, WebKit2.UserMediaPermissionRequest):
            request.allow()
            return True
        return False
    def download(self, context, download):
        def destination(download, name):
            dialog = Gtk.FileChooserDialog(title='Guardar archivo', parent=self.window, action=Gtk.FileChooserAction.SAVE)
            dialog.add_buttons('Cancelar', Gtk.ResponseType.CANCEL, 'Guardar', Gtk.ResponseType.OK)
            dialog.set_current_name(Path(name).name)
            dialog.set_do_overwrite_confirmation(True)
            if dialog.run() == Gtk.ResponseType.OK:
                download.set_allow_overwrite(True)
                download.set_destination(Path(dialog.get_filename()).as_uri())
            else:
                download.cancel()
            dialog.destroy()
            return True
        download.connect('decide-destination', destination)
    def healthy(self):
        try:
            with urllib.request.urlopen(URL+'/health', timeout=2) as response:
                return json.load(response).get('status') == 'healthy'
        except Exception:
            return False
    def start(self):
        try:
            GLib.idle_add(self.set_loading_progress, 0.22, "Comprobando el servicio de voz…")
            if not self.healthy():
                env = os.environ.copy()
                for key in ('PYTHONHOME', 'PYTHONPATH'):
                    env.pop(key, None)
                cache = DATA/'cache'
                (cache/'torch-kernels').mkdir(parents=True, exist_ok=True)
                env.update(XDG_CACHE_HOME=str(cache), NUMBA_CACHE_DIR=str(cache/'numba'), PYTORCH_KERNEL_CACHE_PATH=str(cache/'torch-kernels'))
                env.update(HF_HOME=str(ROOT/'models'), OMP_NUM_THREADS='2', TOKENIZERS_PARALLELISM='false', VOICEBOX_LOW_MEMORY='1', VOICEBOX_SPANISH_TEXT='1', HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', PYTORCH_CUDA_ALLOC_CONF='expandable_segments:True', PATH=str(ROOT/'runtime/native/bin')+os.pathsep+env.get('PATH',''), LD_LIBRARY_PATH=str(ROOT/'runtime/native/lib')+os.pathsep+env.get('LD_LIBRARY_PATH',''), VOICEBOX_ESPEAK_LIBRARY=str(ROOT/'runtime/native/lib/libespeak-ng.so.1'), VOICEBOX_ESPEAK_DATA=str(ROOT/'runtime/native/share/espeak-ng-data'))
                GLib.idle_add(self.set_loading_progress, 0.38, 'Iniciando el servicio de voz…')
                self.log = open(DATA/'server.log', 'a')
                self.process = subprocess.Popen([str(ROOT/'runtime/backend/bin/python'), '-m', 'backend.main', '--host', '127.0.0.1', '--port', str(PORT), '--data-dir', str(DATA/'data')], cwd=SOURCE, env=env, stdout=self.log, stderr=subprocess.STDOUT)
            for _ in range(180):
                if self.closing:
                    return
                if self.healthy():
                    GLib.idle_add(self.set_loading_progress, 0.65, "Servicio listo. Preparando las voces…")
                    self.seed_default()
                    GLib.idle_add(self.open_frontend)
                    return
                if self.process and self.process.poll() is not None:
                    raise RuntimeError('El servidor no pudo arrancar.')
                time.sleep(1)
            raise RuntimeError('El servidor tardó demasiado en arrancar.')
        except Exception as error:
            GLib.idle_add(self.error, str(error))
    def seed_default(self):
        """Seed a public preset only when no profile exists. Never import user data."""
        with urllib.request.urlopen(URL+'/profiles', timeout=10) as response:
            profiles = json.load(response)
        if not profiles:
            payload = json.dumps(dict(name='Español — Alex', description='Voz masculina predefinida en español. Ligera y lista para escribir cualquier texto.', language='es', voice_type='preset', preset_engine='kokoro', preset_voice_id='em_alex', default_engine='kokoro')).encode()
            request = urllib.request.Request(URL+'/profiles', data=payload, headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(request, timeout=20) as response:
                json.load(response)
    def error(self, message):
        import html
        self.frontend_loading = True
        self.view.load_html('<html><body><h2>No se pudo iniciar Voice Box Light Meimei</h2><p>'+html.escape(message)+'</p><p>Registro: '+str(DATA/'server.log')+'</p></body></html>', URL)
    def close(self, *args):
        self.closing = True
        if self.process and self.process.poll() is None:
            self.process.terminate()
            def reap():
                try:
                    self.process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()
            reap()
        self.quit()
        return False
if __name__ == '__main__':
    app = Voicebox()
    app.run(sys.argv)
