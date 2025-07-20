<!-- videoslider/frontend/Index.svelte -->
<!-- Enable programmatic access to the component's props from outside. -->
<svelte:options accessors={true} />

<script lang="ts">
	// Import Gradio types and common components.
	import type { Gradio } from "@gradio/utils";
	import { Block } from "@gradio/atoms";
	import { StatusTracker } from "@gradio/statustracker";
	import type { FileData } from "@gradio/client";
	import type { LoadingStatus } from "@gradio/statustracker";
	
	// Import the two main views for this component.
	import VideoSliderPreview from "./shared/VideoSliderPreview.svelte";
	import InteractiveVideoSlider from "./shared/InteractiveVideoSlider.svelte";

	// ------------------
	// Props from Backend
	// ------------------
	export let elem_id = "";
	export let elem_classes: string[] = [];
	export let visible = true;
	/** The core value of the component: a tuple of two video files. */
	export let value: [FileData | null, FileData | null] = [null, null];
	export let label: string;
	export let show_label: boolean;
	export let root: string;
	export let height: number | undefined;
	export let width: number | undefined;
	export let container = true;
	export let scale: number | null = null;
	export let min_width: number | undefined = undefined;
	export let loading_status: LoadingStatus;
	/** If false, the component is in display-only mode. */
	export let interactive: boolean;
	export let show_download_button: boolean;
	export let show_fullscreen_button: boolean;
	/** The initial position of the slider, from 0 to 100. */
	export let position: number;
	export let autoplay: boolean;
	export let loop: boolean;
	/** The Gradio event dispatcher. */
	export let gradio: Gradio<{
		change: never;
		clear: never;
		upload: never;
		error: string;
	}>;

	// -----------------
	// Internal State
	// -----------------
	/** Holds the fullscreen state for the component. */
	let fullscreen = false;
	/** Stores the previous value to detect changes. */
	let old_value: [FileData | null, FileData | null] = [null, null];
	/** Tracks if the user is dragging over the upload area. */
	let dragging = false;
	
	// -----------------
	// Reactive Logic
	// -----------------
	/** Converts the 0-100 position from Python to a 0-1 scale for CSS. */
	$: normalised_slider_position = Math.max(0, Math.min(100, position)) / 100;

	/** Dispatches a 'change' event whenever the `value` prop is updated from within the component. */
	$: {
		if (JSON.stringify(value) !== JSON.stringify(old_value)) {
			old_value = value;
			gradio.dispatch("change");
		}
	}
</script>

<!-- 
	This block acts as a router. 
	It displays one of two sub-components based on the `interactive` prop from the backend.
-->
{#if !interactive}
	<!-- Static/Output Mode: Shows the side-by-side video player with a slider. -->
	<Block
		{visible}
		variant={"solid"}
		padding={false}
		{elem_id}
		{elem_classes}
		{height}
		{width}
		{container}
		{scale}
		{min_width}
		allow_overflow={false}
		bind:fullscreen
	>
		<StatusTracker
			autoscroll={gradio.autoscroll}
			i18n={gradio.i18n}
			{...loading_status}
		/>
		<VideoSliderPreview
			bind:value
			{interactive}
			{label}
			{show_label}
			{show_download_button}
			{show_fullscreen_button}
			i18n={gradio.i18n}
			position={normalised_slider_position}
			slider_color="var(--border-color-primary)"
			on:clear={() => gradio.dispatch("clear")}
			on:fullscreen={({ detail }) => { fullscreen = detail; }}
			{autoplay}
			{loop}
			upload={(...args) => gradio.client.upload(...args)}
		/>
	</Block>
{:else}
	<!-- Interactive/Input Mode: Shows two upload boxes for the user to add videos. -->
	<Block
		{visible}
		variant={"solid"}
		border_mode={dragging ? "focus" : "base"}
		padding={true}
		{elem_id}
		{elem_classes}
		{height}
		{width}
		{container}
		{scale}
		{min_width}
		allow_overflow={false}
	>
		<StatusTracker
			autoscroll={gradio.autoscroll}
			i18n={gradio.i18n}
			{...loading_status}
		/>
		<InteractiveVideoSlider
			bind:value
			{root}
			on:upload={() => gradio.dispatch("upload")}
			on:clear={() => gradio.dispatch("clear")}
			on:error={({ detail }) => gradio.dispatch("error", detail)}
			{label}
			{show_label}
			max_file_size={gradio.max_file_size}
			i18n={gradio.i18n}
			upload={(...args) => gradio.client.upload(...args)}	
			stream_handler={gradio.client?.stream} 		
			{autoplay}
			{loop}			
		/>
	</Block>
{/if}