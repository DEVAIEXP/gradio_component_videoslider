
import gradio as gr
from app import demo as app
import os

_docs = {'VideoSlider': {'description': 'A custom Gradio component to display a side-by-side video comparison with a slider.\nCan be used as an input (for uploading two videos) or as an output (for displaying two videos).', 'members': {'__init__': {'value': {'type': 'typing.Union[\n    typing.Tuple[str | pathlib.Path, str | pathlib.Path],\n    typing.Callable,\n    NoneType,\n][\n    typing.Tuple[str | pathlib.Path, str | pathlib.Path][\n        str | pathlib.Path, str | pathlib.Path\n    ],\n    Callable,\n    None,\n]', 'default': 'None', 'description': 'A tuple of two video file paths or URLs to display initially. Can also be a callable.'}, 'height': {'type': 'int | None', 'default': 'None', 'description': 'The height of the component container in pixels.'}, 'width': {'type': 'int | None', 'default': 'None', 'description': 'The width of the component container in pixels.'}, 'label': {'type': 'str | None', 'default': 'None', 'description': 'The label for this component that appears above it.'}, 'every': {'type': 'float | None', 'default': 'None', 'description': "If `value` is a callable, run the function 'every' seconds while the client connection is open."}, 'show_label': {'type': 'bool | None', 'default': 'None', 'description': 'If False, the label is not displayed.'}, 'container': {'type': 'bool', 'default': 'True', 'description': 'If False, the component will not be wrapped in a container.'}, 'scale': {'type': 'int | None', 'default': 'None', 'description': "An integer that defines the component's relative size in a layout."}, 'min_width': {'type': 'int', 'default': '160', 'description': 'The minimum width of the component in pixels.'}, 'interactive': {'type': 'bool | None', 'default': 'None', 'description': "If True, the component is in input mode (upload). If False, it's in display-only mode."}, 'visible': {'type': 'bool', 'default': 'True', 'description': 'If False, the component is not rendered.'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'An optional string that is assigned as the id of the component in the HTML.'}, 'elem_classes': {'type': 'typing.Union[typing.List[str], str, NoneType][\n    typing.List[str][str], str, None\n]', 'default': 'None', 'description': 'An optional list of strings that are assigned as the classes of the component in the HTML.'}, 'position': {'type': 'int', 'default': '50', 'description': 'The initial horizontal position of the slider, from 0 (left) to 100 (right).'}, 'show_download_button': {'type': 'bool', 'default': 'True', 'description': 'If True, a download button is shown for the second video.'}, 'show_mute_button': {'type': 'bool', 'default': 'True', 'description': 'If True, a mute/unmute button is shown.'}, 'show_fullscreen_button': {'type': 'bool', 'default': 'True', 'description': 'If True, a fullscreen button is shown.'}, 'video_mode': {'type': '"upload" | "preview"', 'default': '"preview"', 'description': 'The mode of the component, either "upload" or "preview".'}, 'autoplay': {'type': 'bool', 'default': 'False', 'description': 'If True, videos will start playing automatically on load (muted).'}, 'loop': {'type': 'bool', 'default': 'False', 'description': 'If True, videos will loop when they finish playing.'}}, 'postprocess': {'value': {'type': 'typing.Optional[\n    typing.Tuple[\n        str | pathlib.Path | None, str | pathlib.Path | None\n    ]\n][\n    typing.Tuple[\n        str | pathlib.Path | None, str | pathlib.Path | None\n    ][str | pathlib.Path | None, str | pathlib.Path | None],\n    None,\n]', 'description': None}}, 'preprocess': {'return': {'type': 'typing.Optional[\n    typing.Tuple[\n        str | pathlib.Path | None, str | pathlib.Path | None\n    ]\n][\n    typing.Tuple[\n        str | pathlib.Path | None, str | pathlib.Path | None\n    ][str | pathlib.Path | None, str | pathlib.Path | None],\n    None,\n]', 'description': None}, 'value': None}}, 'events': {'change': {'type': None, 'default': None, 'description': 'Triggered when the value of the VideoSlider changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input.'}, 'upload': {'type': None, 'default': None, 'description': 'This listener is triggered when the user uploads a file into the VideoSlider.'}, 'clear': {'type': None, 'default': None, 'description': 'This listener is triggered when the user clears the VideoSlider using the clear button for the component.'}}}, '__meta__': {'additional_interfaces': {}, 'user_fn_refs': {'VideoSlider': []}}}

abs_path = os.path.join(os.path.dirname(__file__), "css.css")

with gr.Blocks(
    css=abs_path,
    theme=gr.themes.Default(
        font_mono=[
            gr.themes.GoogleFont("Inconsolata"),
            "monospace",
        ],
    ),
) as demo:
    gr.Markdown(
"""
# `gradio_videoslider`

<div style="display: flex; gap: 7px;">
<a href="https://pypi.org/project/gradio_videoslider/" target="_blank"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/gradio_videoslider"></a>  
</div>

VideoSlider Component for Gradio
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_videoslider
```

## Usage

```python
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
    \"\"\"This function handles the uploaded videos.\"\"\"
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

```
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `VideoSlider`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["VideoSlider"]["members"]["__init__"], linkify=[])


    gr.Markdown("### Events")
    gr.ParamViewer(value=_docs["VideoSlider"]["events"], linkify=['Event'])




    gr.Markdown("""

### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.



 ```python
def predict(
    value: typing.Optional[
    typing.Tuple[
        str | pathlib.Path | None, str | pathlib.Path | None
    ]
][
    typing.Tuple[
        str | pathlib.Path | None, str | pathlib.Path | None
    ][str | pathlib.Path | None, str | pathlib.Path | None],
    None,
]
) -> typing.Optional[
    typing.Tuple[
        str | pathlib.Path | None, str | pathlib.Path | None
    ]
][
    typing.Tuple[
        str | pathlib.Path | None, str | pathlib.Path | None
    ][str | pathlib.Path | None, str | pathlib.Path | None],
    None,
]:
    return value
```
""", elem_classes=["md-custom", "VideoSlider-user-fn"], header_links=True)




    demo.load(None, js=r"""function() {
    const refs = {};
    const user_fn_refs = {
          VideoSlider: [], };
    requestAnimationFrame(() => {

        Object.entries(user_fn_refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}-user-fn`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })

        Object.entries(refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })
    })
}

""")

demo.launch()
