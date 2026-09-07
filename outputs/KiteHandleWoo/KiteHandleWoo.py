# -*- coding: utf-8 -*-
"""Ручка кайтборда с полостью WOO и съёмной крышкой заподлицо.

КАРТА ФАЙЛА:
- Настройки: размеры, зазоры, параметры креплений и экспорта.
- Вспомогательные функции: контуры, эскизы, операции с телами.
- handle_blank: ручка; woo_geometry: полость; releasable_lock: крепления.
- run: вся последовательность построения и сохранение файлов.

Оси: X — вдоль перекладины, Y — поперёк хвата, Z — высота над доской.
Поверхность доски: Z=0. Крышка находится со стороны +Y.
Левая/правая сторона в коде: -X/+X, независимо от ракурса камеры.
Все длины в настройках — мм, угол lidTiltAngle — градусы.
API хранит координаты в см: перевод выполняется во вспомогательных функциях.
Каждый запуск создаёт новый документ в режиме Direct Design.
Размеры меняются здесь, затем модель строится заново.
"""

# ==================== SETTINGS / НАСТРОЙКИ ====================
scriptVersion = '1.0.22'       # Версия повышается при каждом обновлении.
fitGap = 0.20  # Общий посадочный зазор НА СТОРОНУ, мм.
boltSpacing = 180.0  # Межцентровое расстояние крепёжных болтов по X.
handleTop = 72.0  # Полная высота от поверхности доски.
gripH = 28.0  # Размер постоянного сечения поперёк оси ручки, включая ножки.
gripD = 28.0  # Глубина постоянного сечения по Y, включая ножки.
legLean = 20.0  # Смещение верхнего конца прямой ножки внутрь относительно болта.
boltD = 6.6  # Диаметр сквозного отверстия под M6.
headPocketD = 13.0  # Диаметр доступа к головке болта.
shoulder = 4.0  # Толщина опоры под головкой от поверхности доски.

gripR = 6.0  # Радиус сечения ножек, изгибов и перекладины.
printFriendlySection = True  # Симметричные скосы 45 градусов с обеих сторон по Y.
sectionChamfer = 3.0  # Размер скосов; 3 мм оставляют место вокруг увеличенной полости.
bendR = 17.0  # Радиус осевой линии верхних изгибов, не радиус сечения.
baseTrimMargin = 1.0  # Запас ниже доски перед обрезкой основания на Z=0.

# ПОЛОСТЬ WOO: исходные размеры между точками касания скруглений.
wooTopFlat = 32.044  # Длина верхней прямой между касаниями скруглений.
wooBottomFlat = 51.279  # Длина нижней прямой между касаниями скруглений.
wooSlopeRise = 12.203  # Перепад высоты длинного наклонного прямого участка.
wooTopChord = 0.862  # Хорда верхней дуги для восстановления угла наклона.
wooShortSide = 2.255  # Длина короткого нижнего наклонного участка.
wooTopR = 1.0  # Радиус верхних углов исходного профиля.
wooSideR = 1.0  # Радиус боковых углов исходного профиля.
wooBottomR = 0.5  # Радиус нижних углов исходного профиля.
wooSideChordReference = 0.960  # Справочная хорда из чертежа для сопоставления с отчётом.
wooHalfDepth = 11.0  # Половина полезной глубины: полость от Y=-11 до Y=+11.
wooProfileOffset = 1.0  # Расширение исходного контура наружу в плоскости XZ.
wooZOffset = 0.0  # Сдвиг полости по Z относительно центра перекладины.
wooFitClearance = 0.0  # Дополнительный припуск к профилю ПОСЛЕ wooProfileOffset.
enableDrainHole = True  # Слив из камеры WOO вниз через хват; False отключает отверстие.
drainHoleD = 1.5  # Диаметр сливного отверстия, мм; центр X=0, Y=0, направление вдоль Z.

