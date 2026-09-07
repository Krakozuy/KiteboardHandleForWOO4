# -*- coding: utf-8 -*-
"""Fusion 360: kiteboard handle + flush removable WOO cover.
Edit the SETTINGS below, then run from Utilities > Scripts and Add-Ins.
Each run creates a NEW document. Dimensions below are millimetres.
The design is rebuilt from Python settings (direct solid modelling).
"""

# ==================== SETTINGS / НАСТРОЙКИ ====================
scriptVersion = '1.0.11'       # Incremented with each published update.
boltSpacing = 180.0
handleTop = 72.0
gripH = 28.0                  # Uniform section, normal to path, INCLUDING legs.
gripD = 28.0                  # Uniform section depth along Y, INCLUDING legs.
legLean = 20.0
boltD = 6.6
headPocketD = 13.0
shoulder = 4.0                 # Material beneath bolt head, measured from board.

gripR = 6.0                    # Same section radius for legs, bends and grip.
printFriendlySection = True   # Symmetric 45-degree slopes on BOTH Y faces.
sectionChamfer = 6.0          # Setback of 45-degree slopes, mm; same on both sides.
bendR = 17.0                   # Centre-line radius of the two upper bends.
baseTrimMargin = 1.0           # Extra stock below board before trimming at Z=0.

# Drawing: flat tangent-to-tangent lengths, NOT sharp-vertex widths.
wooTopFlat = 32.044
wooBottomFlat = 51.279
wooSlopeRise = 12.203          # Vertical distance of the LONG straight slope.
wooTopChord = 0.862            # Chord across R1 top arc; determines slope angle.
wooShortSide = 2.255           # Length of the short lower straight side.
wooTopR = 1.0
wooSideR = 1.0
wooBottomR = 0.5
wooSideChordReference = 0.960  # Rounded reference dimension, checked in report.
wooHalfDepth = 11.0            # Empty cavity Y=-11..+11, including under cover.
wooZOffset = 0.0              # Offset from middle height of grip.
wooFitClearance = 0.0          # Optional outward profile clearance; 0 = drawing.

lidBorder = 1.15               # Seat width around opening in XZ.
lidGap = 0.25                  # Radial contour clearance PER SIDE.
lidSeatDepth = 1.1             # Extra rim depth outside useful WOO volume.
lidAxialGap = 0.15             # Gap above seat in assembled position.
lidWingLength = 16.0           # Room for the longitudinal release beam outside WOO.
lidWingH = 11.0                # Wider wing for the in-plane U-slot and edge catch.
lidWingR = 1.0
enableSnapFits = True          # One LEFT rigid tongue + one RIGHT releasable catch.
snapLength = 12.0              # FREE beam length along X, parallel to the cover.
snapThickness = 1.2            # Tip thickness along Z; beam flexes toward -Z.
snapRootThickness = 1.8        # Taper from thick root to thinner tip.
snapWidth = 3.0                # Beam depth along Y, not length of insertion.
snapRootLength = 2.0
snapRootR = 0.3                # Rounded ends of the U-slot at the fixed root.
snapHook = 0.45                # Engagement beyond the seat edge, toward +Z.
snapHookLength = 2.5           # Hook length along X at the free end.
snapRamp = 1.0                 # Both hook ramps: enough run for <=45-degree growth.
snapTipLand = 0.4
snapClearance = 0.2
snapFlexSpace = 0.85           # Lower U-slot gap; remaining cover limits travel.
snapUpperGap = 0.65            # Upper U-slot gap.
snapTipGap = 0.65              # Free-end U-slot gap.
snapEdgeRail = 1.0             # Cover strip outside upper slot, opened at hook.
mechanismKeepout = 0.8         # Separation from maximum WOO profile width.
tongueEngagement = 2.0         # LEFT tongue extends under the handle lip.
tongueThickness = 1.8
tongueWidth = 5.0
tongueRootLength = 3.0
tongueClearance = 0.35
lidTiltAngle = 5.0             # Planned opening angle, degrees.
lidTiltClearance = 0.6         # Extra opening clearance at the left pivot edge.
pryD = 2.5                    # Recess at wing edge to lift the cover.
minimumWall = 1.5              # Geometry guard, not a strength certification.

makeFitSample = False         # Extra pair cropped from right catch/receiver.
sampleWidth = 18.0             # Includes ENTIRE beam and its fixed root.
sampleHeight = 18.0            # Includes the edge hook, U-slot and stop.
exportFiles = True            # Local F3D + separate STL files beside script.
showMessage = True
modelName = 'KiteHandle_WOO'
geometryTolerance = 0.02       # Verification tolerance, mm.
# ================= END OF EDITABLE SETTINGS ==================

import math
import os
import json
import traceback
import adsk.core
import adsk.fusion


def p(x, y, z):
    return adsk.core.Point3D.create(x / 10, y / 10, z / 10)


def val(mm):
    return adsk.core.ValueInput.createByString(f'{mm:.12g} mm')


