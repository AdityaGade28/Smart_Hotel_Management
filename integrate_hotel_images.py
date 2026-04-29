import os
import shutil
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel_project.settings')
django.setup()

from hotels.models import Hotel

# Define source images from brain directory
# Note: These paths are absolute and point to the folder where the model generated them.
brain_dir = r"C:\Users\HP\.gemini\antigravity\brain\714d8de1-6710-4a7a-a2db-330130aba2b9"
media_hotel_dir = os.path.join("media", "hotel_images")

# Create directory if it doesn't exist
if not os.path.exists(media_hotel_dir):
    os.makedirs(media_hotel_dir)
    print(f"Created directory: {media_hotel_dir}")

# Image mapping: (Hotel Name substring, source filename, target filename)
image_map = [
    ("Mumbai Palace", "grand_mumbai_palace_1775846635400.png", "grand_mumbai.png"),
    ("Rajasthan", "rajasthan_haveli_1775846654444.png", "rajasthan_haveli.png"),
    ("Delhi", "delhi_business_suites_1775846672812.png", "delhi_suites.png"),
    ("Goa", "goa_beach_resort_1775846696607.png", "goa_resort.png"),
    ("Bengaluru", "bengaluru_tech_stay_v2_1775846720083.png", "bengaluru_tech.png"),
    ("Shimla", "shimla_retreat_v2_1775846736691.png", "shimla_retreat.png"),
]

print("Starting image integration...")

for hotel_sub, src_name, target_name in image_map:
    src_path = os.path.join(brain_dir, src_name)
    target_path = os.path.join(media_hotel_dir, target_name)
    
    # 1. Copy the file
    if os.path.exists(src_path):
        shutil.copy2(src_path, target_path)
        print(f"Copied {src_name} to {target_path}")
    else:
        print(f"Warning: Source file not found: {src_path}")
        continue

    # 2. Update the Database
    try:
        hotel = Hotel.objects.filter(name__icontains=hotel_sub).first()
        if hotel:
            # The field 'image' in models.py is upload_to='hotel_images/'
            # So we set it to 'hotel_images/filename'
            hotel.image = f"hotel_images/{target_name}"
            hotel.save()
            print(f"Updated database for: {hotel.name}")
        else:
            print(f"Warning: No hotel found containing '{hotel_sub}'")
    except Exception as e:
        print(f"Error updating database for '{hotel_sub}': {e}")

print("Integration complete!")
