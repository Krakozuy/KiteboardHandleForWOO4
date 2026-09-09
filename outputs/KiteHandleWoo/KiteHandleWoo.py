# -*- coding: utf-8 -*-
"""Kiteboard handle with a WOO cavity and a removable flush cover. / Ручка кайтборда с полостью WOO и съёмной крышкой заподлицо.

FILE MAP: / КАРТА ФАЙЛА:
- Settings: dimensions, clearances, fastening and export parameters. / - Настройки: размеры, зазоры, параметры креплений и экспорта.
- Helpers: outlines, sketches, and body operations. / - Вспомогательные функции: контуры, эскизы, операции с телами.
- handle_blank: handle; woo_geometry: cavity; releasable_lock: fasteners. / - handle_blank: ручка; woo_geometry: полость; releasable_lock: крепления.
- run: the complete build sequence and file saving. / - run: вся последовательность построения и сохранение файлов.

Axes: X along the crossbar, Y across the grip, Z above the board. / Оси: X — вдоль перекладины, Y — поперёк хвата, Z — высота над доской.
Board surface: Z=0. The cover is on the +Y side. / Поверхность доски: Z=0. Крышка находится со стороны +Y.
Left/right in the code: -X/+X, regardless of camera angle. / Левая/правая сторона в коде: -X/+X, независимо от ракурса камеры.
All setting lengths are in mm; lidTiltAngle is in degrees. / Все длины в настройках — мм, угол lidTiltAngle — градусы.
The API stores coordinates in cm; helper functions perform the conversion. / API хранит координаты в см: перевод выполняется во вспомогательных функциях.
Each run creates a new document in Direct Design mode. / Каждый запуск создаёт новый документ в режиме Direct Design.
Change dimensions here, then rebuild the model. / Размеры меняются здесь, затем модель строится заново.
"""

# ==================== SETTINGS / НАСТРОЙКИ ====================
scriptVersion = '1.0.35'       # The version is incremented with each update. / Версия повышается при каждом обновлении.
fitGap = 0.1  # General fit clearance PER SIDE, mm. / Общий посадочный зазор НА СТОРОНУ, мм.
boltSpacing = 180.0  # Mounting bolt center-to-center distance along X. / Межцентровое расстояние крепёжных болтов по X.
handleTop = 72.0  # Overall height above the board surface. / Полная высота от поверхности доски.
gripH = 28.0  # Constant section size transverse to the handle axis, including the legs. / Размер постоянного сечения поперёк оси ручки, включая ножки.
gripD = 28.0  # Constant section depth along Y, including the legs. / Глубина постоянного сечения по Y, включая ножки.
legLean = 20.0  # Inward offset of the straight leg's upper end relative to the bolt. / Смещение верхнего конца прямой ножки внутрь относительно болта.
boltD = 6.6  # M6 through-hole diameter. / Диаметр сквозного отверстия под M6.
headPocketD = 13.0  # Bolt head access diameter. / Диаметр доступа к головке болта.
shoulder = 4.0  # Support thickness beneath the head, measured from the board surface. / Толщина опоры под головкой от поверхности доски.

# TPU pads: the base top coincides with the ASA sole at Z=0. / TPU-проставки: верх основания совпадает с подошвой ASA на Z=0.
enableFootPads = True  # Create two pads and matching pockets in the legs. / Создать две проставки и ответные пазы в ножках.
padThickness = 3.0  # Base thickness below the sole; excludes keys. / Толщина основания вниз от подошвы; не включает выступы.
padKeyHeight = 2.0  # Key height above the pad's top plane. / Высота выступов над верхней плоскостью проставки.
padKeyLength = 15.0  # Length of each key along X, the long edge of the sole. / Длина каждого выступа вдоль X, длинного края подошвы.
padKeyWidth = 2.5  # Width of each key along Y. / Ширина каждого выступа по Y.
padKeyEdgeInset = 3.5  # Distance from the sole edge to the nearest long side of the key. / От края подошвы до ближайшей длинной стороны выступа.
padKeyClearance = 0.2  # Matching pocket clearance per side and above the key. / Зазор ответного паза на каждую сторону и над выступом.

gripR = 6.0  # Section radius of the legs, bends, and crossbar. / Радиус сечения ножек, изгибов и перекладины.
printFriendlySection = True  # Symmetric 45-degree chamfers on both Y sides. / Симметричные скосы 45 градусов с обеих сторон по Y.
sectionChamfer = 3.0  # Chamfer size; 3 mm leaves room around the enlarged cavity. / Размер скосов; 3 мм оставляют место вокруг увеличенной полости.
bendR = 17.0  # Centerline radius of the upper bends, not the section radius. / Радиус осевой линии верхних изгибов, не радиус сечения.
baseTrimMargin = 1.0  # Margin below the board before trimming the base at Z=0. / Запас ниже доски перед обрезкой основания на Z=0.

# WOO CAVITY: original dimensions between fillet tangency points. / ПОЛОСТЬ WOO: исходные размеры между точками касания скруглений.
wooTopFlat = 32.044  # Upper straight length between fillet tangency points. / Длина верхней прямой между касаниями скруглений.
wooBottomFlat = 51.279  # Lower straight length between fillet tangency points. / Длина нижней прямой между касаниями скруглений.
wooSlopeRise = 12.203  # Height difference along the long inclined straight segment. / Перепад высоты длинного наклонного прямого участка.
wooTopChord = 0.862  # Upper arc chord used to recover the slope angle. / Хорда верхней дуги для восстановления угла наклона.
wooShortSide = 2.255  # Length of the short lower inclined segment. / Длина короткого нижнего наклонного участка.
wooTopR = 1.0  # Upper corner radius of the original profile. / Радиус верхних углов исходного профиля.
wooSideR = 1.0  # Side corner radius of the original profile. / Радиус боковых углов исходного профиля.
wooBottomR = 0.5  # Lower corner radius of the original profile. / Радиус нижних углов исходного профиля.
wooSideChordReference = 0.960  # Reference chord from the drawing for comparison with the report. / Справочная хорда из чертежа для сопоставления с отчётом.
wooHalfDepth = 11.0  # Half the usable depth: cavity from Y=-11 to Y=+11. / Половина полезной глубины: полость от Y=-11 до Y=+11.
wooProfileOffset = 1  # Outward offset of the original outline in the XZ plane. / Расширение исходного контура наружу в плоскости XZ.
wooZOffset = 0.0  # Cavity Z offset relative to the crossbar center. / Сдвиг полости по Z относительно центра перекладины.
wooFitClearance = 0.0  # Additional profile allowance AFTER wooProfileOffset. / Дополнительный припуск к профилю ПОСЛЕ wooProfileOffset.
enableWooFingerRecesses = True  # Two semicircular recesses for sensor removal; False disables them. / Две полукруглые выемки для извлечения датчика; False отключает.
wooFingerD = 10.0  # Recess diameter in the XZ plane, mm. / Диаметр выемок в плоскости XZ, мм.
wooFingerDepth = 4.0  # Depth along -Y from the cover seat plane, not the outer surface. / Глубина по -Y от плоскости посадки крышки, а не от наружной поверхности.
wooFingerBowlRatio = 0.75  # Smooth ellipsoidal floor shape; value strictly between 0 and 1. / Форма плавного эллипсоидального дна; значение строго между 0 и 1.
wooFingerSeatMargin = 0.2  # Minimum recess margin from the upper/lower edge of the cover side wing. / Минимальный отступ выемок от верхнего/нижнего края бокового крыла крышки.
enableDrainHole = True  # Drain from the WOO chamber down through the grip; False disables the hole. / Слив из камеры WOO вниз через хват; False отключает отверстие.
drainHoleD = 1.5  # Drain hole diameter, mm; center X=0, Y=0, direction along Z. / Диаметр сливного отверстия, мм; центр X=0, Y=0, направление вдоль Z.

