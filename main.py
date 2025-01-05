import os
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


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
    try:
        font = ImageFont.truetype(font_path, 20)
    except IOError:
        raise FileNotFoundError("Font file not found. Please provide a valid .ttf font file.")

    def calculate_font_size(text, max_width, max_height, font_path):
        font_size = 1
        test_font = ImageFont.truetype(font_path, font_size)
        while True:
            test_width, test_height = draw.textbbox((0, 0), text, font=test_font)[2:4]
            if test_width > max_width or test_height > max_height:
                break
            font_size += 1
            test_font = ImageFont.truetype(font_path, font_size)
        return font_size - 1

    text_x = city_image.width + padding * 2
    text_width = content_width - text_x
    text_height = content_height // 2

    city_font_size = calculate_font_size(city, text_width, text_height // 2, font_path)
    country_font_size = calculate_font_size(country, text_width, text_height // 2, font_path)

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

    plaque_width, plaque_height = 6.5 * 28.3465, 2.5 * 28.3465  # wymiary 6.5cm x 2.5cm

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


city_country_data = [
    ("Split", "Croatia"),
    ("Củ Chi", "Vietnam"),
    ("Kuala Lumpur", "Malaysia"),
    ("Budapest", "Hungary"),
    ("San Francisco", "California (USA)"),
    ("Marsa Alam", "Egypt"),
    ("Siem Reap", "Cambodia"),
    ("Milano", "Italy"),
    ("Dubai", "United Arab Emirates"),
    ("Dahab", "Egypt"),
    ("Singapore", "Singapore"),
    ("Kimana", "Kenya"),
    ("Nusa Penida", "Indonesia"),
    ("Havana", "Cuba"),
    ("Lyon", "France"),
    ("Montpellier", "France"),
    ("Jakarta", "Indonesia"),
    ("Ho Chi Minh", "Vietnam"),
    ("Bratislava", "Slovakia"),
    ("Bali", "Indonesia"),
    ("Fuerteventura", "Canary Islands (Spain)"),
    ("Doha", "Qatar"),
    ("Las Vegas", "Nevada (USA)"),
    ("Alberobello", "Italy"),
    ("Rhodes", "Greece"),
    ("Cayo Santa María", "Cuba"),
    ("Berlin", "Germany"),
    ("Seligman", "Arizona (USA)"),
    ("Barcelona", "Spain"),
    ("Tatranská Lomnica", "Slovakia"),
    ("Cinque Terre", "Italy"),
    ("Sal", "Cabo Verde"),
    ("Batu Caves", "Malaysia"),
    ("Rijeka", "Croatia"),
    ("Vienna", "Austria"),
    ("Antalya", "Turkey"),
    ("London", "United Kingdom"),
    ("Los Angeles", "California (USA)"),
    ("Zittau", "Germany"),
    ("Genova", "Italy"),
    ("Sharm El Sheikh", "Egypt"),
    ("Cairo", "Egypt"),
    ("Plitvička Jezera", "Croatia"),
    ("Lago di Garda", "Italy"),
    ("Međugorje", "Bosnia and Herzegovina"),
    ("Jesolo", "Italy"),
    ("Grand Canyon", "Arizona (USA)"),
    ("Crete", "Greece"),
    ("Hollywood", "California (USA)"),
    ("Špindlerův Mlýn", "Czech Republic")
]


city_image_paths = {
    "Split": "split.png",
    "Củ Chi": "cu_chi.png",
    "Kuala Lumpur": "kuala_lumpur.png",
    "Budapest": "budapest.png",
    "San Francisco": "san_francisco.png",
    "Marsa Alam": "marsa_alam.png",
    "Siem Reap": "siem_reap.png",
    "Milano": "milano.png",
    "Dubai": "dubai.png",
    "Dahab": "dahab.png",
    "Singapore": "singapore.png",
    "Kimana": "kimana.png",
    "Nusa Penida": "nusa_penida.png",
    "Havana": "havana.png",
    "Lyon": "lyon.png",
    "Montpellier": "montpellier.png",
    "Jakarta": "jakarta.png",
    "Ho Chi Minh": "ho_chi_minh.png",
    "Bratislava": "bratislava.png",
    "Bali": "bali.png",
    "Fuerteventura": "fuerteventura.png",
    "Doha": "doha.png",
    "Las Vegas": "las_vegas.png",
    "Alberobello": "alberobello.png",
    "Rhodes": "rhodes.png",
    "Cayo Santa María": "cayo_santa_maria.png",
    "Berlin": "berlin.png",
    "Seligman": "seligman.png",
    "Barcelona": "barcelona.png",
    "Tatranská Lomnica": "tatranska_lomnica.png",
    "Cinque Terre": "cinque_terre.png",
    "Sal": "sal.png",
    "Batu Caves": "batu_caves.png",
    "Rijeka": "rijeka.png",
    "Vienna": "vienna.png",
    "Antalya": "antalya.png",
    "London": "london.png",
    "Los Angeles": "los_angeles.png",
    "Zittau": "zittau.png",
    "Genova": "genova.png",
    "Sharm El Sheikh": "sharm_el_sheikh.png",
    "Cairo": "cairo.png",
    "Plitvička Jezera": "plitvicka_jezera.png",
    "Lago di Garda": "lago_di_garda.png",
    "Međugorje": "medjugorje.png",
    "Jesolo": "jesolo.png",
    "Grand Canyon": "grand_canyon.png",
    "Crete": "crete.png",
    "Hollywood": "hollywood.png",
    "Špindlerův Mlýn": "spindleruv_mlyn.png"
}

generate_pdf(city_country_data, city_image_paths)
