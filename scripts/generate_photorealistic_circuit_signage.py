"""
generate_photorealistic_circuit_signage.py
Engineered with Blender 3.6 LTS Headless CLI for AAA Photorealism & 60-120 FPS Performance.

Creates pristine, perfectly centered, photorealistic circuit signage:
1. Brake Markers (200m, 150m, 100m, 50m):
   - Centered at (0, 0, 0) with ZERO artificial offsets.
   - Front display face points towards -Z in Three.js (glTF coordinate system).
   - Molded aerodynamic composite housing, chamfered frame, rear stiffener ribs.
   - Dual FIA breakaway safety posts with rubber bellows at base.
   - Steel anchor baseplate with hex foundation bolts.
   - Recessed front display panel with crisp PBR textures.
   - Clean UV mapping (front face mapped cleanly, rear face with carbon backing).

2. Turn Sign Gantries (Turn 1, Turn 2, Turn 3, Turn 4):
   - Centered at (0, 0, 0) with ZERO artificial offsets.
   - Front display face points towards -Z in Three.js.
   - Twin tubular steel pylons with cross-bracing struts.
   - Dual concrete foundation pedestals with anchor plates.
   - Cantilevered aerodynamic cassette housing with top visor cowl.
   - Overhead LED downlight floodlight bar.
   - Front display face with authentic FIA circuit sector graphics.

3. Sponsor Billboards:
   - Centered at (0, 0, 0).
   - Front display face points towards -Z in Three.js.
   - Heavy-duty cantilevered upright pylons with Armco barrier clamps.
   - Rear horizontal box trusses and diagonal support gussets.
   - Composite backing panel with steel beveled trim.
   - High-resolution sponsor livery.
"""

import bpy
import bmesh
import math
import os

OUTPUT_MODELS_DIR = "/app/applet/public/models"
TEXTURES_DIR = "/app/applet/public/textures/signage"
os.makedirs(OUTPUT_MODELS_DIR, exist_ok=True)
os.makedirs(TEXTURES_DIR, exist_ok=True)

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh, do_unlink=True)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat, do_unlink=True)
    for img in list(bpy.data.images):
        bpy.data.images.remove(img, do_unlink=True)

def create_pbr_material(name, base_color=(0.5, 0.5, 0.5), metallic=0.0, roughness=0.5, image_path=None, emissive_strength=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out_node = nodes.new(type='ShaderNodeOutputMaterial')
    out_node.location = (400, 0)

    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness

    if image_path and os.path.exists(image_path):
        tex_img = bpy.data.images.load(image_path)
        img_node = nodes.new(type='ShaderNodeTexImage')
        img_node.location = (-300, 0)
        img_node.image = tex_img
        links.new(img_node.outputs['Color'], bsdf.inputs['Base Color'])
        if emissive_strength > 0:
            if 'Emission Color' in bsdf.inputs:
                links.new(img_node.outputs['Color'], bsdf.inputs['Emission Color'])
            elif 'Emission' in bsdf.inputs:
                links.new(img_node.outputs['Color'], bsdf.inputs['Emission'])
            if 'Emission Strength' in bsdf.inputs:
                bsdf.inputs['Emission Strength'].default_value = emissive_strength
    else:
        bsdf.inputs['Base Color'].default_value = (*base_color, 1.0)

    links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])
    return mat

def add_box(name, sx, sy, sz, x=0, y=0, z=0, rx=0, ry=0, rz=0, mat=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z), rotation=(rx, ry, rz))
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        obj.data.materials.append(mat)
    return obj

def add_cylinder(name, radius, height, segs, x=0, y=0, z=0, rx=0, ry=0, rz=0, mat=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=segs, radius=radius, depth=height, location=(x, y, z), rotation=(rx, ry, rz))
    obj = bpy.context.active_object
    obj.name = name
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        obj.data.materials.append(mat)
    return obj

