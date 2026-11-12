"""Portable source coverage, closed dependencies and upload-sized review checks."""
import base64
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
import xml.etree.ElementTree as ET
from zipfile import ZipFile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from studio_collection import prepare
from studio_parts import references
spec=importlib.util.spec_from_file_location('review_packager',ROOT/'scripts/package-studio-review.py');packager=importlib.util.module_from_spec(spec);spec.loader.exec_module(packager)
class StudioCollectionTests(unittest.TestCase):
    def test_every_export_has_an_explicit_destination(self):
        frames=json.loads((ROOT/'templates/figma-inventory.json').read_text(encoding='utf-8'))['frames']
        models={e['id'] for e in json.loads((ROOT/'templates/index.json').read_text(encoding='utf-8'))['templates']}
        self.assertEqual(len(frames),1073)
        allowed={'model','example','duplicate','resource','outside-slide-format','excluded'}
        for frame in frames:
            assignment=frame['assignment'];self.assertIn(assignment['destination'],allowed)
            if 'template'in assignment:self.assertIn(assignment['template'],models)
            if assignment['destination']=='example':self.assertEqual(assignment['grouping_status'],'in review')
    def test_crops_have_closed_local_dependencies(self):
        count=prepare(ROOT,check=True);self.assertGreater(count,100)
        parts=json.loads((ROOT/'images/studio/collection/manifest.json').read_text(encoding='utf-8'))['parts']
        self.assertEqual(len({p['name'] for p in parts}),len(parts))
        for part in parts:
            svg=ET.parse(ROOT/part['source']).getroot();ids={n.get('id') for n in svg.iter() if n.get('id')}
            self.assertFalse(references([svg])-ids,part['name'])
            self.assertEqual(part['anchor'],part['render_box'][:2])
            for node in svg.iter():
                for key,value in node.attrib.items():
                    if key.endswith('href') and not value.startswith('#') and node.tag.split('}')[-1] != 'a':
                        self.assertFalse(value.startswith(('http:','https:')))
                        if value.startswith('data:'):
                            header, payload = value.split(',', 1)
                            self.assertIn(';base64', header)
                            self.assertTrue(base64.b64decode(payload, validate=True))
                        else:
                            self.assertTrue(((ROOT/part['source']).parent/value).is_file())
    def test_prepared_part_gallery_is_fresh(self):
        spec=importlib.util.spec_from_file_location('part_gallery',ROOT/'scripts/catalogue-studio-collection.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        count=module.catalogue(ROOT,check=True)
        self.assertEqual(count,sum(len(json.loads((ROOT/('images/studio/'+folder+'/manifest.json')).read_text(encoding='utf-8'))['parts']) for folder in ('collection','parts')))
    def test_original_jpeg_stream_is_embedded_without_recompression(self):
        parts=json.loads((ROOT/'images/studio/collection/manifest.json').read_text(encoding='utf-8'))['parts']
        part=next(p for p in parts if p.get('reference')=='figma-0032' and p.get('renderer'))
        pdf=(ROOT/'images/studio/collection'/(part['name']+'.pdf')).read_bytes()
        original=next(d for d in part['dependencies'] if d['path'].endswith('.jpg'))
        self.assertIn((ROOT/original['path']).read_bytes(),pdf)
    def test_measured_fields_and_aliases_have_valid_defaults(self):
        entries=__import__('studio_templates').inspect_templates(ROOT);ids={e['id'] for e in entries}
        self.assertGreater(len(entries),88)
        for entry in entries:
            self.assertIn(entry['status'],{'in review','changes requested','approved','supplementary'})
            if entry.get('alias_of'):self.assertIn(entry['alias_of'],ids)
            fields=entry['fields'];self.assertEqual(len({f['name'] for f in fields}),len(fields))
            for field in fields:
                if 'box'in field:self.assertTrue(all(isinstance(v,(int,float)) for v in field['box']))
                self.assertIn(field['type'],{'text','graphic','file','math'})
    def test_selected_review_archive_is_reproducible(self):
        with tempfile.TemporaryDirectory() as temp:
            first=packager.package(ROOT,Path(temp)/'one',names=['cover','three-cards','merkle-tree'])
            second=packager.package(ROOT,Path(temp)/'two',names=['cover','three-cards','merkle-tree'])
            self.assertEqual(len(first),1)
            a=Path(temp)/'one'/first[0]['archive'];b=Path(temp)/'two'/second[0]['archive']
            self.assertEqual(a.read_bytes(),b.read_bytes());self.assertLess(a.stat().st_size,50*1024*1024)
            with ZipFile(a) as archive:
                names=archive.namelist();self.assertIn('main.tex',names);self.assertIn('catalogue.tex',names)
                self.assertIn('assets/generated/catalogue.tex',names)
                self.assertEqual(archive.read('assets/generated/catalogue.tex').count(b'\\DeclareBitPolitoAsset{'),171)
                self.assertIn('guides/three-cards.md',names)
                self.assertIn('TEMPLATES.md',names)
                self.assertNotIn('templates/studio/code.tex',names)
                self.assertFalse(any(n.endswith(('.svg','.py','.json')) for n in names))
                self.assertFalse(any('academic'in n or 'design-references'in n for n in names))
    def test_failed_review_packaging_preserves_the_previous_set(self):
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp)/'review'
            packager.package(ROOT,output,names=['cover','three-cards','merkle-tree'])
            before={p.name:p.read_bytes() for p in output.iterdir()}
            original=packager.write_archive
            calls=[]
            def fail_second(*args):
                calls.append(args)
                if len(calls)==2:raise RuntimeError('Simulated second archive failure')
                return original(*args)
            with mock.patch.object(packager,'LIMIT',1), mock.patch.object(packager,'write_archive',side_effect=fail_second):
                with self.assertRaisesRegex(RuntimeError,'second archive'):
                    packager.package(ROOT,output,names=['cover','three-cards','merkle-tree'])
            self.assertEqual(before,{p.name:p.read_bytes() for p in output.iterdir()})
    def test_selected_export_removes_obsolete_review_archives(self):
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp)/'review'
            with mock.patch.object(packager,'LIMIT',1):
                packager.package(ROOT,output,names=['cover','three-cards','merkle-tree'])
            self.assertEqual(len(list(output.glob('*.zip'))),3)
            packager.package(ROOT,output,names=['cover'])
            self.assertEqual(len(list(output.glob('*.zip'))),1)
            self.assertEqual(len(json.loads((output/'index.json').read_text(encoding='utf-8'))['archives']),1)
if __name__=='__main__':unittest.main()
