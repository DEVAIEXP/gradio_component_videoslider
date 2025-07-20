# In backend/videoslider.py
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, List, Tuple

from gradio_client import handle_file
from gradio_client.documentation import document

from gradio import processing_utils
from gradio.components.base import Component
from gradio.data_classes import FileData, GradioRootModel
from gradio.events import Events

class VideoSliderData(GradioRootModel):
    """
    Data model for the VideoSlider component. Represents the data structure
    sent between the frontend and backend, which is a tuple of two FileData objects.
    """
    root: Tuple[FileData | None, FileData | None]

# Type alias for the value passed to or returned from a user's function.
# It's a tuple of two file paths (string or Path object).
VideoSliderValue = Tuple[str | Path | None, str | Path | None]

@document()
class VideoSlider(Component):
    """
    A custom Gradio component to display a side-by-side video comparison with a slider.
    It can be used as both an input (uploading two videos) and an output (displaying two videos).
    """
    # The data model used for communication with the frontend.
    data_model = VideoSliderData
    # The events that this component can trigger.
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
        show_fullscreen_button: bool = True,
        autoplay: bool = False,
        loop: bool = False,
    ):
        """
        Initializes the VideoSlider component.

        Parameters:
            value: A tuple of two video file paths or URLs to display initially.
            height: The height of the component in pixels.
            width: The width of the component in pixels.
            label: The label for this component.
            position: The initial position of the slider, from 0 to 100.
            autoplay: If True, the videos will start playing automatically.
            loop: If True, the videos will loop when they finish.
            interactive: If False, the component will be in display-only mode.
        """
        self.height = height
        self.width = width
        self.position = position
        self.show_download_button = show_download_button
        self.show_fullscreen_button = show_fullscreen_button
        self.autoplay = autoplay
        self.loop = loop
        self.type = "filepath" # The component handles file paths.
        
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
        Processes data from the frontend into a format usable by a Python function.
        It converts the FileData objects into a tuple of simple string file paths.
        """
        if payload is None or payload.root is None:
            return None
        
        video1, video2 = payload.root
        
        p1 = Path(video1.path) if video1 and video1.path else None
        p2 = Path(video2.path) if video2 and video2.path else None
        
        return (str(p1) if p1 else None, str(p2) if p2 else None)

    def postprocess(self, value: VideoSliderValue | None) -> VideoSliderData | None:
        """
        Processes data returned from a Python function into a format for the frontend.
        It takes a tuple of file paths, makes them servable by Gradio, and returns
        a VideoSliderData object.
        """
        if value is None or (value[0] is None and value[1] is None):
            return None
            
        video1_path, video2_path = value
        
        fd1 = None
        if video1_path:
            # Copies the file to a temp cache and returns a FileData object.
            new_path = processing_utils.move_resource_to_block_cache(video1_path, self)
            fd1 = FileData(path=str(new_path))

        fd2 = None
        if video2_path:
            new_path = processing_utils.move_resource_to_block_cache(video2_path, self)
            fd2 = FileData(path=str(new_path))
        
        return VideoSliderData(root=(fd1, fd2))
        
    def api_info(self) -> dict[str, Any]:
        """
        Provides API information for the component.
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