lidBorder = 1.15  # Rim width around the cavity in the XZ plane. / Ширина бортика вокруг полости в плоскости XZ.
lidGap = fitGap  # Cover outline clearance per side. / Зазор по контуру крышки на сторону.
lidSeatDepth = 1.1  # Rim recess depth relative to the usable WOO volume. / Заглубление бортика относительно полезного объёма WOO.
lidAxialGap = 0.1  # Reduced Y clearance above the seat to reduce cover play. / Уменьшенный зазор над посадкой по Y для снижения люфта крышки.
lidWingLength = 16.0  # Length of side fastening sections beyond the cavity. / Длина боковых участков для креплений за пределами полости.
lidWingH = 11.0  # Height of the cover side sections along Z. / Высота боковых участков крышки по Z.
lidWingR = 1.0  # Corner radius of the side sections. / Радиус углов боковых участков.
enableSnapFits = True  # Rigid tongue on the left and two mirrored snap catches on the right. / Жёсткий язычок слева и две зеркальные защёлки справа.
snapLength = 12.0  # Free length of the flexible tongue along X. / Свободная длина упругого язычка вдоль X.
snapThickness = 1.4  # Free-end thickness along Z; both beams are reinforced for a tighter fit. / Толщина свободного конца по Z; обе балки усилены для более тугой посадки.
snapRootThickness = 2.0  # Root thickness; the tongue tapers toward the free end. / Толщина у корня; к свободному концу язычок сужается.
snapWidth = gripD/2-(wooHalfDepth-lidSeatDepth+lidAxialGap)  # Calculated tongue depth along Y: the full cover thickness, without a step. / Вычисляемая глубина язычка по Y: вся толщина крышки, без уступа.
snapRootLength = 2.0  # Length of the fixed section at the catch root. / Длина закреплённого участка у корня защёлки.
snapHook = 0.75  # Engagement depth of both teeth beyond the seat edge: upper toward +Z, lower toward -Z. / Глубина обоих зубьев за край посадки: верхний к +Z, нижний к -Z.
snapHookLength = 2.5  # Tooth length along X at the free end. / Длина зуба вдоль X у свободного конца.
snapYInset = 1.0  # Inset of both working teeth and sockets from the outer surface toward -Y; 0 disables it. / Смещение обоих рабочих зубьев и гнёзд от наружной поверхности к центру по -Y; 0 отключает.
snapRamp = 1.1  # Minimum length of each ramp along Y; increased automatically if needed. / Минимальная длина каждого скоса по Y; при необходимости увеличивается автоматически.
snapTipLand = 0.4  # Flat land at the tooth tip. / Плоский участок на вершине зуба.
snapClearance = 0.2  # Clearance PER SIDE: on both X sides of each tooth stem and in the matching socket. / Зазор НА СТОРОНУ: с обеих сторон стойки каждого зуба по X и в ответном гнезде.
# Calculated length: the ramp is at least as long as the tooth rise to keep the slope at most 45 degrees. / Вычисляемая длина: скос не короче подъёма зуба, чтобы сохранить уклон до 45°.
# Increasing tooth depth or clearance automatically lengthens the ramp. / При увеличении глубины зуба или зазора скос автоматически удлиняется.
snapRampEffective = max(snapRamp, lidGap+snapHook+snapClearance)
snapFlexSpace = 0.85  # Deflection space beneath the tongue; working travel, not fit clearance. / Место для отжима под язычком; рабочий ход, не зазор посадки.
snapUpperGap = snapFlexSpace  # Upper Z gap equals the lower gap: 0.85 mm. / Верхний зазор по Z равен нижнему: 0.85 мм.
snapEdgeRail = 2.0  # Thickness of the cover strip above the slot along Z; it opens at the tooth. / Толщина полосы крышки над пазом по Z; у зуба она раскрывается.
mechanismKeepout = 0.8  # Fastener offset from the maximum WOO cavity width. / Отступ крепления от максимальной ширины полости WOO.
tongueEngagement = 1.2  # Engagement depth of the rigid left tongue in its pocket. / Глубина захода жёсткого левого язычка в карман.
tongueThickness = 1.6  # Rigid tongue thickness along Y at the base. / Толщина жёсткого язычка по Y у основания.
tongueTipThickness = 0.8  # Leading tip thickness: the ramp eases insertion. / Толщина его переднего конца: скос облегчает заход.
tongueWidth = 5.0  # Rigid tongue width along Z. / Ширина жёсткого язычка по Z.
tongueRootLength = 3.0  # Length of the rigid tongue's connection to the cover along X. / Длина соединения жёсткого язычка с крышкой по X.
tongueClearance = fitGap  # Clearance per side in the rigid tongue pocket. / Зазор на сторону в кармане жёсткого язычка.
tongueMotionSteps = 12  # Number of poses used to construct the pocket envelope during tilting. / Число положений для построения огибающей кармана при наклоне.
lidTiltAngle = 2.0  # Design cover tilt angle during removal, degrees. / Расчётный угол наклона крышки при снятии, градусы.
lidTiltClearance = fitGap  # Clearance at the left pivoting edge of the cover. / Зазор у левого поворотного края крышки.
pryWidth = 14.0  # Maximum scoop width along Z; it narrows automatically near the cover. / Максимальная ширина ложбинки по Z; у крышки она автоматически сужается.
pryLength = 13.0  # Length of the smooth approach along X from the edge under the cover outward. / Длина плавного подхода по X от края под крышкой наружу.
pryUnderlap = 0.8  # Scoop underlap beneath the original cover end along X. / Заход ложбинки под исходный торец крышки по X.
pryDepth = gripD/2-(wooHalfDepth-lidSeatDepth+lidAxialGap)  # Calculated depth to the inner plane of the cover edge; currently 4 mm. / Вычисляемая глубина до внутренней плоскости края крышки; сейчас 4 мм.
pryBowlCenterRatio = 0.25  # Floor shape: a gentler floor preserves clearance beneath the lip near the neck. / Форма дна: более пологое дно сохраняет просвет под полочкой у сужения.
pryNeckInset = 0.15  # How far the side edges of the hidden recess end extend inside the cover outline along Z. / Насколько боковые края скрытого конца выемки заходят внутрь контура крышки по Z.
pryLipWidth = 6.0  # Rounded cover lip width along Z. / Ширина округлой полочки крышки по Z.
pryLipProjection = 1.8  # Lip projection along X into the scoop, below the grip surface. / Выступ полочки по X в ложбинку, ниже поверхности хвата.
pryLipThickness = 2.4  # Lip thickness along Y. / Толщина полочки по Y.
pryLipRoot = 1.5  # Lip overlap with the original cover edge along X. / Перекрытие полочки с исходным краем крышки по X.
pryLipR = 0.8  # Lip fillets in the XY and XZ projections. / Скругления полочки в проекциях XY и XZ.
pryLipMinClearance = 0.6  # Minimum clearance beneath the lip; separate from structural wall thickness. / Минимальный просвет под полочкой; отдельно от толщины несущих стенок.
minimumWall = 1.5  # Minimum for geometric constraints, not a strength calculation. / Минимум для геометрических ограничений, не расчёт прочности.

makeFitSample = False  # Create separate fastener sections for a test print. / Создать отдельные фрагменты крепления для пробной печати.
sampleWidth = 18.0  # Sample width along X, including the entire tongue and root. / Ширина фрагмента по X, включая весь язычок и корень.
sampleHeight = 18.0  # Sample height along Z, including the tooth and U-slot. / Высота фрагмента по Z, включая зуб и П-паз.
exportFiles = True  # Save F3D and separate STL files beside the script. / Сохранить F3D и отдельные STL рядом со скриптом.
showMessage = True  # Show the result dialog after building. / Показать итоговое окно после построения.
modelName = 'KiteHandle_WOO'  # Model archive name and message title. / Имя архива модели и заголовок сообщений.
geometryTolerance = 0.02  # Tolerance for built-in dimension checks, mm. / Допуск встроенных проверок размеров, мм.
# ================= END OF EDITABLE SETTINGS / ================= КОНЕЦ ИЗМЕНЯЕМЫХ НАСТРОЕК =================

import math
import os
import json
import traceback
import adsk.core
import adsk.fusion


# UNITS AND API. / ЕДИНИЦЫ И API.
# Create a point, converting millimeters to Fusion centimeters. / Создать точку, переведя миллиметры в сантиметры Fusion.
def p(x, y, z):
    return adsk.core.Point3D.create(x / 10, y / 10, z / 10)


# Pass a dimension to Fusion with explicit mm units. / Передать размер в Fusion с явно указанными единицами мм.
def val(mm):
    return adsk.core.ValueInput.createByString(f'{mm:.12g} mm')


# Convert a Python list to a Fusion object collection. / Преобразовать список Python в коллекцию объектов Fusion.
def collection(items):
    result = adsk.core.ObjectCollection.create()
    for item in items:
        result.add(item)
    return result


# Stop the build with an explanation if the condition is not met. / Остановить построение с объяснением, если условие не выполнено.
def check(condition, message):
    if not condition:
        raise ValueError(message)


# OUTLINES. / КОНТУРЫ.
# Round a convex polygon with counterclockwise winding. / Скруглить выпуклый многоугольник с обходом против часовой стрелки.
# Two elements define a line; three define an arc (start, midpoint, end). / Два элемента задают отрезок, три — дугу (начало, промежуточная точка, конец).
def rounded_polygon(vertices, radii):
    """Return lines/arcs for a convex CCW polygon, all in mm. / Вернуть отрезки/дуги выпуклого многоугольника с обходом против часовой стрелки; всё в мм.
    Arc representation is (start, midpoint, end); line is (start, end). / Дуга представлена как (начало, промежуточная точка, конец), отрезок — (начало, конец).
    This avoids reliance on unstable sketch-fillet edge numbering. / Это исключает зависимость от нестабильной нумерации рёбер скруглений эскиза.
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
        # Radius zero intentionally preserves the bed-face/chamfer junction. / Нулевой радиус намеренно сохраняет стык плоскости печати и скоса.
        # Do not emit a degenerate three-point arc for such a corner. / Для такого угла не создаём вырожденную дугу по трём точкам.
        if c[3] > 0:
            result.append((c[0], c[1], c[2]))
        result.append((c[2], nxt[0]))
    return result


# Convex hull of points: outer outline for the tongue pocket. / Выпуклая оболочка точек: внешний контур для кармана язычка.
def convex_hull(points):
    """CCW supporting polygon for a set of 2D construction points. / Опорный многоугольник с обходом против часовой стрелки для набора двумерных построечных точек."""
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


# The pocket encloses tongue poses during tilting and sliding. / Карман охватывает положения язычка при наклоне и сдвиге.
# An allowance is added between arc samples; this constructs geometry, not a full assembly simulation. / Добавляется запас между отсчётами дуги; это построение, не симуляция всей сборки.
def tongue_pocket_outline(tongue_xy,pivot_x,pivot_y):
    """Clear the tongue's tilt-then-slide route, not just its closed pose. / Обеспечить просвет для наклона и последующего сдвига язычка, а не только для закрытого положения.
    The opposite lid edge is lifted first; the tongue then slides out in +X. / Сначала поднимается противоположный край крышки, затем язычок выдвигается к +X.
    A small analytical sagitta allowance encloses arcs between sampled poses. / Небольшой аналитический припуск на стрелу дуги охватывает дуги между выбранными положениями.
    This builds geometry; it is not a simulation of the full lid assembly. / Здесь строится геометрия; это не симуляция всей сборки крышки.
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


