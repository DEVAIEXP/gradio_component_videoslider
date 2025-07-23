import gradio as gr
from gradio_videoslider import VideoSlider
import os

# --- 1. DEFINE THE PATHS TO YOUR LOCAL VIDEOS ---
#
# IMPORTANT: Replace the values below with the paths to YOUR video files.
#
# Option A: Relative Path (if the video is in the same folder as this app.py)
# video_path_1 = "video_before.mp4"
# video_path_2 = "video_after.mp4"
#
# Option B: Absolute Path (the full path to the file on your computer)
# Example for Windows:
# video_path_1 = "C:\\Users\\YourName\\Videos\\my_video_1.mp4"
#
# Example for Linux/macOS:
# video_path_1 = "/home/yourname/videos/my_video_1.mp4"

# Set your file paths here:
video_path_1 = "examples/SampleVideo 720x480.mp4"
video_path_2 = "examples/SampleVideo 1280x720.mp4"


# --- 2. FUNCTION FOR THE UPLOAD EXAMPLE ---
def process_uploaded_videos(video_inputs):
    """This function handles the uploaded videos."""
    print("Received videos from upload:", video_inputs)
    return video_inputs


# --- 3. GRADIO INTERFACE ---
with gr.Blocks() as demo:
    gr.Markdown("# Video Slider Component Usage Examples")
    gr.Markdown("<span>💻 <a href='https://github.com/DEVAIEXP/gradio_component_videoslider'>Component GitHub Code</a></span>")

    with gr.Tabs():
        # --- TAB 1: UPLOAD EXAMPLE ---
        with gr.TabItem("1. Compare via Upload"):
            gr.Markdown("## Upload two videos to compare them side-by-side.")
            video_slider_input = VideoSlider(label="Your Videos", height=400, width=700, video_mode="upload")
            video_slider_output = VideoSlider(
                label="Video comparision",
                interactive=False,
                autoplay=True,                
                video_mode="preview",
                show_download_button=False,
                loop=True,
                height=400,
                width=700
            )
            submit_btn = gr.Button("Submit")
            submit_btn.click(
                fn=process_uploaded_videos,
                inputs=[video_slider_input],
                outputs=[video_slider_output]
            )

        # --- TAB 2: LOCAL FILE EXAMPLE ---
        with gr.TabItem("2. Compare Local Files"):
            gr.Markdown("## Example with videos pre-loaded from your local disk.")
            
            # This is the key part: we pass a tuple of your local file paths to the `value` parameter.
            VideoSlider(
                label="Video comparision",
                value=(video_path_1, video_path_2),
                interactive=False,
                show_download_button=False,
                autoplay=True,
                video_mode="preview",
                loop=True,
                height=400,
                width=700
            )

# A check to give a helpful error message if files are not found.
if not os.path.exists(video_path_1) or not os.path.exists(video_path_2):
    print("---")
    print(f"WARNING: Could not find one or both video files.")
    print(f"Please make sure these paths are correct in your app.py file:")
    print(f"  - '{os.path.abspath(video_path_1)}'")
    print(f"  - '{os.path.abspath(video_path_2)}'")
    print("---")

if __name__ == '__main__':
    demo.launch(debug=True)
