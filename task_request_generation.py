# -*- coding: utf-8 -*-
"""
Simulates user task requests for an AI image generation tool based on a
guided UI framework. (Version 2.3)

This script generates a dataset of task requests, incorporating varied text inputs
using templates and curated snippets. It simulates reference image inputs using
structured placeholder URLs instead of placeholder filenames.

Enhancements in v2.3:
- Added mandatory 'target_platforms' field to common refinements.
- Added 'checkbox' type handling in simulation logic.
- Updated comments and preprocessing notes.
- (Inherits changes from v2.2: Exportable function, consistent menu desc logic,
  no "Default/AI Choice", placeholder URLs, more options/snippets).

The output is a JSON file containing a list of simulated task request dictionaries.
Requires standard ML preprocessing before use.

To use the generation logic in other files, import the
`generate_simulation_dataset` function.
"""

import random
import json
import uuid
import re # For template filling
import urllib.parse # For encoding URL query parameters

# --- Configuration (for standalone execution) ---
DEFAULT_NUM_PROFILES = 10 # Number of profiles to generate when run directly
OUTPUT_FILENAME = "simulated_task_requests.json" # Updated filename
# Probability controls for optional fields/features
OPTIONAL_FIELD_CHANCE = 0.6 # Chance an optional field gets filled
REFERENCE_IMAGE_CHANCE = 0.3 # Chance a reference image is included
ADDITIONAL_INSTRUCTIONS_CHANCE = 0.5 # Chance the final text area is filled
MENU_ITEM_DESCRIPTION_CHANCE = 0.6 # Chance a menu list includes descriptions

