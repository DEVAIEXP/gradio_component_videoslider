# In backend/videoslider.py
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, List, Literal, Tuple

from gradio_client import handle_file
from gradio_client.documentation import document

from gradio import processing_utils
from gradio.components.base import Component
from gradio.data_classes import FileData, GradioRootModel
from gradio.events import Events

class VideoSliderData(GradioRootModel):
    """
    Pydantic model for the data structure sent between the frontend and backend.
    It represents a tuple of two (optional) FileData objects.
    """
    root: Tuple[FileData | None, FileData | None]

# Type alias for the value that the user's Python function will receive or return.
# It is a tuple of two (optional) file paths.
VideoSliderValue = Tuple[str | Path | None, str | Path | None]

@document()
class VideoSlider(Component):
    """
    A custom Gradio component to display a side-by-side video comparison with a slider.
    Can be used as an input (for uploading two videos) or as an output (for displaying two videos).
    """
    # The data model used for communication with the frontend.
    data_model = VideoSliderData
    # A list of events that this component supports.
    EVENTS = [Events.change, Events.upload, Events.clear]

    def __init__(
        self,
        value: Tuple[str | Path, str | Path] | Callable | None = None,
        *,
        height: int | None = None,
        width: int | None = None,
        label: str | None = None,
        every: float | None = None,
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: List[str] | str | None = None,
        position: int = 50,
        show_download_button: bool = True,
        show_mute_button: bool = True,
        show_fullscreen_button: bool = True,
        video_mode: Literal["upload", "preview"] = "preview",
        autoplay: bool = False,
        loop: bool = False,
    ):
        """
        Initializes the VideoSlider component.

        Parameters:
            value: A tuple of two video file paths or URLs to display initially. Can also be a callable.
            height: The height of the component container in pixels.
            width: The width of the component container in pixels.
            label: The label for this component that appears above it.
            every: If `value` is a callable, run the function 'every' seconds while the client connection is open.
            show_label: If False, the label is not displayed.
            container: If False, the component will not be wrapped in a container.
            scale: An integer that defines the component's relative size in a layout.
            min_width: The minimum width of the component in pixels.
            interactive: If True, the component is in input mode (upload). If False, it's in display-only mode.
            visible: If False, the component is not rendered.
            elem_id: An optional string that is assigned as the id of the component in the HTML.
            elem_classes: An optional list of strings that are assigned as the classes of the component in the HTML.
            position: The initial horizontal position of the slider, from 0 (left) to 100 (right).
            show_download_button: If True, a download button is shown for the second video.
            show_mute_button: If True, a mute/unmute button is shown.
            show_fullscreen_button: If True, a fullscreen button is shown.
            video_mode: The mode of the component, either "upload" or "preview".
            autoplay: If True, videos will start playing automatically on load (muted).
            loop: If True, videos will loop when they finish playing.
        """
        self.height = height
        self.width = width
        self.position = position
        self.show_download_button = show_download_button
        self.show_fullscreen_button = show_fullscreen_button
        self.show_mute_button = show_mute_button
        self.video_mode = video_mode
        self.autoplay = autoplay
        self.loop = loop
        # The component's value is processed as file paths.
        self.type = "filepath"
        
        super().__init__(
            label=label,
            every=every,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            value=value,
        )

    def preprocess(self, payload: VideoSliderData | None) -> VideoSliderValue | None:
        """
        Converts data from the frontend (as FileData) to a format usable by a Python function (a tuple of file paths).
        """
        if payload is None or payload.root is None:
            return None
        
        video1, video2 = payload.root
        
        p1 = Path(video1.path) if video1 and video1.path else None
        p2 = Path(video2.path) if video2 and video2.path else None
        
        return (str(p1) if p1 else None, str(p2) if p2 else None)

    def postprocess(self, value: VideoSliderValue | None) -> VideoSliderData | None:
        """
        Converts data from a Python function (a tuple of file paths) into a format for the frontend (FileData).
        This involves making the local files servable by Gradio.
        """
        if value is None or (value[0] is None and value[1] is None):
            return None
            
        video1_path, video2_path = value
        
        fd1 = None
        if video1_path:
            # Copies the file to a temporary cache and creates a FileData object.
            new_path = processing_utils.move_resource_to_block_cache(video1_path, self)
            fd1 = FileData(path=str(new_path))

        fd2 = None
        if video2_path:
            new_path = processing_utils.move_resource_to_block_cache(video2_path, self)
            fd2 = FileData(path=str(new_path))
        
        return VideoSliderData(root=(fd1, fd2))
        
    def api_info(self) -> dict[str, Any]:
        """
        Provides type information for the component's API documentation.
        """
        return {"type": "array", "items": {"type": "string", "description": "path to video file"}, "length": 2}

    def example_payload(self) -> Any:
        """
        Returns an example payload for the component's API documentation.
        """
        video_url = "https://gradio-builds.s3.amazonaws.com/demo-files/world.mp4"
        return VideoSliderData(root=(handle_file(video_url), handle_file(video_url)))

    def example_value(self) -> Any:
        """
        Returns an example value for the component's API documentation.
        """
        video_url = "https://gradio-builds.s3.amazonaws.com/demo-files/world.mp4"
        return (video_url, video_url)