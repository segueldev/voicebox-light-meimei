"""Deterministic Spanish speech preparation; the saved source text is unchanged."""
import re
import unicodedata
from datetime import date
from num2words import num2words

_MONTHS = ('enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre')
_ABBREVIATIONS = {
    r'\bDra\.': 'doctora', r'\bDr\.': 'doctor', r'\bSrta\.': 'señorita',
    r'\bSra\.': 'señora', r'\bSr\.': 'señor', r'\bAv\.': 'avenida',
    r'\bUd\.': 'usted', r'\bUds\.': 'ustedes', r'\bp\.\s*ej\.': 'por ejemplo',
    r'\betc\.': 'etcétera',
}

def _integer(value):
    sign = ''
    if value.startswith(('+','-')):
        sign = 'más ' if value[0]=='+' else 'menos '
        value=value[1:]
    if len(value)>1 and value.startswith('0'):
        return sign+' '.join(num2words(int(c),lang='es') for c in value)
    if len(value)>12:
        return sign+' '.join(num2words(int(c),lang='es') for c in value)
    return sign+num2words(int(value),lang='es')

def _number(match):
    value=match.group(0)
    # Spanish grouping uses dots; a zero before a dot is a decimal.
    if re.fullmatch(r'[+-]?[1-9]\d{0,2}(?:\.\d{3})+(?:,\d+)?',value):
        value=value.replace('.','')
    if ',' in value or '.' in value:
        integer,fraction=re.split(r'[,.]',value,maxsplit=1)
        return _integer(integer)+' coma '+' '.join(num2words(int(c),lang='es') for c in fraction)
    return _integer(value)

def prepare_spanish_text(text,language='es'):
    if language!='es':
        return text
    text=unicodedata.normalize('NFC',text)
    text=re.sub('[\u200b\u200c\u200d\ufeff]','',text).replace('\xa0',' ')
    protected=[]
    def protect(match):
        protected.append(match.group(0))
        return '\ue000'+chr(0xe100+len(protected)-1)+'\ue001'
    # Do not reinterpret addresses, version numbers or code blocks.
    text=re.sub(r'```[\s\S]*?```|`[^`]+`|https?://[^\s]+|www\.[^\s]+|[\w.+-]+@[\w.-]+\.[\w]+|\bv?\d+(?:\.\d+){2,}\b',protect,text)
    def spoken_date(match):
        day,month,year=map(int,match.groups())
        try:date(year,month,day)
        except ValueError:return match.group(0)
        return f'{num2words(day,lang="es")} de {_MONTHS[month-1]} de {num2words(year,lang="es")}'
    text=re.sub(r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b',spoken_date,text)
    def spoken_time(match):
        hour,minute=map(int,match.groups())
        if hour>23 or minute>59:return match.group(0)
        hour_text = 'una hora' if hour == 1 else num2words(hour,lang='es').replace('uno','una')+' horas'
        minute_text = 'un minuto' if minute == 1 else num2words(minute,lang='es').replace('veintiuno','veintiún')+' minutos'
        return hour_text+(' en punto' if minute==0 else ' y '+minute_text)
    text=re.sub(r'\b(\d{1,2}):(\d{2})\b',spoken_time,text)
    for pattern,replacement in _ABBREVIATIONS.items():
        text=re.sub(pattern,replacement,text,flags=re.IGNORECASE)
    text=re.sub(r'\bIA\b','inteligencia artificial',text)
    text=re.sub(r'\b(?:kHz)\b','kilohercios',text)
    text=re.sub(r'\bHz\b','hercios',text)
    text=text.replace('%',' por ciento ').replace('…','.').replace('—',', ')
    text=re.sub(r'\*\*([^*]+)\*\*',r'\1',text)
    text=re.sub(r'(?<![\w/])(?:[+-]?\d{1,3}(?:\.\d{3})+(?:,\d+)?|[+-]?\d+(?:[.,]\d+)?)(?![\w/])',_number,text)
    text=re.sub(r'[^\S\n]+',' ',text).strip()
    for i,original in enumerate(protected):
        text=text.replace('\ue000'+chr(0xe100+i)+'\ue001',original)
    return text