lidBorder = 1.15  # Ширина бортика вокруг полости в плоскости XZ.
lidGap = fitGap  # Зазор по контуру крышки на сторону.
lidSeatDepth = 1.1  # Заглубление бортика относительно полезного объёма WOO.
lidAxialGap = 0.1  # Уменьшенный зазор над посадкой по Y для снижения люфта крышки.
lidWingLength = 16.0  # Длина боковых участков для креплений за пределами полости.
lidWingH = 11.0  # Высота боковых участков крышки по Z.
lidWingR = 1.0  # Радиус углов боковых участков.
enableSnapFits = True  # Жёсткий язычок слева и две зеркальные защёлки справа.
snapLength = 12.0  # Свободная длина упругого язычка вдоль X.
snapThickness = 1.2  # Толщина свободного конца по Z; отжим к -Z.
snapRootThickness = 1.8  # Толщина у корня; к свободному концу язычок сужается.
snapWidth = gripD/2-(wooHalfDepth-lidSeatDepth+lidAxialGap)  # Вычисляемая глубина язычка по Y: вся толщина крышки, без уступа.
snapRootLength = 2.0  # Длина закреплённого участка у корня защёлки.
snapHook = 0.60  # Глубина обоих зубьев за край посадки: верхний к +Z, нижний к -Z.
snapHookLength = 2.5  # Длина зуба вдоль X у свободного конца.
snapRamp = 1.0  # Длина каждого скоса зуба для постепенного нарастания при печати.
snapTipLand = 0.4  # Плоский участок на вершине зуба.
snapClearance = 0.1  # Локальный зазор гнёзд зубьев; уменьшен для снижения люфта.
snapFlexSpace = 0.85  # Место для отжима под язычком; рабочий ход, не зазор посадки.
snapUpperGap = snapFlexSpace  # Верхний зазор по Z равен нижнему: 0.85 мм.
snapTipGap = fitGap  # Зазор у свободного торца язычка.
snapEdgeRail = 2.0  # Толщина полосы крышки над пазом по Z; у зуба она раскрывается.
mechanismKeepout = 0.8  # Отступ крепления от максимальной ширины полости WOO.
tongueEngagement = 1.2  # Глубина захода жёсткого левого язычка в карман.
tongueThickness = 1.6  # Толщина жёсткого язычка по Y у основания.
tongueTipThickness = 0.8  # Толщина его переднего конца: скос облегчает заход.
tongueWidth = 5.0  # Ширина жёсткого язычка по Z.
tongueRootLength = 3.0  # Длина соединения жёсткого язычка с крышкой по X.
tongueClearance = fitGap  # Зазор на сторону в кармане жёсткого язычка.
tongueMotionSteps = 12  # Число положений для построения огибающей кармана при наклоне.
lidTiltAngle = 2.0  # Расчётный угол наклона крышки при снятии, градусы.
lidTiltClearance = fitGap  # Зазор у левого поворотного края крышки.
pryD = 10.0  # Диаметр полукруглой выемки под палец в плоскости крышки XZ.
pryUnderlap = 0.8  # Насколько выемка заходит под торец крышки по X.
pryDepth = 1.5  # Глубина выемки за посадкой по Y, чтобы подцепить край ногтем.
minimumWall = 1.5  # Минимум для геометрических ограничений, не расчёт прочности.

makeFitSample = False  # Создать отдельные фрагменты крепления для пробной печати.
sampleWidth = 18.0  # Ширина фрагмента по X, включая весь язычок и корень.
sampleHeight = 18.0  # Высота фрагмента по Z, включая зуб и П-паз.
exportFiles = True  # Сохранить F3D и отдельные STL рядом со скриптом.
showMessage = True  # Показать итоговое окно после построения.
modelName = 'KiteHandle_WOO'  # Имя архива модели и заголовок сообщений.
geometryTolerance = 0.02  # Допуск встроенных проверок размеров, мм.
# ================= КОНЕЦ ИЗМЕНЯЕМЫХ НАСТРОЕК =================

import math
import os
import json
import traceback
import adsk.core
import adsk.fusion


# ЕДИНИЦЫ И API.
# Создать точку, переведя миллиметры в сантиметры Fusion.
def p(x, y, z):
    return adsk.core.Point3D.create(x / 10, y / 10, z / 10)


# Передать размер в Fusion с явно указанными единицами мм.
def val(mm):
    return adsk.core.ValueInput.createByString(f'{mm:.12g} mm')


# Преобразовать список Python в коллекцию объектов Fusion.
def collection(items):
    result = adsk.core.ObjectCollection.create()
    for item in items:
        result.add(item)
    return result


# Остановить построение с объяснением, если условие не выполнено.
def check(condition, message):
    if not condition:
        raise ValueError(message)


# КОНТУРЫ.
# Скруглить выпуклый многоугольник с обходом против часовой стрелки.
# Два элемента задают отрезок, три — дугу (начало, промежуточная точка, конец).
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


