---
tags: [gradio-custom-component, ImageSlider]
title: gradio_videoslider
short_description: VideoSlider Component for Gradio
colorFrom: blue
colorTo: yellow
sdk: gradio
pinned: false
app_file: space.py
---

# `gradio_videoslider`
<a href="https://pypi.org/project/gradio_videoslider/" target="_blank"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/gradio_videoslider"></a>  

VideoSlider Component for Gradio

## Installation

```bash
pip install gradio_videoslider
```

## Usage

```python
# In demo/app.py
import gradio as gr
from gradio_videoslider import VideoSlider
import os

# --- 1. DEFINE THE PATHS TO YOUR LOCAL VIDEOS ---
#
# IMPORTANT: Replace the values below with the paths to YOUR video files.
#
# Option A: Relative Path (if the video is in the same folder as this app.py)
# video_path_1 = "video_antes.mp4"
# video_path_2 = "video_depois.mp4"
#
# Option B: Absolute Path (the full path to the file on your computer)
# Example for Windows:
# video_path_1 = "C:\\Users\\YourName\\Videos\\my_video_1.mp4"
#
# Example for Linux/macOS:
# video_path_1 = "/home/yourname/videos/my_video_1.mp4"

# Set your file paths here:
video_path_1 = "src/examples/Samplevideo 720x480.mp4"
video_path_2 = "src/examples/SampleVideo 1280x720.mp4"


# --- 2. FUNCTION FOR THE UPLOAD EXAMPLE (remains the same) ---
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
            video_slider_input = VideoSlider(label="Your Videos", height=400, width=700)
            video_slider_output = VideoSlider(
                label="Video comparision",
                interactive=False,
                autoplay=True,
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
                autoplay=True,
                loop=True,
                height=400,
                width=700
            )

# Optional: A check to give a helpful error message if files are not found.
if not os.path.exists(video_path_1) or not os.path.exists(video_path_2):
    print("---")
    print(f"WARNING: Could not find one or both video files.")
    print(f"Please make sure these paths are correct in your app.py file:")
    print(f"  - '{os.path.abspath(video_path_1)}'")
    print(f"  - '{os.path.abspath(video_path_2)}'")
    print("---")

if __name__ == '__main__':
    demo.launch()

```

## `VideoSlider`

### Initialization

<table>
<thead>
<tr>
<th align="left">name</th>
<th align="left" style="width: 25%;">type</th>
<th align="left">default</th>
<th align="left">description</th>
</tr>
</thead>
<tbody>
<tr>
<td align="left"><code>value</code></td>
<td align="left" style="width: 25%;">

```python
typing.Union[
    typing.Tuple[str | pathlib.Path, str | pathlib.Path],
    typing.Callable,
    NoneType,
][
    typing.Tuple[str | pathlib.Path, str | pathlib.Path][
        str | pathlib.Path, str | pathlib.Path
    ],
    Callable,
    None,
]
```

</td>
<td align="left"><code>None</code></td>
<td align="left">A tuple of two video file paths or URLs to display initially.</td>
</tr>

<tr>
<td align="left"><code>height</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">The height of the component in pixels.</td>
</tr>

<tr>
<td align="left"><code>width</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">The width of the component in pixels.</td>
</tr>

<tr>
<td align="left"><code>label</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">The label for this component.</td>
</tr>

<tr>
<td align="left"><code>every</code></td>
<td align="left" style="width: 25%;">

```python
float | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>show_label</code></td>
<td align="left" style="width: 25%;">

```python
bool | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>container</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>scale</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>min_width</code></td>
<td align="left" style="width: 25%;">

```python
int
```

</td>
<td align="left"><code>160</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>interactive</code></td>
<td align="left" style="width: 25%;">

```python
bool | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">If False, the component will be in display-only mode.</td>
</tr>

<tr>
<td align="left"><code>visible</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>elem_id</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>elem_classes</code></td>
<td align="left" style="width: 25%;">

```python
typing.Union[typing.List[str], str, NoneType][
    typing.List[str][str], str, None
]
```

</td>
<td align="left"><code>None</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>position</code></td>
<td align="left" style="width: 25%;">

```python
int
```

</td>
<td align="left"><code>50</code></td>
<td align="left">The initial position of the slider, from 0 to 100.</td>
</tr>

<tr>
<td align="left"><code>show_download_button</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>show_fullscreen_button</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>autoplay</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>False</code></td>
<td align="left">If True, the videos will start playing automatically.</td>
</tr>

<tr>
<td align="left"><code>loop</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>False</code></td>
<td align="left">If True, the videos will loop when they finish.</td>
</tr>
</tbody></table>


### Events

| name | description |
|:-----|:------------|
| `change` | Triggered when the value of the VideoSlider changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input. |
| `upload` | This listener is triggered when the user uploads a file into the VideoSlider. |
| `clear` | This listener is triggered when the user clears the VideoSlider using the clear button for the component. |



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
 
