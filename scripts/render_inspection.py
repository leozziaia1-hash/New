"""
render_inspection.py
Renders a turntable inspection of the photorealistic 3D assets to verify mesh quality.
"""

import bpy
import math

def render_cabin_inspection():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    # Import the exported GLB
    bpy.ops.import_scene.gltf(filepath="/app/applet/public/models/photorealistic_marshal_cabin.glb")
    
    # Check scene stats
    poly_count = sum(len(o.data.polygons) for o in bpy.data.objects if o.type == 'MESH')
    vert_count = sum(len(o.data.vertices) for o in bpy.data.objects if o.type == 'MESH')
    print(f"=== MARSHAL CABIN INSPECTION ===")
    print(f"Total Objects: {len(bpy.data.objects)}")
    print(f"Total Polygons: {poly_count}")
    print(f"Total Vertices: {vert_count}")

    # Setup Camera
    cam_data = bpy.data.cameras.new("InspectCam")
    cam_data.lens = 45
    cam_obj = bpy.data.objects.new("InspectCam", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # Position camera looking at the cabin at 3/4 angle
    cam_obj.location = (4.8, -5.2, 3.8)
    cam_obj.rotation_euler = (math.radians(65), 0, math.radians(40))

    # Lighting
    sun_data = bpy.data.lights.new("Sun", type='SUN')
    sun_data.energy = 4.5
    sun_obj = bpy.data.objects.new("Sun", sun_data)
    sun_obj.rotation_euler = (math.radians(45), math.radians(30), math.radians(15))
    bpy.context.collection.objects.link(sun_obj)

    fill_data = bpy.data.lights.new("Fill", type='SUN')
    fill_data.energy = 1.8
    fill_obj = bpy.data.objects.new("Fill", fill_data)
    fill_obj.rotation_euler = (math.radians(-30), math.radians(-45), 0)
    bpy.context.collection.objects.link(fill_obj)

    # Render settings
    scene = bpy.context.scene
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = "/app/applet/public/models/cabin_inspection_preview.png"
    scene.render.resolution_x = 960
    scene.render.resolution_y = 540
    scene.render.resolution_percentage = 100

    bpy.ops.render.render(write_still=True)
    print("Inspection render saved to /app/applet/public/models/cabin_inspection_preview.png")

if __name__ == "__main__":
    render_cabin_inspection()