# Offset the straight outline sides outward. / Сдвинуть прямые стороны контура наружу.
# Fillet radii are increased separately by the same amount. / Радиусы скруглений увеличиваются отдельно на ту же величину.
def offset_polygon(vertices, distance):
    """Exact supporting-line offset of a convex CCW polygon. / Точное смещение опорных прямых выпуклого многоугольника с обходом против часовой стрелки."""
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


# Reconstruct the WOO profile from the drawing, then expand it by wooProfileOffset. / Восстановить профиль WOO по чертежу, затем расширить его на wooProfileOffset.
# Return XZ vertices, radii, and dimension information for the report. / Возвращает вершины XZ, радиусы и сведения о размерах для отчёта.
def woo_geometry():
    """Solve rounded six-vertex contour from screenshot dimensions. / Рассчитать скруглённый контур с шестью вершинами по размерам со снимка экрана.
    Top R1 chord fixes alpha. Bottom flat and lower line fix beta. / Хорда верхней дуги R1 задаёт alpha. Нижняя горизонталь и нижняя наклонная задают beta.
    The side R1 chord is an independent rounded check (~0.960 mm). / Хорда боковой дуги R1 служит независимой проверкой с учётом округления (~0.960 мм).
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
    # Intersection of long and short supporting lines. / Пересечение длинной и короткой опорных прямых.
    zside = (topx + height/math.tan(alpha)-bottomx) / (
        1/math.tan(alpha)-1/math.tan(beta))
    xside = bottomx-zside/math.tan(beta)
    # Counterclockwise contour starting at lower left. / Контур против часовой стрелки, начиная с левого нижнего угла.
    verts = [(-bottomx,0),(bottomx,0),(xside,zside),
             (topx,height),(-topx,height),(-xside,zside)]
    zbase = handleTop-gripH/2+wooZOffset-height/2
    verts = [(x,z+zbase) for x,z in verts]
    radii = [wooBottomR,wooBottomR,wooSideR,wooTopR,wooTopR,wooSideR]
    # Offset the supporting lines AND increase arc radii by the same amount. / Сместить опорные прямые И увеличить радиусы дуг на ту же величину.
    # This is an equidistant contour, not scaling or adding to individual widths. / Это эквидистантный контур, а не масштабирование или увеличение отдельных размеров ширины.
    # Apply before lid/seat construction so their central contours follow WOO, / Применить до построения крышки и посадки, чтобы их центральные контуры повторяли WOO,
    # while the side-wing cross-sections and fitting gaps remain independent. / при этом сечения боковых крыльев и посадочные зазоры остаются независимыми.
    check(wooProfileOffset >= 0,'wooProfileOffset must be non-negative.')
    verts = offset_polygon(verts,wooProfileOffset)
    radii = [r+wooProfileOffset for r in radii]
    return verts, radii, {'height_mm':height+2*wooProfileOffset,
                         'drawing_height_mm':height, 'profile_offset_mm':wooProfileOffset,
                         'alpha_deg':math.degrees(alpha),
                         'beta_deg':math.degrees(beta),
                         'side_chord_mm':2*wooSideR*math.sin((beta-alpha)/2)}


# SKETCHES AND BODIES. / ЭСКИЗЫ И ТЕЛА.
# Create a plane from a point and normal, then a sketch on it. / Создать плоскость по точке и нормали и эскиз на ней.
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


# Map 2D curves into a sketch through map_point and obtain a closed profile. / Перенести двумерные кривые в эскиз через map_point и получить замкнутый профиль.
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


# Rectangle outline of width w and height h with fillet radius r. / Контур прямоугольника шириной w и высотой h со скруглениями r.
def rectangle_curves(w, h, r):
    return rounded_polygon([(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)], [r]*4)


# Constant symmetric handle section. / Постоянное симметричное сечение ручки.
# In print mode, chamfers near the Y-facing planes meet the side arcs. / В режиме печати скосы у плоскостей по Y сочетаются с боковыми дугами.
def handle_section_curves():
    """Uniform section mirrored about BOTH in-plane axes. / Постоянное сечение, симметричное относительно ОБЕИХ осей в своей плоскости.
    Y=-gripD/2 and Y=+gripD/2 have identical flat faces and 45-degree / На Y=-gripD/2 и Y=+gripD/2 находятся одинаковые плоские грани и скосы под 45 градусов.
    slopes. Rounding only the slope/sidewall junction keeps the expanding / Скругление только стыка скоса и боковой стенки сохраняет расширяющуюся
    print surface at least 45 degrees to either Y-facing print bed. / печатную поверхность под углом не менее 45 градусов к столу с любой стороны по Y.
    Rounding the flat-face/slope junction would reintroduce the overhang. / Скругление стыка плоской грани и скоса снова создало бы нависание.
    """
    if not printFriendlySection:
        return rectangle_curves(gripH,gripD,gripR)
    a,b,c = gripH/2,gripD/2,sectionChamfer
    vertices = [(-a+c,-b),(a-c,-b),(a,-b+c),(a,b-c),
                (a-c,b),(-a+c,b),(-a,b-c),(-a,-b+c)]
    return rounded_polygon(vertices,[0,0,gripR,gripR,0,0,gripR,gripR])


# Helper section sketch in XY; the main handle is built by handle_blank. / Вспомогательный эскиз сечения в XY; основная ручка строится через handle_blank.
def section_xy(comp,x,z,w,d,r,name):
    sk = sketch_plane(comp,(0,0,z),(0,0,1),name)
    return draw_curves(sk,rectangle_curves(w,d,r),lambda q:(x+q[0],q[1],z))


# Extrude a profile into a new body; the sign of distance selects the direction. / Выдавить профиль в новое тело; знак distance выбирает направление.
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


# Extrude an XZ profile along Y from y0 to y1: cavity and cover. / Профиль XZ выдавливается вдоль Y от y0 до y1: полость и крышка.
def prism_xz(comp, curves, y0, y1, name):
    sk = sketch_plane(comp,(0,y0,0),(0,1,0),name)
    profile = draw_curves(sk,curves,lambda q:(q[0],y0,q[1]))
    return extrude(comp,profile,y1-y0,name)


# Extrude an XY polygon along Z from z0 to z1. / Многоугольник XY выдавливается вдоль Z от z0 до z1.
def prism_xy(comp, vertices, z0, z1, name):
    sk = sketch_plane(comp,(0,0,z0),(0,0,1),name)
    curves = [(vertices[i],vertices[(i+1)%len(vertices)]) for i in range(len(vertices))]
    profile = draw_curves(sk,curves,lambda q:(q[0],q[1],z0))
    return extrude(comp,profile,z1-z0,name)


# Extrude a YZ polygon along X from x0 to x1. / Многоугольник YZ выдавливается вдоль X от x0 до x1.
def prism_yz(comp, vertices, x0, x1, name):
    sk = sketch_plane(comp,(x0,0,0),(1,0,0),name)
    curves = [(vertices[i],vertices[(i+1)%len(vertices)]) for i in range(len(vertices))]
    profile = draw_curves(sk,curves,lambda q:(x0,q[0],q[1]))
    return extrude(comp,profile,x1-x0,name)


# Rectangular volume bounded by X/Y/Z for trimming and cuts. / Прямоугольный объём по границам X/Y/Z для обрезки и вырезов.
def box(comp,x0,x1,y0,y1,z0,z1,name):
    return prism_xy(comp,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z0,z1,name)


# Cylinder along Z for bolt holes and the recess. / Цилиндр вдоль Z для болтовых отверстий и выемки.
def cylinder(comp,x,y,z0,z1,diameter,name):
    sk = sketch_plane(comp,(0,0,z0),(0,0,1),name)
    sk.sketchCurves.sketchCircles.addByCenterRadius(sk.modelToSketchSpace(p(x,y,z0)),diameter/20)
    result = extrude(comp,sk.profiles.item(0),z1-z0,name)
    sk.isVisible = False
    return result


# Modify target using tool, consuming the tool body. / Изменить target с помощью tool, поглотив вспомогательное тело.
# In Direct Design the result remains in target and Combine may return None; body count and connectivity are checked. / В Direct Design результат остаётся в target, а Combine может вернуть None; проверяются число тел и связность.
def boolean(comp, target, tool, operation):
    check(target is not None and target.isValid, 'Invalid Boolean target body.')
    check(tool is not None and tool.isValid, 'Invalid Boolean tool body.')
    body_count_before = comp.bRepBodies.count
    inp = comp.features.combineFeatures.createInput(target,collection([tool]))
    inp.operation = operation
    inp.isKeepToolBodies = False
    feat = comp.features.combineFeatures.add(inp)
    # Autodesk API: add() returns nothing for a non-parametric Combine. / Autodesk API: add() ничего не возвращает для непараметрического Combine.
    # In Direct Design it modifies the target body in place instead. / В Direct Design операция изменяет целевое тело на месте.
    if feat is not None:
        check(feat.bodies.count == 1, 'Boolean operation split the body unexpectedly.')
        result = feat.bodies.item(0)
    else:
        check(target.isValid, 'Combine did not preserve a valid target body.')
        result = target
    # With one consumed tool and one connected result the count drops by one. / При поглощении одного инструмента и одном связном результате число тел уменьшается на одно.
    # This also catches a failed/no-op Combine instead of treating None as success. / Это также выявляет сбой или отсутствие эффекта Combine, не считая None признаком успеха.
    check(comp.bRepBodies.count == body_count_before - 1,
          f'Combine did not consume exactly one tool: bodies before={body_count_before}, '
          f'after={comp.bRepBodies.count}; operation={operation}.')
    check(result.isSolid and result.lumps.count == 1,
          'Combine result is not one connected solid.')
    return result


# Join two intersecting bodies into one. / Объединить два пересекающихся тела в одно.
def join(comp,a,b):
    return boolean(comp,a,b,adsk.fusion.FeatureOperations.JoinFeatureOperation)


# Subtract the second body from the first. / Вычесть второе тело из первого.
def cut(comp,a,b):
    return boolean(comp,a,b,adsk.fusion.FeatureOperations.CutFeatureOperation)


# Keep the common volume of two bodies. / Оставить общий объём двух тел.
def intersect(comp,a,b):
    return boolean(comp,a,b,adsk.fusion.FeatureOperations.IntersectFeatureOperation)


# HANDLE. / РУЧКА.
# Find the angle and tangency points of the arc with the inclined leg and horizontal crossbar. / Найти угол и точки касания дуги с наклонной ножкой и горизонтальной перекладиной.
def bend_geometry():
    """Find an arc tangent to the straight inclined leg and horizontal grip. / Найти дугу, касательную к прямой наклонной ножке и горизонтальному хвату.
    legLean remains the inward offset at the leg/arc tangency point. / legLean остаётся смещением внутрь в точке касания ножки и дуги.
    z_t = z_c - R + R*sin(phi), tan(phi) = legLean / z_t. / Соотношения: z_t = z_c - R + R*sin(phi), tan(phi) = legLean / z_t.
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


