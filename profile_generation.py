import random
import json
import uuid # For generating unique IDs in placeholders

# --- Configuration (for standalone execution) ---
DEFAULT_NUM_PROFILES = 1 # Number of profiles to generate when run directly
OUTPUT_FILENAME = "simulated_profiles.json" # Filename for standalone execution

# --- Define Form Structure and Options ---
# Based on dynamic_form_word_format_v1

# Helper lists for conditions
RESTAURANT_CAFE_TYPES = [
    'Casual Dining Restaurant', 'Fine Dining Restaurant', 'Quick Service Restaurant (QSR) / Fast Food',
    'Cafe / Coffee Shop / Kopitiam', 'Ghost Kitchen / Cloud Kitchen / Virtual Brand',
    'Food Truck / Stall / Hawker Stall', 'Catering Service (Events, Corporate)' # Added Catering based on Q4a condition in source
]
BAKERY_TYPES = ['Bakery / Patisserie']
FOOD_TRUCK_TYPES = ['Food Truck / Stall / Hawker Stall']
CATERING_TYPES = ['Catering Service (Events, Corporate)']
BAR_TYPES = ['Bar / Pub / Lounge']

# Flattened options for easier sampling where applicable
# (Keeping these definitions at module level for accessibility by functions)
CUISINE_OPTIONS_FLAT = [
    'Malay', 'Chinese Malaysian', 'Indian Malaysian (Mamak)', 'Nyonya/Peranakan', 'Borneo Native (Specify)', 'Other Malaysian Regional',
    'Japanese', 'Korean', 'Thai', 'Vietnamese', 'Indonesian', 'Filipino', 'Chinese (Regional/General)', 'Indian (Regional/General)', 'Middle Eastern', 'Other Asian (Specify)',
    'Italian', 'French', 'Spanish', 'American (General/Burgers/Steak)', 'British/Irish', 'Other European (Specify)',
    'Mexican/Latin American', 'African (Specify Region)', 'Caribbean',
    'Fusion', 'Gastropub', 'Seafood', 'Pizzeria', 'Sandwiches/Deli', 'Noodles/Rice Bowls', 'Tapas/Small Plates', 'Breakfast/Brunch Focus', 'Healthy/Salads', 'Plant-Based/Vegan', 'Vegetarian', 'Halal Certified/Muslim-Friendly', 'Gluten-Free Focus', 'Other'
]
SERVICE_OPTIONS_FLAT = [
    'Dine-in (Reservations Recommended/Required)', 'Dine-in (Walk-ins Welcome)', 'Takeaway/Self-Pickup (\'Tapau\')', 'Curbside Pickup',
    'In-House Delivery', 'Third-Party Delivery Platforms', 'Drive-Thru', 'Counter Service', 'Table Service', 'Online Ordering (via Website/App/Social Media)'
]
BAKERY_GOODS_FLAT = [
    'Artisan Bread', 'Local Breads (e.g., Roti)', 'Pastries (Viennoiserie/Puffs)', 'Cakes (Custom/Celebration)', 'Local Kuih/Sweets',
    'Cupcakes', 'Cookies/Biscuits', 'Desserts (Plated/Individual)', 'Savory Items (Pies, Quiches, Puffs)', 'Gluten-Free Options', 'Vegan Options', 'Coffee/Tea/Beverages', 'Other'
]
BAKERY_SELLING_FLAT = [
    'Retail Storefront', 'Online Orders (Local Delivery)', 'Online Orders (Domestic/International Shipping)', 'Wholesale (to other businesses)', 'Markets/Pop-ups (Pasar Malam/Pagi)', 'Catering/Events'
]
FOOD_TRUCK_LOCATIONS_FLAT = [
    'Fixed Hawker Centre Stall', 'Roadside Stall (Regular Location)', 'Mobile Truck (Rotating Locations)', 'Office Parks/Commercial Areas', 'Events/Festivals/Carnivals', 'Markets (Pasar Malam/Pagi)', 'Private Catering/Functions'
]
CATERING_EVENTS_FLAT = [
    'Corporate Events/Meetings', 'Weddings/Engagements', 'Private Parties (Birthdays, Anniversaries)', 'Religious/Cultural Functions', 'Social Gatherings', 'Festivals/Public Events', 'Institutional (Schools, Hospitals)', 'Drop-off Catering/Packed Meals', 'Full-Service Catering'
]
BAR_OFFERINGS_FLAT = [
    'Beer Selection (Local/Import/Craft)', 'Wine List', 'Signature/Craft Cocktails', 'Spirits Selection (Whiskey, Gin etc.)', 'Non-Alcoholic Specialties/Mocktails',
    'Bar Snacks/Small Plates (\'Cicchetti\')', 'Full Food Menu', 'Live Music/Bands/DJs', 'Sports Screening', 'Games (Pool, Darts)', 'Quiz Nights/Events', 'Specific Theme/Atmosphere', 'Other'
]
AUDIENCE_OPTIONS_FLAT = [
    'Families with Children', 'Young Adults (18-30)', 'Professionals/Office Workers (30-55)', 'Seniors (55+)', 'Students (University/College)',
    'Tourists/Visitors (International/Domestic)', 'Local Residents/Community', 'Budget-Conscious Consumers', 'Affluent Consumers', 'Health-Conscious/Wellness Focused',
    'Eco-Conscious Consumers', 'Foodies/Adventurous Eaters', 'Expatriates', 'Specific Dietary Needs (Vegan, GF, Halal, etc.)', 'Business/Corporate Clients', 'Event Planners', 'Other'
]
MARKETING_GOALS_FLAT = [
    'Increase Social Media Likes/Follows/Shares', 'Encourage User-Generated Content/Reviews', 'Build Online Community/Group',
    'Drive Foot Traffic/Reservations', 'Increase Online Orders/Delivery', 'Promote Specific Menu Items/Products', 'Boost Sales During Off-Peak Hours/Specific Days',
    'Build General Brand Awareness', 'Launch New Location/Product/Menu', 'Announce Events/Promotions/Offers', 'Highlight Unique Selling Points',
    'Promote Loyalty Program/Membership', 'Attract Repeat Customers', 'Share updates via WhatsApp Business / Social Media Stories', 'Other'
]
PRIMARY_STYLE_OPTIONS_FLAT = [
    'Modern/Contemporary', 'Rustic/Natural', 'Vintage/Retro', 'Minimalist/Clean', 'Cozy/Comfortable (\'LePak\')', 'Elegant/Sophisticated',
    'Casual/Relaxed', 'Playful/Quirky', 'Industrial', 'Luxe/Opulent', 'Tropical', 'Heritage/Traditional',
    'Vibrant/Bold/Energetic', 'Muted/Subtle/Calm', 'Dark/Moody', 'Light/Airy', 'Classic', 'Whimsical/Creative', 'Nostalgic', 'Other'
]
SECONDARY_STYLE_OPTIONS_FLAT = PRIMARY_STYLE_OPTIONS_FLAT + [ # Include primary options plus extras
    'Instagrammable/Photo-worthy', 'Family-Friendly', 'Romantic', 'Tech-Integrated', 'Community-Focused', 'Sustainable/Eco-Friendly', 'Artsy/Cultural', 'Wabi-Sabi (Imperfect Beauty)'
]
IMAGERY_NEEDS_FLAT = [
    'High-Quality Dish Photography (Styled)', 'Close-up/Detail Shots (\'Food Porn\')', 'Menu Item Features', 'Beverage Photography', 'Ingredient Shots/Preparation Process',
    'Interior/Ambiance Photos (Day/Night)', 'Exterior/Facade Photos', 'Lifestyle Shots', 'Behind-the-Scenes/Staff/Chef Action Shots',
    'Images for Social Media Posts', 'Website Banners/Heroes', 'Email Marketing Visuals', 'Online Ad Creatives', 'Print Menu Design Elements', 'Event Promotion Visuals', 'User-Generated Content Campaign Starters'
]


