import sys
import os
import cv2
from PIL import Image
from classifier_service import classify_waste

def print_colored_result(result: dict):
    """
    Prints a beautiful, color-coded block in the terminal representing the sorting decision.
    """
    item = result.get("item_identified", "Unknown")
    fraction = result.get("fraction", "Unknown")
    bin_color = result.get("bin_color", "Unknown").upper()
    action = result.get("action_required", "Unknown")
    
    # ANSI color mapping (Background Code, Foreground Code)
    ansi_colors = {
        "YELLOW": ("\033[43;30m", "\033[93m"),        # Yellow bg (black text) / Yellow text
        "BLUE": ("\033[44;37m", "\033[94m"),          # Blue bg (white text) / Blue text
        "GREEN": ("\033[42;30m", "\033[92m"),         # Green bg (black text) / Green text
        "BROWN": ("\033[48;5;94;37m", "\033[38;5;94m"), # Brown bg (white text) / Brown text
        "BLACK": ("\033[40;37m", "\033[90m"),         # Black bg (white text) / Gray text
        "STORE RETURN": ("\033[46;30m", "\033[96m"),  # Cyan bg (black text) / Cyan text
    }
    
    bg_code, fg_code = ansi_colors.get(bin_color, ("\033[7m", "\033[1m"))
    reset = "\033[0m"
    bold = "\033[1m"
    
    print("\n" + "=" * 50)
    print(f"{bold}♻️  WROCŁAW WASTE SORTING DECISION ♻️{reset}")
    print("=" * 50)
    print(f"📦 {bold}Item Identified:{reset} {item}")
    print(f"🏷️  {bold}Fraction:{reset} {fg_code}{bold}{fraction}{reset}")
    print(f"🗑️  {bold}Bin Color:{reset} {bg_code}  {bin_color}  {reset}")
    print(f"⚡ {bold}Action Required:{reset} \033[91;1m{action}{reset}")
    print("=" * 50 + "\n")

def run_file_classification(file_path: str):
    """
    Load an image from path and classify it.
    """
    if not os.path.exists(file_path):
        print(f"❌ Error: File '{file_path}' does not exist.")
        sys.exit(1)
        
    print(f"📸 Loading image from: {file_path} ...")
    try:
        image = Image.open(file_path)
        print("🧠 Calling Vision API...")
        result = classify_waste(image)
        print_colored_result(result)
    except Exception as e:
        print(f"❌ Error classifying waste: {e}")
        sys.exit(1)

def run_camera_classification():
    """
    Open the default webcam, show live feed with on-screen commands,
    snap a photo on SPACE, and run waste classification.
    """
    print("📷 Initializing camera...")
    # Open default video capture device (0 is typically the built-in webcam)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Error: Could not open camera.")
        print("\n💡 Troubleshooting:")
        print("1. Grant terminal camera access in macOS Settings > Privacy & Security > Camera.")
        print("2. Alternatively, specify a local file path instead:")
        print("   python waste_classifier_cli.py <path_to_image>")
        sys.exit(1)
        
    print("✅ Camera ready! Press SPACE in the preview window to capture, or ESC to quit.")
    
    window_name = "Wrocław Waste Sorting Assistant"
    cv2.namedWindow(window_name)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to grab frame from camera.")
            break
            
        # Create a copy for displaying text instructions
        display_frame = frame.copy()
        
        # Display instructions overlay on frame
        instruction_text = "Press SPACE to Scan | ESC to Quit"
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(display_frame, instruction_text, (20, 40), font, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
        
        # Display window
        cv2.imshow(window_name, display_frame)
        
        # Key handling
        key = cv2.waitKey(1) & 0xFF
        
        if key == 27: # ESC key
            print("👋 Exiting camera.")
            break
        elif key == 32: # SPACE key
            print("📸 Snapped frame! Processing...")
            
            # Convert BGR (OpenCV format) to RGB (PIL format)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            
            # Show a processing window text
            processing_frame = frame.copy()
            cv2.putText(processing_frame, "PROCESSING...", (20, 40), font, 0.9, (0, 0, 255), 2, cv2.LINE_AA)
            cv2.imshow(window_name, processing_frame)
            cv2.waitKey(100) # give CV time to refresh window
            
            try:
                result = classify_waste(pil_image)
                print_colored_result(result)
            except Exception as e:
                print(f"❌ Error during API classification: {e}")
                
            print("\n💡 Press SPACE to scan another item, or ESC to exit.")
            
    # Clean up
    cap.release()
    cv2.destroyAllWindows()

def main():
    if len(sys.argv) > 1:
        # File mode
        run_file_classification(sys.argv[1])
    else:
        # Camera mode
        run_camera_classification()

if __name__ == "__main__":
    main()
