#!/bin/bash
# Offline, per-user installer. No package manager, sudo, curl or network calls.
set -euo pipefail
BUNDLE_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
APP_ID=voicebox-light-meimei
DEST=${XDG_DATA_HOME:-$HOME/.local/share}/$APP_ID/app
CHECK_ONLY=0
while (($#)); do
    case "$1" in
        --check) CHECK_ONLY=1; shift;;
        --install-dir) DEST=$2; shift 2;;
        --yes) MEIMEI_YES=1; shift;;
        *) echo "Opción desconocida: $1" >&2; exit 2;;
    esac
done
GUI=0
if [[ ${MEIMEI_YES:-0} != 1 && -n ${DISPLAY:-${WAYLAND_DISPLAY:-}} ]] && command -v zenity >/dev/null; then GUI=1; fi
fail() {
    if ((GUI)); then zenity --error --title='Voice Box Light Meimei' --text="$*" || true; else echo "$*" >&2; fi
    exit 1
}
for tool in sha256sum tar gzip df stat awk; do command -v "$tool" >/dev/null || fail "Falta una herramienta básica del sistema: $tool"; done
[[ $(uname -m) == x86_64 ]] || fail 'Esta edición requiere Linux x86_64.'
command -v bwrap >/dev/null || fail 'El sistema debe tener bubblewrap para proteger la ventana WebKit. No se desactiva su protección.'
[[ -r "$BUNDLE_DIR/manifest.txt" ]] || fail 'Falta manifest.txt. Descarga el manifiesto y todas las partes de la misma versión en esta carpeta.'
read -r VERSION UNPACKED MIN_GLIBC < "$BUNDLE_DIR/manifest.txt"
[[ $UNPACKED =~ ^[0-9]+$ && $MIN_GLIBC =~ ^[0-9]+\.[0-9]+$ ]] || fail 'El manifiesto no es válido.'
HOST_GLIBC=$(getconf GNU_LIBC_VERSION | awk '{print $2}')
[[ $(printf '%s\n%s\n' "$MIN_GLIBC" "$HOST_GLIBC" | sort -V | head -n1) == "$MIN_GLIBC" ]] || fail "Se necesita glibc $MIN_GLIBC o posterior. Este sistema tiene $HOST_GLIBC."
PARTS=(); DIGESTS=()
while read -r DIGEST FILE EXTRA; do
    [[ -n $DIGEST ]] || continue
    [[ $DIGEST =~ ^[a-f0-9]{64}$ && $FILE =~ ^meimei-payload\.tar\.gz\.part[0-9]{3}$ && -z ${EXTRA:-} ]] || fail 'El manifiesto contiene un nombre o checksum inválido.'
    [[ -r "$BUNDLE_DIR/$FILE" ]] || fail "Falta $FILE. Descarga todas las partes de la misma versión."
    PARTS+=("$BUNDLE_DIR/$FILE"); DIGESTS+=("$DIGEST")