# --- Curated Snippets Library (Expanded Examples) ---
# (Expand these lists significantly for better variety!)
CURATED_SNIPPETS = {
    "product_features": [
        "crispy golden texture", "freshly baked daily", "locally sourced organic ingredients",
        "vibrant natural colors", "generous family-sized portion", "our secret signature sauce", "artisan hand-crafted quality",
        "healthy and light option", "classic comfort food style", "perfectly cooked medium-rare", "unique umami flavor profile",
        "stone-baked crust", "rich chocolate ganache", "seasonal fruits"
    ],
    "presentation_styles_prod": [ # Corresponds to dropdown options + variations
        "Plated beautifully, top-down view", "Angled shot showing layers", "Close-up macro texture shot",
        "Held in hand to show scale", "Action shot: pouring syrup", "Served in original packaging",
        "Overhead flat lay with props", "Dynamic 3/4 view", "Deconstructed plating", "Rustic family-style platter"
    ],
    "background_settings_prod": [ # Corresponds to dropdown options + variations
        "Simple neutral gradient background", "Clean studio white backdrop", "On a rustic dark wood table",
        "Against a marble countertop", "Blurred cafe background context", "Using brand colors subtly",
        "Textured linen surface", "Outdoor picnic setting", "Slate serving board", "Minimalist concrete surface"
    ],
    "props_prod": [
        "vintage cutlery", "patterned napkin", "fresh herbs garnish", "subtle steam effect",
        "scattered coffee beans", "a slice cut out", "complementary drink", "chopping board",
        "small dipping bowl", "branded coaster", "single flower vase"
    ],
    "lifestyle_scenes": [
        "Friends laughing together sharing pizza outdoors at sunset.",
        "A person working on a laptop enjoying a detailed latte art coffee in a bright, modern cafe.",
        "A couple having a romantic candlelit dinner with wine glasses.",
        "Family gathered around a table for a noisy, happy weekend brunch.",
        "Someone relaxing on a sofa at home watching TV with takeaway noodles.",
        "Students studying intensely together surrounded by snacks and books.",
        "A close-up of hands holding a warm, steaming mug on a cold day.",
        "Busy lunchtime crowd atmosphere with blurred motion.",
        "Outdoor picnic scene on a sunny day with a checkered blanket.",
        "Colleagues having a quick coffee meeting during a break."
    ],
    "lifestyle_moods": [ # Corresponds to dropdown options + variations
        "Cozy, relaxed, and warm atmosphere", "Bright, energetic, and vibrant feel", "Romantic, intimate, low light",
        "Busy, social, and lively setting", "Professional and clean business lunch vibe", "Fun, playful, and casual mood",
        "Aspirational, luxurious, and elegant", "Calm and serene morning light", "Nostalgic and vintage feel", "Exciting and adventurous"
    ],
    "promo_visual_ideas": [
        "Focus on the discounted product itself, looking irresistible.", "Use abstract geometric graphics incorporating brand colors.",
        "Create festive illustrations matching the specific holiday (e.g., Raya, Christmas).", "Show diverse happy customers enjoying the offer.",
        "Clean graphic design emphasizing the bold text offer.", "Use high-energy action shots related to the product.",
        "Minimalist design with elegant typography for the promotion.", "A flat lay including the product and related items."
    ],
    "branding_themes": [
        "Freshness and natural ingredients", "Community and togetherness", "Modern luxury and elegance",
        "Speed and convenience", "Tradition and heritage", "Fun and playful energy", "Sustainability and eco-conscious",
        "Authenticity and craftsmanship", "Innovation and fusion"
    ],
    "location_features": [
        "cozy fireplace", "large sunny windows", "comfortable booth seating", "unique wall art mural",
        "lush green indoor plants", "view of the city skyline", "well-stocked polished bar display", "outdoor patio heaters and fairy lights",
        "exposed brick walls with industrial pipes", "modern minimalist light fixtures", "traditional batik fabric accents"
    ],
    "event_highlights": [
        "Live performance by [Artist Name]", "Exclusive multi-course tasting menu by Chef [Chef's Name]", "Hands-on cooking/baking workshop - limited spots!",
        "Special festive decorations and limited-edition menu", "Meet the guest chef/bartender from [Place]", "Portion of proceeds go to [Charity Name]",
        "Celebrate our [Number] anniversary with us!", "Featuring new seasonal cocktails and mocktails", "Family fun day with activities for kids"
    ],
    "bts_activities": [ # Corresponds to dropdown options + variations
        "Chef carefully plating a signature dish with tweezers.", "Barista creating intricate multi-layered latte art.",
        "Baker kneading dough early in the morning light.", "Staff collaborating smoothly during a busy dinner service.",
        "Close-up of fresh, high-quality local ingredients being prepped.", "Serving a smiling regular customer by name.",
        "The organized chaos and energy of the kitchen line.", "Decorating intricate cakes/pastries with precision.",
        "Receiving fresh produce delivery from a local farm."
    ],
    "bts_feel": [ # Corresponds to dropdown options + variations
        "Authentic, candid, unposed moment capturing real work.", "Clean, professional, and highly organized workspace.",
        "Artistic shot focusing on the details and textures of the craft.", "Energetic, fast-paced kitchen action with motion blur.",
        "Passionate focus of a staff member dedicated to their task.", "Showcasing teamwork, communication, and camaraderie.",
        "Highlighting the quality and freshness of ingredients."
    ],
    "ref_image_instructions": [
        "Match the overall style and mood.", "Use this composition as a reference.",
        "Recreate this scene but with our specific product: [PRODUCT].",
        "Adopt the lighting technique shown here.", "Use similar colors and textures.",
        "Create a graphic layout inspired by this.", "Improve the quality of this photo while keeping the subject.",
        "Draw inspiration from this image's energy.", "Keep the background, change the foreground subject.",
        "Use this image for style guidance only.", "Extract the color palette from this image.",
        "Make my product look as appetizing as the one in this reference."
    ],
    "additional_instructions": [
        "Ensure the final image is photorealistic, 8k resolution.", "Use a 16:9 aspect ratio for website banner.",
        "No people should be visible in the shot.", "Include subtle motion blur for dynamism.",
        "Make the main subject slightly off-center using rule of thirds.", "Avoid using the color blue entirely.",
        "Add a slight vignette effect to draw focus.", "The image needs ample negative space for text overlay.",
        "Focus on creating a warm, inviting, and cozy feeling.", "Keep the composition minimal and clean.",
        "--no text, --no watermark", "Use a shallow depth of field.", "--style raw"
    ]
}

# --- Task Categories and Fields Definition ---

TASK_CATEGORIES = [
    "Product Shot", "Menu Display", "Lifestyle Shot", "Promotional Graphic",
    "Branding Element", "Location/Ambiance Shot", "Event Promotion", "Behind-the-Scenes"
]

