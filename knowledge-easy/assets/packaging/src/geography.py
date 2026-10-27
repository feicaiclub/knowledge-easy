"""Canonical geography renderer shared by catalog and episode variants."""
from pathlib import Path
import json, math

def map_base(prefix,view=(70,15,140,55),w=1680,h=770,data_dir=None):
    K=Path(data_dir) if data_dir else Path(__file__).resolve().parent/"maps"
    lon0,lat0,lon1,lat1=view
    assert -180<=lon0<lon1<=180 and -80<lat0<lat1<80,'Invalid map viewport.'
    merc=lambda lat:math.log(math.tan(math.pi/4+math.radians(lat)/2))
    minx,maxx=math.radians(lon0),math.radians(lon1);miny,maxy=merc(lat0),merc(lat1)
    scale=min((w-90)/(maxx-minx),(h-90)/(maxy-miny));ox=(w-(maxx-minx)*scale)/2;oy=(h-(maxy-miny)*scale)/2
    def point(lon,lat):return (ox+(math.radians(lon)-minx)*scale,oy+(maxy-merc(max(-80,min(80,lat))))*scale)
    def line(coords,close=False):
        pts=[point(*c[:2]) for c in coords];last=None;keep=[]
        for xy in pts:
            if last is None or math.hypot(xy[0]-last[0],xy[1]-last[1])>.8:keep.append(xy);last=xy
        return 'M'+' L'.join(f'{x:.1f} {y:.1f}' for x,y in keep)+('Z' if close else '') if keep else ''
    land_path=K/'ne_50m_land.geojson'
    if not land_path.exists():land_path=K/'ne_110m_land.geojson'
    j=json.loads(land_path.read_text());parts=[]
    for f in j['features']:
        g=f['geometry'];polys=[g['coordinates']] if g['type']=='Polygon' else g['coordinates']
        for poly in polys:parts.append(' '.join(line(r,True) for r in poly))
    grid=''
    for lon in range(int(lon0//10*10),int(lon1)+1,10):
        x1,y1=point(lon,lat0);x2,y2=point(lon,lat1);grid+=f'<path class="gridline" d="M{x1} {y1} L{x2} {y2}"/>'
    for lat in range(int(lat0//10*10),int(lat1)+1,10):
        x1,y1=point(lon0,lat);x2,y2=point(lon1,lat);grid+=f'<path class="gridline" d="M{x1} {y1} L{x2} {y2}"/>'
    rivers='';rf=K/'ne_50m_rivers_lake_centerlines.geojson'
    if rf.exists():
        for f in json.loads(rf.read_text())['features']:
            g=f.get('geometry')
            if not g:continue
            ls=[g['coordinates']] if g['type']=='LineString' else g['coordinates']
            for coords in ls:
                if not any(lon0<=c[0]<=lon1 and lat0<=c[1]<=lat1 for c in coords):continue
                rivers+=f'<path class="river" d="{line(coords)}"/>'
    land=''.join(f'<path class="land" d="{d}" fill-rule="evenodd"/>' for d in parts)
    inside=f'<defs><clipPath id="{prefix}-clip"><rect x="0" y="0" width="{w}" height="{h}"/></clipPath></defs><g clip-path="url(#{prefix}-clip)">{grid}{land}{rivers}</g>'
    point.width=w;point.height=h
    return inside,point