# Sweep one section along the path: leg - arc - crossbar - arc - leg. / Провести одно сечение по пути: ножка — дуга — перекладина — дуга — ножка.
# Sweep preserves the section without widening; the body is trimmed below at Z=0. / Sweep сохраняет сечение без расширений; снизу тело обрезается на Z=0.
def handle_blank(comp):
    half = boltSpacing/2
    legx = half-legLean
    zc = handleTop-gripH/2
    phi,zt,tangentx = bend_geometry()
    sn,cs = math.sin(phi),math.cos(phi)
    arc_center_z = zc-bendR
    # A SINGLE fixed profile follows the entire U path. No lofts or joins / ЕДИНСТВЕННЫЙ постоянный профиль проходит весь П-образный путь. Без лофтов или соединений
    # between differently oriented/sized sections: straight legs are prismatic. / между сечениями разной ориентации/размера: прямые ножки остаются призматическими.
    # Extend far enough that both oblique end caps lie wholly below the board. / Продлить достаточно далеко, чтобы оба наклонных торца полностью оказались под доской.
    sweep_z = -(gripH/2*sn+baseTrimMargin)
    sweep_x = half-sweep_z*math.tan(phi)
    # Every line/arc junction is tangent by construction. / Каждый стык отрезка и дуги касательный по построению.
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
    # Keep only Z>=0. This gives coplanar mounting faces without changing / Оставить только Z>=0. Это даёт компланарные монтажные грани без изменения
    # the constant cross-section along the inclined legs. / постоянного поперечного сечения вдоль наклонных ножек.
    bb = body.boundingBox
    trim = box(comp,bb.minPoint.x*10-baseTrimMargin,bb.maxPoint.x*10+baseTrimMargin,
               bb.minPoint.y*10-baseTrimMargin,bb.maxPoint.y*10+baseTrimMargin,
               0,handleTop+baseTrimMargin,'Board_plane_trim')
    body = intersect(comp,body,trim)
    body.name = 'Handle_blank'
    return body


# Find recess centers on the chamber's straight inclined sides, accounting for its offset. / Найти центры выемок на прямых наклонных боках камеры, с учётом её оффсета.
def woo_finger_recess_geometry(cavity_curves):
    radius = wooFingerD/2
    check(radius > 0 and wooFingerSeatMargin > 0,'Диаметр выемок и отступ от края должны быть положительными.')
    check(0 < wooFingerDepth < 2*wooHalfDepth-lidSeatDepth-minimumWall,
          'Выемки слишком глубокие: оставьте опору датчика у задней части камеры.')
    check(0 < wooFingerBowlRatio < 1,'Коэффициент формы дна wooFingerBowlRatio должен быть между 0 и 1.')
    # Select the longest inclined straight segment on the right side. / У правого бока выбираем самый длинный наклонный прямой участок.
    # Exclude the upper/lower horizontal segments and the short lower chamfer. / Верхняя/нижняя горизонтали и короткий нижний скос сюда не попадают.
    sides = [c for c in cavity_curves if len(c) == 2 and min(c[0][0],c[1][0]) > 0
             and abs(c[1][0]-c[0][0]) > geometryTolerance
             and abs(c[1][1]-c[0][1]) > geometryTolerance]
    check(bool(sides),'Не найден наклонный бок камеры для выемки под палец.')
    side = max(sides,key=lambda c: math.dist(c[0],c[1]))
    low,high = sorted(side,key=lambda q: q[1])
    length = math.dist(low,high)
    check(2*(radius+geometryTolerance) < length,'Выемка шире прямого участка камеры: уменьшите wooFingerD.')
    zc = handleTop-gripH/2+wooZOffset
    wing_half = lidWingH/2+wooFitClearance+lidBorder
    # The entire circle must remain beneath the cover side wing; its diameter must not / Весь круг должен оставаться под боковым крылом крышки; диаметр не должен
    # reach the original side fillets. Choose the height closest to the center. / доходить до скруглений исходного бока. Выбираем ближайшую к центру высоту.
    end_margin = (radius+geometryTolerance)*(high[1]-low[1])/length
    z_low = max(low[1]+end_margin,zc-wing_half+radius+wooFingerSeatMargin)
    z_high = min(high[1]-end_margin,zc+wing_half-radius-wooFingerSeatMargin)
    check(z_low <= z_high,'Выемка не помещается под крышкой: уменьшите wooFingerD или увеличьте lidWingH.')
    center_z = max(z_low,min(zc,z_high))
    center_x = low[0]+(high[0]-low[0])*(center_z-low[1])/(high[1]-low[1])
    y_bottom = wooHalfDepth-lidSeatDepth-wooFingerDepth
    return center_x,center_z,radius,y_bottom


# Smooth bowls using the same principle as the cover removal scoop. / Плавные чаши по тому же принципу, что и ложбинка для снятия крышки.
# A semicircle remains at the seat plane, with depth increasing toward the sensor. / На посадочной плоскости остаётся полукруг, а глубина возрастает к датчику.
def make_woo_finger_recesses(comp,handle,cavity_curves):
    cx,cz,radius,y_bottom = woo_finger_recess_geometry(cavity_curves)
    seat_y = wooHalfDepth-lidSeatDepth
    # Choose the ellipsoid so its section at Y=seat_y has exactly / Подбираем эллипсоид так, чтобы его сечение на Y=seat_y имело точно
    # diameter wooFingerD and its deepest point lies at y_bottom. / диаметр wooFingerD, а самая глубокая точка находилась на y_bottom.
    lateral_radius = radius/math.sqrt(1-wooFingerBowlRatio**2)
    depth_radius = wooFingerDepth/(1-wooFingerBowlRatio)
    center_y = seat_y+depth_radius*wooFingerBowlRatio
    for sign,label in [(-1,'Left'),(1,'Right')]:
        tool = ellipsoid_body(comp,(sign*cx,center_y,cz),lateral_radius,depth_radius,
                              lateral_radius,'WOO_finger_bowl_'+label)
        # Trim the ellipsoid top at the seat: above it the circle would begin / Верхнюю часть эллипсоида отсекаем на посадке: выше неё круг начал бы
        # to widen. This keeps the recess within the original outline beneath the cover. / расширяться. Так выемка остаётся в прежнем контуре под крышкой.
        limit = box(comp,sign*cx-lateral_radius-geometryTolerance,
                    sign*cx+lateral_radius+geometryTolerance,
                    y_bottom-geometryTolerance,seat_y,
                    cz-lateral_radius-geometryTolerance,cz+lateral_radius+geometryTolerance,
                    'WOO_finger_bowl_limit_'+label)
        tool = intersect(comp,tool,limit)
        handle = cut(comp,handle,tool)
    return handle,{'enabled':True,'diameter_mm':wooFingerD,'depth_from_seat_mm':wooFingerDepth,
                   'shape':'ellipsoidal bowl','bowl_ratio':wooFingerBowlRatio,
                   'bottom_y_mm':y_bottom,'centers_xz_mm':[[-cx,cz],[cx,cz]]}


# Shared recess calculation for construction and checking clearance beneath the lip. / Общий расчёт выемки для построения и проверки просвета под полочкой.
def finger_scoop_geometry():
    """Dimensions of a single ellipsoid: a wide entrance with its end hidden beneath the cover. / Размеры единого эллипсоида: широкий вход с концом, скрытым под крышкой."""
    radius = lidWingR+wooFitClearance+lidBorder
    wing_half = lidWingH/2+wooFitClearance+lidBorder
    # Half-width of the rounded wing exactly at the recess X trimming plane. / Полуширина скруглённого крыла точно на плоскости обрезки выемки по X.
    if pryUnderlap < radius:
        end_half = wing_half-radius+math.sqrt(2*radius*pryUnderlap-pryUnderlap**2)
    else:
        end_half = wing_half
    check(0 < pryNeckInset < end_half,'Недопустимый заход боковых краёв выемки под крышку.')
    neck_half = min(pryWidth/2,end_half-pryNeckInset)
    # Shift the maximum width outward. The section at the trim narrows to neck_half, / Смещаем максимум ширины наружу. Сечение у обрезки сужается до neck_half,
    # while the outer end remains pryLength away from the trim. / а наружный конец остаётся на прежнем расстоянии pryLength от обрезки.
    ratio = math.sqrt(max(0.0,1-(2*neck_half/pryWidth)**2))
    front_length = pryLength/(1+ratio)
    center_shift = pryLength-front_length
    factor = math.sqrt(1-pryBowlCenterRatio**2)
    return (center_shift,front_length/factor,pryDepth/(1-pryBowlCenterRatio),
            pryWidth/(2*factor),neck_half)


