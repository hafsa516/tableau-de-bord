from io import BytesIO
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
import os

def get_logo_image():
    """Récupère l'image du logo"""
    logo_paths = [
        "logo_segula.png",
        "logo_segula.jpg",
        "logo_segula.jpeg",
        "logo.png",
    ]
    
    for path in logo_paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    return BytesIO(f.read())
            except:
                continue
    return None

def create_pptx(pivot_table, output_path):
    """
    Crée un PowerPoint avec les graphiques
    """
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    # Slide 1: Logo
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)
    
    logo_buffer = get_logo_image()
    if logo_buffer:
        try:
            slide.shapes.add_picture(logo_buffer, Inches(0), Inches(0),
                                     width=prs.slide_width, height=prs.slide_height)
        except:
            pass
    
    # Les autres slides avec les graphiques...
    # (Cette partie sera simplifiée pour l'application web)
    
    prs.save(output_path)
    return output_path