# Define fields for each task category based on task_request_ui_design_v1 (v2 update)
# Includes optional reference image fields
TASK_FIELDS = {
    "Product Shot": [
        {"id": "item_name", "label": "Food/Drink Item Name:", "type": "text", "required": True, "templates": ["Our signature [ITEM]", "A delicious plate of [ITEM]", "Freshly made [ITEM]", "Classic [ITEM]", "Spicy [ITEM]"]},
        {"id": "features", "label": "Key Ingredients/Features to Highlight:", "type": "tags", "required": False, "snippets_key": "product_features", "max_tags": 3},
        {"id": "presentation", "label": "Desired Presentation:", "type": "dropdown_visual", "required": False, "options": ["Plated (Top-Down/Overhead)", "Plated (Angled/3-Quarter)", "Close-up/Macro", "Held in Hand", "Action (e.g., pouring, cutting)", "In Packaging", "Deconstructed", "Family-Style Platter"]},
        {"id": "background", "label": "Background/Setting:", "type": "dropdown_visual", "required": False, "options": ["Simple/Neutral Gradient", "Studio White", "Rustic Wood", "Marble Surface", "Relevant Context (e.g., Cafe Blur, Kitchen Counter)", "Use Brand Colors", "Slate Board", "Concrete Surface"]},
        {"id": "props", "label": "Props:", "type": "tags", "required": False, "snippets_key": "props_prod", "max_tags": 2},
        {"id": "ref_image", "label": "Reference Image(s):", "type": "file_upload", "required": False}, # Will generate placeholder URL
        {"id": "ref_instructions", "label": "Instructions for Reference Image(s):", "type": "text_area", "required": False, "snippets_key": "ref_image_instructions"},
    ],
    "Menu Display": [
        {"id": "menu_items", "label": "Menu Items:", "type": "structured_list", "required": True, "min_items": 1, "max_items": 5}, # Simulate 1-5 items
        {"id": "section_title", "label": "Menu Section Title (Optional):", "type": "text", "required": False, "templates": ["{Cuisine Type} Specials", "Our Starters", "Desserts Menu", "Drinks List", "Chef Recommendations"]},
        {"id": "layout_style", "label": "Layout Style:", "type": "dropdown_visual", "required": False, "options": ["Simple List", "Two Column", "Grid with Images", "Minimalist Text-Heavy", "Ornate/Themed", "Modern Clean Grid"]},
        {"id": "include_item_images", "label": "Include Item Images?", "type": "checkbox_bool", "required": False}, # Simulate boolean
        {"id": "include_logo", "label": "Include Logo?", "type": "checkbox_bool", "required": False},
        {"id": "ref_image", "label": "Reference Image(s) (e.g., layout examples):", "type": "file_upload", "required": False}, # Placeholder URL
        {"id": "ref_instructions", "label": "Instructions for Reference Image(s):", "type": "text_area", "required": False, "snippets_key": "ref_image_instructions"},
    ],
    "Lifestyle Shot": [
        {"id": "scene_desc", "label": "Describe Scene/Activity:", "type": "text_area", "required": True, "snippets_key": "lifestyle_scenes"},
        {"id": "featured_product", "label": "Product(s) to Feature (if any):", "type": "text", "required": False, "templates": ["Featuring our [ITEM]", "Subtly showing the [ITEM]", "Enjoying a [ITEM]", "Sharing a plate of [ITEM]"]},
        {"id": "setting", "label": "Setting:", "type": "dropdown", "required": False, "options": ["Our Establishment (Interior)", "Our Establishment (Exterior/Patio)", "Relevant Public Space (e.g., Park, Street, Beach)", "Customer's Location (e.g., Home, Office)", "Scenic Viewpoint"]},
        {"id": "people", "label": "People Involved:", "type": "dropdown", "required": False, "options": ["No People (Focus on Product/Setting)", "One Person", "Couple", "Small Group (Friends/Colleagues)", "Family", "Diverse Group"]},
        {"id": "mood_vibe", "label": "Overall Mood/Vibe:", "type": "dropdown", "required": False, "options": ["Cozy/Relaxed", "Bright/Energetic", "Romantic/Intimate", "Busy/Social", "Professional/Business", "Fun/Playful", "Aspirational/Luxury", "Nostalgic", "Adventurous"]},
        {"id": "time_of_day", "label": "Time of Day Suggestion:", "type": "dropdown", "required": False, "options": ["Morning", "Midday/Lunch", "Afternoon", "Golden Hour/Sunset", "Evening/Dinner", "Late Night"]},
        {"id": "ref_image", "label": "Reference Image(s) (e.g., mood, style, composition):", "type": "file_upload", "required": False}, # Placeholder URL
        {"id": "ref_instructions", "label": "Instructions for Reference Image(s):", "type": "text_area", "required": False, "snippets_key": "ref_image_instructions"},
    ],
    "Promotional Graphic": [
        {"id": "promo_type", "label": "Promotion Type:", "type": "dropdown", "required": True, "options": ["Percentage Discount", "Fixed Amount Off", "Buy One Get One (BOGO)", "Free Item", "New Product Launch", "Limited Time Offer (LTO)", "Event Announcement", "Holiday Special", "General Awareness", "Combo Deal"]},
        {"id": "headline", "label": "Main Text/Headline:", "type": "text", "required": True, "templates": ["{Promo Type}: [ITEM]!", "Special Offer!", "Don't Miss Out!", "New Arrival: [ITEM]", "Weekend Deal!", "Limited Time Only!"]},
        {"id": "details", "label": "Offer Details/Sub-headline:", "type": "text", "required": False, "templates": ["Get {Discount}% off today!", "Free {Item} with purchase!", "Available this weekend only.", "RM{Amount} off your next order.", "Buy 2 Get 1 Free!"]},
        {"id": "visual_idea", "label": "Key Visual Element:", "type": "dropdown_text", "required": False, "options": ["Photo of Featured Product", "Abstract Brand Graphics", "Illustrative Elements", "Stock Photo (Themed)", "Text Only", "Animated Graphic Elements"], "templates": ["Focus on the [ITEM]", "Use festive graphics", "Clean text design", "Show happy customer"]},
        {"id": "cta", "label": "Call to Action Text:", "type": "text", "required": False, "options": ["Order Now!", "Visit Us Today!", "Learn More", "Book Your Table", "Shop Now", "Redeem Offer"], "templates": ["Tap to Order", "Find Us Here", "See Menu"]}, # Use options as suggestions
        {"id": "include_logo", "label": "Include Logo?", "type": "checkbox_bool", "required": False},
        {"id": "duration", "label": "Promotion Duration (Optional):", "type": "text", "required": False, "templates": ["Valid until [Date]", "This week only", "Ends Sunday", "From [Date] to [Date]"]},
        {"id": "ref_image", "label": "Reference Image(s) (e.g., style, layout inspiration):", "type": "file_upload", "required": False}, # Placeholder URL
        {"id": "ref_instructions", "label": "Instructions for Reference Image(s):", "type": "text_area", "required": False, "snippets_key": "ref_image_instructions"},
    ],
     "Branding Element": [
        {"id": "element_type", "label": "Element Type:", "type": "dropdown", "required": True, "options": ["Social Media Post Template", "Social Media Story Template", "Website Banner Element", "Brand Pattern (Seamless)", "Icon Set", "Presentation Slide Background", "Email Header Graphic"]},
        {"id": "intended_use", "label": "Intended Use/Platform:", "type": "text", "required": False, "templates": ["For Instagram Feed", "Website Hero Section", "Packaging design", "Internal presentation", "Facebook Ad", "Email Newsletter"]},
        {"id": "theme_keywords", "label": "Key Theme/Keywords:", "type": "tags", "required": False, "snippets_key": "branding_themes", "max_tags": 3},
        {"id": "text_placeholders", "label": "Text Placeholder(s) Needed?", "type": "text", "required": False, "templates": ["Space for headline", "Area for body text", "Button text placeholder", "Price placeholder", "Contact info area"]},
        {"id": "ref_image", "label": "Reference Image(s) (e.g., style examples, existing assets):", "type": "file_upload", "required": False}, # Placeholder URL
        {"id": "ref_instructions", "label": "Instructions for Reference Image(s):", "type": "text_area", "required": False, "snippets_key": "ref_image_instructions"},
    ],
    "Location/Ambiance Shot": [
        {"id": "area_view", "label": "Area/View:", "type": "dropdown_text", "required": True, "options": ["Main Dining Area", "Bar/Counter Area", "Outdoor Seating/Patio", "Entrance/Storefront", "Specific Decor Feature", "Overall Atmosphere", "Washroom Detail", "Kitchen Window View"], "templates": ["Focus on the main dining space", "Show the bar setup", "Capture the outdoor patio vibe", "Wide shot of the entrance"]},
        {"id": "atmosphere", "label": "Desired Atmosphere:", "type": "dropdown", "required": False, "options": ["Busy/Lively", "Quiet/Intimate", "Relaxed/Casual", "Upscale/Elegant", "Cozy/Warm", "Bright/Airy", "Modern/Chic", "Rustic/Homely"]},
        {"id": "time_of_day", "label": "Time of Day:", "type": "dropdown", "required": False, "options": ["Daytime (Bright)", "Golden Hour (Warm)", "Evening (Ambient/Lit)", "Night (Exterior/Interior Glow)", "Blue Hour"]},
        {"id": "features_include", "label": "Key Features to Include (Optional):", "type": "tags", "required": False, "snippets_key": "location_features", "max_tags": 3},
        {"id": "ref_image", "label": "Reference Image(s) (e.g., photos of the actual space, inspiration):", "type": "file_upload", "required": False}, # Placeholder URL
        {"id": "ref_instructions", "label": "Instructions for Reference Image(s):", "type": "text_area", "required": False, "snippets_key": "ref_image_instructions"},
    ],
     "Event Promotion": [
        {"id": "event_name", "label": "Event Name:", "type": "text", "required": True, "templates": ["{Holiday} Special", "Live Music Night", "Guest Chef Dinner", "Anniversary Celebration", "Weekend Brunch Fest"]},
        {"id": "event_type", "label": "Event Type:", "type": "dropdown", "required": True, "options": ["Live Music/Performance", "Tasting Menu/Dinner", "Workshop/Class", "Holiday Special", "Guest Chef/Bartender", "Charity Event", "Opening/Anniversary", "Themed Night", "Sports Screening"]},
        {"id": "event_datetime", "label": "Date(s) & Time(s):", "type": "text", "required": True, "templates": ["Saturday, [Date] at 7 PM", "Weekend of [Date]", "From [Time] to [Time] on [Date]", "Every Friday Night"]},
        {"id": "highlights", "label": "Key Highlights/Description:", "type": "text_area", "required": False, "snippets_key": "event_highlights"},
        {"id": "event_audience", "label": "Target Audience for Event:", "type": "text", "required": False, "templates": ["Perfect for couples", "Family-friendly event", "Ideal for foodies", "Great for corporate teams"]},
        {"id": "visual_idea", "label": "Key Visual Element Idea:", "type": "dropdown_text", "required": False, "options": ["Photo related to event type", "Abstract/Themed Graphics", "Venue photo", "Illustrations of event activity"], "templates": ["Show the live band", "Feature the special menu item", "Use festive graphics", "Illustrate people learning"]},
        {"id": "include_logo", "label": "Include Logo?", "type": "checkbox_bool", "required": False},
        {"id": "ref_image", "label": "Reference Image(s) (e.g., past event photos, style inspiration):", "type": "file_upload", "required": False}, # Placeholder URL
        {"id": "ref_instructions", "label": "Instructions for Reference Image(s):", "type": "text_area", "required": False, "snippets_key": "ref_image_instructions"},
    ],
    "Behind-the-Scenes": [
        {"id": "activity", "label": "Activity/Subject:", "type": "dropdown_text", "required": True, "options": ["Chef Cooking/Prepping", "Chef Plating Dish", "Barista Making Coffee/Drink", "Baker Kneading/Decorating", "Staff Interaction (Teamwork)", "Serving Customer", "Fresh Ingredients Focus", "Kitchen Environment", "Receiving Delivery"], "snippets_key": "bts_activities"},
        {"id": "location_bts", "label": "Location within Business:", "type": "dropdown", "required": False, "options": ["Kitchen", "Bar Area", "Service Counter", "Dining Area (during prep)", "Storage/Receiving", "Outdoor Area (e.g., herb garden)"]},
        {"id": "feel", "label": "Desired Feel:", "type": "dropdown", "required": False, "options": ["Authentic/Candid", "Clean/Professional", "Artistic/Detailed", "Energetic/Busy", "Passionate/Focused", "Educational"]},
        {"id": "emphasize", "label": "Emphasize:", "type": "tags", "required": False, "snippets_key": "bts_feel", "max_tags": 2}, # Use snippets or keywords like Skill, Freshness etc.
        {"id": "ref_image", "label": "Reference Image(s) (e.g., photos of staff/kitchen, style examples):", "type": "file_upload", "required": False}, # Placeholder URL
        {"id": "ref_instructions", "label": "Instructions for Reference Image(s):", "type": "text_area", "required": False, "snippets_key": "ref_image_instructions"},
    ],
}

