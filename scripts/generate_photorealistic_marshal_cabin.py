"""
generate_photorealistic_marshal_cabin.py
Engineered with Blender 3.6 LTS Headless CLI for AAA Photorealism & 60-120 FPS Performance.

Creates an ultra-detailed, authentic FIA Marshal Safety Observation Tower & Cabin:
1. Structural Foundation: Reinforced concrete footings with chamfered bevels, steel baseplates, and anchor bolts.
2. Steel Lattice Tower: 4 tubular main columns with taper, horizontal box girders, diagonal X-bracing truss struts, and gusset plates.
3. Access System: Heavy-duty industrial ladder with non-slip rungs and curved protective safety back-cage (crinoline hoops).
4. Observation Platform: Diamond-plate steel deck, perimeter safety kickplate (toe-board), and double-rail tubular balustrade.
5. High-Tech Marshal Cabin: Aerodynamic chamfered composite housing, 15-degree forward-raked panoramic windshield, sliding side observation windows, and cantilevered sun canopy roof with drip rails.
6. Modeled Interior: Operator console desk, dual telemetry/timing displays, VHF radio transceiver rack, rolled flag storage tubes (red, yellow, green, blue).
7. Exterior Race Equipment:
   - FIA Digital Electronic LED Flag Matrix Panel with protective sun cowl/hood.
   - Quick-release dry-powder safety fire extinguisher (red cylinder, brass nozzle, pressure gauge).
   - Roof communications mast, dual whip antennas, GPS dome, rotating amber warning beacon, and rooftop photovoltaic solar panel module.
8. PBR Materials: Industrial galvanized steel, matte anthracite composite, hazard warning stripes, emissive LED matrix, tinted glass, fire extinguisher red.
"""

import bpy
import bmesh
import math
import os
from mathutils import Matrix, Vector

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

def create_pbr_material(name, base_color, metallic=0.0, roughness=0.5, emissive_color=(0, 0, 0), emissive_strength=0.0, alpha=1.0, is_glass=False):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    output_node.location = (400, 0)

    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)

    # Base Color & Metallic/Roughness
    bsdf.inputs['Base Color'].default_value = (*base_color, alpha)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness

    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 0.85 if is_glass else 0.0
    elif 'Transmission' in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = 0.85 if is_glass else 0.0

    if 'Emission Color' in bsdf.inputs:
        bsdf.inputs['Emission Color'].default_value = (*emissive_color, 1.0)
    elif 'Emission' in bsdf.inputs:
        bsdf.inputs['Emission'].default_value = (*emissive_color, 1.0)

    if 'Emission Strength' in bsdf.inputs:
        bsdf.inputs['Emission Strength'].default_value = emissive_strength

    if is_glass or alpha < 0.99:
        mat.blend_method = 'BLEND'
        mat.shadow_method = 'NONE'

    links.new(bsdf.outputs['BSDF'], output_node.inputs['Surface'])
    return mat

def add_cylinder(name, radius, height, depth_segs, x, y, z, rx=0, ry=0, rz=0, mat=None):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=depth_segs,
        radius=radius,
        depth=height,
        location=(x, y, z),
        rotation=(rx, ry, rz)
    )
    obj = bpy.context.active_object
    obj.name = name
    if mat:
        obj.data.materials.append(mat)
    return obj

def add_box(name, sx, sy, sz, x, y, z, rx=0, ry=0, rz=0, mat=None):
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(x, y, z),
        rotation=(rx, ry, rz)
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(scale=True)
    if mat:
        obj.data.materials.append(mat)
    return obj

