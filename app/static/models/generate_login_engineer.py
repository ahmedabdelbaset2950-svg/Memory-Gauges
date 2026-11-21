import base64
import json
import math
import os
import struct

OUT = os.path.join(os.path.dirname(__file__), "login-engineer.gltf")
binary = bytearray()
buffer_views = []
accessors = []
meshes = []
nodes = []
materials = []


def align4():
    while len(binary) % 4:
        binary.append(0)


def add_accessor(values, fmt, component_type, kind, target=None, bounds=False):
    align4()
    offset = len(binary)
    binary.extend(struct.pack("<" + fmt * len(values), *values))
    view = {"buffer": 0, "byteOffset": offset, "byteLength": len(binary) - offset}
    if target:
        view["target"] = target
    buffer_views.append(view)
    size = {"SCALAR": 1, "VEC3": 3, "VEC4": 4}[kind]
    accessor = {
        "bufferView": len(buffer_views) - 1,
        "componentType": component_type,
        "count": len(values) // size,
        "type": kind,
    }
    if bounds:
        chunks = [values[i:i + size] for i in range(0, len(values), size)]
        accessor["min"] = [min(v[j] for v in chunks) for j in range(size)]
        accessor["max"] = [max(v[j] for v in chunks) for j in range(size)]
    accessors.append(accessor)
    return len(accessors) - 1


def material(name, color, metallic=0.0, roughness=0.78):
    materials.append({"name": name, "pbrMetallicRoughness": {
        "baseColorFactor": [*color, 1.0],
        "metallicFactor": metallic,
        "roughnessFactor": roughness,
    }})
    return len(materials) - 1


NAVY = material("Field coveralls - deep navy", (.035, .12, .23))
BLUE = material("Coveralls panels - blue", (.075, .27, .46))
REFLECT = material("Reflective safety orange", (.96, .34, .045), .05, .43)
HELMET = material("Safety helmet - amber", (.98, .63, .08), .08, .38)
SKIN = material("Face and neck", (.60, .38, .24))
GLOVE = material("Protective gloves", (.13, .17, .19))
BOOT = material("Safety boots", (.045, .06, .075), .05, .74)
STEEL = material("Brushed steel", (.38, .52, .62), .72, .32)
DARK_STEEL = material("Dark equipment steel", (.12, .21, .29), .68, .42)
GAUGE_SCREEN = material("Gauge display", (.05, .62, .77), .22, .28)


def geometry(kind, segments=12):
    positions, normals, indices = [], [], []
    if kind == "box":
        faces = [
            ((0,0,1), [(-.5,-.5,.5),(.5,-.5,.5),(.5,.5,.5),(-.5,.5,.5)]),
            ((0,0,-1), [(.5,-.5,-.5),(-.5,-.5,-.5),(-.5,.5,-.5),(.5,.5,-.5)]),
            ((1,0,0), [(.5,-.5,.5),(.5,-.5,-.5),(.5,.5,-.5),(.5,.5,.5)]),
            ((-1,0,0), [(-.5,-.5,-.5),(-.5,-.5,.5),(-.5,.5,.5),(-.5,.5,-.5)]),
            ((0,1,0), [(-.5,.5,.5),(.5,.5,.5),(.5,.5,-.5),(-.5,.5,-.5)]),
            ((0,-1,0), [(-.5,-.5,-.5),(.5,-.5,-.5),(.5,-.5,.5),(-.5,-.5,.5)]),
        ]
        for normal, corners in faces:
            base = len(positions) // 3
            for point in corners:
                positions.extend(point)
                normals.extend(normal)
            indices.extend((base,base+1,base+2,base,base+2,base+3))
    elif kind == "cylinder":
        n = segments
        for i in range(n):
            angle = 2 * math.pi * i / n
            x, z = math.cos(angle) * .5, math.sin(angle) * .5
            positions.extend((x,-.5,z,x,.5,z))
            normals.extend((math.cos(angle),0,math.sin(angle),math.cos(angle),0,math.sin(angle)))
        for i in range(n):
            a, b = 2*i, 2*((i+1) % n)
            indices.extend((a,b,b+1,a,b+1,a+1))
        for y, normal_y in ((-.5,-1),(.5,1)):
            center = len(positions) // 3
            positions.extend((0,y,0))
            normals.extend((0,normal_y,0))
            ring = len(positions) // 3
            for i in range(n):
                angle = 2 * math.pi * i / n
                positions.extend((math.cos(angle)*.5,y,math.sin(angle)*.5))
                normals.extend((0,normal_y,0))
            for i in range(n):
                cur, nxt = ring+i, ring+(i+1) % n
                indices.extend((center,nxt,cur) if normal_y > 0 else (center,cur,nxt))
    else:
        rows, cols = 8, 12
        for row in range(rows + 1):
            phi = math.pi * row / rows
            for col in range(cols + 1):
                theta = 2 * math.pi * col / cols
                x = .5 * math.sin(phi) * math.cos(theta)
                y = .5 * math.cos(phi)
                z = .5 * math.sin(phi) * math.sin(theta)
                positions.extend((x,y,z))
                length = math.sqrt(x*x+y*y+z*z) or 1
                normals.extend((x/length,y/length,z/length))
        for row in range(rows):
            for col in range(cols):
                a = row*(cols+1)+col
                b = a+cols+1
                indices.extend((a,b,a+1,b,b+1,a+1))
    return positions, normals, indices


