# -*- coding: utf-8 -*-
"""
Generates a synthetic dataset of F&B business profiles based on a simulated
multi-step onboarding form structure.

This script simulates user responses, including handling conditional logic
based on previous answers, and outputs the dataset as a JSON file.
The generated data contains various types (categorical strings, lists of strings,
free text, placeholders, None) and requires standard ML preprocessing before
use in most models.

To use the generation logic in other files, import the
`generate_simulation_dataset` function.
"""

import random
import json
import uuid # For generating unique IDs in placeholders

# --- Configuration (for standalone execution) ---
# Feel free to change these when running the script directly
DEFAULT_NUM_PROFILES = 100 # Number of profiles to generate when run directly
OUTPUT_FILENAME = "simulated_fb_profiles.json" # Filename for standalone execution

# --- Define Form Structure and Options ---
# This section defines the structure of the form being simulated.
# It's based on the form described in 'dynamic_form_word_format_v1'.

# Helper lists for defining conditions based on business type (q1)
RESTAURANT_CAFE_TYPES = [
    'Casual Dining Restaurant', 'Fine Dining Restaurant', 'Quick Service Restaurant (QSR) / Fast Food',
    'Cafe / Coffee Shop / Kopitiam', 'Ghost Kitchen / Cloud Kitchen / Virtual Brand',
    'Food Truck / Stall / Hawker Stall', 'Catering Service (Events, Corporate)'
]
BAKERY_TYPES = ['Bakery / Patisserie']
FOOD_TRUCK_TYPES = ['Food Truck / Stall / Hawker Stall']
CATERING_TYPES = ['Catering Service (Events, Corporate)']
BAR_TYPES = ['Bar / Pub / Lounge']

# Flattened lists of options for questions (especially checkboxes)
# Kept at module level for easy access by simulation functions.
# These lists contain the human-readable options that will be selected during simulation.
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