def collection(items):
    result = adsk.core.ObjectCollection.create()
    for item in items:
        result.add(item)
    return result


def check(condition, message):
    if not condition:
        raise ValueError(message)


def rounded_polygon(vertices, radii):
    """Return lines/arcs for a convex CCW polygon, all in mm.
    Arc representation is (start, midpoint, end); line is (start, end).
    This avoids reliance on unstable sketch-fillet edge numbering.
    """
    corners = []
    for i, (v, r) in enumerate(zip(vertices, radii)):
        prev, nxt = vertices[i - 1], vertices[(i + 1) % len(vertices)]
        a = (prev[0] - v[0], prev[1] - v[1])
        b = (nxt[0] - v[0], nxt[1] - v[1])
        la, lb = math.hypot(*a), math.hypot(*b)
        a, b = (a[0]/la, a[1]/la), (b[0]/lb, b[1]/lb)
        angle = math.acos(max(-1, min(1, a[0]*b[0] + a[1]*b[1])))
        t = r / math.tan(angle/2)
        check(t < min(la, lb), 'Corner radius too large for polygon.')
        bis = (a[0]+b[0], a[1]+b[1])
        bl = math.hypot(*bis)
        bis = (bis[0]/bl, bis[1]/bl)
        center = (v[0]+bis[0]*r/math.sin(angle/2),
                  v[1]+bis[1]*r/math.sin(angle/2))
        start, end = (v[0]+a[0]*t, v[1]+a[1]*t), (v[0]+b[0]*t, v[1]+b[1]*t)
        middle = (center[0]-bis[0]*r, center[1]-bis[1]*r)
        corners.append((start, middle, end, t))
    result = []
    for i, c in enumerate(corners):
        nxt = corners[(i+1) % len(corners)]
        edge = math.dist(vertices[i], vertices[(i+1) % len(vertices)])
        check(c[3]+nxt[3] < edge, 'Adjacent corner fillets overlap.')
        # Radius zero intentionally preserves the bed-face/chamfer junction.
        # Do not emit a degenerate three-point arc for such a corner.
        if c[3] > 0:
            result.append((c[0], c[1], c[2]))
        result.append((c[2], nxt[0]))
    return result


def offset_polygon(vertices, distance):
    """Exact supporting-line offset of a convex CCW polygon."""
    result = []
    for i, v in enumerate(vertices):
        prev, nxt = vertices[i-1], vertices[(i+1) % len(vertices)]
        a = (v[0]-prev[0], v[1]-prev[1])
        b = (nxt[0]-v[0], nxt[1]-v[1])
        a = (a[0]/math.hypot(*a), a[1]/math.hypot(*a))
        b = (b[0]/math.hypot(*b), b[1]/math.hypot(*b))
        na, nb = (a[1], -a[0]), (b[1], -b[0])
        d = 1 + na[0]*nb[0] + na[1]*nb[1]
        result.append((v[0]+distance*(na[0]+nb[0])/d,
                       v[1]+distance*(na[1]+nb[1])/d))
    return result


def woo_geometry():
    """Solve rounded six-vertex contour from screenshot dimensions.
    Top R1 chord fixes alpha. Bottom flat and lower line fix beta.
    The side R1 chord is an independent rounded check (~0.960 mm).
    """
    alpha = 2*math.asin(wooTopChord/(2*wooTopR))
    target = (wooBottomFlat-wooTopFlat)/2
    def dx(beta):
        return ((wooTopR-wooSideR)*math.sin(alpha)
                + wooSlopeRise/math.tan(alpha)
                + (wooSideR-wooBottomR)*math.sin(beta)
                + wooShortSide*math.cos(beta))
    lo, hi = math.pi/2, math.pi-0.01
    check(dx(hi) < target < dx(lo), 'WOO drawing dimensions are inconsistent.')
    for _ in range(70):
        m = (lo+hi)/2
        if dx(m) > target:
            lo = m
        else:
            hi = m
    beta = (lo+hi)/2
    height = (wooTopR*(1-math.cos(alpha)) + wooSlopeRise
              + wooSideR*(math.cos(alpha)-math.cos(beta))
              + wooShortSide*math.sin(beta) + wooBottomR*(1+math.cos(beta)))
    topx = wooTopFlat/2 + wooTopR*math.tan(alpha/2)
    bottomx = wooBottomFlat/2 + wooBottomR*math.tan((math.pi-beta)/2)
    # Intersection of long and short supporting lines.
    zside = (topx + height/math.tan(alpha)-bottomx) / (
        1/math.tan(alpha)-1/math.tan(beta))
    xside = bottomx-zside/math.tan(beta)
    # Counterclockwise contour starting at lower left.
    verts = [(-bottomx,0),(bottomx,0),(xside,zside),
             (topx,height),(-topx,height),(-xside,zside)]
    zbase = handleTop-gripH/2+wooZOffset-height/2
    verts = [(x,z+zbase) for x,z in verts]
    radii = [wooBottomR,wooBottomR,wooSideR,wooTopR,wooTopR,wooSideR]
    return verts, radii, {'height_mm':height, 'alpha_deg':math.degrees(alpha),
                         'beta_deg':math.degrees(beta),
                         'side_chord_mm':2*wooSideR*math.sin((beta-alpha)/2)}