# Выпуклая оболочка точек: внешний контур для кармана язычка.
def convex_hull(points):
    """CCW supporting polygon for a set of 2D construction points."""
    points = sorted(set(points))
    def cross(a,b,c):
        return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    lower,upper = [],[]
    for point in points:
        while len(lower) >= 2 and cross(lower[-2],lower[-1],point) <= 0:
            lower.pop()
        lower.append(point)
    for point in reversed(points):
        while len(upper) >= 2 and cross(upper[-2],upper[-1],point) <= 0:
            upper.pop()
        upper.append(point)
    return lower[:-1]+upper[:-1]


# Карман охватывает положения язычка при наклоне и сдвиге.
# Добавляется запас между отсчётами дуги; это построение, не симуляция всей сборки.
def tongue_pocket_outline(tongue_xy,pivot_x,pivot_y):
    """Clear the tongue's tilt-then-slide route, not just its closed pose.
    The opposite lid edge is lifted first; the tongue then slides out in +X.
    A small analytical sagitta allowance encloses arcs between sampled poses.
    This builds geometry; it is not a simulation of the full lid assembly.
    """
    angle = math.radians(lidTiltAngle)
    points = list(tongue_xy)
    travel = tongueEngagement+tongueClearance
    for i in range(tongueMotionSteps+1):
        a = angle*i/tongueMotionSteps
        ca,sa = math.cos(a),math.sin(a)
        pose = [(pivot_x+(x-pivot_x)*ca-(y-pivot_y)*sa,
                 pivot_y+(x-pivot_x)*sa+(y-pivot_y)*ca) for x,y in tongue_xy]
        points.extend(pose)
        if i == tongueMotionSteps:
            points.extend((x+travel,y) for x,y in pose)
    radius = max(math.hypot(x-pivot_x,y-pivot_y) for x,y in tongue_xy)
    allowance = radius*(1-math.cos(angle/(2*tongueMotionSteps)))
    return offset_polygon(convex_hull(points),tongueClearance+allowance)


# Сдвинуть прямые стороны контура наружу.
# Радиусы скруглений увеличиваются отдельно на ту же величину.
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


# Восстановить профиль WOO по чертежу, затем расширить его на wooProfileOffset.
# Возвращает вершины XZ, радиусы и сведения о размерах для отчёта.
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
    # Offset the supporting lines AND increase arc radii by the same amount.
    # This is an equidistant contour, not scaling or adding to individual widths.
    # Apply before lid/seat construction so their central contours follow WOO,
    # while the side-wing cross-sections and fitting gaps remain independent.
    check(wooProfileOffset >= 0,'wooProfileOffset must be non-negative.')
    verts = offset_polygon(verts,wooProfileOffset)
    radii = [r+wooProfileOffset for r in radii]
    return verts, radii, {'height_mm':height+2*wooProfileOffset,
                         'drawing_height_mm':height, 'profile_offset_mm':wooProfileOffset,
                         'alpha_deg':math.degrees(alpha),
                         'beta_deg':math.degrees(beta),
                         'side_chord_mm':2*wooSideR*math.sin((beta-alpha)/2)}


# ЭСКИЗЫ И ТЕЛА.
# Создать плоскость по точке и нормали и эскиз на ней.
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


# Перенести двумерные кривые в эскиз через map_point и получить замкнутый профиль.
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


# Контур прямоугольника шириной w и высотой h со скруглениями r.
def rectangle_curves(w, h, r):
    return rounded_polygon([(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)], [r]*4)


# Постоянное симметричное сечение ручки.
# В режиме печати скосы у плоскостей по Y сочетаются с боковыми дугами.
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


# Вспомогательный эскиз сечения в XY; основная ручка строится через handle_blank.
def section_xy(comp,x,z,w,d,r,name):
    sk = sketch_plane(comp,(0,0,z),(0,0,1),name)
    return draw_curves(sk,rectangle_curves(w,d,r),lambda q:(x+q[0],q[1],z))


# Выдавить профиль в новое тело; знак distance выбирает направление.
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


# Профиль XZ выдавливается вдоль Y от y0 до y1: полость и крышка.
def prism_xz(comp, curves, y0, y1, name):
    sk = sketch_plane(comp,(0,y0,0),(0,1,0),name)
    profile = draw_curves(sk,curves,lambda q:(q[0],y0,q[1]))
    return extrude(comp,profile,y1-y0,name)


# Многоугольник XY выдавливается вдоль Z от z0 до z1.
def prism_xy(comp, vertices, z0, z1, name):
    sk = sketch_plane(comp,(0,0,z0),(0,0,1),name)
    curves = [(vertices[i],vertices[(i+1)%len(vertices)]) for i in range(len(vertices))]
    profile = draw_curves(sk,curves,lambda q:(q[0],q[1],z0))
    return extrude(comp,profile,z1-z0,name)