FORM_STRUCTURE = [
    # --- Step 1 ---
    {"id": "q1", "type": "dropdown", "options": [
        'Cafe / Coffee Shop / Kopitiam', 'Casual Dining Restaurant', 'Fine Dining Restaurant', 'Quick Service Restaurant (QSR) / Fast Food',
        'Bakery / Patisserie', 'Food Truck / Stall / Hawker Stall', 'Catering Service (Events, Corporate)', 'Bar / Pub / Lounge',
        'Ghost Kitchen / Cloud Kitchen / Virtual Brand', 'Specialty Food Shop (e.g., Grocer, Butcher, Deli)', 'Meal Kit / Subscription Box Service',
        'Beverage Producer / Shop (e.g., Juice Bar, Bubble Tea, Brewery)', 'Other'], "condition": None},
    {"id": "q1a", "type": "text", "options": None, "condition": ('q1', '==', 'Other')},
    {"id": "q2", "type": "radio", "options": [
        'Micro (1-5 employees / Single Owner-Operator)', 'Small (6-20 employees / Single Location)',
        'Medium (21-100 employees / Few Locations)', 'Large (101+ employees / Multi-location / Chain)'], "condition": None},
    {"id": "q3", "type": "text", "options": None, "condition": None},

    # --- Step 2 ---
    {"id": "q4a", "type": "checkbox", "options": CUISINE_OPTIONS_FLAT, "max_select": 5, "condition": ('q1', 'in', RESTAURANT_CAFE_TYPES)},
    {"id": "q4b", "type": "checkbox", "options": SERVICE_OPTIONS_FLAT, "max_select": 4, "condition": ('q1', 'in', RESTAURANT_CAFE_TYPES)}, # Adjusted condition slightly
    {"id": "q4c", "type": "checkbox", "options": BAKERY_GOODS_FLAT, "max_select": 5, "condition": ('q1', 'in', BAKERY_TYPES)},
    {"id": "q4d", "type": "checkbox", "options": BAKERY_SELLING_FLAT, "max_select": 3, "condition": ('q1', 'in', BAKERY_TYPES)},
    {"id": "q4e", "type": "checkbox", "options": FOOD_TRUCK_LOCATIONS_FLAT, "max_select": 3, "condition": ('q1', 'in', FOOD_TRUCK_TYPES)},
    {"id": "q4f", "type": "checkbox", "options": CATERING_EVENTS_FLAT, "max_select": 4, "condition": ('q1', 'in', CATERING_TYPES)},
    {"id": "q4g", "type": "checkbox", "options": BAR_OFFERINGS_FLAT, "max_select": 5, "condition": ('q1', 'in', BAR_TYPES)},
    {"id": "q5", "type": "checkbox", "options": AUDIENCE_OPTIONS_FLAT, "max_select": 4, "condition": None}, # Limit 1-4 as per form text
    {"id": "q6", "type": "checkbox", "options": MARKETING_GOALS_FLAT, "max_select": 5, "condition": None},

    # --- Step 3 ---
    {"id": "q7", "type": "file_upload", "options": None, "condition": None},
    {"id": "q8", "type": "color_picker", "options": None, "num_colors": (2, 4), "condition": None}, # Simulate 2-4 colors
    {"id": "q9", "type": "radio", "options": PRIMARY_STYLE_OPTIONS_FLAT, "condition": None},
    {"id": "q9a", "type": "checkbox", "options": SECONDARY_STYLE_OPTIONS_FLAT, "max_select": 3, "condition": None}, # Optional, so might be empty

    # --- Step 4 (Optional - simulate lower chance of filling these) ---
    {"id": "q10", "type": "checkbox", "options": IMAGERY_NEEDS_FLAT, "max_select": 5, "condition": None, "optional_chance": 0.7},
    {"id": "q11", "type": "file_upload", "options": None, "condition": None, "optional_chance": 0.3},
    {"id": "q12", "type": "file_upload", "options": None, "condition": None, "optional_chance": 0.2},
    {"id": "q13", "type": "text_area", "options": None, "condition": None, "optional_chance": 0.5},
]

