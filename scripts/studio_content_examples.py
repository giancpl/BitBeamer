"""Small editable demonstrations of the typed API, filtered for isolated subsets."""
from studio_guides import command, PREAMBLE, END


def document(entries):
    available={e['id']:e for e in entries}
    samples=[
      ('three-cards', {'text/title':'Your concepts','text/caption-one':'Learn','text/caption-two':'Build','text/caption-three':'Share','icon/1':'alice','icon/2':'cow','icon/3':'bitcoin'}),
      ('two-cards', {'text/1':'People','text/2':'Bitcoin','icon/1':'alice','icon/2':'bitcoin'}),
      ('five-icon-row', {'text/title':'Values','text/2':'Learn','text/3':'Build','text/4':'Save','text/5':'Verify','text/6':'Share','icon/1':'alice','icon/2':'cow','icon/3':'bitcoin','icon/4':'alice','icon/5':'bitcoin'}),
      ('checklist-rail', {'clear':'text','text/title':r'Your\\checklist','heading/1':'Choose hardware','body/1':'Use a device that meets your needs.','heading/2':'Install software','body/2':'Follow the official project instructions.','heading/4':'Verify the setup','body/4':'Check connections and available storage.','heading/5':'Start your node','body/5':'Keep your recovery information safe.'}),
      ('four-card-grid', {'text/title':'Your workshop','text/item-3-1':'Third concept','text/item-3-2':r'\textbullet{} A short takeaway','heading/text-2':'First concept','body/text-2':r'\studiolist{{One point},{Another point}}','heading/text-4':'Second concept','body/text-4':'A short explanation.','heading/text-5':'Next steps','body/text-5':'Share what you learned.'}),
      ('image-left', {'text/title':'Your image','image/1':'assets/generated/cow.pdf'}),
      ('code', {'text/title':'Your commands','file/1':'examples/code/studio-transaction.txt'}),
      ('closing', {'text/title':'Thanks!'})]
    chosen=[(name,values) for name,values in samples if name in available]
    if not chosen and entries:
        entry=entries[0]
        # Every subset gets a useful, valid example, even without a featured model.
        first=next((f for f in entry['fields'] if f['type']=='text'),None)
        chosen=[(entry['id'],{first['slot']['key']:first['default'].replace(r'\\\\',r'\\')} if first else {})]
    lines=['% Editable typed-slot examples. Copy one command into your own document.',PREAMBLE.rstrip()]
    for name,values in chosen:
        lines += ['', '% '+name+' — see its individual guide for every numbered slot.', command(name,values)]
    return '\n'.join(lines)+'\n'+END