GEOS = {}

def add_mesh(name, kind, mat, segments=12):
    key = (kind, segments)
    if key not in GEOS:
        GEOS[key] = geometry(kind, segments)
    positions, normals, indices = GEOS[key]
    position_accessor = add_accessor(positions, "f", 5126, "VEC3", 34962, True)
    normal_accessor = add_accessor(normals, "f", 5126, "VEC3", 34962)
    index_accessor = add_accessor(indices, "H", 5123, "SCALAR", 34963)
    meshes.append({"name": name, "primitives": [{
        "attributes": {"POSITION": position_accessor, "NORMAL": normal_accessor},
        "indices": index_accessor, "material": mat, "mode": 4,
    }]})
    return len(meshes) - 1


MESH = {
    "box_navy": add_mesh("Tailored coverall segment", "box", NAVY),
    "box_blue": add_mesh("Reinforced coverall panel", "box", BLUE),
    "box_reflect": add_mesh("Reflective safety tape", "box", REFLECT),
    "cyl_navy": add_mesh("Coverall limb segment", "cylinder", NAVY),
    "cyl_blue": add_mesh("Reinforced sleeve", "cylinder", BLUE),
    "cyl_reflect": add_mesh("Reflective limb band", "cylinder", REFLECT),
    "sphere_skin": add_mesh("Head and neck form", "sphere", SKIN),
    "sphere_glove": add_mesh("Protective glove", "sphere", GLOVE),
    "sphere_helmet": add_mesh("Safety helmet shell", "sphere", HELMET),
    "box_boot": add_mesh("Steel-toe work boot", "box", BOOT),
    "cyl_steel": add_mesh("Gauge steel housing", "cylinder", STEEL, 16),
    "cyl_dark": add_mesh("Industrial fitting", "cylinder", DARK_STEEL, 12),
    "box_steel": add_mesh("Oilfield frame member", "box", STEEL),
    "box_dark": add_mesh("Oilfield structural member", "box", DARK_STEEL),
    "box_screen": add_mesh("Memory gauge readout", "box", GAUGE_SCREEN),
}


def quat_euler(euler):
    x, y, z = euler
    cx, sx = math.cos(x/2), math.sin(x/2)
    cy, sy = math.cos(y/2), math.sin(y/2)
    cz, sz = math.cos(z/2), math.sin(z/2)
    return [sx*cy*cz-cx*sy*sz, cx*sy*cz+sx*cy*sz,
            cx*cy*sz-sx*sy*cz, cx*cy*cz+sx*sy*sz]


def add_node(name, parent=None, translation=None, rotation=None, scale=None, mesh=None, extras=None):
    node = {"name": name}
    if translation is not None:
        node["translation"] = list(translation)
    if rotation is not None:
        node["rotation"] = quat_euler(rotation)
    if scale is not None:
        node["scale"] = list(scale)
    if mesh is not None:
        node["mesh"] = mesh
    if extras:
        node["extras"] = extras
    index = len(nodes)
    nodes.append(node)
    if parent is not None:
        nodes[parent].setdefault("children", []).append(index)
    return index