# Fields for the common Step 3: Style & Refinements (with Target Platform)
COMMON_REFINEMENT_FIELDS = [
    # --- NEW Mandatory Platform Selection ---
    {"id": "target_platforms", "label": "Target Platform(s):", "type": "checkbox", "required": True, "options": [
        "Instagram Post (Square 1:1)", "Instagram Story/Reel (9:16)", "Facebook Post/Ad (Multiple AR)", "TikTok Video (9:16)",
        "Website Banner (e.g., 16:9 Wide)", "Website Content (Flexible AR)", "Google Business Profile",
        "WhatsApp Status/Broadcast", "Xiaohongshu (Red)", "Print (Specify use in additional instructions)"
        ], "max_select": 3}, # Simulate selecting 1 to 3 platforms
    # --- Existing Refinement Fields ---
    {"id": "visual_style", "label": "Visual Style:", "type": "dropdown_visual", "required": True, "options": ["Photorealistic", "Cinematic", "Illustration", "3D Render", "Watercolor", "Anime/Manga", "Cartoonish", "Modern", "Rustic", "Minimalist", "Vibrant", "Elegant", "Vintage", "Cyberpunk"]},
    {"id": "color_palette_adj", "label": "Specific colors to emphasize or avoid?", "type": "text", "required": False, "templates": ["Emphasize warm tones like orange and brown", "Avoid using bright pink", "Use pastel colors primarily", "Stick to brand palette: [COLOR1], [COLOR2]", "Monochromatic scheme based on [COLOR]"]},
    {"id": "composition_angle", "label": "Preferred angle or shot type?", "type": "dropdown", "required": False, "options": ["Overhead/Flat Lay", "Eye-Level", "Low Angle", "High Angle", "Close-up", "Medium Shot", "Wide Shot", "Dutch Angle", "Point of View (POV)"]},
    {"id": "additional_instructions", "label": "Additional Instructions / Keywords:", "type": "text_area", "required": False, "snippets_key": "additional_instructions"},
]