# =============================================================================
# 1. BRAKE MARKERS (Export individual variants centered at 0, 0, 0)
# =============================================================================
def build_brake_marker_variant(dist_label):
    reset_scene()

    mat_galvanized = create_pbr_material("MatMarkerGalvSteel", (0.55, 0.58, 0.62), metallic=0.85, roughness=0.32)
    mat_steel_dark = create_pbr_material("MatMarkerDarkSteel", (0.12, 0.14, 0.18), metallic=0.80, roughness=0.40)
    mat_rubber = create_pbr_material("MatMarkerBreakawayRubber", (0.08, 0.08, 0.09), metallic=0.05, roughness=0.85)
    mat_composite = create_pbr_material("MatMarkerCompositeHousing", (0.16, 0.18, 0.22), metallic=0.25, roughness=0.45)
    mat_hazard = create_pbr_material("MatMarkerSafetyYellow", (0.95, 0.80, 0.10), metallic=0.10, roughness=0.35)

    tex_path = f"/app/applet/public/textures/signage/brake_marker_{dist_label}.png"
    mat_face = create_pbr_material(f"MatBrakeFace_{dist_label}", image_path=tex_path, roughness=0.25)

    root_empty = bpy.data.objects.new(f"BrakeMarker_{dist_label}", None)
    root_empty.location = (0, 0, 0)
    bpy.context.collection.objects.link(root_empty)

    objs = []

    # Ground Anchor Foundation Baseplate (Z = 0.02)
    base_plate = add_box("Baseplate", 1.40, 0.50, 0.04, 0, 0, 0.02, mat=mat_steel_dark)
    objs.append(base_plate)

    # 4 Foundation Hex Anchor Bolts
    for bx, by in [(-0.55, -0.16), (0.55, -0.16), (-0.55, 0.16), (0.55, 0.16)]:
        bolt = add_cylinder(f"Bolt_{bx}_{by}", 0.022, 0.05, 6, bx, by, 0.045, mat=mat_galvanized)
        objs.append(bolt)

    # Dual FIA Breakaway Posts (Left and Right)
    for px in [-0.42, 0.42]:
        boot = add_cylinder(f"BreakawayBoot_{px}", 0.055, 0.18, 10, px, 0, 0.13, mat=mat_rubber)
        post = add_cylinder(f"SupportPost_{px}", 0.040, 1.25, 8, px, 0, 0.76, mat=mat_galvanized)
        clamp_b = add_box(f"MountClamp_{px}", 0.11, 0.14, 0.10, px, 0, 1.25, mat=mat_steel_dark)
        objs.extend([boot, post, clamp_b])

    # Molded Aerodynamic Composite Board Housing
    # Center height: Z = 1.35m
    BOARD_Z = 1.35
    housing = add_box("BoardHousing", 1.55, 0.08, 1.15, 0, 0.04, BOARD_Z, mat=mat_composite)
    objs.append(housing)

    # Rear horizontal and vertical stiffener ribs
    rib_horiz_top = add_box("RibHorizTop", 1.48, 0.05, 0.04, 0, -0.015, BOARD_Z + 0.38, mat=mat_composite)
    rib_horiz_bot = add_box("RibHorizBot", 1.48, 0.05, 0.04, 0, -0.015, BOARD_Z - 0.38, mat=mat_composite)
    rib_vert_center = add_box("RibVertCenter", 0.04, 0.05, 1.05, 0, -0.015, BOARD_Z, mat=mat_composite)
    objs.extend([rib_horiz_top, rib_horiz_bot, rib_vert_center])

    # Outer safety yellow perimeter bezel frame
    bezel_top = add_box("BezelTop", 1.57, 0.04, 0.04, 0, 0.09, BOARD_Z + 0.57, mat=mat_hazard)
    bezel_bot = add_box("BezelBot", 1.57, 0.04, 0.04, 0, 0.09, BOARD_Z - 0.57, mat=mat_hazard)
    bezel_left = add_box("BezelLeft", 0.04, 0.04, 1.15, -0.77, 0.09, BOARD_Z, mat=mat_hazard)
    bezel_right = add_box("BezelRight", 0.04, 0.04, 1.15, 0.77, 0.09, BOARD_Z, mat=mat_hazard)
    objs.extend([bezel_top, bezel_bot, bezel_left, bezel_right])

    # Recessed Display Face
    # In Blender: Front face normal points in +Y (+Y in Blender -> -Z in glTF/Three.js)
    face = add_box("DisplayFace", 1.46, 0.02, 1.06, 0, 0.088, BOARD_Z, mat=mat_face)
    mesh = face.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    uv_layer = bm.loops.layers.uv.verify()
    for face_elem in bm.faces:
        # Front face (+Y): correctly mapped
        if face_elem.normal.y > 0.5:
            for loop in face_elem.loops:
                vx = loop.vert.co.x / 1.46 + 0.5
                vz = (loop.vert.co.z - (BOARD_Z - 0.53)) / 1.06
                loop[uv_layer].uv = (vx, vz)
        elif face_elem.normal.y < -0.5:
            # Back face (-Y)
            for loop in face_elem.loops:
                vx = 1.0 - (loop.vert.co.x / 1.46 + 0.5)
                vz = (loop.vert.co.z - (BOARD_Z - 0.53)) / 1.06
                loop[uv_layer].uv = (vx, vz)
        else:
            for loop in face_elem.loops:
                loop[uv_layer].uv = (0.01, 0.01)
    bm.to_mesh(mesh)
    bm.free()
    objs.append(face)

    # Parent all objects cleanly to root_empty preserving world location
    for obj in objs:
        obj.parent = root_empty
        obj.matrix_parent_inverse = root_empty.matrix_world.inverted()
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth()
        if hasattr(obj.data, "use_auto_smooth"):
            obj.data.use_auto_smooth = True
            obj.data.auto_smooth_angle = math.radians(35)

    out_file = f"/app/applet/public/models/photorealistic_brake_marker_{dist_label}.glb"
    bpy.ops.export_scene.gltf(
        filepath=out_file,
        export_format='GLB',
        use_selection=False,
        export_yup=True,
        export_materials='EXPORT',
        export_colors=True
    )
    print(f"Exported {out_file}")

