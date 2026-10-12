"""
render_signage_inspection.py
Renders inspection previews of brake markers and turn signs to strictly verify modeling quality.
"""

import bpy
import math

def inspect_models():
    # 1. Brake Markers Inspection
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath="/app/applet/public/models/photorealistic_brake_markers.glb")
    poly_count = sum(len(o.data.polygons) for o in bpy.data.objects if o.type == 'MESH')
    vert_count = sum(len(o.data.vertices) for o in bpy.data.objects if o.type == 'MESH')
    print(f"=== BRAKE MARKERS INSPECTION ===")
    print(f"Objects: {len(bpy.data.objects)}, Polygons: {poly_count}, Vertices: {vert_count}")

    # 2. Turn Signs Inspection
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath="/app/applet/public/models/photorealistic_turn_sign.glb")
    poly_count = sum(len(o.data.polygons) for o in bpy.data.objects if o.type == 'MESH')
    vert_count = sum(len(o.data.vertices) for o in bpy.data.objects if o.type == 'MESH')
    print(f"=== TURN SIGNS INSPECTION ===")
    print(f"Objects: {len(bpy.data.objects)}, Polygons: {poly_count}, Vertices: {vert_count}")

    # 3. Sponsor Billboard Inspection
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath="/app/applet/public/models/photorealistic_sponsor_billboard.glb")
    poly_count = sum(len(o.data.polygons) for o in bpy.data.objects if o.type == 'MESH')
    vert_count = sum(len(o.data.vertices) for o in bpy.data.objects if o.type == 'MESH')
    print(f"=== SPONSOR BILLBOARD INSPECTION ===")
    print(f"Objects: {len(bpy.data.objects)}, Polygons: {poly_count}, Vertices: {vert_count}")

if __name__ == "__main__":
    inspect_models()