def sketch_plane(comp, origin, normal, name):
    inp = comp.constructionPlanes.createInput()
    check(inp.setByPlane(adsk.core.Plane.create(p(*origin),
        adsk.core.Vector3D.create(*normal))), 'Construction plane failed.')
    plane = comp.constructionPlanes.add(inp)
    plane.name = name
    plane.isLightBulbOn = False
    sk = comp.sketches.add(plane)
    sk.name = name
    return sk


def draw_curves(sk, curves, map_point):
    def point(q):
        return sk.modelToSketchSpace(p(*map_point(q)))
    sk.isComputeDeferred = True
    for c in curves:
        if len(c) == 2:
            sk.sketchCurves.sketchLines.addByTwoPoints(point(c[0]),point(c[1]))
        else:
            sk.sketchCurves.sketchArcs.addByThreePoints(point(c[0]),point(c[1]),point(c[2]))
    sk.isComputeDeferred = False
    check(sk.profiles.count == 1, f'{sk.name}: expected one closed profile, got {sk.profiles.count}.')
    sk.isVisible = False
    return sk.profiles.item(0)


def rectangle_curves(w, h, r):
    return rounded_polygon([(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)], [r]*4)


def handle_section_curves():
    """Uniform section mirrored about BOTH in-plane axes.
    Y=-gripD/2 and Y=+gripD/2 have identical flat faces and 45-degree
    slopes. Rounding only the slope/sidewall junction keeps the expanding
    print surface at least 45 degrees to either Y-facing print bed.
    Rounding the flat-face/slope junction would reintroduce the overhang.
    """
    if not printFriendlySection:
        return rectangle_curves(gripH,gripD,gripR)
    a,b,c = gripH/2,gripD/2,sectionChamfer
    vertices = [(-a+c,-b),(a-c,-b),(a,-b+c),(a,b-c),
                (a-c,b),(-a+c,b),(-a,b-c),(-a,-b+c)]
    return rounded_polygon(vertices,[0,0,gripR,gripR,0,0,gripR,gripR])


def section_xy(comp,x,z,w,d,r,name):
    sk = sketch_plane(comp,(0,0,z),(0,0,1),name)
    return draw_curves(sk,rectangle_curves(w,d,r),lambda q:(x+q[0],q[1],z))