# FORM_STRUCTURE defines the sequence, type, options, and conditions for each question.
# - id: Unique identifier for the question/answer key.
# - type: Input type (dropdown, radio, checkbox, text, text_area, file_upload, color_picker).
# - options: List of possible choices for selection types.
# - condition: Tuple defining display logic: (prerequisite_q_id, operator, value(s)). None means always shown.
# - max_select: (For checkbox) Max number of items to randomly select.
# - optional_chance: (For optional questions) Probability (0.0 to 1.0) the question is answered if conditions are met.
FORM_STRUCTURE = [
    # --- Step 1 ---
    {"id": "q1", "type": "dropdown", "options": [
        'Cafe / Coffee Shop / Kopitiam', 'Casual Dining Restaurant', 'Fine Dining Restaurant', 'Quick Service Restaurant (QSR) / Fast Food',
        'Bakery / Patisserie', 'Food Truck / Stall / Hawker Stall', 'Catering Service (Events, Corporate)', 'Bar / Pub / Lounge',
        'Ghost Kitchen / Cloud Kitchen / Virtual Brand', 'Specialty Food Shop (e.g., Grocer, Butcher, Deli)', 'Meal Kit / Subscription Box Service',
        'Beverage Producer / Shop (e.g., Juice Bar, Bubble Tea, Brewery)', 'Other'], "condition": None},
    {"id": "q1a", "type": "text", "options": None, "condition": ('q1', '==', 'Other')}, # Shown only if q1 is 'Other'
    {"id": "q2", "type": "radio", "options": [
        'Micro (1-5 employees / Single Owner-Operator)', 'Small (6-20 employees / Single Location)',
        'Medium (21-100 employees / Few Locations)', 'Large (101+ employees / Multi-location / Chain)'], "condition": None},
    {"id": "q3", "type": "text", "options": None, "condition": None}, # Location text

    # --- Step 2 (Conditional Questions based on q1) ---
    {"id": "q4a", "type": "checkbox", "options": CUISINE_OPTIONS_FLAT, "max_select": 5, "condition": ('q1', 'in', RESTAURANT_CAFE_TYPES)},
    {"id": "q4b", "type": "checkbox", "options": SERVICE_OPTIONS_FLAT, "max_select": 4, "condition": ('q1', 'in', RESTAURANT_CAFE_TYPES)},
    {"id": "q4c", "type": "checkbox", "options": BAKERY_GOODS_FLAT, "max_select": 5, "condition": ('q1', 'in', BAKERY_TYPES)},
    {"id": "q4d", "type": "checkbox", "options": BAKERY_SELLING_FLAT, "max_select": 3, "condition": ('q1', 'in', BAKERY_TYPES)},
    {"id": "q4e", "type": "checkbox", "options": FOOD_TRUCK_LOCATIONS_FLAT, "max_select": 3, "condition": ('q1', 'in', FOOD_TRUCK_TYPES)},
    {"id": "q4f", "type": "checkbox", "options": CATERING_EVENTS_FLAT, "max_select": 4, "condition": ('q1', 'in', CATERING_TYPES)},
    {"id": "q4g", "type": "checkbox", "options": BAR_OFFERINGS_FLAT, "max_select": 5, "condition": ('q1', 'in', BAR_TYPES)},
    # --- Step 2 (Unconditional Questions) ---
    {"id": "q5", "type": "checkbox", "options": AUDIENCE_OPTIONS_FLAT, "max_select": 4, "condition": None}, # Target Audience
    {"id": "q6", "type": "checkbox", "options": MARKETING_GOALS_FLAT, "max_select": 5, "condition": None}, # Marketing Goals

    # --- Step 3 ---
    {"id": "q7", "type": "file_upload", "options": None, "condition": None}, # Logo upload placeholder
    {"id": "q8", "type": "color_picker", "options": None, "num_colors": (2, 4), "condition": None}, # Simulate 2-4 brand colors
    {"id": "q9", "type": "radio", "options": PRIMARY_STYLE_OPTIONS_FLAT, "condition": None}, # Primary Visual Style
    {"id": "q9a", "type": "checkbox", "options": SECONDARY_STYLE_OPTIONS_FLAT, "max_select": 3, "condition": None}, # Secondary Visual Style

    # --- Step 4 (Optional Questions - simulate lower chance of filling these) ---
    {"id": "q10", "type": "checkbox", "options": IMAGERY_NEEDS_FLAT, "max_select": 5, "condition": None, "optional_chance": 0.7}, # Imagery Needs (70% chance)
    {"id": "q11", "type": "file_upload", "options": None, "condition": None, "optional_chance": 0.3}, # Liked examples (30% chance)
    {"id": "q12", "type": "file_upload", "options": None, "condition": None, "optional_chance": 0.2}, # Disliked examples (20% chance)
    {"id": "q13", "type": "text_area", "options": None, "condition": None, "optional_chance": 0.5}, # Specific Requests (50% chance)
]

# --- Helper Functions (Module Level) ---

def evaluate_condition(condition, current_response):
    """
    Checks if a question's display condition is met based on previous answers.

    Args:
        condition (tuple or None): The condition tuple (q_id, operator, value)
                                   or None if always shown.
        current_response (dict): The dictionary of answers simulated so far.

    Returns:
        bool: True if the condition is met (or no condition), False otherwise.
    """
    if condition is None:
        return True # No condition, always show/evaluate

    q_id, operator, value = condition
    # Check if the prerequisite question has been answered and is not None
    if q_id not in current_response or current_response[q_id] is None:
        return False # Condition cannot be met if prerequisite is missing

    response_value = current_response[q_id]

    # Perform the comparison based on the operator
    try:
        if operator == '==':
            return response_value == value
        elif operator == '!=':
            return response_value != value
        elif operator == 'in':
            # Ensure 'value' is iterable for the 'in' operator
            if not isinstance(value, (list, tuple, set)):
                 # Log a warning, but treat condition as False to avoid errors
                 print(f"Warning: 'in' operator expects an iterable value for condition: {condition}")
                 return False
            return response_value in value
        elif operator == 'not in':
             # Ensure 'value' is iterable for the 'not in' operator
            if not isinstance(value, (list, tuple, set)):
                 print(f"Warning: 'not in' operator expects an iterable value for condition: {condition}")
                 return False
            return response_value not in value
        else:
            # Log unknown operators
            print(f"Warning: Unknown operator '{operator}' in condition: {condition}")
            return False
    except Exception as e:
        # Log errors during evaluation
        print(f"Error evaluating condition {condition} with response '{response_value}': {e}")
        return False


