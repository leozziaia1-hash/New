"""
generate_signage_textures.py
Generates ultra-high-definition PBR textures for trackside brake markers, turn gantries, and sponsor billboards.
"""

import os
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = "/app/applet/public/textures/signage"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def draw_carbon_weave(draw, width, height, base_color=(18, 20, 24), weave_color=(28, 32, 38)):
    step = 8
    for y in range(0, height, step):
        for x in range(0, width, step):
            if ((x // step) + (y // step)) % 2 == 0:
                draw.rectangle([x, y, x + step, y + step], fill=weave_color)
            else:
                draw.rectangle([x, y, x + step, y + step], fill=base_color)

def generate_brake_marker_texture(distance_text, filename):
    width = 1024
    height = 1024
    img = Image.new("RGBA", (width, height), (15, 17, 21, 255))
    draw = ImageDraw.Draw(img)

    # Carbon fiber weave background
    draw_carbon_weave(draw, width, height, (14, 16, 20), (22, 25, 30))

    # Outer fluorescent safety yellow border (triple bevel)
    border_w = 48
    draw.rectangle([20, 20, width - 20, height - 20], outline=(250, 204, 21, 255), width=border_w)
    draw.rectangle([72, 72, width - 72, height - 72], outline=(202, 138, 4, 255), width=8)

    # Inner matte asphalt panel
    draw.rectangle([80, 80, width - 80, height - 80], fill=(12, 14, 18, 255))

    # FIA Micro watermark at top
    draw.rectangle([width // 2 - 120, 96, width // 2 + 120, 126], fill=(30, 41, 59, 255))
    try:
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        font_main = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 460)
        font_sponsor = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
    except:
        font_sub = font_main = font_sponsor = None

    draw.text((width // 2, 111), "FIA BRAKING ZONE", fill=(226, 232, 240, 255), anchor="mm", font=font_sub)

    # Large bold high-visibility distance numeral
    # Draw drop shadow for 3D depth
    draw.text((width // 2 + 8, height // 2 + 8), distance_text, fill=(0, 0, 0, 200), anchor="mm", font=font_main)
    # Bright reflective white text
    draw.text((width // 2, height // 2), distance_text, fill=(248, 250, 252, 255), anchor="mm", font=font_main)

    # Bottom sponsor / circuit credentials
    draw.rectangle([80, height - 170, width - 80, height - 80], fill=(20, 24, 32, 255))
    # Red accent stripe
    draw.rectangle([80, height - 174, width - 80, height - 170], fill=(225, 29, 72, 255))
    draw.text((width // 2, height - 125), "APEX GT PERFORMANCE BRAKING", fill=(203, 213, 225, 255), anchor="mm", font=font_sponsor)

    filepath = os.path.join(OUTPUT_DIR, filename)
    img.save(filepath, "PNG")
    print(f"Generated Brake Marker Texture: {filepath}")

def generate_turn_sign_texture(turn_number, direction_text, filename):
    width = 1024
    height = 512
    img = Image.new("RGBA", (width, height), (15, 23, 42, 255))
    draw = ImageDraw.Draw(img)

    # Dark royal FIA blue gradient / carbon background
    draw_carbon_weave(draw, width, height, (15, 23, 42), (24, 38, 70))

    # Outer border (High visibility cyan / white)
    draw.rectangle([14, 14, width - 14, height - 14], outline=(56, 189, 248, 255), width=16)
    draw.rectangle([32, 32, width - 32, height - 32], outline=(14, 116, 144, 255), width=4)

    # Top banner bar
    draw.rectangle([36, 36, width - 36, 90], fill=(30, 58, 138, 255))
    try:
        font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_turn = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 190)
        font_info = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
    except:
        font_header = font_turn = font_info = None

    draw.text((width // 2, 63), "CIRCUIT APEX GT  |  SECTOR TIMING", fill=(255, 255, 255, 255), anchor="mm", font=font_header)

    # Main Turn text
    turn_str = f"TURN {turn_number}"
    # Drop shadow
    draw.text((width // 2 - 80 + 6, height // 2 + 10 + 6), turn_str, fill=(0, 0, 0, 180), anchor="mm", font=font_turn)
    # Bright white text
    draw.text((width // 2 - 80, height // 2 + 10), turn_str, fill=(255, 255, 255, 255), anchor="mm", font=font_turn)

    # Apex chevron arrows on right side
    chevron_x = width - 190
    chevron_y = height // 2 + 10
    for offset_x in [-60, 0, 60]:
        cx = chevron_x + offset_x
        # Draw chevron arrow points
        draw.polygon([
            (cx - 24, chevron_y - 70),
            (cx + 12, chevron_y),
            (cx - 24, chevron_y + 70),
            (cx - 6, chevron_y + 70),
            (cx + 30, chevron_y),
            (cx - 6, chevron_y - 70)
        ], fill=(250, 204, 21, 255))

    # Bottom status bar
    draw.rectangle([36, height - 86, width - 36, height - 36], fill=(15, 23, 42, 255))
    draw.rectangle([36, height - 90, width - 36, height - 86], fill=(56, 189, 248, 255))
    draw.text((width // 2, height - 61), f"GEAR 2  |  SPEED 125 KM/H  |  {direction_text.upper()}", fill=(203, 213, 225, 255), anchor="mm", font=font_info)

    filepath = os.path.join(OUTPUT_DIR, filename)
    img.save(filepath, "PNG")
    print(f"Generated Turn Sign Texture: {filepath}")

def generate_sponsor_billboard_texture(filename):
    width = 2048
    height = 512
    img = Image.new("RGBA", (width, height), (15, 17, 21, 255))
    draw = ImageDraw.Draw(img)

    draw_carbon_weave(draw, width, height, (16, 18, 23), (26, 30, 38))

    # Outer metallic border
    draw.rectangle([12, 12, width - 12, height - 12], outline=(203, 213, 225, 255), width=16)

    # Split into 4 sponsor segments: Pirelli, Brembo, Shell, Apex GT
    segment_w = width // 4
    sponsors = [
        ("PIRELLI", (234, 179, 8, 255), (220, 38, 38, 255)),     # Yellow / Red
        ("BREMBO", (220, 38, 38, 255), (255, 255, 255, 255)),    # Red / White
        ("SHELL", (250, 204, 21, 255), (225, 29, 72, 255)),     # Yellow / Red
        ("APEX GT", (56, 189, 248, 255), (255, 255, 255, 255)),  # Cyan / White
    ]

    try:
        font_brand = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 96)
        font_slogan = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except:
        font_brand = font_slogan = None

    for i, (brand, col1, col2) in enumerate(sponsors):
        x0 = i * segment_w
        x1 = (i + 1) * segment_w
        center_x = (x0 + x1) // 2

        # Separator line
        if i > 0:
            draw.line([(x0, 28), (x0, height - 28)], fill=(71, 85, 105, 255), width=6)

        # Brand badge background
        draw.rectangle([center_x - 180, height // 2 - 80, center_x + 180, height // 2 + 50], fill=(24, 29, 39, 220), outline=col1, width=4)

        # Brand Text
        draw.text((center_x + 3, height // 2 - 15 + 3), brand, fill=(0, 0, 0, 200), anchor="mm", font=font_brand)
        draw.text((center_x, height // 2 - 15), brand, fill=col2, anchor="mm", font=font_brand)

        # Accent stripe
        draw.rectangle([center_x - 120, height // 2 + 58, center_x + 120, height // 2 + 64], fill=col1)
        draw.text((center_x, height // 2 + 82), "OFFICIAL MOTORSPORT PARTNER", fill=(148, 163, 184, 255), anchor="mm", font=font_slogan)

    filepath = os.path.join(OUTPUT_DIR, filename)
    img.save(filepath, "PNG")
    print(f"Generated Sponsor Billboard Texture: {filepath}")

if __name__ == "__main__":
    for dist in ["200", "150", "100", "50"]:
        generate_brake_marker_texture(dist, f"brake_marker_{dist}.png")
    
    turns = [
        (1, "Right 90° Corner"),
        (2, "Right 90° Corner"),
        (3, "Right 90° Corner"),
        (4, "Right 90° Corner"),
    ]
    for t_num, desc in turns:
        generate_turn_sign_texture(t_num, desc, f"turn_sign_{t_num}.png")

    generate_sponsor_billboard_texture("sponsor_billboard_livery.png")
