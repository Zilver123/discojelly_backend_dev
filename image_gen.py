import replicate
import requests
import os
from pathlib import Path

def generate_image(args):
    print(args)
    output = replicate.run(
        "black-forest-labs/flux-1.1-pro",
        input=args
    )

    # The output is a list containing the URL of the generated image
    image_url = output
    # Get the Downloads folder path
    downloads_path = str(Path.home() / "Downloads")

    # Download and save the image
    response = requests.get(image_url)
    if response.status_code == 200:
        # Generate a filename using timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(downloads_path, f"cyberpunk_portrait_{timestamp}.webp")
        
        with open(filename, "wb") as f:
            f.write(response.content)
        return f"Image saved successfully to: {filename}"
    else:
        return "Failed to download the image"