def part(name, parent, mesh, pos=(0,0,0), size=(1,1,1), rotation=None):
    return add_node(name, parent, pos, rotation, size, mesh)


scene_root = add_node("MGMS oilfield login scene")
worker_root = add_node("Field engineer", scene_root, (-1.02,0,0), rotation=(0,.55,0))
pelvis = add_node("Bone_Pelvis", worker_root, (0,1.00,0), extras={"bone": True})
part("Utility belt and pelvis", pelvis, MESH["box_navy"], (0,0,0), (.36,.20,.25))
part("Belt buckle", pelvis, MESH["box_reflect"], (0,.025,.132), (.07,.055,.018))
spine = add_node("Bone_Spine", pelvis, (0,.06,0), extras={"bone": True})
part("Navy field coverall torso", spine, MESH["box_navy"], (0,.235,0), (.42,.49,.28))
part("Chest reinforced panel", spine, MESH["box_blue"], (0,.27,.145), (.32,.25,.018))
part("Chest reflective band upper", spine, MESH["box_reflect"], (0,.345,.157), (.39,.035,.018))
part("Chest reflective band lower", spine, MESH["box_reflect"], (0,.12,.157), (.39,.035,.018))
part("Back reflective safety band", spine, MESH["box_reflect"], (0,.345,-.15), (.39,.035,.018))
neck = add_node("Bone_Neck", spine, (0,.48,0), extras={"bone": True})
part("Engineer neck", neck, MESH["sphere_skin"], (0,.035,0), (.12,.13,.12))
head = add_node("Bone_Head", neck, (0,.10,0), extras={"bone": True})
part("Engineer head", head, MESH["sphere_skin"], (0,.045,.02), (.25,.32,.23))
part("Safety helmet crown", head, MESH["sphere_helmet"], (0,.205,0), (.32,.18,.29))
part("Safety helmet brim", head, MESH["box_reflect"], (0,.145,.07), (.40,.025,.28))
part("Helmet front lamp", head, MESH["box_screen"], (0,.18,.145), (.07,.045,.025))

bones = {"spine": spine, "head": head}
for side, sign in (("L",-1),("R",1)):
    shoulder = add_node(f"Bone_Shoulder_{side}", spine, (sign*.24,.39,0), extras={"bone": True})
    upper = add_node(f"Bone_UpperArm_{side}", shoulder, (sign*.01,-.045,0), extras={"bone": True})
    elbow = add_node(f"Bone_Forearm_{side}", upper, (0,-.34,0), extras={"bone": True})
    hand = add_node(f"Bone_Hand_{side}", elbow, (0,-.30,.015), extras={"bone": True})
    bones[f"upper_{side}"] = upper
    bones[f"fore_{side}"] = elbow
    bones[f"hand_{side}"] = hand
    part(f"Shoulder guard {side}", shoulder, MESH["sphere_glove"], (sign*.015,0,0), (.19,.18,.20))
    part(f"Upper coverall sleeve {side}", upper, MESH["cyl_blue"], (0,-.17,0), (.14,.37,.14))
    part(f"Upper sleeve reflective strip {side}", upper, MESH["cyl_reflect"], (0,-.27,0), (.147,.045,.147))
    part(f"Forearm coverall {side}", elbow, MESH["cyl_navy"], (0,-.155,0), (.12,.33,.12))
    part(f"Wrist reflective strip {side}", elbow, MESH["cyl_reflect"], (0,-.275,0), (.125,.035,.125))
    part(f"Protective glove {side}", hand, MESH["sphere_glove"], (0,-.035,.015), (.105,.12,.10))