# Also build the unified master brake markers GLB containing all 4 variants at origin (0, 0, 0)
def build_all_brake_markers_master():
    reset_scene()
    distances = ["200", "150", "100", "50"]

    mat_galvanized = create_pbr_material("MatMarkerGalvSteel", (0.55, 0.58, 0.62), metallic=0.85, roughness=0.32)
    mat_steel_dark = create_pbr_material("MatMarkerDarkSteel", (0.12, 0.14, 0.18), metallic=0.80, roughness=0.40)
    mat_rubber = create_pbr_material("MatMarkerBreakawayRubber", (0.08, 0.08, 0.09), metallic=0.05, roughness=0.85)
    mat_composite = create_pbr_material("MatMarkerCompositeHousing", (0.16, 0.18, 0.22), metallic=0.25, roughness=0.45)
    mat_hazard = create_pbr_material("MatMarkerSafetyYellow", (0.95, 0.80, 0.10), metallic=0.10, roughness=0.35)

    BOARD_Z = 1.35

    for dist in distances:
        tex_path = f"/app/applet/public/textures/signage/brake_marker_{dist}.png"
        mat_face = create_pbr_material(f"MatBrakeFace_{dist}", image_path=tex_path, roughness=0.25)

        variant_group = bpy.data.objects.new(f"BrakeMarker_{dist}", None)
        variant_group.location = (0, 0, 0)
        bpy.context.collection.objects.link(variant_group)

        objs = []
        base_plate = add_box(f"Baseplate_{dist}", 1.40, 0.50, 0.04, 0, 0, 0.02, mat=mat_steel_dark)
        objs.append(base_plate)

        for bx, by in [(-0.55, -0.16), (0.55, -0.16), (-0.55, 0.16), (0.55, 0.16)]:
            bolt = add_cylinder(f"Bolt_{dist}_{bx}_{by}", 0.022, 0.05, 6, bx, by, 0.045, mat=mat_galvanized)
            objs.append(bolt)

        for px in [-0.42, 0.42]:
            boot = add_cylinder(f"BreakawayBoot_{dist}_{px}", 0.055, 0.18, 10, px, 0, 0.13, mat=mat_rubber)
            post = add_cylinder(f"SupportPost_{dist}_{px}", 0.040, 1.25, 8, px, 0, 0.76, mat=mat_galvanized)
            clamp_b = add_box(f"MountClamp_{dist}_{px}", 0.11, 0.14, 0.10, px, 0, 1.25, mat=mat_steel_dark)
            objs.extend([boot, post, clamp_b])

        housing = add_box(f"BoardHousing_{dist}", 1.55, 0.08, 1.15, 0, 0.04, BOARD_Z, mat=mat_composite)
        rib_horiz_top = add_box(f"RibHorizTop_{dist}", 1.48, 0.05, 0.04, 0, -0.015, BOARD_Z + 0.38, mat=mat_composite)
        rib_horiz_bot = add_box(f"RibHorizBot_{dist}", 1.48, 0.05, 0.04, 0, -0.015, BOARD_Z - 0.38, mat=mat_composite)
        rib_vert_center = add_box(f"RibVertCenter_{dist}", 0.04, 0.05, 1.05, 0, -0.015, BOARD_Z, mat=mat_composite)
        objs.extend([housing, rib_horiz_top, rib_horiz_bot, rib_vert_center])

        bezel_top = add_box(f"BezelTop_{dist}", 1.57, 0.04, 0.04, 0, 0.09, BOARD_Z + 0.57, mat=mat_hazard)
        bezel_bot = add_box(f"BezelBot_{dist}", 1.57, 0.04, 0.04, 0, 0.09, BOARD_Z - 0.57, mat=mat_hazard)
        bezel_left = add_box(f"BezelLeft_{dist}", 0.04, 0.04, 1.15, -0.77, 0.09, BOARD_Z, mat=mat_hazard)
        bezel_right = add_box(f"BezelRight_{dist}", 0.04, 0.04, 1.15, 0.77, 0.09, BOARD_Z, mat=mat_hazard)
        objs.extend([bezel_top, bezel_bot, bezel_left, bezel_right])

        face = add_box(f"DisplayFace_{dist}", 1.46, 0.02, 1.06, 0, 0.088, BOARD_Z, mat=mat_face)
        mesh = face.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        uv_layer = bm.loops.layers.uv.verify()
        for face_elem in bm.faces:
            if face_elem.normal.y > 0.5:
                for loop in face_elem.loops:
                    vx = loop.vert.co.x / 1.46 + 0.5
                    vz = (loop.vert.co.z - (BOARD_Z - 0.53)) / 1.06
                    loop[uv_layer].uv = (vx, vz)
            elif face_elem.normal.y < -0.5:
                for loop in face_elem.loops:
                    vx = 1.0 - (loop.vert.co.x / 1.46 + 0.5)
                    vz = (loop.vert.co.z - (BOARD_Z - 0.53)) / 1.06
                    loop[uv_layer].uv = (vx, vz)
            else:
                for loop in face_elem.loops:
                    loop[uv_layer].uv = (0.01, 0.01)
        bm.to_mesh(mesh)
        bm.free()
        objs.append(face)

        for obj in objs:
            obj.parent = variant_group
            obj.matrix_parent_inverse = variant_group.matrix_world.inverted()
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.shade_smooth()
            if hasattr(obj.data, "use_auto_smooth"):
                obj.data.use_auto_smooth = True
                obj.data.auto_smooth_angle = math.radians(35)

    out_file = "/app/applet/public/models/photorealistic_brake_markers.glb"
    bpy.ops.export_scene.gltf(
        filepath=out_file,
        export_format='GLB',
        use_selection=False,
        export_yup=True,
        export_materials='EXPORT',
        export_colors=True
    )
    print(f"Exported master Brake Markers to: {out_file}")