# Многоугольник YZ выдавливается вдоль X от x0 до x1.
def prism_yz(comp, vertices, x0, x1, name):
    sk = sketch_plane(comp,(x0,0,0),(1,0,0),name)
    curves = [(vertices[i],vertices[(i+1)%len(vertices)]) for i in range(len(vertices))]
    profile = draw_curves(sk,curves,lambda q:(x0,q[0],q[1]))
    return extrude(comp,profile,x1-x0,name)


# Прямоугольный объём по границам X/Y/Z для обрезки и вырезов.
def box(comp,x0,x1,y0,y1,z0,z1,name):
    return prism_xy(comp,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z0,z1,name)


# Цилиндр вдоль Z для болтовых отверстий и выемки.
def cylinder(comp,x,y,z0,z1,diameter,name):
    sk = sketch_plane(comp,(0,0,z0),(0,0,1),name)
    sk.sketchCurves.sketchCircles.addByCenterRadius(sk.modelToSketchSpace(p(x,y,z0)),diameter/20)
    result = extrude(comp,sk.profiles.item(0),z1-z0,name)
    sk.isVisible = False
    return result


# Изменить target с помощью tool, поглотив вспомогательное тело.
# В Direct Design результат остаётся в target, а Combine может вернуть None; проверяются число тел и связность.
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


# Объединить два пересекающихся тела в одно.
def join(comp,a,b):
    return boolean(comp,a,b,adsk.fusion.FeatureOperations.JoinFeatureOperation)


# Вычесть второе тело из первого.
def cut(comp,a,b):
    return boolean(comp,a,b,adsk.fusion.FeatureOperations.CutFeatureOperation)


# Оставить общий объём двух тел.
def intersect(comp,a,b):
    return boolean(comp,a,b,adsk.fusion.FeatureOperations.IntersectFeatureOperation)


# РУЧКА.
# Найти угол и точки касания дуги с наклонной ножкой и горизонтальной перекладиной.
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


# Провести одно сечение по пути: ножка — дуга — перекладина — дуга — ножка.
# Sweep сохраняет сечение без расширений; снизу тело обрезается на Z=0.
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


# Встроенные ограничения размеров сечения, полости, болтов и креплений.
# Выполняются при запуске; это не испытание готовой детали.
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
    if enableDrainHole:
        # Канал должен целиком входить в центральную часть камеры.
        check(0 < drainHoleD < min(2*wooHalfDepth,wooTopFlat),
              'Диаметр слива должен быть положительным и меньше ширины и глубины камеры WOO.')
    check(abs(wooZOffset)+info['height_mm']/2+wooFitClearance+lidBorder+lidGap < gripH/2,'Cover seat does not fit grip height.')
    check(lidGap > 0 and lidBorder > lidGap and lidSeatDepth > lidAxialGap,'Invalid lid seat/gap.')
    wing_half = lidWingH/2+wooFitClearance+lidBorder
    check(0 < pryD/2 < wing_half-minimumWall,
          'Выемка под палец слишком широкая: оставьте материал до верхнего и нижнего края.')
    check(0 < pryDepth < wooHalfDepth-lidSeatDepth+gripD/2-minimumWall and
          0 < pryUnderlap < lidWingLength,
          'Недопустимая глубина выемки или заход под торец крышки.')
    if enableSnapFits:
        check(0 < snapClearance < snapHook < snapFlexSpace,'Invalid latch engagement/release travel.')
        check(snapRootThickness >= snapThickness > 0 and snapRootLength > snapFlexSpace/2,
              'Invalid tapered beam/root dimensions.')
        check(snapWidth > 2*snapRamp+snapTipLand and
              snapWidth <= gripD/2-(wooHalfDepth-lidSeatDepth+lidAxialGap)+geometryTolerance,
              'Beam must fit within the cover thickness and contain both hook ramps.')
        check(snapRamp >= lidGap+snapHook+snapClearance,
              'Hook ramps must be at least as long as the hook rise for printable slopes.')
        check(0 < snapHookLength < snapLength and mechanismKeepout > snapClearance,
              'Invalid hook length or WOO keepout.')
        check(mechanismKeepout+snapRootLength+snapLength+snapTipGap+minimumWall
              < lidWingLength+lidBorder,'Lid wing too short for the in-plane U-slot.')
        check(snapUpperGap > 0 and snapFlexSpace > 0 and
              snapTipGap > 0 and snapEdgeRail > 0,'Invalid U-slot widths.')
        wing_half = lidWingH/2+wooFitClearance+lidBorder
        check(wing_half-snapEdgeRail-snapUpperGap-snapRootThickness-snapFlexSpace
              > -wing_half+minimumWall,'U-slot leaves too little material below the beam.')
        # Между зеркальными пазами должна остаться непрерывная центральная полоса.
        check(2*(wing_half-snapEdgeRail-snapUpperGap-snapRootThickness-snapFlexSpace)
              >= minimumWall,'Зеркальные пазы сближаются: увеличьте lidWingH или уменьшите размеры пазов.')
        check(lidWingLength+wooFitClearance+lidBorder-pryUnderlap >
              mechanismKeepout+snapRootLength+snapLength+snapClearance,
              'Выемка под палец заходит в гнёзда защёлок: уменьшите pryUnderlap.')
        # All of the latch must start on the same flat outer print face.
        flat_half = gripH/2-(sectionChamfer if printFriendlySection else gripR)
        check(abs(wooZOffset)+wing_half+lidGap+snapHook+snapClearance < flat_half,
              'Edge catch reaches the curved outer skin; reduce lidWingH or hook size.')
        check(tongueRootLength > 0 and tongueThickness > 0 and
              tongueEngagement > 0 and tongueClearance > 0,'Invalid rigid tongue.')
        check(0 < tongueTipThickness < tongueThickness,
              'Tongue tip must be thinner than the root.')
        check(isinstance(tongueMotionSteps,int) and tongueMotionSteps >= 4,
              'tongueMotionSteps must be an integer >= 4.')
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
    check(xmax+lidWingLength+wooFitClearance+lidBorder-pryUnderlap+pryD/2+minimumWall
          < tangentx,'Выемка под палец достигает изгиба ручки; уменьшите pryD.')
    if enableSnapFits:
        check(xmax+lidWingLength+wooFitClearance+lidBorder+tongueEngagement+
              tongueClearance+minimumWall < tangentx,'Left tongue reaches the handle bend.')


