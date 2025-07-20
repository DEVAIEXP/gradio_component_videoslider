<!--
@component
This component provides an interactive area for a single video. It can handle
uploading a video file, recording from a webcam, or displaying an existing video.
It's a building block for more complex components like the InteractiveVideoSlider.
-->
<script lang="ts">
	import { createEventDispatcher } from "svelte";
	import { Upload } from "@gradio/upload";
	import type { FileData, Client } from "@gradio/client";
	import { BlockLabel, SelectSource } from "@gradio/atoms";
	import { Webcam } from "@gradio/image";
	import { Video } from "@gradio/icons";
	import type { WebcamOptions } from "./utils";
	import { prettyBytes } from "./utils";
	import Player from "./Player.svelte";
	import type { I18nFormatter } from "@gradio/utils";

	// ------------------
	// Props
	// ------------------
	/** The FileData object representing the current video. */
	export let value: FileData | null = null;
	export let subtitle: FileData | null = null;
	/** The available input sources, e.g., 'upload', 'webcam'. */
	export let sources:
		| ["webcam"]
		| ["upload"]
		| ["webcam", "upload"]
		| ["upload", "webcam"] = ["webcam", "upload"];
	export let label: string | undefined = undefined;
	export let show_download_button = false;
	export let show_label = true;
	export let webcam_options: WebcamOptions;
	export let include_audio: boolean;
	export let autoplay: boolean;
	export let root: string;
	export let i18n: I18nFormatter;
	/** The currently selected input source. */
	export let active_source: "webcam" | "upload" = "webcam";
	export let handle_reset_value: () => void = () => {};
	export let max_file_size: number | null = null;
	export let upload: Client["upload"];
	export let stream_handler: Client["stream"];
	export let loop: boolean;
	export let uploading = false;

	// -----------------
	// Internal State
	// -----------------
	/** Tracks if the video has been edited (e.g., trimmed). */
	let has_change_history = false;
	/** Tracks if the user is dragging a file over the component. */
	let dragging = false;

	const dispatch = createEventDispatcher<{
		change: FileData | null;
		drag: boolean;
		error: string;
		upload: FileData;
	}>();

	// -----------------
	// Event Handlers
	// -----------------

	/** Handles the 'load' event from the Upload component. */
	function handle_load({ detail }: CustomEvent<FileData | null>): void {
		value = detail;
		dispatch("change", detail);
		dispatch("upload", detail!);
	}

	/** Handles the 'clear' event. */
	function handle_clear(): void {
		value = null;
		dispatch("change", null);
	}

	/** Handles changes from the Player (e.g., after trimming). */
	function handle_change(video: FileData): void {
		has_change_history = true;
		dispatch("change", video);
	}

	/** Handles a new video captured from the webcam. */
	function handle_capture({
		detail
	}: CustomEvent<FileData | any | null>): void {
		dispatch("change", detail);
	}

	/** Dispatches the 'drag' event when the dragging state changes. */
	$: dispatch("drag", dragging);
</script>

<BlockLabel {show_label} Icon={Video} label={label || "Video"} />

<div data-testid="video" class="video-container">
	<!-- If no video is loaded, show the upload or webcam interface. -->
	{#if value === null || value.url === undefined}
		<div class="upload-container">
			{#if active_source === "upload"}
				<Upload
					bind:dragging
					bind:uploading
					filetype="video/x-m4v,video/*"
					on:load={handle_load}
					{max_file_size}
					on:error={({ detail }) => dispatch("error", detail)}
					{root}
					{upload}
					{stream_handler}
					aria_label={i18n("video.drop_to_upload")}
				>
					<slot />
				</Upload>
			{:else if active_source === "webcam"}
				<Webcam
					{root}
					mirror_webcam={webcam_options.mirror}
					webcam_constraints={webcam_options.constraints}
					{include_audio}
					mode="video"
					on:error
					on:capture={handle_capture}
					on:start_recording
					on:stop_recording
					{i18n}
					{upload}
					stream_every={1}
				/>
			{/if}
		</div>
	<!-- If a video is loaded, display the player. -->
	{:else if value?.url}
		<!-- Use a key to force re-rendering of the Player when the video URL changes. -->
		{#key value?.url}
			<Player
				{upload}
				{root}
				interactive
				src={value.url}
				subtitle={subtitle?.url}
				is_stream={false}
				mirror={webcam_options.mirror && active_source === "webcam"}
				{label}
				{handle_change}
				{handle_reset_value}
				{loop}
				{value}
				{i18n}
				{show_download_button}
				{handle_clear}
				{has_change_history}
			/>
		{/key}
	<!-- Fallback for file data without a URL (e.g., before upload completes). -->
	{:else if value.size}
		<div class="file-name">{value.orig_name || value.url}</div>
		<div class="file-size">
			{prettyBytes(value.size)}
		</div>
	{/if}

	<!-- Show the source selection buttons (upload/webcam). -->
	<SelectSource {sources} bind:active_source {handle_clear} />
</div>

<style>
	.file-name {
		padding: var(--size-6);
		font-size: var(--text-xxl);
		word-break: break-all;
	}

	.file-size {
		padding: var(--size-2);
		font-size: var(--text-xl);
	}

	.upload-container {
		height: 100%;
		width: 100%;
	}

	.video-container {
		display: flex;
		height: 100%;
		flex-direction: column;
		justify-content: center;
		align-items: center;
	}
</style>