# Built-in dimensional constraints for the section, cavity, bolts, and fasteners. / Встроенные ограничения размеров сечения, полости, болтов и креплений.
# Executed at startup; this is not a test of the finished part. / Выполняются при запуске; это не испытание готовой детали.
def validate(info, vertices, radii):
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
    if enableFootPads:
        check(min(padThickness,padKeyHeight,padKeyLength,padKeyWidth,
                  padKeyEdgeInset,padKeyClearance) > 0,'Размеры TPU-проставок должны быть положительными.')
        check(padKeyHeight+padKeyClearance+minimumWall <= shoulder,
              'Пазы проставок слишком глубокие относительно опоры головки болта.')
        check(padKeyLength+2*padKeyClearance < foot_width,
              'Выступы проставки слишком длинные для подошвы.')
        check(gripD/2-padKeyEdgeInset-padKeyWidth-padKeyClearance > boltD/2,
              'Выступы проставки или их пазы достигают отверстия M6.')
    if enableDrainHole:
        # The channel must fit entirely within the central chamber section. / Канал должен целиком входить в центральную часть камеры.
        check(0 < drainHoleD < min(2*wooHalfDepth,wooTopFlat),
              'Диаметр слива должен быть положительным и меньше ширины и глубины камеры WOO.')
    check(abs(wooZOffset)+info['height_mm']/2+wooFitClearance+lidBorder+lidGap < gripH/2,'Cover seat does not fit grip height.')
    check(lidGap > 0 and lidBorder > lidGap and lidSeatDepth > lidAxialGap,'Invalid lid seat/gap.')
    wing_half = lidWingH/2+wooFitClearance+lidBorder
    # The scoop lies beyond the cover end, so it may be wider than the wing. / Ложбинка расположена за торцом крышки, поэтому может быть шире её крыла.
    # Sockets are protected by the X underlap limit below; preserve the handle sidewalls along Z. / Гнёзда защищены ограничением захода по X ниже; по Z сохраняем боковые стенки ручки.
    check(0 < pryWidth/2 and abs(wooZOffset)+pryWidth/2+minimumWall < gripH/2,
          'Ложбинка слишком широкая: уменьшите pryWidth, чтобы сохранить края ручки.')
    cover_inner_y = wooHalfDepth-lidSeatDepth+lidAxialGap
    check(0 < pryDepth <= gripD/2-cover_inner_y and
          pryDepth < gripD-minimumWall and 0 < pryUnderlap < lidWingLength,
          'Недопустимая глубина ложбинки или заход под крышку.')
    check(pryLength > pryDepth and 0 < pryBowlCenterRatio < 1,
          'Подход ложбинки должен быть длиннее глубины; коэффициент формы должен быть между 0 и 1.')
    check(0 < pryLipWidth < pryWidth and 0 < pryLipProjection < pryLength-pryUnderlap and
          0 < pryLipRoot < lidWingLength and 0 < pryLipThickness <= snapWidth,
          'Недопустимые размеры полочки для захвата.')
    check(0 < pryLipR < min(pryLipRoot+pryLipProjection,pryLipWidth,pryLipThickness)/2,
          'Радиус полочки слишком большой.')
    shift,bowl_rx,bowl_ry,bowl_rz,neck_half = finger_scoop_geometry()
    # The cover seat is already cut beneath the lip root. Check only the portion / Под корнем полочки уже вырезана посадка крышки. Проверяем только часть,
    # projecting beyond the seat; account for its rounding at the lip's Z extremes. / выступающую за посадку; учитываем её скругление на крайних Z полочки.
    seat_radius = lidWingR+wooFitClearance+lidBorder+lidGap
    corner_z = max(0.0,pryLipWidth/2-(lidWingH/2-lidWingR))
    check(corner_z < seat_radius,'Полочка слишком широкая для посадки крышки.')
    exposed_start = max(0.0,pryUnderlap+lidGap-seat_radius+
                        math.sqrt(seat_radius**2-corner_z**2))
    exposed_end = pryUnderlap+pryLipProjection
    check(exposed_start < exposed_end,'Полочка не выступает за посадку крышки.')
    farthest_x = max(abs(exposed_start-shift),abs(exposed_end-shift))
    lip_q = 1-(farthest_x/bowl_rx)**2-(pryLipWidth/(2*bowl_rz))**2
    check(lip_q > 0,'Полочка выходит за пределы ложбинки.')
    lip_floor = gripD/2+bowl_ry*pryBowlCenterRatio-bowl_ry*math.sqrt(lip_q)
    # This is free space for finger access, not wall thickness: minimumWall does not apply here. / Это свободное место для подцепления, а не толщина стенки: minimumWall здесь не применяем.
    check(pryLipMinClearance > 0 and
          gripD/2-pryLipThickness-lip_floor >= pryLipMinClearance,
          'Под полочкой недостаточный просвет: расширьте ложбинку или уменьшите толщину полочки.')
    if enableSnapFits:
        check(0 < snapClearance < snapHook < snapFlexSpace,'Invalid latch engagement/release travel.')
        check(snapRootThickness >= snapThickness > 0 and snapRootLength > snapFlexSpace/2,
              'Invalid tapered beam/root dimensions.')
        check(snapRamp > 0,'Минимальная длина скоса snapRamp должна быть положительной.')
        check(snapYInset >= 0 and (snapYInset == 0 or snapYInset > snapClearance),
              'Смещение по Y должно быть нулевым либо больше snapClearance, чтобы перед пазом оставалась стенка.')
        check(snapWidth > snapYInset+2*snapRampEffective+snapTipLand and
              snapWidth <= gripD/2-(wooHalfDepth-lidSeatDepth+lidAxialGap)+geometryTolerance,
              'В толщине крышки не помещается смещённый по Y зуб с обоими скосами: '
              'уменьшите snapYInset, snapRamp, snapHook или snapClearance либо увеличьте толщину крышки.')
        check(gripD/2-snapYInset-2*snapRampEffective-snapTipLand-snapClearance >=
              wooHalfDepth-lidSeatDepth,
              'Смещённое гнездо уходит за дно посадки: уменьшите snapYInset или размеры зуба.')
        check(0 < snapHookLength < snapLength and mechanismKeepout > snapClearance,
              'Invalid hook length or WOO keepout.')
        check(snapHookLength+snapClearance < snapLength,
              'Боковой зазор зуба должен быть положительным и не доходить до корня балки.')
        check(mechanismKeepout+snapRootLength+snapLength+snapClearance+minimumWall
              < lidWingLength+lidBorder,'Lid wing too short for the in-plane U-slot.')
        check(snapUpperGap > 0 and snapFlexSpace > 0 and
              snapEdgeRail > 0,'Invalid U-slot widths.')
        wing_half = lidWingH/2+wooFitClearance+lidBorder
        check(wing_half-snapEdgeRail-snapUpperGap-snapRootThickness-snapFlexSpace
              > -wing_half+minimumWall,'U-slot leaves too little material below the beam.')
        # A continuous central strip must remain between the mirrored slots. / Между зеркальными пазами должна остаться непрерывная центральная полоса.
        check(2*(wing_half-snapEdgeRail-snapUpperGap-snapRootThickness-snapFlexSpace)
              >= minimumWall,'Зеркальные пазы сближаются: увеличьте lidWingH или уменьшите размеры пазов.')
        check(lidWingLength+wooFitClearance+lidBorder-pryUnderlap >
              mechanismKeepout+snapRootLength+snapLength+snapClearance,
              'Выемка под палец заходит в гнёзда защёлок: уменьшите pryUnderlap.')
        # The teeth and their supporting bases must remain within the cover's flat section. / Зубья и их опорные основания должны оставаться в пределах плоского участка крышки.
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
    if enableWooFingerRecesses:
        cavity_curves = rounded_polygon(offset_polygon(vertices,wooFitClearance),
                                        [r+wooFitClearance for r in radii])
        finger_x,finger_z,finger_radius,finger_bottom = woo_finger_recess_geometry(cavity_curves)
        check(finger_x+finger_radius+wooFingerSeatMargin <
              xmax+lidWingLength-lidWingR,
              'Выемки доходят до скруглённых торцов крышки: уменьшите wooFingerD.')
        if enableSnapFits:
            nearest_lock_x = min(xmax+mechanismKeepout+snapRootLength+snapLength-snapHookLength-snapClearance,
                                 xmax+lidWingLength+wooFitClearance+lidBorder-tongueRootLength-
                                 tongueClearance-lidTiltClearance)
            check(finger_x+finger_radius+minimumWall < nearest_lock_x,
                  'Выемки подходят к гнёздам креплений: уменьшите wooFingerD.')
    check(xmax+lidWingLength+lidGap+minimumWall < tangentx,
          'Bolt spacing too short: cover wings reach bends. Increase boltSpacing or reduce wings.')
    check(xmax+lidWingLength+wooFitClearance+lidBorder-pryUnderlap+pryLength+minimumWall
          < boltSpacing/2-headPocketD/2,'Ложбинка достигает зоны болта; уменьшите pryLength.')
    if enableSnapFits:
        check(xmax+lidWingLength+wooFitClearance+lidBorder+tongueEngagement+
              tongueClearance+minimumWall < tangentx,'Left tongue reaches the handle bend.')


# COVER. / КРЫШКА.
# Central outline plus two side fastening sections. / Центральный контур плюс два боковых участка креплений.
# This function builds both the cover and the seat with different offsets and depths. / Функция строит и крышку, и посадку с разными смещениями и глубиной.
def make_cover_outline(comp,vertices,radii,offset,y0,y1,wing_start,wing_end,zc,name):
    body = prism_xz(comp,rounded_polygon(offset_polygon(vertices,offset),[r+offset for r in radii]),y0,y1,name)
    for sign in [-1,1]:
        xa,xb = sorted([sign*(wing_start-offset),sign*(wing_end+offset)])
        wing = rounded_polygon([(xa,zc-lidWingH/2-offset),(xb,zc-lidWingH/2-offset),
                                 (xb,zc+lidWingH/2+offset),(xa,zc+lidWingH/2+offset)], [lidWingR+offset]*4)
        body = join(comp,body,prism_xz(comp,wing,y0,y1,name+'_wing'))
    return body