# КРЫШКА.
# Центральный контур плюс два боковых участка креплений.
# Функция строит и крышку, и посадку с разными смещениями и глубиной.
def make_cover_outline(comp,vertices,radii,offset,y0,y1,wing_start,wing_end,zc,name):
    body = prism_xz(comp,rounded_polygon(offset_polygon(vertices,offset),[r+offset for r in radii]),y0,y1,name)
    for sign in [-1,1]:
        xa,xb = sorted([sign*(wing_start-offset),sign*(wing_end+offset)])
        wing = rounded_polygon([(xa,zc-lidWingH/2-offset),(xb,zc-lidWingH/2-offset),
                                 (xb,zc+lidWingH/2+offset),(xa,zc+lidWingH/2+offset)], [lidWingR+offset]*4)
        body = join(comp,body,prism_xz(comp,wing,y0,y1,name+'_wing'))
    return body


# Справа создаются две зеркальные упругие защёлки в сквозных П-пазах.
# Слева — жёсткий язычок с подкосом и карман для захода под наклоном.
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
    # Край крышки остаётся на месте. Утолщение верхней полосы и увеличение
    # зазора опускают всю балку: в v1.0.18 на 1.75 мм относительно v1.0.17.
    beam_top = edge_z-snapEdgeRail-snapUpperGap
    root_bottom = beam_top-snapRootThickness
    tip_bottom = beam_top-snapThickness

    # One continuous U-cut leaves the original lid material as the beam.
    # The lower slot also provides a mechanical stop after snapFlexSpace travel.
    # Exact semicircular caps, tangent to the two edges of each slot.
    # The lower slot is inclined: use its NORMAL width, not the vertical gap.
    slope = (tip_bottom-root_bottom)/snapLength
    scale = math.sqrt(1+slope*slope)
    lower_r = snapFlexSpace/(2*scale)
    center = (root_x,root_bottom-snapFlexSpace/2)
    lower_start = (center[0]+lower_r*slope/scale,center[1]-lower_r/scale)
    lower_end = (center[0]-lower_r*slope/scale,center[1]+lower_r/scale)
    lower_mid = (center[0]-lower_r/scale,center[1]-lower_r*slope/scale)
    top_start = (root_x,beam_top)
    top_end = (root_x,beam_top+snapUpperGap)
    top_mid = (root_x-snapUpperGap/2,beam_top+snapUpperGap/2)
    outer_top = (end_x+snapTipGap,beam_top+snapUpperGap)
    outer_bottom = (end_x+snapTipGap,tip_bottom-snapFlexSpace+slope*snapTipGap)
    curves = [(top_end,outer_top),(outer_top,outer_bottom),
              (outer_bottom,lower_start),(lower_start,lower_mid,lower_end),
              (lower_end,(end_x,tip_bottom)),((end_x,tip_bottom),(end_x,beam_top)),
              ((end_x,beam_top),top_start),(top_start,top_mid,top_end)]
    # Один профиль задаёт обе защёлки. Нижняя — точное отражение относительно Z=zc.
    # При подъёме крышки скосы зубьев направляют верхнюю балку к -Z, нижнюю к +Z.
    base_z = edge_z-snapClearance
    peak_z = edge_z+lidGap+snapHook
    nose_y = outer_y-2*snapRamp-snapTipLand
    hook_profile = [(nose_y,beam_top-snapClearance),(outer_y,beam_top-snapClearance),
                    (outer_y,base_z),(outer_y-snapRamp,peak_z),
                    (outer_y-snapRamp-snapTipLand,peak_z),(nose_y,base_z)]
    notch_profile = offset_polygon(hook_profile,snapClearance)
    for sign, label in [(1,'Upper'),(-1,'Lower')]:
        def mirror_point(point):
            return (point[0],zc+sign*(point[1]-zc))
        slot_curves = [tuple(mirror_point(pt) for pt in curve) for curve in curves]
        tooth = [mirror_point(pt) for pt in hook_profile]
        receiver = [mirror_point(pt) for pt in notch_profile]
        if sign < 0:
            # После отражения возвращаем прежнее направление обхода контура.
            slot_curves = [tuple(reversed(curve)) for curve in reversed(slot_curves)]
            tooth.reverse()
            receiver.reverse()
        cover = cut(comp,cover,prism_xz(comp,slot_curves,-gripD,gripD,
                                        label+'_Through_U_release_slot'))
        za,zb = sorted([zc+sign*(beam_top-zc),zc+sign*(edge_z+snapClearance-zc)])
        mouth = box(comp,end_x-snapHookLength-snapClearance,end_x+snapTipGap,
                    -gripD,gripD,za,zb,label+'_Edge_release_access')
        cover = cut(comp,cover,mouth)
        # Оба скоса сохранены: заход при закрытии и выход при подъёме пальцем.
        hook = prism_yz(comp,tooth,end_x-snapHookLength,end_x,label+'_Release_hook')
        cover = join(comp,cover,hook)
        notch = prism_yz(comp,receiver,end_x-snapHookLength-snapClearance,
                         end_x+snapClearance,label+'_Edge_hook_recess')
        handle = cut(comp,handle,notch)

    # Left tongue has a continuous 45-degree print gusset. With +Y down,
    # its projecting footprint grows one mm per mm of build height.
    left_edge = -(wing_end+wooFitClearance+lidBorder)
    tongue_front = seat_y-tongueClearance-tongueThickness
    tongue_back = seat_y-tongueClearance
    tongue_xy = [(left_edge-tongueEngagement,tongue_back-tongueTipThickness),
                 (left_edge,tongue_front),
                 (left_edge+tongueRootLength,tongue_front),
                 (left_edge+tongueRootLength,tongue_back+tongueEngagement),
                 (left_edge,tongue_back+tongueEngagement),
                 (left_edge-tongueEngagement,tongue_back)]
    tongue = prism_xy(comp,tongue_xy,zc-tongueWidth/2,zc+tongueWidth/2,'Gusseted_left_tongue')
    cover = join(comp,cover,tongue)
    pocket_outline = tongue_pocket_outline(tongue_xy,left_edge,tongue_back)
    pocket = prism_xy(comp,pocket_outline,
                      zc-tongueWidth/2-tongueClearance,zc+tongueWidth/2+tongueClearance,'Gusseted_tongue_pocket')
    handle = cut(comp,handle,pocket)
    # Follow the SAME rounded wing contour as the cover, with clearance.
    # A rectangular strip here used to leave square ears beyond the corners.
    # Retain opening room by offsetting the rounded outline instead.
    pivot_offset = wooFitClearance+lidBorder+max(lidGap,lidTiltClearance)
    pivot_half_h = lidWingH/2+pivot_offset
    pivot_left = -wing_end-pivot_offset
    pivot_right = -wooTopFlat/2+pivot_offset
    pivot_vertices = [(pivot_left,zc-pivot_half_h),(pivot_right,zc-pivot_half_h),
                      (pivot_right,zc+pivot_half_h),(pivot_left,zc+pivot_half_h)]
    pivot_curves = rounded_polygon(pivot_vertices,[lidWingR+pivot_offset]*4)
    pivot = prism_xz(comp,pivot_curves,seat_y,gripD,'Rounded_lid_pivot_clearance')
    handle = cut(comp,handle,pivot)
    return handle,cover,{'sample_center_x':(root_left+end_x)/2,
                         'sample_min_y':min(beam_front,tongue_front)-snapClearance,
                         'free_beam_length_mm':snapLength,
                         'beam_depth_mm':snapWidth,
                         'upper_slot_gap_z_mm':snapUpperGap,
                         'lower_slot_gap_z_mm':snapFlexSpace,
                         'upper_cover_rail_z_mm':snapEdgeRail,
                         'beam_top_z_mm':beam_top,
                         'hook_rise_from_beam_mm':peak_z-beam_top,
                         'print_face_y_mm':outer_y,
                         'latch_count':2,
                         'finger_recess_diameter_mm':pryD,
                         'slot_type':'Two mirrored through U-slots and edge hooks',
                         'release_direction':'Lift latch edge +Y; upper beam flexes -Z, lower +Z; then slide +X',
                         'planned_opening_angle_deg':lidTiltAngle}