def simulate_text_input(question_id):
    """Generates placeholder text for text input fields."""
    if question_id == 'q1a': # Specific text for 'Other' business type
        return f"Other Business Type - {random.choice(['Events Space', 'Cookery School', 'Food Consultancy'])}"
    elif question_id == 'q3': # Simulate a location
        # Simple Malaysian-like location simulation
        state = random.choice(['Selangor', 'Kuala Lumpur', 'Penang', 'Johor', 'Sabah', 'Sarawak', 'Melaka', 'Perak'])
        city = random.choice(['Petaling Jaya', 'George Town', 'Johor Bahru', 'Kota Kinabalu', 'Kuching', 'Subang Jaya', 'Ipoh', 'Shah Alam', 'Melaka City'])
        return f"{city}, {state}, Malaysia"
    # General handler for other text fields, potentially specifying 'Other' options
    elif question_id.endswith('a') and len(question_id) == 3:
         return f"Other specified - {random.choice(['Details A', 'Details B', 'Details C'])}"
    else: # Default placeholder for any other text field
        return f"Simulated Text {uuid.uuid4().hex[:6]}"

def simulate_text_area(question_id):
     """Generates longer placeholder text for text area fields."""
     phrases = [
         "Focus on natural lighting.", "Highlight local ingredients.", "Must show Halal logo clearly.",
         "Avoid overly cluttered images.", "Prefer candid shots of customers.", "Showcase our unique packaging.",
         "Emphasize vibrant colors.", "Needs images suitable for Instagram Reels.", "No photos of alcohol.",
         "Modern minimalist aesthetic preferred.", "Include shots of the coffee making process."
     ]
     # Add some chance of the text area being left empty even if the question is shown
     if random.random() < 0.1:
         return "" # Simulate empty input
     return random.choice(phrases) + f" (Simulated Guideline {uuid.uuid4().hex[:4]})"


def simulate_file_upload(question_id):
    """Generates a placeholder filename for file upload fields."""
    prefix = "logo" if question_id == "q7" else "image_example"
    # Simulate different common image file extensions
    extension = random.choice(['png', 'jpg', 'jpeg', 'svg', 'webp'])
    return f"{prefix}_sim_{uuid.uuid4().hex[:8]}.{extension}"

def simulate_color_picker(num_range):
    """Generates a list of random hex color codes."""
    # Determine how many colors to generate within the specified range
    num_colors = random.randint(num_range[0], num_range[1])
    colors = []
    for _ in range(num_colors):
        # Generate a random 24-bit color hex string
        colors.append(f"#{random.randint(0, 0xFFFFFF):06x}")
    return colors

# --- Core Simulation Function (Module Level) ---