done < <(tail -n +2 "$BUNDLE_DIR/manifest.txt")
((${#PARTS[@]} > 0)) || fail 'No hay partes en el manifiesto.'
if ((!CHECK_ONLY)); then
    mkdir -p "$(dirname -- "$DEST")"
    FREE=$(df -PB1 "$(dirname -- "$DEST")" | awk 'NR==2 {print $4}')
    REQUIRED=$((UNPACKED+1073741824))
    ((FREE>=REQUIRED)) || fail "No hay suficiente espacio. Se necesitan $((REQUIRED/1073741824+1)) GiB libres para instalar."
    if ((GUI)); then
        zenity --question --title='Instalar Voice Box Edición Light Meimei' --width=460 --text="Instalación sin conexión de $VERSION.\n\nIncluye las voces y dependencias. Usa aproximadamente $((UNPACKED/1073741824+1)) GiB en disco.\nDestino: $DEST\n\nNo necesita administrador. ¿Instalar?" || exit 0
    elif [[ ${MEIMEI_YES:-0} != 1 ]]; then
        read -r -p "Instalar $VERSION en $DEST (s/N): " REPLY
        [[ $REPLY == [sS] ]] || exit 0
    fi
fi
perform() {
    for index in "${!PARTS[@]}"; do
        echo "# Verificando ${PARTS[$index]##*/}…"
        ACTUAL=$(sha256sum "${PARTS[$index]}" | awk '{print $1}')
        [[ $ACTUAL == "${DIGESTS[$index]}" ]] || { echo 'Archivo dañado: vuelve a descargar esa parte.' >&2; return 1; }
        echo "$(((index+1)*25/${#PARTS[@]}))"
    done
    ((CHECK_ONLY)) && { echo '100'; return 0; }
    STAGE=$(mktemp -d "${DEST}.install-XXXXXX")
    trap '[[ -z ${STAGE:-} ]] || rm -rf -- "$STAGE"' EXIT
    echo '# Extrayendo aplicación y modelos. Esto puede tardar varios minutos…'; echo 30
    cat "${PARTS[@]}" | tar -xzf - --no-same-owner -C "$STAGE"
    echo '# Preparando el lanzador…'; echo 85
    PREFIX_ESCAPED=$(printf '%s' "$DEST" | sed 's/[\\&|]/\\&/g')
    sed -i "s|@MEIMEI_ROOT@|$PREFIX_ESCAPED|g" "$STAGE/runtime/backend/pyvenv.cfg"
    chmod +x "$STAGE/linux-light/launch" "$STAGE/linux-light/uninstall"
    # Verify the bundled Python bindings before replacing any previous version.
    PYTHONHOME="$STAGE/runtime/desktop" LD_LIBRARY_PATH="$STAGE/runtime/native/lib" GI_TYPELIB_PATH="$STAGE/runtime/native/girepository-1.0" "$STAGE/runtime/desktop/bin/python" -c "import gi; gi.require_version('Gtk','3.0'); gi.require_version('WebKit2','4.1'); from gi.repository import Gtk,WebKit2"
    BACKUP=''
    if [[ -e $DEST ]]; then BACKUP="${DEST}.previous-$(date +%s)"; mv -- "$DEST" "$BACKUP"; fi
    if ! mv -- "$STAGE" "$DEST"; then [[ -z $BACKUP ]] || mv -- "$BACKUP" "$DEST"; return 1; fi
    STAGE=''
    APPLICATIONS=${XDG_DATA_HOME:-$HOME/.local/share}/applications
    ICONS=${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/scalable/apps
    mkdir -p "$APPLICATIONS" "$ICONS"
    cp "$DEST/linux-light/meimei-icon.svg" "$ICONS/$APP_ID.svg"
    # Escape the Exec field according to the Desktop Entry Specification.
    EXEC_PATH=${DEST//\\/\\\\}; EXEC_PATH=${EXEC_PATH//\"/\\\"}; EXEC_PATH=${EXEC_PATH//\$/\\\$}; EXEC_PATH=${EXEC_PATH//\`/\\\`}; EXEC_PATH=${EXEC_PATH//%/%%}
    cat > "$APPLICATIONS/$APP_ID.desktop" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Voice Box Edición Light Meimei
Comment=Generación y clonación de voz local en español — edición de segueldev
Exec="$EXEC_PATH/linux-light/launch"
Icon=$APP_ID
Terminal=false
Categories=AudioVideo;Audio;
StartupNotify=true
StartupWMClass=io.github.segueldev.voiceboxlightmeimei
EOF
    if command -v desktop-file-validate >/dev/null; then desktop-file-validate "$APPLICATIONS/$APP_ID.desktop"; fi
    if command -v kbuildsycoca6 >/dev/null; then kbuildsycoca6 --noincremental >/dev/null 2>&1 || true; fi
    echo 100
    [[ -z $BACKUP ]] || echo "Versión anterior conservada en $BACKUP" >&2
}
if ((GUI)); then
    ERROR_LOG=$(mktemp)
    if perform 2>"$ERROR_LOG" | zenity --progress --title='Instalando Light Meimei' --text='Comprobando archivos…' --percentage=0 --auto-close --no-cancel --width=480; then
        rm -f "$ERROR_LOG"
        zenity --info --title='Instalación completa' --text='Voice Box Edición Light Meimei está en el menú de aplicaciones. Puedes generar voces sin conexión.'
    else
        MESSAGE=$(cat "$ERROR_LOG"); rm -f "$ERROR_LOG"; fail "No se completó la instalación. $MESSAGE"
    fi
else
    perform
    if ((!CHECK_ONLY)); then echo 'Instalación completa. Abre Voice Box Edición Light Meimei desde el menú.'; else echo 'Todas las partes son válidas.'; fi
fi