# ОТЧЁТ.
# Получить связность, объём в мм3 и границы тела в мм.
def report_body(body):
    bb = body.boundingBox
    return {'solid':body.isSolid,'lumps':body.lumps.count,'volume_mm3':body.volume*1000,
            'bounds_mm':[[bb.minPoint.x*10,bb.minPoint.y*10,bb.minPoint.z*10],
                         [bb.maxPoint.x*10,bb.maxPoint.y*10,bb.maxPoint.z*10]]}


# ГЛАВНАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ.
# Fusion вызывает run при запуске.
# Переменная stage хранит текущий этап для сообщения об ошибке.
def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    folder = os.path.dirname(os.path.abspath(__file__))
    stage = 'Validate settings'
    report = {}
    try:
        # 1. Рассчитать профиль полости и проверить допустимость настроек.
        vertices,radii,info = woo_geometry()
        validate(info,vertices)
        report['woo_profile'] = info
        report['settings'] = {k:v for k,v in globals().items() if not k.startswith('_') and isinstance(v,(int,float,bool,str))}
        report['settings'].pop('folder',None)
        # 2. Создать новый документ и отдельный компонент ручки.
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
        # 3. Построить ручку и сохранить копию её исходной поверхности.
        # Эта копия позже ограничит крышку, чтобы она точно повторяла ручку.
        handle = handle_blank(comp)
        # Saved pristine skin is the source for the EXACT flush cover surface.
        skin = adsk.fusion.TemporaryBRepManager.get().copy(handle)
        stage = 'Bolt bores and head access'
        # 4. Два сквозных отверстия и углубления под головки с опорой shoulder.
        for sign in [-1,1]:
            handle = cut(comp,handle,cylinder(comp,sign*boltSpacing/2,0,-1,handleTop+1,boltD,'M6_bore'))
            handle = cut(comp,handle,cylinder(comp,sign*boltSpacing/2,0,shoulder,handleTop+1,headPocketD,'M6_head_access'))
        stage = 'WOO cavity and cover seat'
        # 5. Полость открывается к +Y; расширенная неглубокая посадка окружает её.
        cavity_curves = rounded_polygon(offset_polygon(vertices,wooFitClearance),[r+wooFitClearance for r in radii])
        # Open to +Y; cover closes it at Y=+wooHalfDepth.
        handle = cut(comp,handle,prism_xz(comp,cavity_curves,-wooHalfDepth,gripD,'WOO_opening'))
        zc = handleTop-gripH/2+wooZOffset
        if enableDrainHole:
            stage = 'WOO drain hole'
            # Вертикальный канал по центру: от точки ниже нижней грани хвата
            # до середины пустой камеры. Верхняя стенка камеры не затрагивается.
            drain = cylinder(comp,0,0,handleTop-gripH-baseTrimMargin,zc,
                             drainHoleD,'WOO_drain_hole')
            handle = cut(comp,handle,drain)
        report['drain_hole'] = {'enabled':enableDrainHole,
                                'diameter_mm':drainHoleD if enableDrainHole else None,
                                'center_xy_mm':[0,0],'direction':'-Z'}
        stage = 'WOO cavity and cover seat'
        xmax = max(abs(x) for x,z in vertices)+wooFitClearance
        wing_start,wing_end = wooTopFlat/2, xmax+lidWingLength
        seat_y = wooHalfDepth-lidSeatDepth
        seat = make_cover_outline(comp,vertices,radii,wooFitClearance+lidBorder+lidGap,
                                  seat_y,gripD,wing_start,wing_end,zc,'Cover_seat')
        handle = cut(comp,handle,seat)
        # Cover starts deeper at the rim; WOO envelope is subtracted below.
        # 6. Заготовка крышки: обрезать по исходной поверхности ручки,
        # затем убрать с обратной стороны материал из полезного объёма датчика.
        cover = make_cover_outline(comp,vertices,radii,wooFitClearance+lidBorder,
                                   seat_y+lidAxialGap,gripD,wing_start,wing_end,zc,'Cover_stock')
        cover = intersect(comp,cover,comp.bRepBodies.add(skin))
        cover = cut(comp,cover,prism_xz(comp,cavity_curves,-gripD,wooHalfDepth,'Cover_inner_clearance'))
        stage = 'Rigid tongue and accessible release catch'
        # 7. Добавить крепления крышки и соответствующие карманы в ручке.
        if enableSnapFits:
            handle,cover,lock_info = releasable_lock(comp,handle,cover,xmax,wing_end,zc,seat_y)
            report['cover_lock'] = lock_info
        stage = 'Finger/tool release recess'
        # 8. Добавить доступ для поддевания крышки у края.
        # Настоящий полукруг виден со стороны крышки: диаметр вдоль Z,
        # дуга выходит наружу по X. Небольшой заход под торец открывает край.
        pry_x = wing_end+wooFitClearance+lidBorder-pryUnderlap
        radius = pryD/2
        pry_curves = [((pry_x,zc-radius),(pry_x+radius,zc),(pry_x,zc+radius)),
                      ((pry_x,zc+radius),(pry_x,zc-radius))]
        pry = prism_xz(comp,pry_curves,seat_y-pryDepth,gripD,'Finger_semicircle_recess')
        handle = cut(comp,handle,pry)
        handle.name = 'Handle'
        cover.name = 'Cover'
        stage = 'Check solids and assembled clearances'
        # 9. При запуске проверить целостность, высоту и пересечение деталей.
        # Проверяется закрытая сборка, а не вся траектория установки и снятия.
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
        # 10. При необходимости выделить образцы крепления для пробной печати.
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
        # 11. Перенести крышку в свой компонент для отдельного STL.
        cover_occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        cover_occ.component.name = 'Cover'
        cover = cover.moveToComponent(cover_occ)
        for component in [comp,cover_occ.component]:
            for sk in component.sketches:
                sk.isVisible = False
            for plane in component.constructionPlanes:
                plane.isLightBulbOn = False
        stage = 'Export'
        # 12. Сохранить отдельные STL и общую модель F3D рядом со скриптом.
        if exportFiles:
            manager = design.exportManager
            for component,name in [(comp,'Handle'),(cover_occ.component,'Cover')]:
                opt = manager.createSTLExportOptions(component,os.path.join(folder,name+'.stl'))
                opt.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
                check(manager.execute(opt),'STL export failed: '+name)
            check(manager.execute(manager.createFusionArchiveExportOptions(os.path.join(folder,modelName+'.f3d'))),'F3D export failed.')
        # 13. Настроить вид, записать JSON-отчёт и показать результат.
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
                ('Слева жёсткий язычок, справа две зеркальные защёлки.\n'
                 'Снятие: подцепить край в полукруглой выемке, поднять к +Y и сдвинуть крышку к +X.\n'
                 'Посадку и ход снятия проверьте пробной печатью.\n' if enableSnapFits
                 else 'Крышка без защёлок: сохранён посадочный бортик, фиксации нет.\n')+
                'STL/F3D и отчёт: '+folder,modelName+' v'+scriptVersion)
    except Exception:
        # Сохранить этап и полный traceback, чтобы найти причину сбоя.
        report['status'] = 'FAIL'
        report['stage'] = stage
        report['error'] = traceback.format_exc()
        with open(os.path.join(folder,'build_report.json'),'w',encoding='utf-8') as stream:
            json.dump(report,stream,ensure_ascii=False,indent=2)
        ui.messageBox('Версия: '+scriptVersion+'\nОшибка на этапе: '+stage+'\n\n'+traceback.format_exc(),modelName+' v'+scriptVersion)


# Завершение скрипта: постоянных обработчиков событий здесь нет.
def stop(context):
    pass