# --- Helper Functions (Module Level) ---

def evaluate_condition(condition, current_response):
    """Checks if a question's condition is met based on previous answers."""
    if condition is None:
        return True

    q_id, operator, value = condition
    # Ensure the prerequisite answer exists before trying to evaluate
    if q_id not in current_response or current_response[q_id] is None:
        return False # Can't evaluate if the prerequisite question wasn't answered or applicable

    response_value = current_response[q_id]

    try:
        if operator == '==':
            return response_value == value
        elif operator == '!=':
            return response_value != value
        elif operator == 'in':
            # Ensure value is iterable (list, tuple, set) for 'in' operator
            if not isinstance(value, (list, tuple, set)):
                 print(f"Warning: 'in' operator expects an iterable value for condition: {condition}")
                 return False
            return response_value in value
        elif operator == 'not in':
             # Ensure value is iterable (list, tuple, set) for 'not in' operator
            if not isinstance(value, (list, tuple, set)):
                 print(f"Warning: 'not in' operator expects an iterable value for condition: {condition}")
                 return False
            return response_value not in value
        else:
            print(f"Warning: Unknown operator '{operator}' in condition: {condition}")
            return False
    except Exception as e:
        print(f"Error evaluating condition {condition} with response '{response_value}': {e}")
        return False