# =============================================================================
# 2. TURN SIGN GANTRIES (Turn 1, 2, 3, 4 centered at 0, 0, 0)
# =============================================================================
def build_turn_sign_variant(t_num):
    reset_scene()

    mat_concrete = create_pbr_material("MatGantryConcrete", (0.35, 0.36, 0.38), metallic=0.05, roughness=0.85)
    mat_galvanized = create_pbr_material("MatGantryGalvSteel", (0.55, 0.58, 0.62), metallic=0.82, roughness=0.35)
    mat_steel_dark = create_pbr_material("MatGantryDarkSteel", (0.12, 0.14, 0.17), metallic=0.85, roughness=0.35)
    mat_cassette = create_pbr_material("MatGantryCassetteHousing", (0.18, 0.20, 0.24), metallic=0.45, roughness=0.35)
    mat_floodlight_led = create_pbr_material("MatGantryLedLight", (0.95, 0.98, 1.0), metallic=0.1, roughness=0.1, emissive_strength=6.0)

    tex_path = f"/app/applet/public/textures/signage/turn_sign_{t_num}.png"
    mat_face = create_pbr_material(f"MatTurnFace_{t_num}", image_path=tex_path, roughness=0.22, emissive_strength=0.8)

    root_empty = bpy.data.objects.new(f"TurnSign_{t_num}", None)
    root_empty.location = (0, 0, 0)
    bpy.context.collection.objects.link(root_empty)

    objs = []

    # Dual Concrete Pedestals & Baseplates (X = -1.10 and +1.10)
    for px in [-1.10, 1.10]:
        ped = add_box(f"Pedestal_{px}", 0.55, 0.55, 0.35, px, 0, 0.175, mat=mat_concrete)
        plate = add_box(f"Plate_{px}", 0.44, 0.44, 0.04, px, 0, 0.37, mat=mat_steel_dark)
        col = add_cylinder(f"Column_{px}", 0.065, 2.80, 10, px, 0, 1.77, mat=mat_galvanized)
        objs.extend([ped, plate, col])

    # Cross-bracing struts between columns
    strut1 = add_cylinder("GantryStrut1", 0.035, 2.20, 8, 0, 0, 1.05, ry=math.pi/2, mat=mat_steel_dark)
    strut2 = add_cylinder("GantryStrut2", 0.035, 2.20, 8, 0, 0, 1.95, ry=math.pi/2, mat=mat_steel_dark)
    objs.extend([strut1, strut2])

    SIGN_Z = 2.45
    cassette = add_box("SignCassette", 2.75, 0.12, 1.45, 0, 0.08, SIGN_Z, mat=mat_cassette)
    visor = add_box("VisorCowl", 2.82, 0.22, 0.06, 0, 0.16, SIGN_Z + 0.74, rx=-math.radians(12), mat=mat_steel_dark)
    objs.extend([cassette, visor])

    rear_clamp_l = add_box("RearClampL", 0.14, 0.16, 1.10, -1.10, 0, SIGN_Z, mat=mat_steel_dark)
    rear_clamp_r = add_box("RearClampR", 0.14, 0.16, 1.10, 1.10, 0, SIGN_Z, mat=mat_steel_dark)
    objs.extend([rear_clamp_l, rear_clamp_r])

    # Overhead LED Downlight Floodlight Bar
    flood_arm_l = add_cylinder("FloodArmL", 0.025, 0.45, 6, -0.90, 0.28, SIGN_Z + 0.85, rx=math.radians(35), mat=mat_galvanized)
    flood_arm_r = add_cylinder("FloodArmR", 0.025, 0.45, 6, 0.90, 0.28, SIGN_Z + 0.85, rx=math.radians(35), mat=mat_galvanized)
    flood_bar = add_box("FloodlightBar", 2.40, 0.08, 0.06, 0, 0.42, SIGN_Z + 0.95, mat=mat_steel_dark)
    flood_led = add_box("FloodlightLed", 2.30, 0.04, 0.02, 0, 0.42, SIGN_Z + 0.92, mat=mat_floodlight_led)
    objs.extend([flood_arm_l, flood_arm_r, flood_bar, flood_led])

    # Front Display Face (+Y in Blender -> -Z in glTF/Three.js)
    face = add_box("TurnDisplayFace", 2.65, 0.02, 1.35, 0, 0.142, SIGN_Z, mat=mat_face)
    mesh = face.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    uv_layer = bm.loops.layers.uv.verify()
    for face_elem in bm.faces:
        if face_elem.normal.y > 0.5:
            for loop in face_elem.loops:
                vx = loop.vert.co.x / 2.65 + 0.5
                vz = (loop.vert.co.z - (SIGN_Z - 0.675)) / 1.35
                loop[uv_layer].uv = (vx, vz)
        elif face_elem.normal.y < -0.5:
            for loop in face_elem.loops:
                vx = 1.0 - (loop.vert.co.x / 2.65 + 0.5)
                vz = (loop.vert.co.z - (SIGN_Z - 0.675)) / 1.35
                loop[uv_layer].uv = (vx, vz)
        else:
            for loop in face_elem.loops:
                loop[uv_layer].uv = (0.01, 0.01)
    bm.to_mesh(mesh)
    bm.free()
    objs.append(face)

    for obj in objs:
        obj.parent = root_empty
        obj.matrix_parent_inverse = root_empty.matrix_world.inverted()
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth()
        if hasattr(obj.data, "use_auto_smooth"):
            obj.data.use_auto_smooth = True
            obj.data.auto_smooth_angle = math.radians(35)

    out_file = f"/app/applet/public/models/photorealistic_turn_sign_{t_num}.glb"
    bpy.ops.export_scene.gltf(
        filepath=out_file,
        export_format='GLB',
        use_selection=False,
        export_yup=True,
        export_materials='EXPORT',
        export_colors=True
    )
    print(f"Exported {out_file}")