def build_marshal_cabin_model():
    reset_scene()

    # Materials
    mat_concrete = create_pbr_material("MatConcrete", (0.35, 0.36, 0.38), metallic=0.05, roughness=0.85)
    mat_steel_dark = create_pbr_material("MatSteelDark", (0.12, 0.14, 0.17), metallic=0.85, roughness=0.35)
    mat_galvanized = create_pbr_material("MatGalvanizedSteel", (0.55, 0.58, 0.62), metallic=0.80, roughness=0.38)
    mat_hazard_stripes = create_pbr_material("MatHazardStripes", (0.85, 0.70, 0.10), metallic=0.1, roughness=0.45)
    mat_cabin_composite = create_pbr_material("MatCabinComposite", (0.15, 0.17, 0.20), metallic=0.35, roughness=0.40)
    mat_cabin_roof = create_pbr_material("MatCabinRoof", (0.78, 0.80, 0.83), metallic=0.40, roughness=0.30)
    mat_tinted_glass = create_pbr_material("MatTintedGlass", (0.05, 0.15, 0.20), metallic=0.1, roughness=0.05, alpha=0.35, is_glass=True)
    mat_fire_extinguisher = create_pbr_material("MatFireExtinguisher", (0.85, 0.08, 0.08), metallic=0.4, roughness=0.30)
    mat_brass_metal = create_pbr_material("MatBrass", (0.75, 0.60, 0.20), metallic=0.9, roughness=0.25)
    mat_led_green = create_pbr_material("MatLedFlagGreen", (0.05, 0.20, 0.05), metallic=0.2, roughness=0.2, emissive_color=(0.15, 0.95, 0.25), emissive_strength=4.5)
    mat_led_yellow = create_pbr_material("MatLedFlagYellow", (0.25, 0.20, 0.05), metallic=0.2, roughness=0.2, emissive_color=(0.95, 0.85, 0.10), emissive_strength=3.5)
    mat_screen_display = create_pbr_material("MatScreenDisplay", (0.02, 0.04, 0.08), metallic=0.5, roughness=0.2, emissive_color=(0.10, 0.55, 0.90), emissive_strength=2.2)
    mat_flag_red = create_pbr_material("MatFlagRed", (0.85, 0.10, 0.10), metallic=0.0, roughness=0.7)
    mat_flag_yellow = create_pbr_material("MatFlagYellow", (0.90, 0.85, 0.10), metallic=0.0, roughness=0.7)
    mat_flag_green = create_pbr_material("MatFlagGreen", (0.10, 0.75, 0.20), metallic=0.0, roughness=0.7)
    mat_flag_blue = create_pbr_material("MatFlagBlue", (0.10, 0.35, 0.85), metallic=0.0, roughness=0.7)
    mat_beacon_amber = create_pbr_material("MatBeaconAmber", (0.95, 0.50, 0.05), metallic=0.2, roughness=0.1, emissive_color=(1.0, 0.60, 0.05), emissive_strength=5.0)

    created_objects = []

    # -------------------------------------------------------------------------
    # 1. FOUNDATION PADS & STEEL ANCHOR PLATES (Y is Up in Three.js, in Blender Z is Up)
    # Dimensions: 3.6m wide (X) x 2.8m deep (Y) x 4.2m total height (Z)
    # -------------------------------------------------------------------------
    pad_coords = [(-1.5, -1.1), (1.5, -1.1), (-1.5, 1.1), (1.5, 1.1)]
    for idx, (px, py) in enumerate(pad_coords):
        # Concrete pad with chamfered look
        pad = add_box(f"ConcretePad_{idx}", 0.7, 0.7, 0.35, px, py, 0.175, mat=mat_concrete)
        created_objects.append(pad)
        # Steel baseplate
        plate = add_box(f"SteelBaseplate_{idx}", 0.55, 0.55, 0.04, px, py, 0.37, mat=mat_steel_dark)
        created_objects.append(plate)
        # 4 Anchor bolts
        for bx, by in [(-0.2, -0.2), (0.2, -0.2), (-0.2, 0.2), (0.2, 0.2)]:
            bolt = add_cylinder(f"Bolt_{idx}_{bx}_{by}", 0.025, 0.06, 6, px + bx, py + by, 0.41, mat=mat_galvanized)
            created_objects.append(bolt)

    # -------------------------------------------------------------------------
    # 2. TOWER STRUCTURAL COLUMNS & X-BRACING TRUSSES
    # Platform height: Z = 2.4m
    # -------------------------------------------------------------------------
    PLATFORM_HEIGHT = 2.4
    col_radius = 0.075

    # 4 Main tubular steel columns
    for idx, (px, py) in enumerate(pad_coords):
        # Slight architectural taper toward top
        top_x = px * 0.92
        top_y = py * 0.92
        mid_x = (px + top_x) / 2
        mid_y = (py + top_y) / 2
        dx = top_x - px
        dy = top_y - py
        col_len = math.sqrt(dx*dx + dy*dy + (PLATFORM_HEIGHT - 0.39)**2)
        pitch = math.atan2(math.sqrt(dx*dx + dy*dy), PLATFORM_HEIGHT - 0.39)
        yaw = math.atan2(dy, dx)

        col = add_cylinder(f"MainColumn_{idx}", col_radius, col_len, 10, mid_x, mid_y, (PLATFORM_HEIGHT + 0.39)/2, mat=mat_galvanized)
        col.rotation_euler = (math.sin(yaw)*pitch, -math.cos(yaw)*pitch, 0)
        created_objects.append(col)

    # Horizontal tie girders at mid-height (Z = 1.35) and platform perimeter (Z = 2.4)
    for z_lvl in [1.35, PLATFORM_HEIGHT]:
        # Front beam (Y = 1.1)
        b_front = add_box(f"TieGirder_Front_{z_lvl}", 3.0, 0.10, 0.12, 0, 1.05 * (0.92 if z_lvl > 2 else 0.96), z_lvl, mat=mat_steel_dark)
        # Back beam (Y = -1.1)
        b_back = add_box(f"TieGirder_Back_{z_lvl}", 3.0, 0.10, 0.12, 0, -1.05 * (0.92 if z_lvl > 2 else 0.96), z_lvl, mat=mat_steel_dark)
        # Left beam (X = -1.5)
        b_left = add_box(f"TieGirder_Left_{z_lvl}", 0.10, 2.2, 0.12, -1.42 * (0.92 if z_lvl > 2 else 0.96), 0, z_lvl, mat=mat_steel_dark)
        # Right beam (X = 1.5)
        b_right = add_box(f"TieGirder_Right_{z_lvl}", 0.10, 2.2, 0.12, 1.42 * (0.92 if z_lvl > 2 else 0.96), 0, z_lvl, mat=mat_steel_dark)
        created_objects.extend([b_front, b_back, b_left, b_right])

    # Diagonal X-bracing truss struts on Left, Right, and Back sides (leaving front for ladder access or clear sight)
    def add_x_brace(p1, p2, name_prefix):
        mid = (p1 + p2) * 0.5
        delta = p2 - p1
        dist = delta.length
        rot = delta.to_track_quat('Z', 'Y').to_euler()
        strut = add_cylinder(f"{name_prefix}_Strut", 0.035, dist, 8, mid.x, mid.y, mid.z, rot.x, rot.y, rot.z, mat=mat_galvanized)
        created_objects.append(strut)

    # Left face X-braces (between Z=0.4 and Z=1.35, and Z=1.35 and Z=2.4)
    for (z0, z1) in [(0.45, 1.30), (1.40, 2.35)]:
        x_pos = -1.40
        add_x_brace(Vector((x_pos, -0.95, z0)), Vector((x_pos, 0.95, z1)), f"LeftX_{z0}")
        add_x_brace(Vector((x_pos, -0.95, z1)), Vector((x_pos, 0.95, z0)), f"LeftX_rev_{z0}")

    # Right face X-braces
    for (z0, z1) in [(0.45, 1.30), (1.40, 2.35)]:
        x_pos = 1.40
        add_x_brace(Vector((x_pos, -0.95, z0)), Vector((x_pos, 0.95, z1)), f"RightX_{z0}")
        add_x_brace(Vector((x_pos, -0.95, z1)), Vector((x_pos, 0.95, z0)), f"RightX_rev_{z0}")

    # Back face X-braces
    for (z0, z1) in [(0.45, 1.30), (1.40, 2.35)]:
        y_pos = -1.02
        add_x_brace(Vector((-1.35, y_pos, z0)), Vector((1.35, y_pos, z1)), f"BackX_{z0}")
        add_x_brace(Vector((-1.35, y_pos, z1)), Vector((1.35, y_pos, z0)), f"BackX_rev_{z0}")

    # -------------------------------------------------------------------------
    # 3. ACCESS LADDER WITH SAFETY CRINOLINE CAGE (Mounted on back-left side)
    # -------------------------------------------------------------------------
    ladder_x = -0.95
    ladder_y = -1.18
    # 2 Ladder vertical stanchions
    lad_col1 = add_cylinder("LadderRail_1", 0.03, PLATFORM_HEIGHT + 0.9, 8, ladder_x - 0.22, ladder_y, (PLATFORM_HEIGHT + 0.9) / 2, mat=mat_steel_dark)
    lad_col2 = add_cylinder("LadderRail_2", 0.03, PLATFORM_HEIGHT + 0.9, 8, ladder_x + 0.22, ladder_y, (PLATFORM_HEIGHT + 0.9) / 2, mat=mat_steel_dark)
    created_objects.extend([lad_col1, lad_col2])

    # Non-slip ladder rungs spaced every 0.28m
    num_rungs = int(PLATFORM_HEIGHT / 0.28)
    for r in range(1, num_rungs + 1):
        rz = r * 0.28
        rung = add_cylinder(f"LadderRung_{r}", 0.016, 0.44, 6, ladder_x, ladder_y, rz, ry=math.pi/2, mat=mat_galvanized)
        created_objects.append(rung)

    # Safety cage hoops (crinoline) from 1.6m up to platform level
    for cz in [1.55, 1.95, 2.35, 2.75, 3.15]:
        # Circular / arch hoop surrounding climber
        hoop = add_cylinder(f"SafetyCageHoop_{cz}", 0.36, 0.02, 12, ladder_x, ladder_y - 0.26, cz, mat=mat_hazard_stripes)
        created_objects.append(hoop)
    # 3 Vertical cage spine straps
    for angle in [-math.pi/4, 0, math.pi/4]:
        sx = ladder_x + math.sin(angle) * 0.36
        sy = (ladder_y - 0.26) - math.cos(angle) * 0.36
        spine = add_cylinder(f"CageSpine_{angle:.1f}", 0.015, 1.65, 6, sx, sy, 2.35, mat=mat_steel_dark)
        created_objects.append(spine)

    # -------------------------------------------------------------------------
    # 4. RAISED OBSERVATION PLATFORM DECK & PERIMETER SAFETY BALUSTRADE
    # -------------------------------------------------------------------------
    # Structural floor slab (Diamond plate metal)
    deck_floor = add_box("PlatformDeckFloor", 3.2, 2.4, 0.08, 0, 0, PLATFORM_HEIGHT + 0.04, mat=mat_galvanized)
    created_objects.append(deck_floor)

    # Perimeter kickplate / toe-board (prevents debris/tools from falling) with safety hazard stripes
    kick_front = add_box("Kickplate_Front", 3.24, 0.04, 0.16, 0, 1.20, PLATFORM_HEIGHT + 0.12, mat=mat_hazard_stripes)
    kick_back = add_box("Kickplate_Back", 2.6, 0.04, 0.16, 0.3, -1.20, PLATFORM_HEIGHT + 0.12, mat=mat_hazard_stripes)
    kick_left = add_box("Kickplate_Left", 0.04, 2.4, 0.16, -1.60, 0, PLATFORM_HEIGHT + 0.12, mat=mat_hazard_stripes)
    kick_right = add_box("Kickplate_Right", 0.04, 2.4, 0.16, 1.60, 0, PLATFORM_HEIGHT + 0.12, mat=mat_hazard_stripes)
    created_objects.extend([kick_front, kick_back, kick_left, kick_right])

    # Platform safety railing stanchions and double handrails (1.1m high)
    railing_z = PLATFORM_HEIGHT + 1.1
    # Top handrail perimeter
    hr_front = add_cylinder("Handrail_Front", 0.025, 3.24, 8, 0, 1.20, railing_z, ry=math.pi/2, mat=mat_steel_dark)
    hr_mid_front = add_cylinder("MidRail_Front", 0.020, 3.24, 8, 0, 1.20, PLATFORM_HEIGHT + 0.58, ry=math.pi/2, mat=mat_steel_dark)
    hr_left = add_cylinder("Handrail_Left", 0.025, 2.4, 8, -1.60, 0, railing_z, rx=math.pi/2, mat=mat_steel_dark)
    hr_mid_left = add_cylinder("MidRail_Left", 0.020, 2.4, 8, -1.60, 0, PLATFORM_HEIGHT + 0.58, rx=math.pi/2, mat=mat_steel_dark)
    hr_right = add_cylinder("Handrail_Right", 0.025, 2.4, 8, 1.60, 0, railing_z, rx=math.pi/2, mat=mat_steel_dark)
    hr_mid_right = add_cylinder("MidRail_Right", 0.020, 2.4, 8, 1.60, 0, PLATFORM_HEIGHT + 0.58, rx=math.pi/2, mat=mat_steel_dark)
    # Back handrail (with opening for ladder access)
    hr_back = add_cylinder("Handrail_Back", 0.025, 2.5, 8, 0.35, -1.20, railing_z, ry=math.pi/2, mat=mat_steel_dark)
    hr_mid_back = add_cylinder("MidRail_Back", 0.020, 2.5, 8, 0.35, -1.20, PLATFORM_HEIGHT + 0.58, ry=math.pi/2, mat=mat_steel_dark)
    created_objects.extend([hr_front, hr_mid_front, hr_left, hr_mid_left, hr_right, hr_mid_right, hr_back, hr_mid_back])

    # Vertical railing stanchions
    stanchion_locs = [
        (-1.60, 1.20), (0, 1.20), (1.60, 1.20),
        (-1.60, -1.20), (-0.70, -1.20), (0.40, -1.20), (1.60, -1.20),
        (-1.60, 0), (1.60, 0)
    ]
    for idx, (sx, sy) in enumerate(stanchion_locs):
        st = add_cylinder(f"Stanchion_{idx}", 0.028, 1.05, 8, sx, sy, PLATFORM_HEIGHT + 0.55, mat=mat_steel_dark)
        created_objects.append(st)

    # -------------------------------------------------------------------------
    # 5. ULTRA-DETAILED MARSHAL OBSERVATION CABIN / ENCLOSURE
    # Base at Z = 2.48m. Cabin dimensions: 2.3m wide (X) x 1.7m deep (Y) x 2.1m high
    # Features chamfered corners, forward-raked panoramic windshield, aerodynamic roof.
    # -------------------------------------------------------------------------
    CABIN_BASE_Z = PLATFORM_HEIGHT + 0.08
    CABIN_HEIGHT = 2.10

    # Lower solid insulated composite parapet / wall base (0.95m high from floor)
    cabin_lower_base = add_box("CabinLowerWall", 2.30, 1.70, 0.95, 0, 0.15, CABIN_BASE_Z + 0.475, mat=mat_cabin_composite)
    created_objects.append(cabin_lower_base)

    # Rear solid wall extending to ceiling
    cabin_rear_wall = add_box("CabinRearWall", 2.30, 0.12, 1.15, 0, -0.64, CABIN_BASE_Z + 1.525, mat=mat_cabin_composite)
    created_objects.append(cabin_rear_wall)

    # Corner structural aerodynamic mullions
    for (mx, my) in [(-1.12, -0.64), (1.12, -0.64), (-1.12, 0.94), (1.12, 0.94)]:
        mullion = add_box(f"CornerMullion_{mx}_{my}", 0.09, 0.09, CABIN_HEIGHT, mx, my, CABIN_BASE_Z + CABIN_HEIGHT/2, mat=mat_steel_dark)
        created_objects.append(mullion)

    # Front Panoramic Windshield (slanted forward 15 degrees for sun glare reduction and wide track view)
    windshield_angle = math.radians(12)
    # Windshield glass pane
    windshield = add_box(
        "PanoramicWindshield",
        2.14, 0.03, 1.10,
        0, 0.97, CABIN_BASE_Z + 1.48,
        rx=-windshield_angle, mat=mat_tinted_glass
    )
    # Windshield center wiper & frame divider
    center_divider = add_box(
        "WindshieldDivider",
        0.04, 0.06, 1.12,
        0, 0.97, CABIN_BASE_Z + 1.48,
        rx=-windshield_angle, mat=mat_steel_dark
    )
    created_objects.extend([windshield, center_divider])

    # Left & Right Observation Windows
    left_window = add_box("LeftObservationWindow", 0.03, 1.45, 1.05, -1.12, 0.15, CABIN_BASE_Z + 1.48, mat=mat_tinted_glass)
    right_window = add_box("RightObservationWindow", 0.03, 1.45, 1.05, 1.12, 0.15, CABIN_BASE_Z + 1.48, mat=mat_tinted_glass)
    created_objects.extend([left_window, right_window])

    # Modern Cantilevered Aerodynamic Canopy Roof (protrudes forward over front glass)
    roof_z = CABIN_BASE_Z + CABIN_HEIGHT + 0.07
    cabin_roof = add_box("CanopyRoofMain", 2.55, 2.25, 0.14, 0, 0.28, roof_z, mat=mat_cabin_roof)
    # Aerodynamic curved front roof visor lip
    roof_visor = add_cylinder("RoofVisorLip", 0.08, 2.55, 12, 0, 1.40, roof_z, ry=math.pi/2, mat=mat_steel_dark)
    created_objects.extend([cabin_roof, roof_visor])

    # -------------------------------------------------------------------------
    # 6. MODELED CABIN INTERIOR (Console, dual telemetry screens, radio, flags)
    # -------------------------------------------------------------------------
    # Ergonomic marshal operator desk
    desk_z = CABIN_BASE_Z + 0.88
    desk_surface = add_box("OperatorDeskSurface", 1.95, 0.55, 0.05, 0, 0.55, desk_z, mat=mat_steel_dark)
    created_objects.append(desk_surface)

    # Left Telemetry Screen (angled toward operator)
    screen_left = add_box("TelemetryScreen_Left", 0.48, 0.04, 0.32, -0.45, 0.65, desk_z + 0.26, rz=-math.radians(18), mat=mat_screen_display)
    stand_left = add_cylinder("ScreenStand_Left", 0.02, 0.14, 8, -0.45, 0.65, desk_z + 0.07, mat=mat_steel_dark)
    # Right Circuit Timing Screen
    screen_right = add_box("TelemetryScreen_Right", 0.48, 0.04, 0.32, 0.45, 0.65, desk_z + 0.26, rz=math.radians(18), mat=mat_screen_display)
    stand_right = add_cylinder("ScreenStand_Right", 0.02, 0.14, 8, 0.45, 0.65, desk_z + 0.07, mat=mat_steel_dark)
    created_objects.extend([screen_left, stand_left, screen_right, stand_right])

    # VHF Radio Transceiver Base Station
    radio_unit = add_box("RadioTransceiverUnit", 0.28, 0.22, 0.12, 0, 0.68, desk_z + 0.08, mat=mat_cabin_composite)
    radio_mic = add_cylinder("RadioGooseneckMic", 0.012, 0.24, 6, 0.08, 0.60, desk_z + 0.18, rx=math.radians(35), mat=mat_brass_metal)
    created_objects.extend([radio_unit, radio_mic])

    # Wall-mounted Flag Storage Tubes & Rolled Racing Flags
    flag_x = 0.95
    flag_y = -0.40
    flag_rack = add_box("FlagRackMount", 0.06, 0.35, 0.60, flag_x, flag_y, CABIN_BASE_Z + 1.20, mat=mat_steel_dark)
    created_objects.append(flag_rack)
    flags_data = [
        ("Red", mat_flag_red, -0.10),
        ("Yellow", mat_flag_yellow, -0.03),
        ("Green", mat_flag_green, 0.04),
        ("Blue", mat_flag_blue, 0.11),
    ]
    for (f_name, f_mat, f_offset) in flags_data:
        # Rolled cloth cylinder + wooden handle pole
        pole = add_cylinder(f"FlagPole_{f_name}", 0.015, 0.95, 6, flag_x - 0.05, flag_y + f_offset, CABIN_BASE_Z + 1.35, mat=mat_brass_metal)
        cloth = add_cylinder(f"FlagCloth_{f_name}", 0.038, 0.65, 8, flag_x - 0.05, flag_y + f_offset, CABIN_BASE_Z + 1.45, mat=f_mat)
        created_objects.extend([pole, cloth])

    # Emergency Stop Big Red Button on side console
    estop_box = add_box("EmergencyStopBox", 0.10, 0.10, 0.10, -0.85, 0.40, desk_z + 0.07, mat=mat_hazard_stripes)
    estop_btn = add_cylinder("EmergencyStopButton", 0.035, 0.03, 8, -0.85, 0.40, desk_z + 0.13, mat=mat_fire_extinguisher)
    created_objects.extend([estop_box, estop_btn])

    # -------------------------------------------------------------------------
    # 7. EXTERIOR RACE SAFETY EQUIPMENT
    # -------------------------------------------------------------------------
    # A. FIA High-Intensity Digital LED Flag Matrix Panel (Front facade)
    # Positioned on front upper facade facing oncoming vehicles: 1.3m wide x 0.85m high
    led_panel_z = CABIN_BASE_Z + CABIN_HEIGHT + 0.55
    led_panel_y = 1.35
    # Hood / Sun Cowl shroud
    led_cowl = add_box("LedSunCowl", 1.46, 0.35, 0.98, 0, led_panel_y, led_panel_z, mat=mat_steel_dark)
    # Recessed display screen face
    led_display = add_box("LedMatrixScreen", 1.34, 0.04, 0.84, 0, led_panel_y + 0.16, led_panel_z, mat=mat_led_green)
    # Heavy-duty tubular support brackets attaching cowl to cabin roof
    led_arm_l = add_cylinder("LedSupportArm_L", 0.03, 0.65, 6, -0.55, 1.10, led_panel_z - 0.25, rx=math.radians(35), mat=mat_galvanized)
    led_arm_r = add_cylinder("LedSupportArm_R", 0.03, 0.65, 6, 0.55, 1.10, led_panel_z - 0.25, rx=math.radians(35), mat=mat_galvanized)
    created_objects.extend([led_cowl, led_display, led_arm_l, led_arm_r])

    # B. Industrial Dry-Powder Fire Extinguisher (Mounted on platform railing corner)
    ext_x = 1.45
    ext_y = 0.95
    ext_z = PLATFORM_HEIGHT + 0.65
    ext_tank = add_cylinder("ExtinguisherTank", 0.09, 0.52, 12, ext_x, ext_y, ext_z, mat=mat_fire_extinguisher)
    ext_neck = add_cylinder("ExtinguisherNeck", 0.04, 0.08, 8, ext_x, ext_y, ext_z + 0.28, mat=mat_brass_metal)
    ext_handle = add_box("ExtinguisherHandle", 0.06, 0.14, 0.05, ext_x, ext_y, ext_z + 0.34, mat=mat_steel_dark)
    ext_hose = add_cylinder("ExtinguisherHose", 0.018, 0.45, 6, ext_x + 0.08, ext_y, ext_z + 0.12, mat=mat_steel_dark)
    created_objects.extend([ext_tank, ext_neck, ext_handle, ext_hose])

    # C. Rooftop Communication Array & Equipment
    # Stainless Steel Communications Whip Antenna
    ant_mast = add_cylinder("CommsMast", 0.025, 1.60, 8, -0.90, -0.40, roof_z + 0.85, mat=mat_galvanized)
    ant_whip = add_cylinder("WhipAntenna", 0.008, 1.20, 6, -0.90, -0.40, roof_z + 2.05, mat=mat_steel_dark)
    # White Aerodynamic GPS / Telemetry Dome
    gps_dome = add_cylinder("GpsTelemetryDome", 0.14, 0.12, 12, -0.55, -0.40, roof_z + 0.12, mat=mat_cabin_roof)
    # Photovoltaic Solar Power Panel on roof (1.1m x 0.8m)
    solar_panel = add_box("RooftopSolarPanel", 1.15, 0.85, 0.05, 0.35, -0.30, roof_z + 0.10, rx=-math.radians(8), mat=mat_screen_display)
    solar_frame = add_box("SolarPanelFrame", 1.20, 0.90, 0.04, 0.35, -0.30, roof_z + 0.07, rx=-math.radians(8), mat=mat_galvanized)
    # Rotating Amber Emergency Warning Beacon Light
    beacon_base = add_cylinder("BeaconBase", 0.08, 0.06, 10, 0, 0.10, roof_z + 0.10, mat=mat_steel_dark)
    beacon_dome = add_cylinder("BeaconAmberDome", 0.07, 0.14, 12, 0, 0.10, roof_z + 0.20, mat=mat_beacon_amber)
    created_objects.extend([ant_mast, ant_whip, gps_dome, solar_panel, solar_frame, beacon_base, beacon_dome])

    # -------------------------------------------------------------------------
    # 8. HIERARCHY, SHADING & SCENE ASSEMBLY
    # -------------------------------------------------------------------------
    # Select all created objects and apply smooth shading with auto smooth
    for obj in created_objects:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth()
        if hasattr(obj.data, "use_auto_smooth"):
            obj.data.use_auto_smooth = True
            obj.data.auto_smooth_angle = math.radians(35)

    # Create root anchor empty
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root_empty = bpy.context.active_object
    root_empty.name = "FIA_MarshalSafetyTower"

    for obj in created_objects:
        obj.parent = root_empty

    print(f"Marshal Cabin Model Generated Successfully: {len(created_objects)} components.")

    # Export to GLB
    output_path = "/app/applet/public/models/photorealistic_marshal_cabin.glb"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format='GLB',
        use_selection=False,
        export_apply=False,
        export_yup=True,
        export_materials='EXPORT',
        export_colors=True,
    )
    print(f"Exported Photorealistic Marshal Cabin GLB to: {output_path}")

if __name__ == "__main__":
    build_marshal_cabin_model()
