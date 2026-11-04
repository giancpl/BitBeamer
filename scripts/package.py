"""Create a minimal, self-contained Overleaf ZIP from prepared artwork."""

import argparse
from pathlib import Path
import re
import sys
from zipfile import ZIP_STORED, ZipFile, ZipInfo

from asset_library import check_prepared, inspect_library
from asset_catalogue import check_catalogue
from studio_assets import prepare_studio
from studio_templates import inspect_templates, inspect_aliases, prepare_catalogue, catalogue_document, registry_document

ROOT = Path(__file__).resolve().parents[1]
DOCUMENT_SOURCES = {
    'main.tex': 'start-academic.tex',
    'academic-showcase.tex': 'main-academic.tex',
    'start.tex': 'start-academic.tex',
    'assets-example.tex': 'examples/assets-example.tex',
    'asset-catalogue.tex': 'examples/asset-catalogue.tex',
    'icon-cheatsheet.tex': 'examples/icon-cheatsheet.tex',
    'cover-layouts.tex': 'examples/cover-layouts.tex',
}
DOCUMENTS = tuple(DOCUMENT_SOURCES)
THEME_FILES = (
    'beamerthemebitpolito-academic.sty',
    'beamerthemebitpolito.sty', 'beamerinnerthemebitpolito.sty',
    'beamerouterthemebitpolito.sty', 'beamercolorthemebitpolito.sty',
    'beamerfontthemebitpolito.sty', 'bitpolitoassets.sty',
)
# A fixed list keeps unused PDFs and local experiments out of release downloads.
BRAND_FILES = (
    'logo-white.pdf', 'bull-white.pdf', 'monogram-white.pdf', 'bitcoin-white.pdf',
    'polito-coat-of-arms-white.pdf', 'crypto-primary-white.pdf',
    'crypto-symbol-white.pdf', 'first-page-background.pdf', 'LICENSE',
)


STYLES = ('academic', 'studio')
ARCHIVES = {'academic': 'bitbeamer-academic-overleaf.zip', 'studio': 'bitbeamer-studio-overleaf.zip'}
STUDIO_DOCUMENT_SOURCES = {**DOCUMENT_SOURCES, 'main.tex': 'main-studio.tex', 'start.tex': 'start-studio.tex'}
STUDIO_DOCUMENT_SOURCES.pop('cover-layouts.tex')
STUDIO_DOCUMENT_SOURCES.pop('academic-showcase.tex')
STUDIO_DOCUMENT_SOURCES['studio-template-catalogue.tex'] = 'examples/studio-template-catalogue.tex'
STUDIO_DOCUMENT_SOURCES['customization.tex'] = 'examples/studio-customization.tex'
STUDIO_DOCUMENT_SOURCES['studio-agendas.tex'] = 'examples/studio-agendas.tex'
STUDIO_DOCUMENT_SOURCES['studio-team.tex'] = 'examples/studio-team.tex'
STUDIO_DOCUMENT_SOURCES['studio-closing.tex'] = 'examples/studio-closing.tex'
STUDIO_THEME_FILES = (
    'bitpolitostudiomodels.sty', 'bitpolitostudioslots.sty', 'bitpolitostudiopilots.sty', 'bitpolitostudiotemplates.sty', 'bitpolitostudiolayouts.sty', 'bitpolitostudiomeasured.sty',
    'beamerthemebitpolito-studio.sty', 'beamerinnerthemebitpolito-studio.sty',
    'beamerouterthemebitpolito-studio.sty', 'beamerfontthemebitpolito-studio.sty',
    'beamerfontthemebitpolito.sty', 'beamercolorthemebitpolito.sty', 'bitpolitoassets.sty',
)
STUDIO_BRAND_FILES = ('bull-white.pdf', 'polito-coat-of-arms-white.pdf', 'LICENSE')
STUDIO_ASSETS = ('alice-white.pdf', 'bob-white.pdf', 'pig-white.pdf', 'cover-pattern-white.pdf',
                 'closing/qrcode.pdf', 'closing/telegram.pdf', 'closing/instagram.pdf',
                 'closing/twitter.pdf', 'closing/youtube.pdf')
LEGACY_ARCHIVE = 'bitbeamer-overleaf.zip'


def document_sources(style):
    if style not in STYLES:
        raise ValueError('Select academic or studio for a single package.')
    return DOCUMENT_SOURCES if style == 'academic' else STUDIO_DOCUMENT_SOURCES


BUDGET = 45 * 1024 * 1024
UPLOAD_LIMIT = 50 * 1024 * 1024