def build_all_turn_signs_master():
    reset_scene()
    turn_ids = [1, 2, 3, 4]

    mat_concrete = create_pbr_material("MatGantryConcrete", (0.35, 0.36, 0.38), metallic=0.05, roughness=0.85)
    mat_galvanized = create_pbr_material("MatGantryGalvSteel", (0.55, 0.58, 0.62), metallic=0.82, roughness=0.35)
    mat_steel_dark = create_pbr_material("MatGantryDarkSteel", (0.12, 0.14, 0.17), metallic=0.85, roughness=0.35)
    mat_cassette = create_pbr_material("MatGantryCassetteHousing", (0.18, 0.20, 0.24), metallic=0.45, roughness=0.35)
    mat_floodlight_led = create_pbr_material("MatGantryLedLight", (0.95, 0.98, 1.0), metallic=0.1, roughness=0.1, emissive_strength=6.0)

    SIGN_Z = 2.45

    for t_num in turn_ids:
        tex_path = f"/app/applet/public/textures/signage/turn_sign_{t_num}.png"
        mat_face = create_pbr_material(f"MatTurnFace_{t_num}", image_path=tex_path, roughness=0.22, emissive_strength=0.8)

        variant_group = bpy.data.objects.new(f"TurnSign_{t_num}", None)
        variant_group.location = (0, 0, 0)
        bpy.context.collection.objects.link(variant_group)

        objs = []
        for px in [-1.10, 1.10]:
            ped = add_box(f"Pedestal_{t_num}_{px}", 0.55, 0.55, 0.35, px, 0, 0.175, mat=mat_concrete)
            plate = add_box(f"Plate_{t_num}_{px}", 0.44, 0.44, 0.04, px, 0, 0.37, mat=mat_steel_dark)
            col = add_cylinder(f"Column_{t_num}_{px}", 0.065, 2.80, 10, px, 0, 1.77, mat=mat_galvanized)
            objs.extend([ped, plate, col])

        strut1 = add_cylinder(f"GantryStrut1_{t_num}", 0.035, 2.20, 8, 0, 0, 1.05, ry=math.pi/2, mat=mat_steel_dark)
        strut2 = add_cylinder(f"GantryStrut2_{t_num}", 0.035, 2.20, 8, 0, 0, 1.95, ry=math.pi/2, mat=mat_steel_dark)
        objs.extend([strut1, strut2])

        cassette = add_box(f"SignCassette_{t_num}", 2.75, 0.12, 1.45, 0, 0.08, SIGN_Z, mat=mat_cassette)
        visor = add_box(f"VisorCowl_{t_num}", 2.82, 0.22, 0.06, 0, 0.16, SIGN_Z + 0.74, rx=-math.radians(12), mat=mat_steel_dark)
        objs.extend([cassette, visor])

        rear_clamp_l = add_box(f"RearClampL_{t_num}", 0.14, 0.16, 1.10, -1.10, 0, SIGN_Z, mat=mat_steel_dark)
        rear_clamp_r = add_box(f"RearClampR_{t_num}", 0.14, 0.16, 1.10, 1.10, 0, SIGN_Z, mat=mat_steel_dark)
        objs.extend([rear_clamp_l, rear_clamp_r])

        flood_arm_l = add_cylinder(f"FloodArmL_{t_num}", 0.025, 0.45, 6, -0.90, 0.28, SIGN_Z + 0.85, rx=math.radians(35), mat=mat_galvanized)
        flood_arm_r = add_cylinder(f"FloodArmR_{t_num}", 0.025, 0.45, 6, 0.90, 0.28, SIGN_Z + 0.85, rx=math.radians(35), mat=mat_galvanized)
        flood_bar = add_box(f"FloodlightBar_{t_num}", 2.40, 0.08, 0.06, 0, 0.42, SIGN_Z + 0.95, mat=mat_steel_dark)
        flood_led = add_box(f"FloodlightLed_{t_num}", 2.30, 0.04, 0.02, 0, 0.42, SIGN_Z + 0.92, mat=mat_floodlight_led)
        objs.extend([flood_arm_l, flood_arm_r, flood_bar, flood_led])

        face = add_box(f"TurnDisplayFace_{t_num}", 2.65, 0.02, 1.35, 0, 0.142, SIGN_Z, mat=mat_face)
        mesh = face.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        uv_layer = bm.loops.layers.uv.verify()
        for face_elem in bm.faces:
            if face_elem.normal.y > 0.5:
                for loop in face_elem.loops:
                    vx = loop.vert.co.x / 2.65 + 0.5
                    vz = (loop.vert.co.z - (SIGN_Z - 0.675)) / 1.35
                    loop[uv_layer].uv = (vx, vz)
            elif face_elem.normal.y < -0.5:
                for loop in face_elem.loops:
                    vx = 1.0 - (loop.vert.co.x / 2.65 + 0.5)
                    vz = (loop.vert.co.z - (SIGN_Z - 0.675)) / 1.35
                    loop[uv_layer].uv = (vx, vz)
            else:
                for loop in face_elem.loops:
                    loop[uv_layer].uv = (0.01, 0.01)
        bm.to_mesh(mesh)
        bm.free()
        objs.append(face)

        for obj in objs:
            obj.parent = variant_group
            obj.matrix_parent_inverse = variant_group.matrix_world.inverted()
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.shade_smooth()
            if hasattr(obj.data, "use_auto_smooth"):
                obj.data.use_auto_smooth = True
                obj.data.auto_smooth_angle = math.radians(35)

    out_file = "/app/applet/public/models/photorealistic_turn_sign.glb"
    bpy.ops.export_scene.gltf(
        filepath=out_file,
        export_format='GLB',
        use_selection=False,
        export_yup=True,
        export_materials='EXPORT',
        export_colors=True
    )
    print(f"Exported master Turn Signs to: {out_file}")