def simulate_text_input(question_id):
    """Generates placeholder text."""
    if question_id == 'q1a':
        return f"Other Business Type - {random.choice(['Events Space', 'Cookery School', 'Food Consultancy'])}"
    elif question_id == 'q3':
        # Simple Malaysian-like location simulation
        state = random.choice(['Selangor', 'Kuala Lumpur', 'Penang', 'Johor', 'Sabah', 'Sarawak', 'Melaka', 'Perak'])
        city = random.choice(['Petaling Jaya', 'George Town', 'Johor Bahru', 'Kota Kinabalu', 'Kuching', 'Subang Jaya', 'Ipoh', 'Shah Alam', 'Melaka City'])
        return f"{city}, {state}, Malaysia"
    # General handler for 'Other' specification text fields based on convention qXa
    elif question_id.endswith('a') and len(question_id) == 3: # Catches q1a, q9a (though q9a is checkbox) - refine if needed
         return f"Other specified - {random.choice(['Details A', 'Details B', 'Details C'])}"
    else: # Default placeholder for any other text field
        return f"Simulated Text {uuid.uuid4().hex[:6]}"

def simulate_text_area(question_id):
     """Generates longer placeholder text."""
     phrases = [
         "Focus on natural lighting.", "Highlight local ingredients.", "Must show Halal logo clearly.",
         "Avoid overly cluttered images.", "Prefer candid shots of customers.", "Showcase our unique packaging.",
         "Emphasize vibrant colors.", "Needs images suitable for Instagram Reels.", "No photos of alcohol."
     ]
     # Add some chance of being empty even if selected
     if random.random() < 0.1:
         return ""
     return random.choice(phrases) + f" (Simulated {uuid.uuid4().hex[:4]})"


def simulate_file_upload(question_id):
    """Generates placeholder filename."""
    prefix = "logo" if question_id == "q7" else "image_example"
    return f"{prefix}_sim_{uuid.uuid4().hex[:8]}.{random.choice(['png', 'jpg', 'svg'])}"

def simulate_color_picker(num_range):
    """Generates list of random hex color codes."""
    num_colors = random.randint(num_range[0], num_range[1])
    colors = []
    for _ in range(num_colors):
        colors.append(f"#{random.randint(0, 0xFFFFFF):06x}")
    return colors

# --- Core Simulation Function (Module Level) ---