def generate_profile(structure):
    """
    Generates a single simulated profile dictionary based on the form structure.

    Args:
        structure (list): The FORM_STRUCTURE list defining questions, types,
                          options, and conditions.

    Returns:
        dict: A dictionary representing one simulated profile, with question IDs
              as keys and simulated answers as values. Includes None for questions
              not answered due to conditions or optional skipping.
    """
    profile_data = {}
    answered_other = {} # Tracks if 'Other' was selected for dropdown/radio/checkbox

    # Iterate through each question defined in the structure
    for question in structure:
        q_id = question["id"]
        condition = question.get("condition", None)
        q_type = question["type"]
        options = question.get("options", [])
        optional_chance = question.get("optional_chance", 1.0) # Default: not optional

        # 1. Check if the display condition for this question is met
        if not evaluate_condition(condition, profile_data):
            profile_data[q_id] = None # Mark as not applicable / not shown
            continue # Skip to the next question

        # 2. Check if an optional question is skipped by chance
        if optional_chance < 1.0 and random.random() > optional_chance:
             profile_data[q_id] = None # Mark as explicitly skipped optional question
             continue # Skip to the next question

        # --- If condition met and optional chance passed, simulate an answer ---
        answer = None
        try:
            # Simulate based on question type
            if q_type == "dropdown" or q_type == "radio":
                if options:
                    answer = random.choice(options)
                    # Flag if 'Other' is chosen to potentially trigger dependent text fields
                    if answer == 'Other':
                       answered_other[q_id] = True
                else:
                     # Log warning if a selection question has no options defined
                     print(f"Warning: No options defined for single-choice question {q_id}")
                     answer = "Error: No Options Defined"

            elif q_type == "checkbox":
                if options:
                    max_s = question.get("max_select", len(options)) # Max items to select
                    # Determine number of items (k) to select (at least 1 if possible)
                    min_k = 1 if len(options) > 0 and max_s > 0 else 0
                    upper_bound = min(max_s, len(options))
                    k = random.randint(min_k, upper_bound) if upper_bound >= min_k else 0

                    if k > 0:
                        answer = random.sample(options, k) # Select k unique options
                        # Flag if 'Other' is chosen among the selections
                        if 'Other' in answer:
                            answered_other[q_id] = True
                    else:
                        answer = [] # Select empty list if k is 0
                else:
                     # Log warning if checkbox question has no options
                     print(f"Warning: No options defined for checkbox question {q_id}")
                     answer = []

            elif q_type == "text":
                # Generate placeholder text (could be refined to check if it's specifying 'Other')
                answer = simulate_text_input(q_id)

            elif q_type == "text_area":
                 answer = simulate_text_area(q_id)
            elif q_type == "file_upload":
                answer = simulate_file_upload(q_id)
            elif q_type == "color_picker":
                num_range = question.get("num_colors", (1, 1)) # Get range of colors to pick
                answer = simulate_color_picker(num_range)
            else:
                # Log unknown question types
                print(f"Warning: Unknown question type '{q_type}' encountered for {q_id}")
                answer = f"Error: Unknown Type '{q_type}'"

        except Exception as e:
             # Log errors during the simulation process for a specific question
             print(f"Error simulating answer for {q_id} (Type: {q_type}): {e}")
             answer = "Error: Simulation Failed"

        # Store the simulated answer (or None if skipped/error)
        profile_data[q_id] = answer

    # Return the complete profile dictionary for this simulation run
    return profile_data


