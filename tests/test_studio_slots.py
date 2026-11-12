"""Typed slot coverage, preserved card dependencies and strict read-only artwork checks."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import studio_slots
import studio_templates
from studio_parts import references


class StudioSlotTests(unittest.TestCase):
    def test_every_public_field_has_a_unique_typed_slot(self):
        entries=studio_templates.inspect_templates(ROOT)
        self.assertEqual(len(entries),196)
        for entry in entries:
            studio_slots.validate([entry])
            self.assertEqual(len({f['slot']['key'] for f in entry['fields']}),len(entry['fields']))
        broken=copy.deepcopy(entries[0])
        broken['fields'][1]['slot']=dict(broken['fields'][0]['slot'])
        with self.assertRaisesRegex(RuntimeError,'Invalid Studio slot'):
            studio_slots.validate([broken])

    def test_missing_frame_dependency_is_rejected_before_packaging(self):
        entry=copy.deepcopy(next(e for e in studio_templates.inspect_templates(ROOT) if e.get('slot_parts')))
        entry['slot_parts']=[]
        with self.assertRaisesRegex(RuntimeError,'slot dependencies disagree'):
            studio_slots.validate([entry])

    def test_slot_numbers_survive_metadata_reordering(self):
        entry=next(e for e in studio_templates.inspect_templates(ROOT) if e['id']=='five-icon-row')
        before=set(studio_slots.declarations(entry))
        entry=copy.deepcopy(entry);entry['fields'].reverse()
        self.assertEqual(set(studio_slots.declarations(entry)),before)
        graphics=sorted((f for f in entry['fields'] if f['type']=='graphic'),key=lambda f:f['slot']['number'])
        self.assertEqual([f['box'][0] for f in graphics],sorted(f['box'][0] for f in graphics))

    def test_reviewed_icon_cards_keep_common_bounds_when_reannotated(self):
        entries=studio_templates.inspect_templates(ROOT)
        for name in ('two-cards','three-cards'):
            entry=next(e for e in entries if e['id']==name)
            for field in entry['fields']:
                if field['type']!='graphic':continue
                self.assertEqual(field['slot']['content'][2:],[216,216])
                recipe=studio_slots.card_recipe(ROOT,field)
                if recipe:
                    self.assertEqual(recipe['content'][2:],[216,216])
                    self.assertEqual(recipe['frame_box'],[488,489])

    def test_separated_cards_keep_the_original_shadow_canvas(self):
        data=json.loads((ROOT/'images/studio/slots/manifest.json').read_text(encoding="utf-8"))
        self.assertEqual(len(data['parts']),34)
        for part in data['parts']:
            source=ET.parse(ROOT/part['source']).getroot()
            parent=ET.parse(ROOT/part['parent']).getroot()
            self.assertEqual(source.get('viewBox'),parent.get('viewBox'))
            nodes=[n for n in source if not n.tag.endswith('defs')]
            self.assertEqual(len(nodes),1)
            self.assertTrue(nodes[0].get('filter'))
            ids={n.get('id') for n in source.iter() if n.get('id')}
            self.assertFalse(references([source])-ids)

    def test_prepared_slot_check_is_read_only_and_needs_no_converter(self):
        files=list((ROOT/'images/studio/slots').rglob('*'))
        before={p:p.stat().st_mtime_ns for p in files if p.is_file()}
        with mock.patch('asset_library.rsvg_modules',side_effect=AssertionError('No converter on a normal build')):
            self.assertEqual(studio_slots.prepare(ROOT,check=True),34)
        self.assertEqual({p:p.stat().st_mtime_ns for p in before},before)

    def test_stale_slot_pdf_is_rejected_without_overwriting_it(self):
        item=json.loads((ROOT/'images/studio/slots/manifest.json').read_text(encoding="utf-8"))['parts'][0]
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for name in [item['source'],item['parent'],item['pdf']]:
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
            manifest=root/'images/studio/slots/manifest.json'
            manifest.write_text(json.dumps({'parts':[item]}), encoding="utf-8")
            target=root/item['pdf'];target.write_bytes(b'changed')
            with self.assertRaisesRegex(RuntimeError,'Stale Studio slot background'):
                studio_slots.prepare(root,check=True)
            self.assertEqual(target.read_bytes(),b'changed')

    def test_aliases_and_custom_exports_include_slot_dependencies(self):
        import importlib.util
        spec=importlib.util.spec_from_file_location('slots_packager',ROOT/'scripts/package-studio-review.py')
        packager=importlib.util.module_from_spec(spec);spec.loader.exec_module(packager)
        for entry in studio_templates.inspect_templates(ROOT)+studio_templates.inspect_aliases(ROOT):
            files=packager.entry_files(ROOT,entry)
            self.assertTrue(set(entry.get('slot_parts',[])) <= set(files))
        alias=studio_templates.inspect_aliases(ROOT)[0]
        registry=studio_templates.registry_document([], [alias])
        self.assertIn(r'\DeclareStudioTemplate{'+alias['alias_of']+'}',registry)
        self.assertIn(r'\DeclareStudioTextSlot{'+alias['alias_of']+'}',registry)


if __name__=='__main__':unittest.main()