def studio_data(root):
    from studio_review import selected, package_selection
    from studio_guides import portable_guides
    prepare_studio(root, check=True)
    from studio_slots import prepare as check_slots
    check_slots(root, check=True)
    from studio_palettes import check as check_palettes
    check_palettes(root)
    prepare_catalogue(root, check=True)
    all_entries = inspect_templates(root)
    by_id = {e['id']:e for e in all_entries}
    catalogue_entries = [by_id[item['id']] for item in selected(root,all_entries)]
    entries = [by_id[item['id']] for item in package_selection(root)]
    names = {e['id'] for e in entries}
    aliases = [a for a in inspect_aliases(root,all_entries) if a['alias_of'] in names]
    files = {name:root/name for name in STUDIO_THEME_FILES}
    files.update({name:root/name for name in ('bibliography.bib','LICENSE','.latexmkrc')})
    files.update({'images/bitpolito/'+name:root/'images/bitpolito'/name for name in STUDIO_BRAND_FILES})
    files.update({'images/studio/'+name:root/'images/studio'/name for name in STUDIO_ASSETS})
    from studio_models import dependencies as palette_dependencies
    files.update(palette_dependencies(root, entries + aliases))
    for entry in entries + aliases:
        files[entry['source']] = root/entry['source']
        for name in entry.get('slot_parts', []):
            files[name] = root/name
        for part in entry.get('parts',[]):
            path = next((root/'images/studio'/folder/(part+'.pdf') for folder in ('parts','collection')
                         if (root/'images/studio'/folder/(part+'.pdf')).is_file()),None)
            if path is None:
                raise RuntimeError('Missing prepared part: '+part)
            files[path.relative_to(root).as_posix()] = path
    for path in (root/'assets/generated').glob('*.pdf'):
        files[path.relative_to(root).as_posix()] = path
    for relative in ('assets/generated/catalogue.tex','examples/code/studio-transaction.txt','examples/data/studio-line.csv'):
        files[relative] = root/relative
    data = {name:path.read_bytes() for name,path in files.items()}
    for name, source in STUDIO_DOCUMENT_SOURCES.items():
        if name == 'customization.tex':
            from studio_content_examples import document as customization_document
            data[name] = customization_document(entries).encode()
        elif name == 'studio-template-catalogue.tex':
            data[name] = catalogue_document(catalogue_entries).encode()
        else:
            raw = (root/source).read_bytes()
            if name in ('assets-example.tex','asset-catalogue.tex'):
                raw = raw.replace(b'\\usetheme{bitpolito}',b'\\usetheme{bitpolito-studio}')
            data[name] = raw
    data['templates/studio/registry.tex'] = registry_document(entries,aliases).encode()
    data.update(portable_guides(root,entries))
    data['README.md'] = ('''# BitBeamer Studio — Overleaf

Open main.tex and select pdfLaTeX. It contains the current compact selection.
For an editable starting document, select start.tex: cover, team introduction, automatic contents, two content slides and closing.
Select studio-template-catalogue.tex for a labelled view of the working selection.
The classic blue title page is the default. Optional BitGeneration covers are included.

See [slide guides](TEMPLATES.md), [Studio commands](STUDIO.md) and [icons](ICONS.md).
Create a new .tex file at the project root and copy a guide's complete example.
No Python, Docker, converter, shell escape or original Figma export is needed.
With installed TeX Live or MacTeX, run `latexmk -pdf main.tex`.

This project includes selected compositions, the optional standard covers, team introduction and four/five-item agendas with their dependencies.
The full repository retains every composition and supports custom review exports.
Compilation checks do not imply graphical approval.
''').encode()
    data['STUDIO.md'] = ('''# Studio commands

Use `\\usetheme{bitpolito-studio}` in a 16:9 Beamer document.
Load `\\usepackage{bitpolitostudiotemplates}` for the named compositions.
Each `\\studiotemplate[fields]{name}` creates a complete frame, outside a frame environment.
The [individual guides](TEMPLATES.md) list included models, exact fields and complete examples.
Empty fields preserve geometry. Unknown fields and overflow produce diagnostics.
Edit the corresponding source under templates/studio for structural changes.

Standard pages use `\\studiotitleframe`, `\\studiotocframe` and `\\closingframe`.
The cover uses document metadata; contents uses `\\section` declarations.
The default cover is classic blue. Use `\\studiotitleframe[variant=bitgeneration]`
for the light BitGeneration cover or `\\studiotitleframe[variant=bitgeneration-photo]`
for its photographic version. Both use `\\title`, `\\author` and `\\institute`.
Classic also supports `\\subtitle` and `\\date`; variants retain their original text slots.
Insert `\\studioteamframe` between cover and contents for the supplied team slide.
Its four values and captions are editable; `image-one` replaces the entire collage.
The supplied team figures are examples: update them before presenting.
The closing QR is visible by default: use `\\closingframe[qrcode=false]` to hide it
and centre the same text/social group. `qr-image={images/my-qr.pdf}` replaces it.
Title, subtitle and copyright remain editable; each call resets its options.
See studio-closing.tex for examples.
Use `\\studiotocframe[variant=panels]` for four section titles or
`\\studiotocframe[variant=panels-five]` for five. These preserve the original panel
geometry, ignore subsections and leave unused panels blank. Too many sections
produce an explicit error. Both measured agenda variants are included.
For manual content, use the `agenda` model with `item-one` through `item-four` or
`item-five`. Omitted fields retain descriptive defaults; use `{}` for empty text.
Use `\\studiotocframe[title={Agenda}]` to change its heading and
`\\studioframe[subtitle={Optional subtitle}]{Title}{Content}` for a simple aligned slide.
All these commands create complete frames. Place catalogue calls outside them.

Normal Beamer frames and Studio components remain available alongside templates:
`\\studiotocframe`, `\\studiosectionframe{title}`, `\\studiostatementframe{text}`,
`studiocards` with `\\studiocard{graphic}{caption}`, `\\studiosplitframe{upper}{lower}`,
`\\studiofigureframe{caption}{graphic}`, and `\\closingframe`.
Prepared parts use `\\studiopart[width=...]{name}` and preserve proportions.

On Overleaf use pdfLaTeX. With installed TeX, run `latexmk -pdf main.tex`.
See [the quick start](README.md) and [icon guide](ICONS.md).
''').encode()
    data['ICONS.md'] = icon_guide(root)
    return data