# --- Reusable Dataset Generation Function ---
def generate_simulation_dataset(n):
    """
    Generates a dataset of n simulated F&B profiles.

    This function orchestrates the generation of multiple profiles using the
    `generate_profile` function and the defined `FORM_STRUCTURE`.

    Args:
        n (int): The number of profiles to generate. Must be 1 or greater.

    Returns:
        list: A list of dictionaries. Each dictionary represents a simulated profile.
              Returns an empty list if n < 1.

    --- ML Preprocessing Notes for Output Data ---
    The generated dataset contains various data types that require specific
    preprocessing before being used in most machine learning models:

    1.  Single-Choice Categorical (from 'dropdown'/'radio', e.g., q1, q2, q9):
        - Type: String
        - Preprocessing: Needs encoding (e.g., One-Hot Encoding using
          sklearn.preprocessing.OneHotEncoder) to convert categories into
          numerical format.

    2.  Multi-Choice Categorical (from 'checkbox', e.g., q4a, q5, q6, q9a, q10):
        - Type: List of Strings
        - Preprocessing: Needs multi-label binarization (e.g., using
          sklearn.preprocessing.MultiLabelBinarizer) to create a binary
          vector/matrix indicating which options were selected.

    3.  Text Data (from 'text'/'text_area', e.g., q1a, q3, q13):
        - Type: String
        - Preprocessing: Requires Natural Language Processing (NLP) techniques
          to convert text into numerical vectors (e.g., TF-IDF using
          sklearn.feature_extraction.text.TfidfVectorizer, or more advanced
          word/sentence embeddings like Word2Vec, GloVe, Sentence-BERT).

    4.  Missing Values:
        - Type: None
        - Represents questions not shown due to conditional logic or optional
          questions skipped by chance.
        - Preprocessing: Requires a strategy for handling missing data, such as
          imputation (filling with mean, median, mode, or a constant value using
          sklearn.impute.SimpleImputer) or using ML models that can inherently
          handle missing values.

    5.  Placeholders (from 'file_upload'/'color_picker', e.g., q7, q8, q11, q12):
        - Type: String (filename) or List of Strings (hex codes)
        - Preprocessing: Needs custom handling depending on the ML goal.
          - File uploads might become a binary feature (0/1 for presence/absence).
          - Colors could be converted to numerical representations (e.g., RGB vectors)
            or treated categorically if a fixed palette emerges.

    Use tools like scikit-learn's `ColumnTransformer` and `Pipeline` to apply
    these different preprocessing steps systematically to the appropriate columns
    when preparing the data for model training.
    """
    # Validate input n
    if not isinstance(n, int) or n < 1:
        print("Error: Number of profiles requested (n) must be a positive integer.")
        return []

    print(f"Starting generation of {n} simulated profiles...")
    dataset = []
    # Loop n times to generate the specified number of profiles
    for i in range(n):
        # Generate one profile using the defined structure
        profile = generate_profile(FORM_STRUCTURE)
        dataset.append(profile)
        # Print progress update periodically
        if (i + 1) % 50 == 0 or n <= 50 and (i+1) % 10 == 0 : # More frequent for small n
             print(f"Generated {i + 1}/{n} profiles...")

    print(f"\nFinished generating {len(dataset)} profiles.")
    return dataset

# --- Main Execution Block ---
# This code runs only when the script is executed directly (not imported).
if __name__ == "__main__":
    print("Running profile simulation script directly...")

    # Generate the dataset using the reusable function
    simulated_data = generate_simulation_dataset(DEFAULT_NUM_PROFILES)

    # Export the generated dataset to a JSON file
    if simulated_data: # Proceed only if data generation was successful
        print(f"\nAttempting to save data to {OUTPUT_FILENAME}...")
        try:
            # Open the output file in write mode with UTF-8 encoding
            with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
                # Dump the dataset list into the file as JSON
                # indent=4 makes the file human-readable
                # ensure_ascii=False allows non-ASCII characters (important for names/locations)
                json.dump(simulated_data, f, indent=4, ensure_ascii=False)
            print(f"Successfully saved {len(simulated_data)} profiles to {OUTPUT_FILENAME}")
        except IOError as e:
            # Handle file writing errors
            print(f"\nError: Could not save dataset to {OUTPUT_FILENAME}. IOError: {e}")
        except TypeError as e:
            # Handle errors during JSON conversion (e.g., non-serializable data types)
             print(f"\nError: Could not serialize dataset to JSON. TypeError: {e}")
             # Optionally print the first problematic profile to help debug
             # if simulated_data:
             #     try:
             #         print("First profile data that might have caused issue:", simulated_data[0])
             #     except IndexError:
             #         print("Dataset appears empty.")
    else:
        # Message if no data was generated (e.g., if n=0 was requested)
        print("\nNo data generated, skipping file save.")