# Create two mirrored flexible catches in through U-slots on the right. / Справа создаются две зеркальные упругие защёлки в сквозных П-пазах.
# On the left: a rigid tongue with a gusset and a pocket for tilted insertion. / Слева — жёсткий язычок с подкосом и карман для захода под наклоном.
def releasable_lock(comp,handle,cover,xmax,wing_end,zc,seat_y):
    """Integral in-plane beam in a through U-slot; left tongue has a gusset. / Цельная балка в плоскости крышки в сквозном П-пазу; левый язычок имеет подкос.
    Print with +Y facing the bed: the lid AND beam start at Y=gripD/2. / Печатать стороной +Y к столу: крышка И балка начинаются на Y=gripD/2.
    There is no suspended beam beneath a closed cover surface. / Под сплошной поверхностью крышки нет подвешенной балки.
    """
    outer_y = gripD/2
    beam_front = outer_y-snapWidth
    root_left = xmax+mechanismKeepout
    root_x = root_left+snapRootLength
    end_x = root_x+snapLength
    edge_z = zc+lidWingH/2+wooFitClearance+lidBorder
    # The cover edge stays in place. Thickening the upper strip and increasing / Край крышки остаётся на месте. Утолщение верхней полосы и увеличение
    # the gap lowers the entire beam: by 1.75 mm in v1.0.18 relative to v1.0.17. / зазора опускают всю балку: в v1.0.18 на 1.75 мм относительно v1.0.17.
    beam_top = edge_z-snapEdgeRail-snapUpperGap
    root_bottom = beam_top-snapRootThickness
    tip_bottom = beam_top-snapThickness

    # One continuous U-cut leaves the original lid material as the beam. / Один непрерывный П-образный вырез оставляет исходный материал крышки в качестве балки.
    # The lower slot also provides a mechanical stop after snapFlexSpace travel. / Нижний паз также служит механическим упором после хода snapFlexSpace.
    # Exact semicircular caps, tangent to the two edges of each slot. / Точные полукруглые окончания, касательные к двум краям каждого паза.
    # The lower slot is inclined: use its NORMAL width, not the vertical gap. / Нижний паз наклонён: используем ширину по НОРМАЛИ, а не вертикальный зазор.
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
    # Use the same X clearance at the free end and behind the tooth stem. / У свободного торца и с обратной стороны стойки зуба один зазор по X.
    outer_top = (end_x+snapClearance,beam_top+snapUpperGap)
    outer_bottom = (end_x+snapClearance,tip_bottom-snapFlexSpace+slope*snapClearance)
    curves = [(top_end,outer_top),(outer_top,outer_bottom),
              (outer_bottom,lower_start),(lower_start,lower_mid,lower_end),
              (lower_end,(end_x,tip_bottom)),((end_x,tip_bottom),(end_x,beam_top)),
              ((end_x,beam_top),top_start),(top_start,top_mid,top_end)]
    # One profile defines both catches. The lower one is an exact reflection about Z=zc. / Один профиль задаёт обе защёлки. Нижняя — точное отражение относительно Z=zc.
    # When lifting the cover, the tooth ramps guide the upper beam toward -Z and the lower toward +Z. / При подъёме крышки скосы зубьев направляют верхнюю балку к -Z, нижнюю к +Z.
    base_z = edge_z-snapClearance
    peak_z = edge_z+lidGap+snapHook
    # Both catches are on the +Y side, so shift both toward -Y. / Обе защёлки находятся на стороне +Y, поэтому обе смещаем к -Y.
    # Mirroring the lower catch changes only Z; its Y depth stays the same. / Отражение нижней защёлки меняет только Z; её глубина по Y та же.
    hook_outer_y = outer_y-snapYInset
    nose_y = hook_outer_y-2*snapRampEffective-snapTipLand
    hook_profile = [(nose_y,beam_top-snapClearance),(hook_outer_y,beam_top-snapClearance),
                    (hook_outer_y,base_z),(hook_outer_y-snapRampEffective,peak_z),
                    (hook_outer_y-snapRampEffective-snapTipLand,peak_z),(nose_y,base_z)]
    notch_profile = offset_polygon(hook_profile,snapClearance)
    for sign, label in [(1,'Upper'),(-1,'Lower')]:
        def mirror_point(point):
            return (point[0],zc+sign*(point[1]-zc))
        slot_curves = [tuple(mirror_point(pt) for pt in curve) for curve in curves]
        tooth = [mirror_point(pt) for pt in hook_profile]
        receiver = [mirror_point(pt) for pt in notch_profile]
        if sign < 0:
            # Restore the original outline winding after mirroring. / После отражения возвращаем прежнее направление обхода контура.
            slot_curves = [tuple(reversed(curve)) for curve in reversed(slot_curves)]
            tooth.reverse()
            receiver.reverse()
        cover = cut(comp,cover,prism_xz(comp,slot_curves,-gripD,gripD,
                                        label+'_Through_U_release_slot'))
        za,zb = sorted([zc+sign*(beam_top-zc),zc+sign*(edge_z+snapClearance-zc)])
        # The stem spans X from end_x-snapHookLength to end_x. / Стойка занимает X от end_x-snapHookLength до end_x.
        # Expand the cut by snapClearance on BOTH sides without changing tooth size. / Расширяем вырез на snapClearance с ОБЕИХ сторон, не меняя размер зуба.
        mouth = box(comp,end_x-snapHookLength-snapClearance,end_x+snapClearance,
                    -gripD,gripD,za,zb,label+'_Edge_release_access')
        cover = cut(comp,cover,mouth)
        # Keep both ramps: insertion when closing and release when lifting with a finger. / Оба скоса сохранены: заход при закрытии и выход при подъёме пальцем.
        hook = prism_yz(comp,tooth,end_x-snapHookLength,end_x,label+'_Release_hook')
        cover = join(comp,cover,hook)
        if snapYInset > 0:
            # Extend the stem base to the +Y print plane. It remains below the seat / Низ стойки доводим до печатной плоскости +Y. Он остаётся ниже края
            # edge and does not cut the handle's outer wall. The working ramps above it / посадки и не вырезает наружную стенку ручки. Рабочие скосы над ним
            # are inset, but grow from the base during printing rather than starting in midair. / смещены вглубь, но при печати растут от основания, а не из воздуха.
            support_z0,support_z1 = sorted([zc+sign*(beam_top-snapClearance-zc),
                                           zc+sign*(base_z-zc)])
            support = box(comp,end_x-snapHookLength,end_x,nose_y,outer_y,
                          support_z0,support_z1,label+'_Hook_print_base')
            cover = join(comp,cover,support)
        # Build the socket from the inset tooth only, excluding its print base. / Гнездо строится только по смещённому зубу, без его печатного основания.
        notch = prism_yz(comp,receiver,end_x-snapHookLength-snapClearance,
                         end_x+snapClearance,label+'_Edge_hook_recess')
        handle = cut(comp,handle,notch)

    # Left tongue has a continuous 45-degree print gusset. With +Y down, / Левый язычок имеет непрерывный подкос под 45 градусов для печати. При +Y вниз
    # its projecting footprint grows one mm per mm of build height. / его выступающий контур растёт на один мм на каждый мм высоты печати.
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
    # Follow the SAME rounded wing contour as the cover, with clearance. / Повторить ТОТ ЖЕ скруглённый контур крыла крышки с зазором.
    # A rectangular strip here used to leave square ears beyond the corners. / Прямоугольная полоса здесь раньше оставляла квадратные выступы за углами.
    # Retain opening room by offsetting the rounded outline instead. / Сохранить место для открывания смещением скруглённого контура.
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
                         'hook_inset_y_mm':snapYInset,
                         'hook_front_y_mm':hook_outer_y,
                         'socket_front_skin_y_mm':max(0.0,outer_y-max(y for y,z in notch_profile)),
                         'print_face_y_mm':outer_y,
                         'latch_count':2,
                         'finger_recess_width_mm':pryWidth,
                         'slot_type':'Two mirrored through U-slots and edge hooks',
                         'release_direction':'Lift latch edge +Y; upper beam flexes -Z, lower +Z; then slide +X',
                         'planned_opening_angle_deg':lidTiltAngle}


# Create an ellipsoidal floor by scaling a sphere nonuniformly. / Эллипсоидальное дно получается неравномерным масштабированием сферы.
# The sphere and scale point are created in one component, so the axes are the handle's X/Y/Z. / Сфера и точка масштаба создаются в одном компоненте, поэтому оси — X/Y/Z ручки.
def ellipsoid_body(comp, center, rx, ry, rz, name):
    tbm = adsk.fusion.TemporaryBRepManager.get()
    # Initial sphere radius is 1 mm; scale factors are dimensionless. / Исходная сфера радиусом 1 мм; коэффициенты масштаба безразмерные.
    sphere = tbm.createSphere(p(*center),0.1)
    check(sphere is not None,'Не удалось создать сферу для ложбинки.')
    body = comp.bRepBodies.add(sphere)
    sk = sketch_plane(comp,center,(0,0,1),name+'_scale_origin')
    origin = sk.sketchPoints.add(sk.modelToSketchSpace(p(*center)))
    scales = comp.features.scaleFeatures
    inp = scales.createInput(collection([body]),origin,adsk.core.ValueInput.createByReal(1))
    check(inp.setToNonUniform(adsk.core.ValueInput.createByReal(rx),
                             adsk.core.ValueInput.createByReal(ry),
                             adsk.core.ValueInput.createByReal(rz)),
          'Не удалось задать форму ложбинки.')
    feature = scales.add(inp)
    # In Direct Design some operations modify the body without a history object. / В Direct Design некоторые операции изменяют тело без объекта истории.
    if feature is not None:
        check(feature.bodies.count == 1,'Масштабирование должно дать одно тело.')
        body = feature.bodies.item(0)
    check(body is not None and body.isValid and body.isSolid,'Не удалось получить тело ложбинки.')
    body.name = name
    sk.isVisible = False
    return body