# --- Helper Functions (Module Level) ---

def evaluate_condition(condition, current_response):
    """Checks if a question's display condition is met based on previous answers."""
    # (Implementation remains the same as v2.2)
    if condition is None: return True
    q_id, operator, value = condition
    if q_id not in current_response or current_response[q_id] is None: return False
    response_value = current_response[q_id]
    try:
        if operator == '==': return response_value == value
        elif operator == '!=': return response_value != value
        elif operator == 'in': return isinstance(value, (list, tuple, set)) and response_value in value
        elif operator == 'not in': return isinstance(value, (list, tuple, set)) and response_value not in value
        else: return False
    except Exception as e:
        print(f"Error evaluating condition {condition}: {e}")
        return False

def get_random_snippet(key):
    """Selects a random snippet from the CURATED_SNIPPETS library."""
    # (Implementation remains the same as v2.2)
    if key in CURATED_SNIPPETS and CURATED_SNIPPETS[key]:
        return random.choice(CURATED_SNIPPETS[key])
    return ""

def fill_template(templates, context):
    """Selects a random template and attempts to fill placeholders."""
    # (Implementation remains the same as v2.2)
    if not templates: return f"Generic text {uuid.uuid4().hex[:4]}"
    template = random.choice(templates)
    filled_template = template
    placeholders = re.findall(r'\[(.*?)\]|\{(.*?)\}', template)
    placeholders = [ph for group in placeholders for ph in group if ph]
    placeholder_map = {
        "ITEM": context.get("item_name", context.get("featured_product", "the featured product")),
        "Promo Type": context.get("promo_type", "Special Offer"),
        "Discount": str(random.randint(10, 50)),
        "Amount": str(random.randint(5, 20)),
        "Date": f"{random.randint(1, 28)}/{random.randint(1, 12)}/2025",
        "Time": f"{random.randint(1, 12)}:{random.choice(['00', '30'])} {random.choice(['AM', 'PM'])}",
        "Holiday": context.get("event_name", random.choice(["Holiday", "Festive"])),
        "Artist Name": random.choice(["The Jazz Trio", "Acoustic Nights", "DJ Spinmaster"]),
        "Chef's Name": random.choice(["Chef Wan", "Chef Ismail", "Chef Florence Tan"]),
        "Place": random.choice(["[Local City]", "Paris", "Tokyo"]),
        "Charity Name": random.choice(["Local Food Bank", "Orphanage Fund", "Wildlife Conservation"]),
        "Number": str(random.randint(1, 10)),
        "COLOR": random.choice(['Red', 'Blue', 'Green', 'Yellow', 'Black', 'White']),
        "COLOR1": f"#{random.randint(0, 0xFFFFFF):06x}",
        "COLOR2": f"#{random.randint(0, 0xFFFFFF):06x}",
        "Cuisine Type": context.get("cuisine_type", "our delicious"),
    }
    for ph in placeholders:
        replacement = placeholder_map.get(ph, f"[{ph}]")
        escaped_ph = re.escape(ph)
        filled_template = re.sub(r'(\[' + escaped_ph + r'\]|\{' + escaped_ph + r'\})', str(replacement), filled_template, count=1)
    if filled_template == template and not placeholders:
         filled_template += f" {random.choice(['info', 'detail', 'spec'])} {uuid.uuid4().hex[:3]}"
    return filled_template

