"""Append declared long-copy/empty-field specimens to the active comparison PDF."""
from pathlib import Path
import re
import textwrap


def validate_specimen(root, batch):
    specimen = batch.get('specimen')
    if not specimen:
        return
    source = root / specimen['source']
    if not source.resolve().is_relative_to((root / 'examples').resolve()) or source.suffix != '.tex' or not source.is_file():
        raise ValueError('Review specimens must be existing official examples: ' + batch['id'])
    for sample in specimen['samples']:
        if sample['composition'] not in batch['compositions'] or type(sample['page']) is not int or sample['page'] < 1 or not sample.get('label'):
            raise ValueError('Invalid specimen page mapping: ' + batch['id'])


def invocations(text):
    from lesson_library import tex_source
    text = tex_source(text)
    result = []
    for match in re.finditer(r'\\studiotemplate\b', text):
        position = match.end()
        while text[position].isspace(): position += 1
        if text[position] == '[':
            braces = 0
            position += 1
            while position < len(text):
                char = text[position]
                if char == '{': braces += 1
                elif char == '}': braces -= 1
                elif char == ']' and braces == 0:
                    position += 1
                    break
                position += 1
        identifier = re.match(r'\s*\{[a-z][a-z0-9-]*\}', text[position:])
        if not identifier:
            raise ValueError('Review specimens need literal public template invocations')
        result.append(text[match.start():position + identifier.end()])
    return result


def append_specimens(root, target, batches, backend, image):
    import pymupdf as fitz
    from review import compile_document
    additions = []
    for batch in batches:
        if not batch.get('specimen'):
            continue
        samples = [s for s in batch['specimen']['samples'] if s['composition'] in batch['compositions']]
        if not samples:
            continue
        validate_specimen(root, dict(batch, specimen=dict(batch['specimen'], samples=samples)))
        source = root / batch['specimen']['source']
        commands = invocations(source.read_text(encoding='utf-8'))
        output = root / 'build/review/specimens' / batch['id']
        output.mkdir(parents=True, exist_ok=True)
        pdf = compile_document(root, source, output, backend, image)
        with fitz.open(pdf) as document:
            if len(document) != len(commands):
                raise ValueError('Specimen commands must correspond one-to-one with PDF pages')
            for sample in samples:
                if sample['page'] > len(document):
                    raise ValueError('Specimen page exceeds its compiled PDF')
                additions.append(dict(sample, pdf=pdf, command=commands[sample['page'] - 1], family=batch['family']))
    if not additions:
        return None
    base_names = [(name, batch['family']) for batch in batches for name in batch['compositions']]
    total = len(base_names) + len(additions)
    temporary = target.with_suffix('.specimens.pdf')
    with fitz.open(target) as base, fitz.open() as result:
        if len(base) != len(base_names):
            raise ValueError('Base comparison does not match its pending compositions')
        for index, (name, family) in enumerate(base_names):
            page = result.new_page(width=1400, height=1000)
            page.insert_text((20,28), f'{index+1} / {total} | {family} | {name} | Original / current', fontsize=14)
            page.show_pdf_page(fitz.Rect(0,65,1400,920), base, index,
                               clip=fitz.Rect(0,30,base[index].rect.width,base[index].rect.height))
        for sample in additions:
            page = result.new_page(width=1400, height=1000)
            page.insert_text((20,28), f'{len(result)} / {total} | {sample["family"]} | {sample["composition"]} | {sample["label"]}', fontsize=14)
            with fitz.open(sample['pdf']) as source:
                page.show_pdf_page(fitz.Rect(20,60,1380,825), source, sample['page'] - 1)
            for i, line in enumerate(textwrap.wrap('Use: ' + ' '.join(sample['command'].split()), width=185,
                                                  break_long_words=False, break_on_hyphens=False)):
                page.insert_text((20,850+11*i), line, fontsize=9, fontname='cour')
        result.set_metadata({'title': 'BitBeamer - pending original comparisons and content specimens'})
        result.save(temporary, garbage=4, deflate=True)
    temporary.replace(target)
    return total