def extrude(comp, profile, distance, name):
    inp = comp.features.extrudeFeatures.createInput(profile,
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    extent = adsk.fusion.DistanceExtentDefinition.create(val(abs(distance)))
    direction = (adsk.fusion.ExtentDirections.PositiveExtentDirection if distance > 0
                 else adsk.fusion.ExtentDirections.NegativeExtentDirection)
    inp.setOneSideExtent(extent,direction)
    feat = comp.features.extrudeFeatures.add(inp)
    body = feat.bodies.item(0)
    body.name = name
    return body


def prism_xz(comp, curves, y0, y1, name):
    sk = sketch_plane(comp,(0,y0,0),(0,1,0),name)
    profile = draw_curves(sk,curves,lambda q:(q[0],y0,q[1]))
    return extrude(comp,profile,y1-y0,name)


def prism_xy(comp, vertices, z0, z1, name):
    sk = sketch_plane(comp,(0,0,z0),(0,0,1),name)
    curves = [(vertices[i],vertices[(i+1)%len(vertices)]) for i in range(len(vertices))]
    profile = draw_curves(sk,curves,lambda q:(q[0],q[1],z0))
    return extrude(comp,profile,z1-z0,name)


def prism_yz(comp, vertices, x0, x1, name):
    sk = sketch_plane(comp,(x0,0,0),(1,0,0),name)
    curves = [(vertices[i],vertices[(i+1)%len(vertices)]) for i in range(len(vertices))]
    profile = draw_curves(sk,curves,lambda q:(x0,q[0],q[1]))
    return extrude(comp,profile,x1-x0,name)


def box(comp,x0,x1,y0,y1,z0,z1,name):
    return prism_xy(comp,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z0,z1,name)


def cylinder(comp,x,y,z0,z1,diameter,name):
    sk = sketch_plane(comp,(0,0,z0),(0,0,1),name)
    sk.sketchCurves.sketchCircles.addByCenterRadius(sk.modelToSketchSpace(p(x,y,z0)),diameter/20)
    result = extrude(comp,sk.profiles.item(0),z1-z0,name)
    sk.isVisible = False
    return result


def boolean(comp, target, tool, operation):
    check(target is not None and target.isValid, 'Invalid Boolean target body.')
    check(tool is not None and tool.isValid, 'Invalid Boolean tool body.')
    body_count_before = comp.bRepBodies.count
    inp = comp.features.combineFeatures.createInput(target,collection([tool]))
    inp.operation = operation
    inp.isKeepToolBodies = False
    feat = comp.features.combineFeatures.add(inp)
    # Autodesk API: add() returns nothing for a non-parametric Combine.
    # In Direct Design it modifies the target body in place instead.
    if feat is not None:
        check(feat.bodies.count == 1, 'Boolean operation split the body unexpectedly.')
        result = feat.bodies.item(0)
    else:
        check(target.isValid, 'Combine did not preserve a valid target body.')
        result = target
    # With one consumed tool and one connected result the count drops by one.
    # This also catches a failed/no-op Combine instead of treating None as success.
    check(comp.bRepBodies.count == body_count_before - 1,
          f'Combine did not consume exactly one tool: bodies before={body_count_before}, '
          f'after={comp.bRepBodies.count}; operation={operation}.')
    check(result.isSolid and result.lumps.count == 1,
          'Combine result is not one connected solid.')
    return result


def join(comp,a,b):
    return boolean(comp,a,b,adsk.fusion.FeatureOperations.JoinFeatureOperation)


def cut(comp,a,b):
    return boolean(comp,a,b,adsk.fusion.FeatureOperations.CutFeatureOperation)


def intersect(comp,a,b):
    return boolean(comp,a,b,adsk.fusion.FeatureOperations.IntersectFeatureOperation)


def bend_geometry():
    """Find an arc tangent to the straight inclined leg and horizontal grip.
    legLean remains the inward offset at the leg/arc tangency point.
    z_t = z_c - R + R*sin(phi), tan(phi) = legLean / z_t.
    """
    zc = handleTop-gripH/2
    check(zc > bendR and legLean >= 0, 'Invalid height, bend radius or leg lean.')
    lo,hi = 0.0,math.pi/2-0.001
    for _ in range(70):
        phi = (lo+hi)/2
        zt = zc-bendR+bendR*math.sin(phi)
        if zt*math.tan(phi) < legLean:
            lo = phi
        else:
            hi = phi
    phi = (lo+hi)/2
    zt = zc-bendR+bendR*math.sin(phi)
    return phi,zt,boltSpacing/2-legLean-bendR*math.cos(phi)


def handle_blank(comp):
    half = boltSpacing/2
    legx = half-legLean
    zc = handleTop-gripH/2
    phi,zt,tangentx = bend_geometry()
    sn,cs = math.sin(phi),math.cos(phi)
    arc_center_z = zc-bendR
    # A SINGLE fixed profile follows the entire U path. No lofts or joins
    # between differently oriented/sized sections: straight legs are prismatic.
    # Extend far enough that both oblique end caps lie wholly below the board.
    sweep_z = -(gripH/2*sn+baseTrimMargin)
    sweep_x = half-sweep_z*math.tan(phi)
    # Every line/arc junction is tangent by construction.
    pathsk = sketch_plane(comp,(0,0,0),(0,-1,0),'Grip_path')
    def q(x,z):
        return pathsk.modelToSketchSpace(p(x,0,z))
    arcs = pathsk.sketchCurves.sketchArcs
    lines = pathsk.sketchCurves.sketchLines
    middle_angle = (phi+math.pi/2)/2
    arc_mid_x = tangentx+bendR*math.cos(middle_angle)
    arc_mid_z = arc_center_z+bendR*math.sin(middle_angle)
    entry = lines.addByTwoPoints(q(-sweep_x,sweep_z),q(-legx,zt))
    left = arcs.addByThreePoints(q(-legx,zt),q(-arc_mid_x,arc_mid_z),q(-tangentx,zc))
    bridge = lines.addByTwoPoints(q(-tangentx,zc),q(tangentx,zc))
    right = arcs.addByThreePoints(q(tangentx,zc),q(arc_mid_x,arc_mid_z),q(legx,zt))
    exit_curve = lines.addByTwoPoints(q(legx,zt),q(sweep_x,sweep_z))
    path = comp.features.createPath(collection([entry,left,bridge,right,exit_curve]),False)
    check(path is not None and path.count == 5, 'Handle path must contain two straight legs, two bends and the grip.')
    startsk = sketch_plane(comp,(-sweep_x,0,sweep_z),(sn,0,cs),'Grip_sweep_section')
    profile = draw_curves(startsk,handle_section_curves(),
                         lambda q:(-sweep_x+q[0]*cs,q[1],sweep_z-q[0]*sn))
    inp = comp.features.sweepFeatures.createInput(profile,path,adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    sweep = comp.features.sweepFeatures.add(inp)
    pathsk.isVisible = False
    body = sweep.bodies.item(0)
    # Keep only Z>=0. This gives coplanar mounting faces without changing
    # the constant cross-section along the inclined legs.
    bb = body.boundingBox
    trim = box(comp,bb.minPoint.x*10-baseTrimMargin,bb.maxPoint.x*10+baseTrimMargin,
               bb.minPoint.y*10-baseTrimMargin,bb.maxPoint.y*10+baseTrimMargin,
               0,handleTop+baseTrimMargin,'Board_plane_trim')
    body = intersect(comp,body,trim)
    body.name = 'Handle_blank'
    return body


def validate(info, vertices):
    for name in ['boltSpacing','handleTop','gripH','gripD','baseTrimMargin',
                 'boltD','headPocketD','shoulder','wooHalfDepth','snapLength','snapThickness']:
        check(globals()[name] > 0, name+' must be positive.')
    check(0 < gripR < min(gripH,gripD)/2, 'Section radius must be smaller than half section size.')
    if printFriendlySection:
        check(0 < sectionChamfer < min(gripH,gripD)/2,'Invalid symmetric section chamfer.')
        setback = gripR*math.tan(math.pi/8)
        check(setback < sectionChamfer*math.sqrt(2),
              'gripR too large: it consumes the entire 45-degree slope.')
        check(sectionChamfer+setback < gripD/2,
              'Opposite chamfer/sidewall fillets overlap; reduce gripR or sectionChamfer.')
    phi,zt,tangentx = bend_geometry()
    check(bendR > gripH/2,'bendR must exceed gripH/2.')
    check(0 <= legLean < boltSpacing/2,'Invalid legLean.')
    foot_width = gripH/math.cos(phi)
    check(headPocketD > boltD and headPocketD+2*minimumWall < min(foot_width,gripD),'Bolt pocket leaves too little material.')
    check(0 < shoulder < zt-gripH/2*math.sin(phi),'Invalid shoulder.')
    check(headPocketD/2+shoulder*math.tan(phi)+minimumWall < foot_width/2,
          'Head pocket leaves too little material at the shoulder on the inclined leg.')
    check(gripD/2-wooHalfDepth >= minimumWall,'WOO leaves insufficient side wall.')
    check(abs(wooZOffset)+info['height_mm']/2+wooFitClearance+lidBorder+lidGap < gripH/2,'Cover seat does not fit grip height.')
    check(lidGap > 0 and lidBorder > lidGap and lidSeatDepth > lidAxialGap,'Invalid lid seat/gap.')
    if enableSnapFits:
        check(0 < snapClearance < snapHook < snapFlexSpace,'Invalid latch engagement/release travel.')
        check(snapRootThickness >= snapThickness > 0 and snapRootLength > 2*snapRootR,
              'Invalid tapered beam/root dimensions.')
        check(snapWidth > 2*snapRamp+snapTipLand and
              snapWidth < gripD/2-(wooHalfDepth-lidSeatDepth+lidAxialGap),
              'Beam must fit within the cover thickness and contain both hook ramps.')
        check(snapRamp >= lidGap+snapHook+snapClearance,
              'Hook ramps must be at least as long as the hook rise for printable slopes.')
        check(0 < snapHookLength < snapLength and mechanismKeepout > snapClearance,
              'Invalid hook length or WOO keepout.')
        check(mechanismKeepout+snapRootLength+snapLength+snapTipGap+minimumWall
              < lidWingLength+lidBorder,'Lid wing too short for the in-plane U-slot.')
        check(0 < snapRootR < min(snapUpperGap,snapFlexSpace)/2 and
              snapTipGap > 0 and snapEdgeRail > 0,'Invalid U-slot widths or end radii.')
        wing_half = lidWingH/2+wooFitClearance+lidBorder
        check(wing_half-snapEdgeRail-snapUpperGap-snapRootThickness-snapFlexSpace
              > -wing_half+minimumWall,'U-slot leaves too little material below the beam.')
        # All of the latch must start on the same flat outer print face.
        flat_half = gripH/2-(sectionChamfer if printFriendlySection else gripR)
        check(abs(wooZOffset)+wing_half+lidGap+snapHook+snapClearance < flat_half,
              'Edge catch reaches the curved outer skin; reduce lidWingH or hook size.')
        check(tongueRootLength > 0 and tongueThickness > 0 and
              tongueEngagement > 0 and tongueClearance > 0,'Invalid rigid tongue.')
        check(0 < lidTiltAngle < 15,'Use a small lid opening angle.')
        angle = math.radians(lidTiltAngle)
        check(lidTiltClearance+lidGap > (gripD/2-wooHalfDepth+lidSeatDepth+tongueClearance)*math.sin(angle),
              'Increase lidTiltClearance for the chosen opening angle.')
        check(tongueClearance > tongueEngagement*math.sin(angle),
              'Increase tongueClearance for the chosen opening angle.')
        check(wooHalfDepth-lidSeatDepth-tongueClearance+tongueEngagement
              > wooHalfDepth-lidSeatDepth+lidAxialGap,
              'Left tongue gusset must overlap the cover.')
        if makeFitSample:
            check(sampleWidth > snapLength+snapRootLength+2*snapClearance,
                  'Fit sample must include the whole beam and root.')
    check(abs(info['side_chord_mm']-wooSideChordReference) < 0.04,'WOO side chord differs from drawing; verify inputs.')
    xmax = max(abs(x) for x,z in vertices)+wooFitClearance
    check(xmax+lidWingLength+lidGap+minimumWall < tangentx,
          'Bolt spacing too short: cover wings reach bends. Increase boltSpacing or reduce wings.')
    if enableSnapFits:
        check(xmax+lidWingLength+wooFitClearance+lidBorder+tongueEngagement+
              tongueClearance+minimumWall < tangentx,'Left tongue reaches the handle bend.')


def make_cover_outline(comp,vertices,radii,offset,y0,y1,wing_start,wing_end,zc,name):
    body = prism_xz(comp,rounded_polygon(offset_polygon(vertices,offset),[r+offset for r in radii]),y0,y1,name)
    for sign in [-1,1]:
        xa,xb = sorted([sign*(wing_start-offset),sign*(wing_end+offset)])
        wing = rounded_polygon([(xa,zc-lidWingH/2-offset),(xb,zc-lidWingH/2-offset),
                                 (xb,zc+lidWingH/2+offset),(xa,zc+lidWingH/2+offset)], [lidWingR+offset]*4)
        body = join(comp,body,prism_xz(comp,wing,y0,y1,name+'_wing'))
    return body


def releasable_lock(comp,handle,cover,xmax,wing_end,zc,seat_y):
    """Integral in-plane beam in a through U-slot; left tongue has a gusset.
    Print with +Y facing the bed: the lid AND beam start at Y=gripD/2.
    There is no suspended beam beneath a closed cover surface.
    """
    outer_y = gripD/2
    beam_front = outer_y-snapWidth
    root_left = xmax+mechanismKeepout
    root_x = root_left+snapRootLength
    end_x = root_x+snapLength
    edge_z = zc+lidWingH/2+wooFitClearance+lidBorder
    beam_top = edge_z-snapEdgeRail-snapUpperGap
    root_bottom = beam_top-snapRootThickness
    tip_bottom = beam_top-snapThickness

    # One continuous U-cut leaves the original lid material as the beam.
    # The lower slot also provides a mechanical stop after snapFlexSpace travel.
    u = [(root_x,beam_top+snapUpperGap),(end_x+snapTipGap,beam_top+snapUpperGap),
         (end_x+snapTipGap,tip_bottom-snapFlexSpace),
         (root_x,root_bottom-snapFlexSpace),(root_x,root_bottom),
         (end_x,tip_bottom),(end_x,beam_top),(root_x,beam_top)]
    curves = [(u[i],u[(i+1)%len(u)]) for i in range(len(u))]
    cover = cut(comp,cover,prism_xz(comp,curves,-gripD,gripD,'Through_U_release_slot'))
    # Round the two closed slot ends where the beam meets the fixed lid.
    for z in [beam_top+snapUpperGap/2,root_bottom-snapFlexSpace/2]:
        sk = sketch_plane(comp,(0,-gripD,0),(0,1,0),'U_slot_root_relief')
        sk.sketchCurves.sketchCircles.addByCenterRadius(
            sk.modelToSketchSpace(p(root_x,-gripD,z)),snapRootR/10)
        tool = extrude(comp,sk.profiles.item(0),2*gripD,'U_slot_root_relief')
        sk.isVisible = False
        cover = cut(comp,cover,tool)

    # Remove excess from the back of the free beam, not from its print face.
    # The beam remains attached at its left root and starts directly on the bed.
    back_relief = box(comp,root_x,end_x, -gripD,beam_front,
                      root_bottom-snapClearance,beam_top+snapClearance,'Beam_back_relief')
    cover = cut(comp,cover,back_relief)

    # Open the outer rail beside the hook so the hook cannot fuse to the lid.
    mouth = box(comp,end_x-snapHookLength-snapClearance,end_x+snapTipGap,
                -gripD,gripD,beam_top,edge_z+snapClearance,'Edge_release_access')
    cover = cut(comp,cover,mouth)

    # The tooth grows from a stem on the first layer. Both flanks are sloped,
    # avoiding a horizontal shelf when printed with the outer face down.
    base_z = edge_z-snapClearance
    peak_z = edge_z+lidGap+snapHook
    nose_y = outer_y-2*snapRamp-snapTipLand
    hook_profile = [(nose_y,beam_top-snapClearance),(outer_y,beam_top-snapClearance),
                    (outer_y,base_z),(outer_y-snapRamp,peak_z),
                    (outer_y-snapRamp-snapTipLand,peak_z),(nose_y,base_z)]
    hook = prism_yz(comp,hook_profile,end_x-snapHookLength,end_x,'Release_hook')
    cover = join(comp,cover,hook)
    # A matching recess is in the SIDE of the lid seat, not deep under the beam.
    notch = prism_yz(comp,offset_polygon(hook_profile,snapClearance),
                     end_x-snapHookLength-snapClearance,end_x+snapClearance,'Edge_hook_recess')
    handle = cut(comp,handle,notch)

    # Left tongue has a continuous 45-degree print gusset. With +Y down,
    # its projecting footprint grows one mm per mm of build height.
    left_edge = -(wing_end+wooFitClearance+lidBorder)
    tongue_front = seat_y-tongueClearance-tongueThickness
    tongue_back = seat_y-tongueClearance
    tongue_xy = [(left_edge-tongueEngagement,tongue_front),
                 (left_edge+tongueRootLength,tongue_front),
                 (left_edge+tongueRootLength,tongue_back+tongueEngagement),
                 (left_edge,tongue_back+tongueEngagement),
                 (left_edge-tongueEngagement,tongue_back)]
    tongue = prism_xy(comp,tongue_xy,zc-tongueWidth/2,zc+tongueWidth/2,'Gusseted_left_tongue')
    cover = join(comp,cover,tongue)
    pocket = prism_xy(comp,offset_polygon(tongue_xy,tongueClearance),
                      zc-tongueWidth/2-tongueClearance,zc+tongueWidth/2+tongueClearance,'Gusseted_tongue_pocket')
    handle = cut(comp,handle,pocket)
    # Relieve only the left pivot edge. This is intentional room for the
    # cover thickness to swing past the seat while the right end is lifted.
    pivot_half_h = lidWingH/2+wooFitClearance+lidBorder+lidGap
    pivot = box(comp,left_edge-lidTiltClearance,left_edge+lidTiltClearance,
                seat_y,gripD,zc-pivot_half_h,zc+pivot_half_h,'Lid_pivot_clearance')
    handle = cut(comp,handle,pivot)
    return handle,cover,{'sample_center_x':(root_left+end_x)/2,
                         'sample_min_y':min(beam_front,tongue_front)-snapClearance,
                         'free_beam_length_mm':snapLength,
                         'beam_depth_mm':snapWidth,
                         'print_face_y_mm':outer_y,
                         'slot_type':'Through U-slot; integral beam; open edge hook',
                         'release_direction':'-Z; lift right edge toward +Y, then slide +X',
                         'planned_opening_angle_deg':lidTiltAngle}


def report_body(body):
    bb = body.boundingBox
    return {'solid':body.isSolid,'lumps':body.lumps.count,'volume_mm3':body.volume*1000,
            'bounds_mm':[[bb.minPoint.x*10,bb.minPoint.y*10,bb.minPoint.z*10],
                         [bb.maxPoint.x*10,bb.maxPoint.y*10,bb.maxPoint.z*10]]}


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    folder = os.path.dirname(os.path.abspath(__file__))
    stage = 'Validate settings'
    report = {}
    try:
        vertices,radii,info = woo_geometry()
        validate(info,vertices)
        report['woo_profile'] = info
        report['settings'] = {k:v for k,v in globals().items() if not k.startswith('_') and isinstance(v,(int,float,bool,str))}
        report['settings'].pop('folder',None)
        app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.DirectDesignType
        design.unitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
        root = design.rootComponent
        # Fusion does not allow renaming the root component directly.
        # modelName is used for the exported archive filename instead.
        occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        comp = occurrence.component
        comp.name = 'Handle'
        stage = 'Build handle'
        handle = handle_blank(comp)
        # Saved pristine skin is the source for the EXACT flush cover surface.
        skin = adsk.fusion.TemporaryBRepManager.get().copy(handle)
        stage = 'Bolt bores and head access'
        for sign in [-1,1]:
            handle = cut(comp,handle,cylinder(comp,sign*boltSpacing/2,0,-1,handleTop+1,boltD,'M6_bore'))
            handle = cut(comp,handle,cylinder(comp,sign*boltSpacing/2,0,shoulder,handleTop+1,headPocketD,'M6_head_access'))
        stage = 'WOO cavity and cover seat'
        cavity_curves = rounded_polygon(offset_polygon(vertices,wooFitClearance),[r+wooFitClearance for r in radii])
        # Open to +Y; cover closes it at Y=+wooHalfDepth.
        handle = cut(comp,handle,prism_xz(comp,cavity_curves,-wooHalfDepth,gripD,'WOO_opening'))
        zc = handleTop-gripH/2+wooZOffset
        xmax = max(abs(x) for x,z in vertices)+wooFitClearance
        wing_start,wing_end = wooTopFlat/2, xmax+lidWingLength
        seat_y = wooHalfDepth-lidSeatDepth
        seat = make_cover_outline(comp,vertices,radii,wooFitClearance+lidBorder+lidGap,
                                  seat_y,gripD,wing_start,wing_end,zc,'Cover_seat')
        handle = cut(comp,handle,seat)
        # Cover starts deeper at the rim; WOO envelope is subtracted below.
        cover = make_cover_outline(comp,vertices,radii,wooFitClearance+lidBorder,
                                   seat_y+lidAxialGap,gripD,wing_start,wing_end,zc,'Cover_stock')
        cover = intersect(comp,cover,comp.bRepBodies.add(skin))
        cover = cut(comp,cover,prism_xz(comp,cavity_curves,-gripD,wooHalfDepth,'Cover_inner_clearance'))
        stage = 'Rigid tongue and accessible release catch'
        if enableSnapFits:
            handle,cover,lock_info = releasable_lock(comp,handle,cover,xmax,wing_end,zc,seat_y)
            report['cover_lock'] = lock_info
        stage = 'Finger/tool release recess'
        # Vertical small cylinder at outer right wing edge, recessed in front skin.
        pry = cylinder(comp,wing_end+wooFitClearance+lidBorder,gripD/2,
                       zc-pryD/2,zc+pryD/2,pryD,'Lift_recess')
        handle = cut(comp,handle,pry)
        handle.name = 'Handle'
        cover.name = 'Cover'
        stage = 'Check solids and assembled clearances'
        report['handle'] = report_body(handle)
        report['cover'] = report_body(cover)
        for body in [handle,cover]:
            check(body.isSolid and body.lumps.count == 1,'Expected one connected solid per part.')
        check(abs(handle.boundingBox.maxPoint.z*10-handleTop) < geometryTolerance,'Overall height differs from handleTop.')
        check(abs(handle.boundingBox.minPoint.z*10) < geometryTolerance,'Feet do not lie at Z=0.')
        tbm = adsk.fusion.TemporaryBRepManager.get()
        overlap = tbm.copy(handle)
        ok = tbm.booleanOperation(overlap,tbm.copy(cover),adsk.fusion.BooleanTypes.IntersectionBooleanType)
        check(ok,'Could not verify cover interference.')
        report['overlap_mm3'] = overlap.volume*1000
        check(overlap.volume < 0.00001,'Cover interferes with handle; check catch relief.')
        if makeFitSample and enableSnapFits:
            stage = 'Fit sample'
            sx = lock_info['sample_center_x']
            sample_y = lock_info['sample_min_y']-baseTrimMargin
            for original,label in [(handle,'Receiver_sample'),(cover,'Catch_sample')]:
                piece = comp.bRepBodies.add(tbm.copy(original))
                crop = box(comp,sx-sampleWidth/2,sx+sampleWidth/2,sample_y,gripD,
                           zc-sampleHeight/2,zc+sampleHeight/2,label+'_crop')
                piece = intersect(comp,piece,crop)
                sample_occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
                sample_occ.component.name = label
                piece.moveToComponent(sample_occ)
                matrix = adsk.core.Matrix3D.create()
                matrix.translation = adsk.core.Vector3D.create((boltSpacing/2+gripD-sx)/10,0,-(zc-sampleHeight/2)/10)
                sample_occ.transform2 = matrix
        cover_occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        cover_occ.component.name = 'Cover'
        cover = cover.moveToComponent(cover_occ)
        for component in [comp,cover_occ.component]:
            for sk in component.sketches:
                sk.isVisible = False
            for plane in component.constructionPlanes:
                plane.isLightBulbOn = False
        stage = 'Export'
        if exportFiles:
            manager = design.exportManager
            for component,name in [(comp,'Handle'),(cover_occ.component,'Cover')]:
                opt = manager.createSTLExportOptions(component,os.path.join(folder,name+'.stl'))
                opt.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
                check(manager.execute(opt),'STL export failed: '+name)
            check(manager.execute(manager.createFusionArchiveExportOptions(os.path.join(folder,modelName+'.f3d'))),'F3D export failed.')
        camera = app.activeViewport.camera
        camera.eye = p(130,210,135)
        camera.target = p(0,0,handleTop/2)
        camera.upVector = adsk.core.Vector3D.create(0,0,1)
        camera.isFitView = True
        app.activeViewport.camera = camera
        app.activeViewport.refresh()
        report['status'] = 'PASS'
        with open(os.path.join(folder,'build_report.json'),'w',encoding='utf-8') as stream:
            json.dump(report,stream,ensure_ascii=False,indent=2)
        if showMessage:
            ui.messageBox('Ручка и крышка созданы в новом документе.\n'
                f'Полость Y: {-wooHalfDepth:g} .. +{wooHalfDepth:g} мм.\n'
                f'Высота профиля Woo: {info["height_mm"]:.3f} мм.\n'+
                ('Слева язычок, справа защёлка с доступом через паз.\n'
                 'Снятие: отжать язычок в пазу к -Z, поднять правый край к +Y, сдвинуть крышку к +X.\n'
                 'Посадку и ход снятия проверьте пробной печатью.\n' if enableSnapFits
                 else 'Крышка без защёлок: сохранён посадочный бортик, фиксации нет.\n')+
                'STL/F3D и отчёт: '+folder,modelName+' v'+scriptVersion)
    except Exception:
        report['status'] = 'FAIL'
        report['stage'] = stage
        report['error'] = traceback.format_exc()
        with open(os.path.join(folder,'build_report.json'),'w',encoding='utf-8') as stream:
            json.dump(report,stream,ensure_ascii=False,indent=2)
        ui.messageBox('Версия: '+scriptVersion+'\nОшибка на этапе: '+stage+'\n\n'+traceback.format_exc(),modelName+' v'+scriptVersion)


def stop(context):
    pass