# =============================================================================
# 3. SPONSOR BILLBOARDS (Centered at 0, 0, 0, front face +Y in Blender -> -Z in glTF)
# =============================================================================
def build_sponsor_billboards():
    reset_scene()

    tex_path = "/app/applet/public/textures/signage/sponsor_billboard_livery.png"
    mat_face = create_pbr_material("MatBillboardLivery", image_path=tex_path, roughness=0.30)
    mat_steel_dark = create_pbr_material("MatBillboardSteel", (0.12, 0.14, 0.17), metallic=0.85, roughness=0.35)
    mat_galvanized = create_pbr_material("MatBillboardGalv", (0.55, 0.58, 0.62), metallic=0.80, roughness=0.38)
    mat_composite = create_pbr_material("MatBillboardBacking", (0.16, 0.18, 0.22), metallic=0.30, roughness=0.45)

    root_empty = bpy.data.objects.new("SponsorBillboard", None)
    root_empty.location = (0, 0, 0)
    bpy.context.collection.objects.link(root_empty)
    objs = []

    BB_Z = 2.0
    for px in [-3.0, -1.0, 1.0, 3.0]:
        clamp = add_box(f"BarrierClamp_{px}", 0.16, 0.22, 0.28, px, -0.15, 0.85, mat=mat_steel_dark)
        pylon = add_cylinder(f"UprightPylon_{px}", 0.05, 2.20, 8, px, -0.15, 1.85, mat=mat_galvanized)
        gusset = add_cylinder(f"Gusset_{px}", 0.035, 1.45, 6, px, -0.45, 1.25, rx=-math.radians(35), mat=mat_steel_dark)
        objs.extend([clamp, pylon, gusset])

    truss_top = add_box("TrussTop", 8.2, 0.08, 0.10, 0, -0.06, BB_Z + 0.65, mat=mat_steel_dark)
    truss_mid = add_box("TrussMid", 8.2, 0.08, 0.10, 0, -0.06, BB_Z, mat=mat_steel_dark)
    truss_bot = add_box("TrussBot", 8.2, 0.08, 0.10, 0, -0.06, BB_Z - 0.65, mat=mat_steel_dark)
    objs.extend([truss_top, truss_mid, truss_bot])

    backing = add_box("BackingPlate", 8.10, 0.06, 1.85, 0, 0.02, BB_Z, mat=mat_composite)
    trim_top = add_box("TrimTop", 8.16, 0.04, 0.05, 0, 0.07, BB_Z + 0.92, mat=mat_steel_dark)
    trim_bot = add_box("TrimBot", 8.16, 0.04, 0.05, 0, 0.07, BB_Z - 0.92, mat=mat_steel_dark)
    trim_left = add_box("TrimLeft", 0.05, 0.04, 1.85, -4.05, 0.07, BB_Z, mat=mat_steel_dark)
    trim_right = add_box("TrimRight", 0.05, 0.04, 1.85, 4.05, 0.07, BB_Z, mat=mat_steel_dark)
    objs.extend([backing, trim_top, trim_bot, trim_left, trim_right])

    face = add_box("BillboardDisplayFace", 8.0, 0.02, 1.80, 0, 0.065, BB_Z, mat=mat_face)
    mesh = face.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    uv_layer = bm.loops.layers.uv.verify()
    for face_elem in bm.faces:
        if face_elem.normal.y > 0.5:
            for loop in face_elem.loops:
                vx = loop.vert.co.x / 8.0 + 0.5
                vz = (loop.vert.co.z - (BB_Z - 0.90)) / 1.80
                loop[uv_layer].uv = (vx, vz)
        elif face_elem.normal.y < -0.5:
            for loop in face_elem.loops:
                vx = 1.0 - (loop.vert.co.x / 8.0 + 0.5)
                vz = (loop.vert.co.z - (BB_Z - 0.90)) / 1.80
                loop[uv_layer].uv = (vx, vz)
        else:
            for loop in face_elem.loops:
                loop[uv_layer].uv = (0.01, 0.01)
    bm.to_mesh(mesh)
    bm.free()
    objs.append(face)

    for obj in objs:
        obj.parent = root_empty
        obj.matrix_parent_inverse = root_empty.matrix_world.inverted()
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth()
        if hasattr(obj.data, "use_auto_smooth"):
            obj.data.use_auto_smooth = True
            obj.data.auto_smooth_angle = math.radians(35)

    out_file = "/app/applet/public/models/photorealistic_sponsor_billboard.glb"
    bpy.ops.export_scene.gltf(
        filepath=out_file,
        export_format='GLB',
        use_selection=False,
        export_yup=True,
        export_materials='EXPORT',
        export_colors=True
    )
    print(f"Exported Sponsor Billboard GLB to: {out_file}")

if __name__ == "__main__":
    # Generate textures first if needed
    os.system("python3 /scripts/generate_signage_textures.py")

    # Generate individual variant models
    for dist in ["200", "150", "100", "50"]:
        build_brake_marker_variant(dist)
    build_all_brake_markers_master()

    for t_id in [1, 2, 3, 4]:
        build_turn_sign_variant(t_id)
    build_all_turn_signs_master()

    build_sponsor_billboards()
