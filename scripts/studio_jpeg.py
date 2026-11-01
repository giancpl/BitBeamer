"""Keep original JPEG streams in prepared SVG crops; no image recompression."""
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from asset_library import rsvg_modules
HREF='{http://www.w3.org/1999/xlink}href'
def jpeg_pdf(source,target):
    from PIL import Image
    tree=ET.parse(source).getroot();lookup={e.get('id'):e for e in tree.iter() if e.get('id')}
    cairo,Rsvg=rsvg_modules();plans={};surfaces=[]
    def jpeg_pattern(e):
        if e.tag.split('}')[-1]!='rect':return None
        match=re.fullmatch(r'url\(#([^)]*)\)',e.get('fill',''))
        if not match:return None
        pattern=lookup.get(match.group(1))
        if pattern is None or pattern.tag.split('}')[-1]!='pattern' or pattern.get('patternContentUnits')!='objectBoundingBox':return None
        uses=list(pattern)
        if len(uses)!=1 or uses[0].tag.split('}')[-1]!='use':return None
        use=uses[0];image=lookup.get(use.get(HREF,use.get('href',''))[1:])
        if image is None or image.tag.split('}')[-1]!='image':return None
        filename=image.get(HREF,image.get('href',''))
        if not filename.lower().endswith(('.jpg','.jpeg')):return None
        transform=use.get('transform','');m=re.fullmatch(r'matrix\(([^)]+)\)',transform)
        if m:
            values=[float(x) for x in re.split('[, ]+',m.group(1).strip())]
            if len(values)!=6:return None
        else:
            scale=re.fullmatch(r'scale\(([^)]+)\)',transform)
            if not scale:return None
            factors=[float(x) for x in re.split('[, ]+',scale.group(1).strip())]
            if len(factors) not in (1,2):return None
            values=[factors[0],0,0,factors[-1],0,0]
        return source.parent/filename,values
    counter=0
    def supported_mask(node):
        match=re.fullmatch(r'url\(#([^)]*)\)',node.get('mask',''))
        if not match:return True
        mask=lookup.get(match.group(1))
        return mask is not None and len(mask)==1 and mask[0].tag.split('}')[-1]=='rect' and not mask[0].get('transform')
    def inspect(node,ancestors=()):
        nonlocal counter
        tag=node.tag.split('}')[-1]
        if tag in ['defs','mask','clipPath']:return
        counter+=1
        if not node.get('id'):node.set('id','jpeg-preparation-'+str(counter))
        plan=jpeg_pattern(node)
        if plan:
            # A filter on a photograph requires the ordinary SVG compositor.
            if any(a.get('filter') for a in ancestors) or node.get('filter'):return
            if not all(supported_mask(a) for a in ancestors+(node,)):return
            plans[node.get('id')]=plan
        for child in node:inspect(child,ancestors+(node,))
    inspect(tree)
    if not plans:return False
    # Loading must happen with the base URI already set for all external resources.
    handle=Rsvg.Handle.new_with_flags(Rsvg.HandleFlags.FLAG_UNLIMITED);handle.set_base_uri(source.resolve().as_uri());handle.write(ET.tostring(tree));handle.close()
    vx,vy,w,h=map(float,tree.get('viewBox').split());viewport=Rsvg.Rectangle();viewport.x=viewport.y=0;viewport.width=w;viewport.height=h
    def transform(context,value):
        for command,args in re.findall(r'(matrix|translate|scale|rotate)\(([^)]+)\)',value):
            vals=[float(x) for x in re.split('[, ]+',args.strip())]
            if command=='matrix':context.transform(cairo.Matrix(*vals))
            elif command=='translate':context.translate(vals[0],vals[1] if len(vals)>1 else 0)
            elif command=='scale':context.scale(vals[0],vals[1] if len(vals)>1 else vals[0])
            elif command=='rotate':
                x,y=vals[1:] if len(vals)>1 else (0,0);context.translate(x,y);context.rotate(vals[0]*math.pi/180);context.translate(-x,-y)
    def rounded(context,x,y,w,h,r):
        r=min(r,w/2,h/2);context.new_path()
        if not r:context.rectangle(x,y,w,h);return
        context.arc(x+w-r,y+r,r,-math.pi/2,0);context.arc(x+w-r,y+h-r,r,0,math.pi/2);context.arc(x+r,y+h-r,r,math.pi/2,math.pi);context.arc(x+r,y+r,r,math.pi,3*math.pi/2);context.close_path()
    with cairo.PDFSurface(str(target),w,h) as pdf:
        pdf.restrict_to_version(cairo.PDF_VERSION_1_5);context=cairo.Context(pdf)
        def draw(node,ancestors=()):
            tag=node.tag.split('}')[-1]
            if tag in ['defs','mask','clipPath']:return
            key=node.get('id')
            if key in plans:
                filename,matrix=plans[key];original=filename.read_bytes();image=Image.open(filename).convert('RGB');raw=bytearray(image.tobytes('raw','BGRX'))
                surface=cairo.ImageSurface.create_for_data(raw,cairo.FORMAT_RGB24,image.width,image.height,image.width*4);surface.set_mime_data('image/jpeg',original);surfaces.append((surface,raw,original))
                context.save();context.rectangle(0,0,w,h);context.clip();context.translate(-vx,-vy)
                for a in ancestors+(node,):
                    transform(context,a.get('transform',''))
                    maskid=re.fullmatch(r'url\(#([^)]*)\)',a.get('mask',''))
                    if maskid:
                        mask=lookup[maskid.group(1)][0]
                        rounded(context,float(mask.get('x',0)),float(mask.get('y',0)),float(mask.get('width')),float(mask.get('height')),float(mask.get('rx',0)))
                        context.clip()
                    clipid=re.fullmatch(r'url\(#([^)]*)\)',a.get('clip-path',''))
                    if clipid:
                        clip=lookup.get(clipid.group(1))
                        if clip is not None and len(clip)==1 and clip[0].tag.split('}')[-1]=='rect':
                            r=clip[0];context.rectangle(float(r.get('x',0)),float(r.get('y',0)),float(r.get('width')),float(r.get('height')));context.clip()
                x=float(node.get('x',0));y=float(node.get('y',0));rw=float(node.get('width'));rh=float(node.get('height'))
                rounded(context,x,y,rw,rh,float(node.get('rx',0)));context.clip();context.translate(x,y);context.scale(rw,rh);context.transform(cairo.Matrix(*matrix));context.set_source_surface(surface);context.paint();context.restore()
            elif tag=='g' and not node.get('filter'):
                for child in node:draw(child,ancestors+(node,))
            elif node.get('filter'):
                # Rasterize this isolated shadow layer, never the photograph above it.
                layer=cairo.ImageSurface(cairo.FORMAT_ARGB32,math.ceil(w),math.ceil(h));lc=cairo.Context(layer)
                handle.render_layer(lc,'#'+key,viewport);context.set_source_surface(layer);context.paint()
            elif tag!='svg':handle.render_layer(context,'#'+key,viewport)
            else:
                for child in node:draw(child,ancestors)
        draw(tree)
    return True