def simulate_placeholder_url(context):
    """Generates a plausible placeholder URL encoding context."""
    # (Implementation remains the same as v2.2)
    query_parts = [context.get('task_category', 'image')]
    keys_to_include = ['item_name', 'scene_desc', 'activity', 'element_type', 'area_view','event_name', 'visual_style', 'mood_vibe', 'atmosphere', 'feel']
    added_terms = set()
    for key in keys_to_include:
        value = context.get(key)
        term_to_add = None
        if value and isinstance(value, str):
            if len(value.split()) > 4: value = ' '.join(value.split()[:4])
            term_to_add = re.sub(r'[^\w\s-]', '', value).strip()
        elif value and isinstance(value, list):
             term_to_add = " ".join(value)
             term_to_add = re.sub(r'[^\w\s-]', '', term_to_add).strip()
        if term_to_add and term_to_add not in added_terms:
            query_parts.append(term_to_add)
            added_terms.add(term_to_add)
    query_string = " ".join(query_parts)
    query_string = re.sub(r'\s+', '+', query_string.strip())
    encoded_query = urllib.parse.quote(query_string)
    return f"https://simulated-image-reference.example.com/search?query={encoded_query}&sim_id={uuid.uuid4().hex[:8]}"


def simulate_field_value(field_definition, context):
    """
    Simulates a value for a single field based on its definition.
    Handles the new 'checkbox' type.
    """
    field_type = field_definition["type"]
    options = field_definition.get("options", [])
    templates = field_definition.get("templates", [])
    snippets_key = field_definition.get("snippets_key", None)

    answer = None
    try:
        if field_type == "text":
             # (Logic remains the same as v2.2)
            if templates: answer = fill_template(templates, context)
            elif snippets_key: answer = get_random_snippet(snippets_key)
            else: answer = f"Simulated {field_definition.get('label', 'Text').replace(':', '')} text {uuid.uuid4().hex[:4]}"
        elif field_type == "text_area":
             # (Logic remains the same as v2.2)
            if snippets_key: answer = get_random_snippet(snippets_key)
            else: answer = f"Simulated detailed text for {field_definition.get('label', 'TextArea').replace(':', '')}. {random.choice(['Focus on quality.', 'Make it appealing.', 'Keep it concise.'])}"
        elif field_type == "tags" or field_type == "checkbox": # Combine logic for multi-select
            # Determine max number of selections
            max_select = field_definition.get("max_select", 3 if field_type == "tags" else len(options)) # Default max for checkbox is all options
            # Determine min number of selections (1 if required and options exist, else 0)
            is_required = field_definition.get("required", False)
            min_k = 1 if is_required and options else 0
            # Ensure k is within bounds
            upper_bound = min(max_select, len(options))
            if upper_bound < min_k: k = 0
            else: k = random.randint(min_k, upper_bound)

            if k > 0:
                # Select from options if available, otherwise use snippets or generate placeholders
                if options:
                    answer = random.sample(options, k)
                elif snippets_key and CURATED_SNIPPETS.get(snippets_key):
                    num_available = len(CURATED_SNIPPETS[snippets_key])
                    k = min(k, num_available)
                    answer = random.sample(CURATED_SNIPPETS[snippets_key], k) if k > 0 else []
                else: # Fallback for tags if no options/snippets
                    answer = [f"SimTag{i+1}_{uuid.uuid4().hex[:3]}" for i in range(k)] if field_type == "tags" else []
            else:
                answer = [] # Empty list if k=0
        elif field_type == "dropdown" or field_type == "dropdown_visual":
             # (Logic remains the same as v2.2)
            if options: answer = random.choice(options)
            else: answer = "Error: No Options"
        elif field_type == "dropdown_text":
             # (Logic remains the same as v2.2)
             if options and random.random() < 0.7: answer = random.choice(options)
             else: answer = fill_template(templates, context) if templates else f"Simulated text entry {uuid.uuid4().hex[:4]}"
        elif field_type == "checkbox_bool":
            # (Logic remains the same as v2.2)
            answer = random.choice([True, False])
        elif field_type == "structured_list":
            # (Logic remains the same as v2.2 - consistent description)
            min_items = field_definition.get("min_items", 1)
            max_items = field_definition.get("max_items", 3)
            num_items = random.randint(min_items, max_items)
            answer = []
            include_descriptions = random.random() < MENU_ITEM_DESCRIPTION_CHANCE
            for i in range(num_items):
                 adj = random.choice(["Spicy", "Classic", "Grilled", "Homemade", "Signature", "Crispy", "Creamy", "Authentic", "Zesty"])
                 noun = random.choice(["Chicken", "Beef", "Lamb", "Fish", "Vegetable", "Tofu", "Noodle", "Rice", "Curry", "Soup", "Sambal", "Quinoa"])
                 dish_type = random.choice(["Rendang", "Satay", "Laksa", "Burger", "Pizza", "Salad", "Stir-fry", "Bowl", "Taco", "Wrap"])
                 item_name = f"{adj} {noun} {dish_type} {uuid.uuid4().hex[:2]}"
                 price = f"RM{random.uniform(8.0, 75.0):.2f}"
                 desc = f"A brief description for {item_name}, {random.choice(['highly recommended', 'customer favorite', 'new item', 'must try!', 'perfect for sharing'])}." if include_descriptions else None
                 answer.append({"Item Name": item_name, "Price": price, "Brief Description": desc})
        elif field_type == "file_upload":
            # (Logic remains the same as v2.2)
            answer = simulate_placeholder_url(context)
        else:
            answer = f"Error: Unknown Type '{field_type}'"

    except Exception as e:
        print(f"Error simulating value for field {field_definition.get('id', 'N/A')}: {e}")
        answer = "Error: Simulation Failed"

    return answer