for side, sign in (("L",-1),("R",1)):
    thigh = add_node(f"Bone_Thigh_{side}", pelvis, (sign*.12,-.07,0), extras={"bone": True})
    knee = add_node(f"Bone_Knee_{side}", thigh, (0,-.39,0), extras={"bone": True})
    ankle = add_node(f"Bone_Ankle_{side}", knee, (0,-.37,.015), extras={"bone": True})
    bones[f"thigh_{side}"] = thigh
    bones[f"knee_{side}"] = knee
    part(f"Trousers upper leg {side}", thigh, MESH["cyl_navy"], (0,-.205,0), (.19,.43,.22))
    part(f"Knee reinforcement {side}", knee, MESH["box_blue"], (0,-.035,.055), (.17,.13,.12))
    part(f"Trousers lower leg {side}", knee, MESH["cyl_navy"], (0,-.19,0), (.15,.38,.17))
    part(f"Lower leg reflective tape {side}", knee, MESH["cyl_reflect"], (0,-.27,0), (.16,.04,.18))
    part(f"Oilfield safety boot {side}", ankle, MESH["box_boot"], (0,-.045,.075), (.18,.14,.31))
    part(f"Boot toe cap {side}", ankle, MESH["box_steel"], (0,-.02,.16), (.13,.07,.08))

gauge = add_node("Memory Gauge assembly", scene_root, (.42,.51,.02))
part("Gauge body", gauge, MESH["cyl_steel"], (0,0,0), (.24,.70,.24))
part("Gauge lower collar", gauge, MESH["cyl_dark"], (0,-.30,0), (.30,.10,.30))
part("Gauge upper collar", gauge, MESH["cyl_dark"], (0,.31,0), (.29,.09,.29))
part("Gauge sensor cap", gauge, MESH["cyl_steel"], (0,.40,0), (.18,.12,.18))
part("Gauge status display", gauge, MESH["box_screen"], (0,.04,.124), (.12,.13,.025))
part("Gauge stand", scene_root, MESH["box_dark"], (.42,.10,.02), (.54,.16,.50))
part("Gauge stand foot", scene_root, MESH["box_steel"], (.42,.015,.02), (.72,.05,.62))
for x, height in ((1.85,2.35),(2.38,2.0)):
    tower = add_node("Drilling rig mast", scene_root, (x,height/2,-.60))
    part("Mast left rail", tower, MESH["box_steel"], (-.16,0,0), (.055,height,.055))
    part("Mast right rail", tower, MESH["box_steel"], (.16,0,0), (.055,height,.055))
    part("Mast cross brace", tower, MESH["box_dark"], (0,0,0), (.38,.045,.045))
    for y in (-.38,0,.38):
        brace = add_node("Diagonal rig brace", tower, (0,y,0))
        part("Steel diagonal", brace, MESH["box_steel"], (0,0,0), (.43,.035,.035), (0,0,math.pi/4))
pipes = add_node("Ground pipe rack", scene_root, (1.45,.17,.48))
for index in range(4):
    part(f"Parallel steel pipe {index+1}", pipes, MESH["cyl_steel"], (index*.12,0,0), (.075,1.0,.075), (0,0,math.pi/2))


def quat_x(angle):
    return [math.sin(angle/2),0,0,math.cos(angle/2)]


def add_animation(name, tracks):
    samplers, channels = [], []
    for key, values in tracks.items():
        node_index = bones[key] if key in bones else worker_root if key == "worker" else None
        if node_index is None:
            continue
        values = sorted(values, key=lambda item: item[0])
        path = "translation" if key == "worker" else "rotation"
        input_accessor = add_accessor([t for t,_ in values], "f", 5126, "SCALAR", bounds=True)
        output = []
        for _, value in values:
            output.extend(value if path == "translation" else quat_x(value))
        output_accessor = add_accessor(output, "f", 5126, "VEC3" if path == "translation" else "VEC4")
        samplers.append({"input": input_accessor, "output": output_accessor, "interpolation": "LINEAR"})
        channels.append({"sampler": len(samplers)-1, "target": {"node": node_index, "path": path}})
    return {"name": name, "samplers": samplers, "channels": channels}


