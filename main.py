import os
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from data import *


def change_black_to_gray(image):
    pixels = image.load()
    black_threshold = 50
    light_gray = (200, 200, 200)

    for y in range(image.height):
        for x in range(image.width):
            r, g, b = pixels[x, y]
            if r < black_threshold and g < black_threshold and b < black_threshold:
                pixels[x, y] = light_gray
    return image


def calculate_dynamic_font_size(text, base_size, max_size, max_characters):
    length = max(len(text), 1)
    factor = min(max_characters / length, 1.5)  # Linear scaling factor
    font_size = int(base_size * (factor ** 0.7))  # Slight exponential scaling
    return max(min(font_size, max_size), base_size // 2)




def create_plaque(city, country, city_image_path, output_path):
    width, height = int(6.5 * 118.11), int(2.5 * 118.11)

    plaque = Image.new("RGB", (width, height), "black")
    draw = ImageDraw.Draw(plaque)

    outline_color = (192, 192, 192)
    outline_thickness = 10
    draw.rectangle([outline_thickness, outline_thickness, width - outline_thickness, height - outline_thickness],
                   outline=outline_color, width=outline_thickness)

    padding = 10
    content_width = width - 2 * (outline_thickness + padding)
    content_height = height - 2 * (outline_thickness + padding)

    city_image = Image.open(city_image_path).convert("RGBA")
    city_image.thumbnail((content_height, content_height))
    plaque.paste(city_image, (outline_thickness + padding, (height - city_image.height) // 2), city_image)

    font_path = "OpenSans-Regular.ttf"
    base_font_size = 44
    max_font_size = 60
    max_characters = 20

    try:
        font = ImageFont.truetype(font_path, base_font_size)
    except IOError:
        raise FileNotFoundError("Font file not found. Please provide a valid .ttf font file.")

    text_x = city_image.width + padding * 2
    text_width = content_width - text_x
    text_height = content_height // 2

    # Dynamic font size calculations
    city_font_size = calculate_dynamic_font_size(city, base_font_size, max_font_size, max_characters)
    country_font_size = calculate_dynamic_font_size(country, base_font_size, max_font_size, max_characters)

    city_font = ImageFont.truetype(font_path, city_font_size)
    country_font = ImageFont.truetype(font_path, country_font_size)

    city_text_width, city_text_height = draw.textbbox((0, 0), city, font=city_font)[2:4]
    country_text_width, country_text_height = draw.textbbox((0, 0), country, font=country_font)[2:4]

    city_x = text_x + (text_width - city_text_width) // 2
    city_y = (content_height // 2 - city_text_height) // 2

    country_x = text_x + (text_width - country_text_width) // 2
    country_y = content_height // 2 + (content_height // 2 - country_text_height) // 2

    draw.text((city_x, city_y), city, fill="lightgray", font=city_font)

    line_y = content_height // 2
    draw.line((text_x, line_y, width - outline_thickness - padding, line_y), fill="lightgray", width=5)

    draw.text((country_x, country_y), country, fill="lightgray", font=country_font)

    plaque.save(output_path)
    print(f"Plaque saved to {output_path}")


def generate_pdf(city_country_list, city_image_paths, output_pdf="output_pdf/plaques.pdf"):
    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)

    a4_width, a4_height = A4
    plaque_width, plaque_height = 6.5 * 28.3465, 2.5 * 28.3465  # Dimensions: 6.5cm x 2.5cm

    margin = 10
    x_spacing, y_spacing = 5, 5

    c = canvas.Canvas(output_pdf, pagesize=A4)
    c.setFillColorRGB(0, 0, 0)
    c.rect(0, 0, a4_width, a4_height, fill=True)

    x, y = margin, a4_height - margin - plaque_height

    for city, country in city_country_list:
        city_image_path = os.path.join("input_photos", city_image_paths.get(city, ""))
        if not os.path.isfile(city_image_path):
            raise ValueError(f"No image file found for city: {city} at {city_image_path}")

        plaque_path = os.path.join("output_images", f"{city}_{country}_plaque.png")
        create_plaque(city, country, city_image_path, plaque_path)

        c.drawImage(plaque_path, x, y, width=plaque_width, height=plaque_height)

        x += plaque_width + x_spacing
        if x + plaque_width + margin > a4_width:
            x = margin
            y -= plaque_height + y_spacing

        if y < margin:
            c.showPage()
            x, y = margin, a4_height - margin - plaque_height

            c.setFillColorRGB(0, 0, 0)
            c.rect(0, 0, a4_width, a4_height, fill=True)

    c.save()
    print(f"PDF saved to {output_pdf}")




generate_pdf(city_country_data_2, city_image_paths_2)
