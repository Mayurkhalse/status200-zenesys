"""
Scan Simulator: Applies artificial degradation (blur, noise, rotation, skew, brightness, compression)
to simulate scanned business documents.
"""
import random
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance

def apply_scan_effects(image: Image.Image, degradation_type: str = "random") -> Image.Image:
    """
    Applies image degradation transformations to a PIL Image.
    """
    if degradation_type == "none":
        return image

    img = image.convert("RGB")
    
    available_effects = ["blur", "noise", "rotation", "skew", "brightness", "compression"]
    if degradation_type == "random":
        chosen_effects = random.sample(available_effects, k=random.randint(1, 3))
    elif degradation_type in available_effects:
        chosen_effects = [degradation_type]
    else:
        chosen_effects = ["blur"]

    for effect in chosen_effects:
        if effect == "blur":
            radius = random.uniform(0.5, 1.5)
            img = img.filter(ImageFilter.GaussianBlur(radius=radius))
        elif effect == "noise":
            arr = np.array(img)
            noise = np.random.normal(0, random.uniform(5, 20), arr.shape)
            arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
            img = Image.fromarray(arr)
        elif effect == "rotation":
            angle = random.uniform(-3.0, 3.0)
            img = img.rotate(angle, resample=Image.BICUBIC, expand=False, fillcolor=(255, 255, 255))
        elif effect == "brightness":
            factor = random.uniform(0.7, 1.3)
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(factor)
        elif effect == "compression":
            import io
            buffer = io.BytesIO()
            quality = random.randint(20, 50)
            img.save(buffer, format="JPEG", quality=quality)
            buffer.seek(0)
            img = Image.open(buffer).convert("RGB")
            
    return img