# The scoop rises smoothly from the deep area beneath the lip to the outer skin. / Ложбинка плавно поднимается от глубокого места под полочкой к наружной коже.
# Unlike the former extruded semicircle, its floor and sides are curved. / В отличие от прежнего выдавленного полукруга, её дно и боковины криволинейные.
def finger_scoop(comp,handle,cover,wing_end,zc):
    edge_x = wing_end+wooFitClearance+lidBorder
    start_x = edge_x-pryUnderlap
    outer_y = gripD/2
    shift,rx,ry,rz,neck_half = finger_scoop_geometry()
    cy = outer_y+ry*pryBowlCenterRatio
    scoop = ellipsoid_body(comp,(start_x+shift,cy,zc),rx,ry,rz,'Finger_scoop_ellipsoid')
    # Limit the X underlap beneath the cover and the Y depth to its inner plane. / Ограничиваем заход под крышку по X и глубину её внутренней плоскостью по Y.
    # The end section now lies entirely within the seat: the flat trim leaves no / Концевое сечение теперь целиком внутри посадки: плоский срез не оставляет
    # visible step at the top or bottom. The floor stays within the cover's inner plane depth. / видимой ступеньки сверху и снизу. Дно не уходит глубже внутренней плоскости крышки.
    cover_inner_y = wooHalfDepth-lidSeatDepth+lidAxialGap
    mask = box(comp,start_x,start_x+pryLength+geometryTolerance,cover_inner_y,cy+ry+geometryTolerance,
               zc-rz-geometryTolerance,zc+rz+geometryTolerance,'Finger_scoop_limit')
    scoop = intersect(comp,scoop,mask)
    handle = cut(comp,handle,scoop)

    # The lip projects into the scoop along X but never rises above Y=gripD/2. / Полочка выступает в ложбинку по X, но никогда не поднимается выше Y=gripD/2.
    # Intersecting two rounded prisms softens the end both in plan and through its thickness. / Пересечение двух скруглённых призм смягчает торец как в плане, так и по толщине.
    xa, xb = edge_x-pryLipRoot, edge_x+pryLipProjection
    za, zb = zc-pryLipWidth/2, zc+pryLipWidth/2
    ya = outer_y-pryLipThickness
    outline = rounded_polygon([(xa,za),(xb,za),(xb,zb),(xa,zb)],[pryLipR]*4)
    lip = prism_xz(comp,outline,ya,outer_y,'Rounded_finger_lip')
    rounding = rounded_polygon([(xa,ya),(xb,ya),(xb,outer_y),(xa,outer_y)],[pryLipR]*4)
    sk = sketch_plane(comp,(0,0,za),(0,0,1),'Finger_lip_thickness_rounding')
    profile = draw_curves(sk,rounding,lambda q:(q[0],q[1],za))
    lip = intersect(comp,lip,extrude(comp,profile,pryLipWidth,'Finger_lip_rounding_tool'))
    cover = join(comp,cover,lip)
    return handle,cover,{'type':'curved ellipsoidal scoop with rounded pull lip',
                         'length_mm':pryLength,'width_mm':pryWidth,'depth_mm':pryDepth,
                         'floor_limit_y_mm':cover_inner_y,
                         'neck_width_mm':2*neck_half,'bowl_center_shift_mm':shift,
                         'lip_min_clearance_mm':pryLipMinClearance,
                         'lip_projection_mm':pryLipProjection,'lip_thickness_mm':pryLipThickness}

# TPU PADS. Copy the flat leg end after trimming at Z=0. / TPU-ПРОСТАВКИ. Копируем плоский торец ножки после обрезки на Z=0.
# Its fillets when inclined differ from those of a standard rounded rectangle. / Его скругления при наклоне не равны обычному прямоугольнику с радиусами.
def make_foot_pads(comp, handle):
    tbm = adsk.fusion.TemporaryBRepManager.get()
    feet = []
    for face in handle.faces:
        bounds = face.boundingBox
        if (abs(bounds.minPoint.z*10) < geometryTolerance and
                abs(bounds.maxPoint.z*10) < geometryTolerance and
                adsk.core.Plane.cast(face.geometry) is not None):
            feet.append(face)
    check(len(feet) == 2,'Ожидались две плоские подошвы ножек на Z=0.')
    feet.sort(key=lambda face: face.boundingBox.minPoint.x)
    pads = []
    pockets = []
    # Project both soles first. Cut the ASA later, / Сначала спроецировать обе подошвы. Вырезы в ASA делаются позже,
    # so topology changes do not invalidate references to the original faces. / чтобы изменение топологии не сделало ссылки на исходные грани невалидными.
    for face, sign, label in zip(feet,[-1,1],['Left','Right']):
        bounds = face.boundingBox
        x_center = sign*boltSpacing/2
        y_min, y_max = bounds.minPoint.y*10, bounds.maxPoint.y*10
        outer = [loop for loop in face.loops if loop.isOuter]
        check(len(outer) == 1,'У подошвы должен быть один внешний контур.')
        sk = sketch_plane(comp,(0,0,0),(0,0,1),'TPU_'+label+'_exact_footprint')
        # Unlinked projections preserve the exact lines/arcs/curves of the end face. / Несвязанные проекции сохраняют точные линии/дуги/кривые торца.
        # Do not project holes: cut M6 on the same axis and with the same diameter / Не проецируем отверстия: M6 вырезается по той же оси и диаметру,
        # as the leg hole after creating the solid pad base. / что и отверстие ножки, после создания сплошного основания проставки.
        sk.isComputeDeferred = True
        try:
            edges = [edge for edge in outer[0].edges]
            sk.project2(edges,False)
        finally:
            sk.isComputeDeferred = False
        check(sk.profiles.count == 1,'Не удалось получить замкнутый внешний контур подошвы.')
        pad = extrude(comp,sk.profiles.item(0),-padThickness,'TPU_Pad_'+label)
        sk.isVisible = False
        pad = cut(comp,pad,cylinder(comp,x_center,0,-padThickness-geometryTolerance,
                                   geometryTolerance,boltD,'TPU_'+label+'_M6'))
        key_centers = [y_min+padKeyEdgeInset+padKeyWidth/2,
                       y_max-padKeyEdgeInset-padKeyWidth/2]
        for index, yc in enumerate(key_centers,1):
            xa, xb = x_center-padKeyLength/2, x_center+padKeyLength/2
            ya, yb = yc-padKeyWidth/2, yc+padKeyWidth/2
            # A small overlap into the base ensures a reliable Join. / Небольшое перекрытие внутрь основания обеспечивает надёжное Join.
            # Above Z=0 the height remains exactly padKeyHeight. / Над Z=0 высота остаётся точно padKeyHeight.
            key = box(comp,xa,xb,ya,yb,-min(geometryTolerance,padThickness/2),
                      padKeyHeight,'TPU_'+label+'_Key_'+str(index))
            pad = join(comp,pad,key)
            gap = padKeyClearance
            pocket = box(comp,xa-gap,xb+gap,ya-gap,yb+gap,0,padKeyHeight+gap,
                         'ASA_'+label+'_Key_pocket_'+str(index))
            # Runtime check: the entire pocket is inside the leg, without breaking through a side / Проверка при запуске: весь паз внутри ножки, без выхода в боковую
            # wall, fillet, or bolt channel. API volumes are in cubic centimeters. / стенку, скругление или болтовой канал. Объёмы API выражены в см³.
            inside = tbm.copy(pocket)
            ok = tbm.booleanOperation(inside,tbm.copy(handle),
                                     adsk.fusion.BooleanTypes.IntersectionBooleanType)
            check(ok and abs(inside.volume-pocket.volume) < 1e-7,
                  'Паз TPU-проставки выходит за материал ножки; скорректируйте отступ или длину выступа.')
            pockets.append(pocket)
        pad.name = 'TPU_Pad_'+label
        pads.append(pad)
    for pocket in pockets:
        handle = cut(comp,handle,pocket)
    return handle,pads

# REPORT. Get connectivity, volume in cubic mm, and body bounds in mm. / ОТЧЁТ. Получить связность, объём в мм3 и границы тела в мм.
def report_body(body):
    bb = body.boundingBox
    return {'solid':body.isSolid,'lumps':body.lumps.count,'volume_mm3':body.volume*1000,
            'bounds_mm':[[bb.minPoint.x*10,bb.minPoint.y*10,bb.minPoint.z*10],
                         [bb.maxPoint.x*10,bb.maxPoint.y*10,bb.maxPoint.z*10]]}


