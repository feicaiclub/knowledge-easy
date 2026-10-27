"""Geometry checks for designed diagram lanes, independent of paint order.

Boxes use x, y, width, height in the 1920x1080 composition. Full-bleed
footage and decorative surfaces are not information boxes.
"""
import math

INFORMATION_SAFE = (150, 80, 1770, 830)
CONNECTOR_CLEARANCE = 16


def segment_hits_box(a, b, box, padding=0):
    x, y, w, h = box
    limits = ((x-padding, x+w+padding), (y-padding, y+h+padding))
    lo, hi = 0.0, 1.0
    for axis, (low, high) in enumerate(limits):
        delta = b[axis]-a[axis]
        if abs(delta) < 1e-9:
            if not low <= a[axis] <= high:
                return False
        else:
            t0, t1 = (low-a[axis])/delta, (high-a[axis])/delta
            lo, hi = max(lo, min(t0, t1)), min(hi, max(t0, t1))
            if lo > hi:
                return False
    return True


def validate_layout(boxes, connectors=(), safe=INFORMATION_SAFE):
    left, top, right, bottom = safe
    for key, (x, y, w, h) in boxes.items():
        if not all(math.isfinite(v) for v in (x, y, w, h)) or w <= 0 or h <= 0:
            raise ValueError('Invalid information bounds: '+key)
        if x < left or y < top or x+w > right or y+h > bottom:
            raise ValueError('Information crosses the safe area or caption reserve: '+key)
    items=list(boxes.items())
    for i,(key,(x,y,w,h)) in enumerate(items):
        for other,(ox,oy,ow,oh) in items[i+1:]:
            if x < ox+ow and x+w > ox and y < oy+oh and y+h > oy:
                raise ValueError('Information boxes overlap: '+key+' / '+other)
    for line in connectors:
        points = line['points']
        if len(points) < 2:
            raise ValueError('A connector needs two endpoints: '+line['id'])
        head=arrow_points(points) if line.get('arrow',True) else []
        for point in [*points,*head]:
            if not all(math.isfinite(v) for v in point) or not (left <= point[0] <= right and top <= point[1] <= bottom):
                raise ValueError('Connector leaves the safe area: '+line['id'])
        for a, b in [*zip(points, points[1:]),*zip(head,head[1:])]:
            if a == b:
                raise ValueError('Zero-length connector segment: '+line['id'])
            for key, box in boxes.items():
                if segment_hits_box(a, b, box, CONNECTOR_CLEARANCE):
                    raise ValueError('Connector '+line['id']+' crosses or crowds '+key+'; reroute it, do not hide it behind the image.')
    return {'information_safe': list(safe), 'boxes': boxes, 'connectors': list(connectors)}


def path_data(points):
    return 'M'+' L'.join(f'{x:g} {y:g}' for x,y in points)


def arrow_points(points, length=12, half_width=6):
    a,b=points[-2:]
    distance=math.hypot(b[0]-a[0],b[1]-a[1])
    if distance < length:
        raise ValueError('The last connector segment is too short for its arrowhead.')
    ux,uy=(b[0]-a[0])/distance,(b[1]-a[1])/distance
    return [(b[0]-length*ux-half_width*uy,b[1]-length*uy+half_width*ux),b,
            (b[0]-length*ux+half_width*uy,b[1]-length*uy-half_width*ux)]