def icon_guide(root):
    raw = (root/'docs/ICONS.md').read_bytes()
    return raw.replace(b'../assets/CATALOGUE.md',b'asset-catalogue.tex').replace(
        b'../examples/icon-cheatsheet.tex',b'icon-cheatsheet.tex').replace(
        b'(ASSETS.md)',b'(README.md)').replace(
        b'python3 scripts/build.py examples/icon-cheatsheet.tex',b'latexmk -pdf icon-cheatsheet.tex')


def write_archive(target, data, budget=None):
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name+'.tmp')
    try:
        with ZipFile(temporary,'w',ZIP_STORED) as archive:
            for name, content in sorted(data.items()):
                if Path(name).suffix in {'.tex','.sty','.md','.bib','.csv','.txt'}:
                    content = content.replace(b'\r\n',b'\n')
                info = ZipInfo(name,date_time=(1980,1,1,0,0,0))
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                archive.writestr(info,content)
        if budget and temporary.stat().st_size > budget:
            raise RuntimeError('Studio selection exceeds the 45 MiB packaging budget; use custom split review packages. Previous output preserved.')
        if temporary.stat().st_size > UPLOAD_LIMIT:
            raise RuntimeError('Overleaf archive exceeds 50 MiB. Previous output preserved.')
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    return target


def package(root=ROOT, target=None, style='studio', review=False):
    root = root.resolve()
    if style not in STYLES:
        raise ValueError('Select academic or studio')
    if style == 'studio' and not review:
        from studio_review import require_approved
        require_approved(root)
    check_prepared(root)
    check_catalogue(root)
    target = Path(target) if target else root/('build/review/packages' if review else 'dist')/ARCHIVES[style]
    if review and target.resolve().is_relative_to((root/'dist').resolve()):
        raise ValueError('Review packages must stay outside dist/')
    if style == 'studio':
        data = studio_data(root)
    else:
        _, records, _, _ = inspect_library(root)
        files = {name:root/source for name,source in DOCUMENT_SOURCES.items()}
        files.update({name:root/name for name in (*THEME_FILES,'bibliography.bib','LICENSE','.latexmkrc')})
        files['README.md'] = root/'docs/OVERLEAF.md'
        for name in BRAND_FILES:
            files['images/bitpolito/'+name] = root/'images/bitpolito'/name
        files['assets/generated/catalogue.tex'] = root/'assets/generated/catalogue.tex'
        for record in records.values():
            files['assets/generated/'+record['output']] = root/'assets/generated'/record['output']
        data = {name:path.read_bytes() for name,path in files.items()}
        data['ICONS.md'] = icon_guide(root)
    write_archive(target,data,BUDGET if style == 'studio' else None)
    if style == 'academic' and target.name == ARCHIVES['academic'] and target.parent == root/'dist':
        alias = target.with_name(LEGACY_ARCHIVE)
        temporary = alias.with_suffix('.zip.tmp')
        try:
            temporary.write_bytes(target.read_bytes())
            temporary.replace(alias)
        finally:
            temporary.unlink(missing_ok=True)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--style',choices=(*STYLES,'all'),default='studio')
    parser.add_argument('--review',action='store_true',help='Package unapproved work under build/review/, never dist/')
    args = parser.parse_args()
    try:
        if args.style == 'all':
            if args.output:
                raise ValueError('--output requires one style')
            import tempfile
            destination = ROOT/('build/review/packages' if args.review else 'dist')
            if not args.review:
                from studio_review import require_approved
                require_approved(ROOT)
            destination.mkdir(parents=True,exist_ok=True)
            with tempfile.TemporaryDirectory(prefix='.packages-',dir=destination) as temporary:
                for style in STYLES:
                    package(target=Path(temporary)/ARCHIVES[style],style=style,review=args.review)
                for style in STYLES:
                    source = Path(temporary)/ARCHIVES[style]
                    source.replace(destination/source.name)
                    print(destination/source.name)
                if not args.review:
                    (destination/LEGACY_ARCHIVE).write_bytes((destination/ARCHIVES['academic']).read_bytes())
        else:
            print(package(target=args.output,style=args.style,review=args.review))
    except (OSError,RuntimeError,ValueError) as error:
        print('Packaging failed: '+str(error),file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