# MAIN SEQUENCE. / ГЛАВНАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ.
# Fusion calls run at startup. / Fusion вызывает run при запуске.
# The stage variable stores the current step for error reporting. / Переменная stage хранит текущий этап для сообщения об ошибке.
def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    folder = os.path.dirname(os.path.abspath(__file__))
    stage = 'Validate settings'
    report = {}
    try:
        # 1. Calculate the cavity profile and validate the settings. / 1. Рассчитать профиль полости и проверить допустимость настроек.
        vertices,radii,info = woo_geometry()
        validate(info,vertices,radii)
        report['woo_profile'] = info
        report['settings'] = {k:v for k,v in globals().items() if not k.startswith('_') and isinstance(v,(int,float,bool,str))}
        report['settings'].pop('folder',None)
        # 2. Create a new document and a separate handle component. / 2. Создать новый документ и отдельный компонент ручки.
        app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.DirectDesignType
        design.unitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
        root = design.rootComponent
        # Fusion does not allow renaming the root component directly. / Fusion не позволяет напрямую переименовать корневой компонент.
        # modelName is used for the exported archive filename instead. / modelName используется для имени экспортируемого архива.
        occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        comp = occurrence.component
        comp.name = 'Handle'
        stage = 'Build handle'
        # 3. Build the handle and save a copy of its original surface. / 3. Построить ручку и сохранить копию её исходной поверхности.
        # This copy will later trim the cover to match the handle exactly. / Эта копия позже ограничит крышку, чтобы она точно повторяла ручку.
        handle = handle_blank(comp)
        # Saved pristine skin is the source for the EXACT flush cover surface. / Сохранённая исходная оболочка задаёт ТОЧНУЮ поверхность крышки заподлицо.
        skin = adsk.fusion.TemporaryBRepManager.get().copy(handle)
        stage = 'Bolt bores and head access'
        # 4. Two through-holes and head recesses with shoulder support. / 4. Два сквозных отверстия и углубления под головки с опорой shoulder.
        for sign in [-1,1]:
            handle = cut(comp,handle,cylinder(comp,sign*boltSpacing/2,0,-1,handleTop+1,boltD,'M6_bore'))
            handle = cut(comp,handle,cylinder(comp,sign*boltSpacing/2,0,shoulder,handleTop+1,headPocketD,'M6_head_access'))
        stage = 'WOO cavity and cover seat'
        # 5. The cavity opens toward +Y; an enlarged shallow seat surrounds it. / 5. Полость открывается к +Y; расширенная неглубокая посадка окружает её.
        cavity_curves = rounded_polygon(offset_polygon(vertices,wooFitClearance),[r+wooFitClearance for r in radii])
        # Open to +Y; cover closes it at Y=+wooHalfDepth. / Открыто к +Y; крышка закрывает полость на Y=+wooHalfDepth.
        handle = cut(comp,handle,prism_xz(comp,cavity_curves,-wooHalfDepth,gripD,'WOO_opening'))
        zc = handleTop-gripH/2+wooZOffset
        if enableDrainHole:
            stage = 'WOO drain hole'
            # Central vertical channel: from below the grip's lower face / Вертикальный канал по центру: от точки ниже нижней грани хвата
            # to the middle of the empty chamber. The chamber's upper wall is unaffected. / до середины пустой камеры. Верхняя стенка камеры не затрагивается.
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
        report['woo_finger_recesses'] = {'enabled':False}
        if enableWooFingerRecesses:
            stage = 'WOO finger recesses'
            # Modify only the handle: the cover retains its outline and closes both recesses. / Меняем только ручку: крышка сохраняет контур и закрывает обе выемки.
            handle,recess_info = make_woo_finger_recesses(comp,handle,cavity_curves)
            report['woo_finger_recesses'] = recess_info
        stage = 'WOO cover'
        # Cover starts deeper at the rim; WOO envelope is subtracted below. / Крышка начинается глубже у бортика; объём WOO вычитается ниже.
        # 6. Cover blank: trim to the original handle surface, / 6. Заготовка крышки: обрезать по исходной поверхности ручки,
        # then remove material from the back within the sensor's usable volume. / затем убрать с обратной стороны материал из полезного объёма датчика.
        cover = make_cover_outline(comp,vertices,radii,wooFitClearance+lidBorder,
                                   seat_y+lidAxialGap,gripD,wing_start,wing_end,zc,'Cover_stock')
        cover = intersect(comp,cover,comp.bRepBodies.add(skin))
        cover = cut(comp,cover,prism_xz(comp,cavity_curves,-gripD,wooHalfDepth,'Cover_inner_clearance'))
        stage = 'Rigid tongue and accessible release catch'
        # 7. Add cover fasteners and matching pockets in the handle. / 7. Добавить крепления крышки и соответствующие карманы в ручке.
        if enableSnapFits:
            handle,cover,lock_info = releasable_lock(comp,handle,cover,xmax,wing_end,zc,seat_y)
            report['cover_lock'] = lock_info
        stage = 'Smooth finger scoop and rounded pull lip'
        handle,cover,scoop_info = finger_scoop(comp,handle,cover,wing_end,zc)
        report['finger_access'] = scoop_info
        pad_bodies = []
        if enableFootPads:
            stage = 'TPU foot pads and matching pockets'
            handle,pad_bodies = make_foot_pads(comp,handle)
        handle.name = 'Handle'
        cover.name = 'Cover'
        stage = 'Check solids and assembled clearances'
        # 9. At runtime, check integrity, height, and part interference. / 9. При запуске проверить целостность, высоту и пересечение деталей.
        # Check the closed assembly, not the entire installation and removal path. / Проверяется закрытая сборка, а не вся траектория установки и снятия.
        report['handle'] = report_body(handle)
        report['cover'] = report_body(cover)
        report['foot_pads'] = [report_body(pad) for pad in pad_bodies]
        report['assembly_height_mm'] = handleTop+(padThickness if enableFootPads else 0)
        for body in [handle,cover]+pad_bodies:
            check(body.isSolid and body.lumps.count == 1,'Expected one connected solid per part.')
        check(abs(handle.boundingBox.maxPoint.z*10-handleTop) < geometryTolerance,'Overall height differs from handleTop.')
        check(abs(handle.boundingBox.minPoint.z*10) < geometryTolerance,'Feet do not lie at Z=0.')
        tbm = adsk.fusion.TemporaryBRepManager.get()
        overlap = tbm.copy(handle)
        ok = tbm.booleanOperation(overlap,tbm.copy(cover),adsk.fusion.BooleanTypes.IntersectionBooleanType)
        check(ok,'Could not verify cover interference.')
        report['overlap_mm3'] = overlap.volume*1000
        check(overlap.volume < 0.00001,'Cover interferes with handle; check catch relief.')
        for pad in pad_bodies:
            overlap = tbm.copy(handle)
            ok = tbm.booleanOperation(overlap,tbm.copy(pad),
                                      adsk.fusion.BooleanTypes.IntersectionBooleanType)
            check(ok and overlap.volume < 0.00001,'TPU-проставка пересекается с материалом ножки.')
            check(abs(pad.boundingBox.minPoint.z*10+padThickness) < geometryTolerance,
                  'Неверная толщина основания TPU-проставки.')
        # 10. If needed, isolate fastener samples for a test print. / 10. При необходимости выделить образцы крепления для пробной печати.
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
        # 11. Move the cover into its own component for a separate STL. / 11. Перенести крышку в свой компонент для отдельного STL.
        cover_occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        cover_occ.component.name = 'Cover'
        cover = cover.moveToComponent(cover_occ)
        # Each TPU pad is a separate body in a separate component. / Каждая TPU-проставка — отдельное тело в отдельном компоненте.
        # Moving does not change the assembly position: the TPU bottom is at Z=-padThickness. / Перенос не меняет положение сборки: низ TPU на Z=-padThickness.
        pad_components = []
        for pad in pad_bodies:
            pad_name = pad.name
            pad_occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
            pad_occ.component.name = pad_name
            pad.moveToComponent(pad_occ)
            pad_components.append((pad_occ.component,pad_name))
        for component in [comp,cover_occ.component]+[c for c,n in pad_components]:
            for sk in component.sketches:
                sk.isVisible = False
            for plane in component.constructionPlanes:
                plane.isLightBulbOn = False
        stage = 'Export'
        # 12. Save separate STL files and the complete F3D model beside the script. / 12. Сохранить отдельные STL и общую модель F3D рядом со скриптом.
        if exportFiles:
            manager = design.exportManager
            for component,name in [(comp,'Handle'),(cover_occ.component,'Cover')]+pad_components:
                opt = manager.createSTLExportOptions(component,os.path.join(folder,name+'.stl'))
                opt.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
                check(manager.execute(opt),'STL export failed: '+name)
            check(manager.execute(manager.createFusionArchiveExportOptions(os.path.join(folder,modelName+'.f3d'))),'F3D export failed.')
        # 13. Set the view, write the JSON report, and show the result. / 13. Настроить вид, записать JSON-отчёт и показать результат.
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
            ui.messageBox('The handle and cover have been created in a new document.\n'
                f'Cavity Y: {-wooHalfDepth:g} .. +{wooHalfDepth:g} mm.\n'
                f'WOO profile height: {info["height_mm"]:.3f} mm.\n'+
                ('Rigid tongue on the left, two mirrored snap catches on the right.\n'
                 'Removal: hook a finger under the rounded lip in the scoop, lift toward +Y, and slide the cover toward +X.\n'
                 'Verify the fit and removal motion with a test print.\n' if enableSnapFits
                 else 'Cover without snap catches: the seating rim is retained, but there is no locking mechanism.\n')+
                ('TPU: two pads, separate STL files TPU_Pad_Left and TPU_Pad_Right.\n' if enableFootPads else '')+
                'STL/F3D files and report: '+folder,modelName+' v'+scriptVersion)
    except Exception:
        # Save the stage and full traceback to locate the failure cause. / Сохранить этап и полный traceback, чтобы найти причину сбоя.
        report['status'] = 'FAIL'
        report['stage'] = stage
        report['error'] = traceback.format_exc()
        with open(os.path.join(folder,'build_report.json'),'w',encoding='utf-8') as stream:
            json.dump(report,stream,ensure_ascii=False,indent=2)
        ui.messageBox('Версия: '+scriptVersion+'\nОшибка на этапе: '+stage+'\n\n'+traceback.format_exc(),modelName+' v'+scriptVersion)


# Script shutdown: there are no persistent event handlers here. / Завершение скрипта: постоянных обработчиков событий здесь нет.
def stop(context):
    pass