# --- Core Task Request Simulation Function (Generates ONE request) ---

def generate_task_request():
    """
    Generates a single simulated task request dictionary.

    Returns:
        dict: A dictionary representing one simulated task request.
    """
    task_data = {} # Stores the data for the task being generated

    # 1. Select Task Category
    task_category = random.choice(TASK_CATEGORIES)
    task_data['task_category'] = task_category

    # 2. Simulate Core Task Details based on selected category
    if task_category in TASK_FIELDS:
        for field_def in TASK_FIELDS[task_category]:
            field_id = field_def["id"]
            is_required = field_def.get("required", False)
            should_simulate = True # Assume we simulate unless optional check fails

            # Determine if an optional field should be simulated based on chance
            if not is_required:
                # Apply general optional chance
                should_simulate = (random.random() < OPTIONAL_FIELD_CHANCE)
                # Override chance specifically for reference images
                if field_def["type"] == "file_upload" and field_id == "ref_image":
                     should_simulate = (random.random() < REFERENCE_IMAGE_CHANCE)
                # Instructions only relevant if reference image exists
                elif field_def["type"] == "text_area" and field_id == "ref_instructions":
                     should_simulate = (task_data.get("ref_image") is not None) and \
                                       (random.random() < OPTIONAL_FIELD_CHANCE)

            # Simulate the value if required or if optional chance passed
            if should_simulate:
                # Pass current task_data as context for potential template filling
                simulated_value = simulate_field_value(field_def, task_data)
                # Update task_data immediately so subsequent fields can use it in context
                task_data[field_id] = simulated_value
            else:
                task_data[field_id] = None # Mark optional field as not filled

    # 3. Simulate Common Refinements (Style, Color, Composition, etc.)
    for field_def in COMMON_REFINEMENT_FIELDS:
        field_id = field_def["id"]
        is_required = field_def.get("required", False)
        should_simulate = True # Assume we simulate unless optional/required logic dictates otherwise

        # Handle mandatory fields (like target_platforms)
        if is_required:
            should_simulate = True
        # Handle optional fields
        elif not is_required:
            chance = ADDITIONAL_INSTRUCTIONS_CHANCE if field_id == "additional_instructions" else OPTIONAL_FIELD_CHANCE
            should_simulate = (random.random() < chance)

        if should_simulate:
             simulated_value = simulate_field_value(field_def, task_data)
             task_data[field_id] = simulated_value
        else:
             task_data[field_id] = None

    return task_data