walk = {
    "worker": [(0,(-1.02,0,0)),(.6,(-.84,0,0)),(1.2,(-.63,0,0)),(1.8,(-.49,0,0)),(2.4,(-.49,0,0))],
    "spine": [(0,0),(.6,.04),(1.2,-.02),(1.8,0),(2.4,0)],
    "upper_L": [(0,-.30),(.6,.42),(1.2,-.35),(1.8,.32),(2.4,-.30)],
    "upper_R": [(0,.30),(.6,-.38),(1.2,.34),(1.8,-.34),(2.4,.30)],
    "fore_L": [(0,-.10),(.6,-.22),(1.2,.14),(1.8,-.16),(2.4,-.10)],
    "fore_R": [(0,.10),(.6,.18),(1.2,-.12),(1.8,.16),(2.4,.10)],
    "thigh_L": [(0,-.42),(.6,.43),(1.2,-.42),(1.8,.43),(2.4,-.42)],
    "thigh_R": [(0,.42),(.6,-.43),(1.2,.42),(1.8,-.43),(2.4,.42)],
    "knee_L": [(0,.62),(.6,.10),(1.2,.62),(1.8,.10),(2.4,.62)],
    "knee_R": [(0,.10),(.6,.62),(1.2,.10),(1.8,.62),(2.4,.10)],
}
inspect = {
    "worker": [(0,(-.49,0,0)),(5.0,(-.49,0,0))],
    "spine": [(0,0),(.8,.30),(1.4,.34),(2.0,.30),(3.8,.30),(4.5,.05),(5.0,0)],
    "head": [(0,0),(.8,.10),(1.4,.13),(2.2,.12),(3.8,.12),(4.5,.02),(5.0,0)],
    "upper_L": [(0,-.30),(.8,-.55),(1.4,-.82),(2.2,-.76),(2.55,-.84),(2.9,-.72),(3.8,-.78),(4.5,-.22),(5.0,-.30)],
    "fore_L": [(0,-.10),(.8,-.18),(1.4,-.10),(2.2,-.02),(2.55,-.26),(2.9,-.02),(3.8,-.10),(4.5,-.10),(5.0,-.10)],
    "hand_L": [(0,0),(.8,0),(1.4,-.06),(2.2,.02),(2.55,-.08),(2.9,.05),(3.8,0),(4.5,0),(5.0,0)],
    "upper_R": [(0,.30),(.8,-.10),(1.4,-.45),(2.2,-.45),(3.8,-.45),(4.5,.18),(5.0,.30)],
    "fore_R": [(0,.10),(.8,.05),(1.4,-.12),(2.2,-.12),(3.8,-.12),(4.5,.10),(5.0,.10)],
    "thigh_R": [(0,0),(.8,-.50),(1.4,-.88),(2.2,-.88),(3.8,-.88),(4.5,-.16),(5.0,0)],
    "knee_R": [(0,0),(.8,1.05),(1.4,1.45),(2.2,1.45),(3.8,1.45),(4.5,.08),(5.0,0)],
    "thigh_L": [(0,0),(.8,.18),(1.4,.08),(2.2,.08),(3.8,.08),(4.5,0),(5.0,0)],
    "knee_L": [(0,0),(.8,.02),(1.4,.10),(2.2,.10),(3.8,.10),(4.5,0),(5.0,0)],
}
stand = {
    "worker": [(0,(-.49,0,0)),(1.4,(-.49,0,0))],
    "spine": [(0,0),(.7,.025),(1.4,0)],
    "upper_L": [(0,-.3),(.7,-.34),(1.4,-.3)],
    "upper_R": [(0,.3),(.7,.34),(1.4,.3)],
    "thigh_L": [(0,0),(.7,.03),(1.4,0)],
    "thigh_R": [(0,0),(.7,-.03),(1.4,0)],
}
animations = [add_animation("Walk to equipment", walk),
              add_animation("Kneel, inspect and rise", inspect),
              add_animation("Standing inspection idle", stand)]
align4()
model = {
    "asset": {"version": "2.0", "generator": "MGMS original procedural oilfield engineer"},
    "scene": 0,
    "scenes": [{"name": "MGMS oilfield inspection", "nodes": [scene_root]}],
    "nodes": nodes,
    "meshes": meshes,
    "materials": materials,
    "buffers": [{"uri": "data:application/octet-stream;base64," + base64.b64encode(binary).decode("ascii"), "byteLength": len(binary)}],
    "bufferViews": buffer_views,
    "accessors": accessors,
    "animations": animations,
}
with open(OUT, "w", encoding="utf-8") as file:
    json.dump(model, file, separators=(",", ":"))
print(f"Wrote {OUT} ({os.path.getsize(OUT)} bytes, {len(nodes)} nodes, {len(meshes)} meshes, {len(animations)} clips)")
