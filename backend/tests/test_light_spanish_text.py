import importlib.util,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('spanish_text',Path(__file__).resolve().parents[1]/'utils/spanish_text.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class SpanishTextChecks(unittest.TestCase):
 def test_decimal_percent(self):self.assertEqual(m.prepare_spanish_text('12,5 %'), 'doce coma cinco por ciento')
 def test_valid_date_and_time(self):self.assertEqual(m.prepare_spanish_text('11/10/2026 a las 14:30.'),'once de octubre de dos mil veintiséis a las catorce horas y treinta minutos.')
 def test_grouping_and_fraction(self):self.assertEqual(m.prepare_spanish_text('1.250 pesos y 0.125 gramos.'),'mil doscientos cincuenta pesos y cero coma uno dos cinco gramos.')
 def test_abbreviations(self):self.assertEqual(m.prepare_spanish_text('Dr. Pérez, Av. Central, IA y 24 kHz.'),'doctor Pérez, avenida Central, inteligencia artificial y veinticuatro kilohercios.')
 def test_time_grammar(self):self.assertEqual(m.prepare_spanish_text('01:01 y 21:21'),'una hora y un minuto y veintiuna horas y veintiún minutos')
 def test_keep_addresses_versions_code(self):
  text='Visita https://ejemplo.cl/v1.2.3 o correo@ejemplo.cl. Versión v1.2.3. `id=123`.'
  self.assertEqual(m.prepare_spanish_text(text),text)
 def test_keep_other_languages(self):self.assertEqual(m.prepare_spanish_text('12.5% on 11/10/2026','en'),'12.5% on 11/10/2026')
 def test_leading_zeros(self):self.assertEqual(m.prepare_spanish_text('Código 0012.'),'Código cero cero uno dos.')
 def test_invalid_date_unchanged(self):self.assertEqual(m.prepare_spanish_text('31/02/2026'),'31/02/2026')
 def test_accents_and_invisible_spaces(self):self.assertEqual(m.prepare_spanish_text('man\u0303ana\u200b y Ñuñoa'),'mañana y Ñuñoa')
if __name__=='__main__':unittest.main()