# --- Exportable Function to Generate N Task Requests ---
def generate_simulation_dataset(n):
    """
    Generates a dataset of n simulated F&B task requests.

    This function orchestrates the generation of multiple task requests using the
    `generate_task_request` function and the defined task structures. It's designed
    to be imported and used by other Python files.

    Args:
        n (int): The number of task requests to generate. Must be 1 or greater.

    Returns:
        list: A list of dictionaries. Each dictionary represents a simulated task request.
              Returns an empty list if n < 1.

    --- ML Preprocessing Notes for Output Data ---
    The generated dataset contains various data types that require specific
    preprocessing before being used in most machine learning models:

    1.  Single-Choice Categorical (from 'dropdown'/'radio', e.g., task_category, presentation): String -> Needs One-Hot Encoding.
    2.  Multi-Choice Categorical (from 'tags'/'checkbox', e.g., features, props, target_platforms): List of Strings -> Needs Multi-Label Binarization.
    3.  Text Data (from 'text'/'text_area', e.g., item_name, scene_desc, ref_instructions): String -> Needs NLP Vectorization (TF-IDF, Embeddings).
    4.  Structured Data (from 'structured_list', e.g., menu_items): List of Dicts -> Needs Flattening/Feature Engineering.
    5.  Boolean Data (from 'checkbox_bool', e.g., include_logo): Boolean -> Convert to 0/1.
    6.  Missing Values (None): Represents optional fields not filled -> Needs Imputation or specific model handling.
    7.  Placeholder URLs (from 'file_upload', e.g., ref_image): String (URL) -> Binary feature (present/absent) or extract/encode query params.

    Use tools like scikit-learn's `ColumnTransformer` and `Pipeline` to apply
    these different preprocessing steps systematically.
    """
    # (Implementation remains the same as v2.2)
    if not isinstance(n, int) or n < 1:
        print("Error: Number of task requests requested (n) must be a positive integer.")
        return []
    print(f"Starting generation of {n} simulated task requests...")
    dataset = []
    for i in range(n):
        task = generate_task_request()
        dataset.append(task)
        if (i + 1) % 10 == 0 or n <= 10:
             print(f"Generated {i + 1}/{n} task requests...")
    print(f"\nFinished generating {len(dataset)} task requests.")
    for data in dataset:
        print(json.dumps(data, indent=4))
    return dataset


# --- Main Execution Block ---
if __name__ == "__main__":
    # (Implementation remains the same as v2.2)
    print("Running task request simulation script directly...")
    simulated_data = generate_simulation_dataset(DEFAULT_NUM_PROFILES)
    if simulated_data:
        print(f"\nAttempting to save data to {OUTPUT_FILENAME}...")
        try:
            with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
                json.dump(simulated_data, f, indent=4, ensure_ascii=False)
            print(f"Successfully saved {len(simulated_data)} task requests to {OUTPUT_FILENAME}")
        except IOError as e:
            print(f"\nError: Could not save dataset. IOError: {e}")
        except TypeError as e:
             print(f"\nError: Could not serialize dataset to JSON. TypeError: {e}")
             for idx, item in enumerate(simulated_data):
                 try: json.dumps(item)
                 except TypeError:
                     print(f"\nSerialization error likely occurred at index {idx}:")
                     print(f"Item keys: {list(item.keys())}")
                     break
    else:
        print("\nNo data generated, skipping file save.")

