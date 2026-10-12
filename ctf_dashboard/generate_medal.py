from PIL import Image, ImageDraw

def draw_medal():
    img = Image.new('RGBA', (200, 250), (255, 255, 255, 0))
    d = ImageDraw.Draw(img)
    
    # Ribbon
    d.polygon([(60, 0), (140, 0), (100, 100)], fill=(220, 20, 60))
    d.polygon([(60, 0), (100, 0), (100, 100)], fill=(200, 0, 40))
    
    # Medal base (gold circle)
    d.ellipse([(50, 70), (150, 170)], fill=(255, 215, 0))
    
    # Inner circles for detail
    d.ellipse([(60, 80), (140, 160)], fill=(238, 201, 0))
    d.ellipse([(65, 85), (135, 155)], fill=(255, 215, 0))
    
    # Add some text or symbol inside (star or "1")
    # Star coordinates
    cx, cy = 100, 120
    star_points = [
        (cx, cy - 25), (cx + 6, cy - 8), (cx + 25, cy - 8),
        (cx + 9, cy + 5), (cx + 15, cy + 22), (cx, cy + 12),
        (cx - 15, cy + 22), (cx - 9, cy + 5), (cx - 25, cy - 8),
        (cx - 6, cy - 8)
    ]
    d.polygon(star_points, fill=(255, 255, 255))
    
    img.save('static/medal.png')

draw_medal()