def generate_profile(structure):
    """Generates a single simulated profile based on the form structure."""
    profile_data = {}
    answered_other = {} # Track if 'Other' was selected for fields needing text specification

    for question in structure:
        q_id = question["id"]
        condition = question.get("condition", None)
        q_type = question["type"]
        options = question.get("options", [])
        optional_chance = question.get("optional_chance", 1.0) # Default to 100% chance unless specified

        # Check condition first - if condition not met, mark as None and skip simulation
        if not evaluate_condition(condition, profile_data):
            profile_data[q_id] = None # Mark as not applicable / not shown
            continue

        # Decide if optional question should be answered based on chance
        if optional_chance < 1.0 and random.random() > optional_chance:
             profile_data[q_id] = None # Explicitly mark as skipped optional question
             continue

        # --- Simulate answer only if condition met and optional chance passed ---
        answer = None
        try:
            if q_type == "dropdown" or q_type == "radio":
                if options:
                    answer = random.choice(options)
                    if answer == 'Other':
                       answered_other[q_id] = True # Flag that 'Other' was chosen
                else:
                     print(f"Warning: No options defined for {q_id}")
                     answer = "Error: No Options"

            elif q_type == "checkbox":
                if options:
                    max_s = question.get("max_select", len(options))
                    # Ensure k is at least 1 if options exist, unless max_select is 0 (edge case)
                    min_k = 1 if len(options) > 0 and max_s > 0 else 0
                    # Ensure k is not more than available options or max_select
                    upper_bound = min(max_s, len(options))
                    if min_k > upper_bound: # Handle cases like max_select=0 or no options
                        k = 0
                    else:
                        k = random.randint(min_k, upper_bound)

                    if k > 0:
                        answer = random.sample(options, k)
                        if 'Other' in answer:
                            answered_other[q_id] = True # Flag that 'Other' was chosen
                    else:
                        answer = [] # Empty list if k is 0
                else:
                     print(f"Warning: No options defined for {q_id}")
                     answer = []

            elif q_type == "text":
                # Check if this text field is for specifying an 'Other' choice made previously
                is_other_specifier = False
                if condition and condition[1] == '==': # Simple check for 'Other' conditions like ('q1', '==', 'Other')
                     prereq_id = condition[0]
                     # Check if the prerequisite question's answer *was* 'Other'
                     if prereq_id in profile_data and profile_data[prereq_id] == 'Other':
                         is_other_specifier = True
                 # This logic might need refinement if 'Other' can be selected in checkboxes and trigger text

                answer = simulate_text_input(q_id) # Generate text regardless for simplicity now

            elif q_type == "text_area":
                 answer = simulate_text_area(q_id)
            elif q_type == "file_upload":
                answer = simulate_file_upload(q_id)
            elif q_type == "color_picker":
                num_range = question.get("num_colors", (1, 1))
                answer = simulate_color_picker(num_range)
            else:
                print(f"Warning: Unknown question type '{q_type}' for {q_id}")
                answer = "Error: Unknown Type"

        except Exception as e:
             print(f"Error simulating answer for {q_id} (Type: {q_type}): {e}")
             answer = "Error: Simulation Failed"

        profile_data[q_id] = answer

    # Return the raw profile data including None values
    return profile_data


# --- NEW Reusable Function ---
def generate_simulation_dataset(n):
    """
    Generates a dataset of n simulated F&B profiles based on FORM_STRUCTURE.

    Args:
        n (int): The number of profiles to generate.

    Returns:
        list: A list of dictionaries, where each dictionary represents a simulated profile.
              Returns an empty list if n is less than 1.
    """
    if n < 1:
        print("Warning: Number of profiles requested (n) must be 1 or greater.")
        return []

    print(f"Generating {n} simulated profiles...")
    dataset = []
    # Loop to generate n profiles
    for i in range(n):
        profile = generate_profile(FORM_STRUCTURE) # Assumes FORM_STRUCTURE is accessible
        dataset.append(profile)
        # Print progress indicator every 10 profiles or if n is small
        if (i + 1) % 10 == 0 or n <= 10:
             print(f"Generated {i + 1}/{n} profiles...")
    print(f"\nFinished generating {len(dataset)} profiles.")
    return dataset

# --- Main Execution Block (for running the script directly) ---
if __name__ == "__main__":
    # Generate the dataset using the function
    simulated_data = generate_simulation_dataset(DEFAULT_NUM_PROFILES)
    print(f"{simulated_data}")

    # Optional: Print the first generated profile for inspection
    # if simulated_data:
    #     print("\nFirst generated profile:")
    #     print(json.dumps(simulated_data[0], indent=4, ensure_ascii=False))

    # Export to JSON
    if simulated_data: # Only save if data was generated
        try:
            with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
                json.dump(simulated_data, f, indent=4, ensure_ascii=False)
            print(f"\nSuccessfully saved dataset to {OUTPUT_FILENAME}")
        except IOError as e:
            print(f"\nError saving dataset to {OUTPUT_FILENAME}: {e}")
        except TypeError as e:
             print(f"\nError during JSON serialization: {e}")
             # Optionally print the first problematic profile to help debug serialization issues
             # print("First profile data:", simulated_data[0])
    else:
        print("\nNo data generated, skipping file save.")

