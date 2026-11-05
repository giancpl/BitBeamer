"""Reject retired visual interfaces while preserving redirects and source provenance."""
from pathlib import Path


def check_retired_galleries(root):
    for name in ('scripts/studio_gallery.py','scripts/studio-gallery.js','scripts/studio_pages_review.py','library/catalogue.js'):
        if (root/name).exists():raise ValueError('Retired gallery code was restored: '+name)
    pages=[root/'docs/templates/index.html',root/'library/index.html',root/'design-references/figma/review.html']
    for folder in ('design-references/figma/collection-review','design-references/figma/official-decks/review','design-references/figma/pilot-review','build/review/pages','build/review/style-validation','build/review/team','build/review/closing','build/review/agendas','build/library/economics-refinement'):
        path=root/folder
        if path.exists():pages.extend(path.rglob('*.html'))
    for path in pages:
        if not path.exists():continue
        text=path.read_text(encoding='utf-8')
        if 'location.replace' not in text or len(text.encode())>4096:
            raise ValueError('Retired gallery must redirect to the unified guide: '+str(path.relative_to(root)))
    for path in [root/'README.md',*(root/'docs').glob('*.md'),*(root/'library').glob('*.md')]:
        if path.name=='CHECKS.md':continue  # Dated verification reports may describe earlier artifacts.
        text=path.read_text(encoding='utf-8')
        if ']('+('templates/index.html')+')' in text or ']('+('../docs/templates/index.html')+')' in text:
            raise ValueError('Documentation still recommends a retired gallery: '+str(path.relative_to(root)))
    return len(pages)


def check_guide_links(root):
    """Check HTML and deferred catalogue links without a browser or network."""
    from html.parser import HTMLParser
    from urllib.parse import unquote,urlsplit
    from slide_guide import catalogue,lesson_catalogue
    base=root/'docs/slides';urls=[]
    class Links(HTMLParser):
        def handle_starttag(self,tag,attrs):
            for key,value in attrs:
                if key in ('href','src') and value:urls.append(value)
    Links().feed((base/'index.html').read_text(encoding='utf-8'))
    for row in catalogue(root)['rows']:
        for choice in row['choices']:
            urls.extend(choice[key] for key in ('source','guide','content_source') if choice.get(key))
            urls.extend(choice['preview'][key] for key in ('url','hd') if choice['preview'].get(key))
    for slide in lesson_catalogue(root)['slides'].values():
        urls.append(slide['source']);urls.extend(slide['preview'][key] for key in ('url','hd') if slide['preview'].get(key))
    urls.extend(['catalogue-lessons.js','catalogue-library.js'])
    for url in set(urls):
        parts=urlsplit(url)
        if parts.scheme or not parts.path:continue
        target=(base/unquote(parts.path)).resolve()
        if not target.is_relative_to(root.resolve()) or not target.is_file():raise ValueError('Broken slide guide link: '+url)
    return len(set(urls))
