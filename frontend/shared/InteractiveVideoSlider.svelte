<!--
@component
This component provides the user interface for uploading two videos side-by-side.
It acts as the "input" mode for the main VideoSlider component. It uses two
instances of the InteractiveVideo component to handle the individual uploads.
-->
<script lang="ts">
	import { createEventDispatcher } from "svelte";
	import type { FileData, Client } from "@gradio/client";
	import type { I18nFormatter } from "@gradio/utils";
	import type { WebcamOptions } from "./utils";

	import InteractiveVideo from "./InteractiveVideo.svelte";
	import { BlockLabel } from "@gradio/atoms";
	import { Video as VideoIcon } from "@gradio/icons";

	// ------------------
	// Props
	// ------------------
	/** The core value: a tuple containing the two uploaded video files. */
	export let value: [FileData | null, FileData | null] = [null, null];
	export let label: string | undefined = undefined;
	export let show_label: boolean;
	export let root: string;
	export let i18n: I18nFormatter;
	export let max_file_size: number | null = null;
	export let upload: Client["upload"];
	export let stream_handler: Client["stream"]; 
	export let autoplay: boolean;
	export let loop: boolean;
	
	const dispatch = createEventDispatcher<{
		upload: [FileData | null, FileData | null];
		clear: void;
		error: string;
	}>();

	/** Default options for webcam recording, passed down to the child component. */
	const webcam_options: WebcamOptions = {
		mirror: true,
		constraints: {}
	};

	/**
	 * Handles the 'change' event from either of the child InteractiveVideo components.
	 * It updates the correct slot in the `value` tuple and dispatches an event.
	 * @param detail The new FileData object from the child component.
	 * @param slot The index (0 for left, 1 for right) of the video that changed.
	 */
	function handle_change(
		detail: FileData | null,
		slot: 0 | 1
	): void {
		const new_value: [FileData | null, FileData | null] = [...value];
		new_value[slot] = detail;
		value = new_value;

		if (value[0] === null && value[1] === null) {
			dispatch("clear");
		} else {
			dispatch("upload", new_value);
		}
	}
</script>

<BlockLabel {show_label} Icon={VideoIcon} label={label || "Video Slider"} />

<div class="container" data-testid="video-slider-input">
	<!-- Left Video Slot -->
	<div class="video-slot">
		<InteractiveVideo
			value={value[0]}
			on:change={({ detail }) => handle_change(detail, 0)}
			sources={["upload"]}
			active_source="upload"
			{root}
			{upload}
			{stream_handler}
			{i18n}
			{max_file_size}
			show_label={false}
			{webcam_options}
			{autoplay}
			{loop}
			include_audio={true}
		>
			<!-- This text is displayed inside the upload box. -->
			<p class="upload-text">Upload Video 1</p>
		</InteractiveVideo>
	</div>

	<!-- Right Video Slot -->
	<div class="video-slot">
		<InteractiveVideo
			value={value[1]}
			on:change={({ detail }) => handle_change(detail, 1)}
			sources={["upload"]}
			active_source="upload"
			{root}
			{upload}
			{stream_handler}
			{i18n}
			{max_file_size}
			show_label={false}
			{webcam_options}
			{autoplay}
			{loop}
			include_audio={true}
		>
			<p class="upload-text">Upload Video 2</p>
		</InteractiveVideo>
	</div>
</div>

<style>
	.container {
		display: flex;
		flex-direction: row;
		gap: var(--spacing-lg);
		width: 100%;
		height: 100%;
	}
	.video-slot {
		flex: 1;
		display: flex;
		justify-content: center;
		align-items: center;
		min-height: var(--size-60);
		border: 1px solid var(--border-color-primary);
		border-radius: var(--radius-lg);
		overflow: hidden;
		position: relative;
	}
	/* Use :global to style the slotted content passed to the child component. */
	:global(.video-slot .upload-text) {
		color: var(--body-text-color-subdued);
        text-align: center;
	}
</style>