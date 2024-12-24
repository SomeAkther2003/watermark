import os
from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip
from moviepy.config import change_settings
from colorama import init, Fore
from concurrent.futures import ThreadPoolExecutor

# Initialize colorama
init(autoreset=True)

# Set the correct path for ImageMagick if needed
change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})

def sanitize_path(path):
    """Sanitize the file path to remove any unwanted characters."""
    # Remove trailing quotes and strip any extra spaces
    return path.replace('"', '').strip()

def add_watermarks(video_path, top_watermark_text, middle_watermark_text, text_color, text_size, output_path):
    try:
        print(f"{Fore.CYAN}Processing video: {video_path}")
        video = VideoFileClip(video_path)
        
        print(f"{Fore.CYAN}Creating top watermark...")
        top_watermark = (TextClip(top_watermark_text, fontsize=text_size, color=text_color, font='Arial-Bold')
                         .set_duration(video.duration)
                         .set_opacity(0.3)  # Opacity set to 30%
                         .set_pos(('center', 10)))  # Positioned at the top with 10 pixels padding from top

        print(f"{Fore.CYAN}Creating middle watermark...")
        middle_watermark = (TextClip(middle_watermark_text, fontsize=text_size, color=text_color, font='Arial-Bold')
                            .set_duration(video.duration)
                            .set_opacity(0.3)  # Opacity set to 30%
                            .set_pos(('center', 'center')))  
        
        print(f"{Fore.CYAN}Compositing video with watermarks...")
        final_video = CompositeVideoClip([video, top_watermark, middle_watermark])
        
        # Sanitize the output path to remove any invalid characters
        corrected_output_path = sanitize_path(output_path)

        print(f"{Fore.CYAN}Writing final video to {corrected_output_path}...")
        final_video.write_videofile(corrected_output_path, codec="libx264", preset="ultrafast", fps=video.fps, verbose=True)
        print(f"{Fore.GREEN}Processed {video_path}")
        
    except Exception as e:
        print(f"{Fore.RED}Error processing {video_path}: {e}")

def process_videos_in_folder(folder_path, top_watermark_text, middle_watermark_text, text_color, text_size, output_folder):
    # Clean the folder path
    folder_path = sanitize_path(folder_path)
    
    try:
        video_files = [f for f in os.listdir(folder_path) if f.endswith((".mp4", ".avi", ".mov", ".mkv"))]
    except OSError as e:
        print(f"{Fore.RED}Error accessing the folder: {e}")
        return
    
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = []
        for filename in video_files:
            video_path = os.path.join(folder_path, filename)
            output_path = os.path.join(sanitize_path(output_folder), "edited_" + filename)
            futures.append(executor.submit(add_watermarks, video_path, top_watermark_text, middle_watermark_text, text_color, text_size, output_path))
        
        for future in futures:
            future.result()  # Wait for all tasks to complete

print(Fore.BLUE + "Please enter the following details:")
folder_path = input(Fore.YELLOW + "Enter the folder path containing videos: ").strip('"').strip()
top_watermark_text = input(Fore.YELLOW + "Enter the top watermark text: ").strip('"')
middle_watermark_text = input(Fore.YELLOW + "Enter the middle watermark text: ").strip('"')
text_color = input(Fore.YELLOW + "Enter the text color (e.g., 'white', 'red'): ").strip('"')
text_size = int(input(Fore.YELLOW + "Enter the text size (e.g., 24): "))
output_folder = input(Fore.YELLOW + "Enter the output folder path: ").strip('"').strip()

process_videos_in_folder(folder_path, top_watermark_text, middle_watermark_text, text_color, text_size, output_folder)
