#!/usr/bin/env python3
"""Assemble a local offline runtime from a verified installation. No network use."""
import argparse, os, re, shutil, subprocess, sys
from pathlib import Path
parser=argparse.ArgumentParser()
parser.add_argument('--installation', type=Path, required=True, help='Existing verified .local/share/voicebox')
parser.add_argument('--output', type=Path, required=True)
args=parser.parse_args()
repo=Path(__file__).resolve().parents[1]
out=args.output.resolve(); out.mkdir(parents=True,exist_ok=True)
native=out/'runtime/native'; (native/'lib').mkdir(parents=True,exist_ok=True)
packages=set(); scanned=set(); copied=set()
def run(*argv): return subprocess.check_output(argv,text=True).strip()
def copytree(src,dst,exclude=()):
    dst.mkdir(parents=True,exist_ok=True)
    subprocess.run(['rsync','-a','--no-owner','--no-group','--delete',*[f'--exclude={s}' for s in exclude],str(src)+'/',str(dst)+'/'],check=True)
def copyfile(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run(['cp','--reflink=auto','--remove-destination','-L',str(src),str(dst)],check=True)
def owner(path):
    result=subprocess.run(['pacman','-Qqo',str(path)],text=True,capture_output=True)
    if result.returncode==0: packages.update(result.stdout.splitlines())
def collect(path):
    path=Path(path)
    if not path.exists() or str(path) in scanned: return
    scanned.add(str(path)); owner(path)
    # glibc and loader belong to the target OS, not the app.
    if re.match(r'^(libc\.so|libm\.so|libpthread\.so|libdl\.so|librt\.so|libresolv\.so|libutil\.so|ld-linux)',path.name): return
    dest=native/'lib'/path.name
    if path.name not in copied:
        copyfile(path,dest); copied.add(path.name)
    result=subprocess.run(['ldd',str(path)],text=True,capture_output=True)
    for dep in re.findall(r'=>\s+(/\S+)',result.stdout): collect(dep)
installed=args.installation/'app/work'
copytree(repo,out/'source',('.git','.venv','node_modules','dist','frontend','__pycache__','.pytest_cache','linux-light','landing','docs','tauri','data','.agents','.github'))
copytree(repo/'linux-light',out/'linux-light',('__pycache__',))
copytree(repo/'frontend',out/'source/frontend')
copytree(installed/'tools/python/cpython-3.12.15-linux-x86_64-gnu',out/'runtime/python312',('__pycache__',))
copytree(installed/'voicebox-0.5.0/.venv',out/'runtime/backend',('__pycache__',))
venv=out/'runtime/backend'
for filename in ('python','python3','python3.12'):
    path=venv/'bin'/filename
    if path.exists() or path.is_symlink(): path.unlink()
    path.symlink_to('../../python312/bin/python3.12')
for path in (venv/'bin').iterdir():
    if path.name not in ('python','python3','python3.12') and (path.is_file() or path.is_symlink()): path.unlink()
for path in venv.rglob('direct_url.json'):
    if 'file://' in path.read_text(): path.unlink()
# pyvenv.cfg is rewritten to its final absolute prefix by the installer.
(venv/'pyvenv.cfg').write_text('home = @MEIMEI_ROOT@/runtime/python312/bin\nimplementation = CPython\nversion_info = 3.12.15\ninclude-system-site-packages = false\n')
loader=venv/'lib/python3.12/site-packages/espeakng_loader/__init__.py'
s=loader.read_text()
s=s.replace('import platform','import platform\nimport os')
s=s.replace('def get_library_path():','def get_library_path():\n    if os.environ.get("VOICEBOX_ESPEAK_LIBRARY"): return os.environ["VOICEBOX_ESPEAK_LIBRARY"]')
s=s.replace('def get_data_path():','def get_data_path():\n    if os.environ.get("VOICEBOX_ESPEAK_DATA"): return os.environ["VOICEBOX_ESPEAK_DATA"]')
# Actual loader names differ between versions; reject a missing adaptation.
if 'return os.environ["VOICEBOX_ESPEAK_LIBRARY"]' not in s:
    s=s.replace('def get_library_path() -> str:', 'def get_library_path() -> str:\n    if os.environ.get("VOICEBOX_ESPEAK_LIBRARY"): return os.environ["VOICEBOX_ESPEAK_LIBRARY"]')
if 'return os.environ["VOICEBOX_ESPEAK_DATA"]' not in s:
    s=s.replace('def get_data_path() -> str:', 'def get_data_path() -> str:\n    if os.environ.get("VOICEBOX_ESPEAK_DATA"): return os.environ["VOICEBOX_ESPEAK_DATA"]')
loader.write_text(s)
assert 'return os.environ["VOICEBOX_ESPEAK_LIBRARY"]' in s, 'Check espeakng_loader API'
copytree(args.installation/'models/hub',out/'models/hub',('.locks',))
# GUI runtime: only stdlib and the two Python bindings, no user's Python packages.
pyver=f'python{sys.version_info.major}.{sys.version_info.minor}'
desktop=out/'runtime/desktop'
copyfile(Path(sys.executable),desktop/'bin/python')
copytree(Path('/usr/lib')/pyver,desktop/'lib'/pyver,('site-packages','__pycache__','test','tests','ensurepip'))
for name in ('gi','cairo'):
    src=Path('/usr/lib')/pyver/'site-packages'/name
    copytree(src,desktop/'lib'/pyver/'site-packages'/name,('__pycache__',))
collect(sys.executable)
for path in (desktop/'lib'/pyver).rglob('*.so'): collect(path)
for path in ['/usr/lib/libgtk-3.so.0','/usr/lib/libwebkit2gtk-4.1.so.0','/usr/lib/libjavascriptcoregtk-4.1.so.0','/usr/lib/libespeak-ng.so.1']:
    collect(path)
copytree(Path('/usr/lib/girepository-1.0'),native/'girepository-1.0')
copytree(Path('/usr/lib/webkit2gtk-4.1'),native/'webkit2gtk-4.1')
for path in (native/'webkit2gtk-4.1').rglob('*'):
    if path.is_file(): collect(path)
for dirname in ('gstreamer-1.0','gio/modules','gdk-pixbuf-2.0'):
    src=Path('/usr/lib')/dirname
    if src.exists():
        copytree(src,native/dirname)
        for path in src.rglob('*.so'): collect(path)
# GUI depends on those native schemas and pronunciation data, not user settings.
for dirname in ('glib-2.0/schemas','espeak-ng-data'):
    copytree(Path('/usr/share')/dirname,native/'share'/dirname)
for executable in ('sox',):
    executable_path=shutil.which(executable)
    if not executable_path: executable_path=str(installed/'tools/sox/usr/bin'/executable)
    copyfile(executable_path,native/'bin'/executable); collect(executable_path)
soxlibs=installed/'tools/sox/usr/lib'
if soxlibs.exists():
    for path in soxlibs.glob('*.so*'):
        if path.is_file(): copyfile(path,native/'lib'/path.name)
licenses=out/'licenses'; licenses.mkdir(exist_ok=True)
for name in packages:
    src=Path('/usr/share/licenses')/name
    if src.exists(): copytree(src,licenses/'native'/name)
for shared in ('common','spdx'):
    src=Path('/usr/share/licenses')/shared
    if src.exists(): copytree(src,licenses/'native'/shared)
(licenses/'native-packages.txt').write_text('\n'.join(run('pacman','-Q',n) for n in sorted(packages))+'\n')
for name in ('LICENSE','CREDITS.md','CHANGELOG-LIGHT.md','README.md'):
    copyfile(repo/name,licenses/name)
(licenses/'BUILD-HOST.txt').write_text(run('uname','-srmo')+'\n'+run('getconf','GNU_LIBC_VERSION')+'\n')
print(f'Payload assembled: {out}',flush=True)
