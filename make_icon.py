from PIL import Image

try:
    # 1. Open your original PNG
    logo = Image.open("AppIcon.png")
    
    # 2. Save it as a true, multi-layered Windows ICO file
    logo.save("AppIcon.ico", format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32)])
    
    print("SUCCESS! You now have a perfect AppIcon.ico file.")
except Exception as e:
    print(f"Error: {e}")