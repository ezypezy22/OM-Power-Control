import importlib.util,re,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('generate_themes',Path(__file__).with_name('scripts')/'generate-themes.py')
gt=importlib.util.module_from_spec(spec);spec.loader.exec_module(gt)
PAGE=Path(__file__).with_name('live.html').read_text(encoding='utf-8')

class ThemeTests(unittest.TestCase):
 def test_generated_blocks_are_current(self):
  out,_,_=gt.build(gt.read(PAGE))
  self.assertIn(gt.block(out),PAGE,'run scripts/generate-themes.py')
 def test_text_meets_the_contrast_target_in_every_theme(self):
  _,report,failed=gt.build(gt.read(PAGE))
  self.assertFalse(failed,[r for r in report if r[2]<gt.TARGET[r[0]]-.05])
  self.assertTrue(all(r[2]>=7-.05 for r in report if r[0].startswith('hc')))
 def test_page_has_no_hard_coded_colours_outside_the_token_blocks(self):
  style=PAGE[PAGE.index('<style>'):PAGE.index('</style>')]
  body=re.sub(r':root\{[^}]*\}','',style,count=1)
  body=re.sub(r'/\*THEMES:START\*/.*?/\*THEMES:END\*/','',body,flags=re.S)
  self.assertEqual(re.findall(r'#[0-9a-fA-F]{3,8}\b',body),[])
 def test_every_theme_defines_every_token(self):
  dark=gt.read(PAGE);out,_,_=gt.build(dark)
  tokens={k for k in dark if re.match(r'(bg|tx|ln|fl|sh)-',k)}|set(gt.NAMED)
  for theme,vals in out.items():self.assertTrue(tokens<=set(vals),theme)
if __name__=='__main__':unittest.main()
