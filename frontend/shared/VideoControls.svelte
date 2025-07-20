<!--
@component
This component provides editing controls for a video, such as trimming.
It appears below the main player when in `interactive` mode. It uses FFmpeg
(loaded in the browser via WebAssembly) to perform the trimming operation.
-->
<script lang="ts">
	import { Undo, Trim, Clear } from "@gradio/icons";
	import VideoTimeline from "./VideoTimeline.svelte";
	import { trimVideo } from "./utils";
	import { FFmpeg } from "@ffmpeg/ffmpeg";
	import loadFfmpeg from "./utils";
	import { onMount } from "svelte";
	import { format_time } from "@gradio/utils";
	import { IconButton } from "@gradio/atoms";
	import { ModifyUpload } from "@gradio/upload";
	import type { FileData } from "@gradio/client";

	// ------------------
	// Props
	// ------------------
	/** A direct reference to the HTML <video> element to be controlled. */
	export let videoElement: HTMLVideoElement;
	/** If true, shows the 'Undo' button. */
	export let showRedo = false;
	export let interactive = true;
	/** The current editing mode (e.g., 'edit' for trimming). */
	export let mode = "";
	/** A callback function to reset the video to its original state. */
	export let handle_reset_value: () => void;
	/** A callback function to handle the new, trimmed video blob. */
	export let handle_trim_video: (videoBlob: Blob) => void;
	/** Two-way bound prop to indicate if the video is currently being processed by FFmpeg. */
	export let processingVideo = false;
	export let i18n: (key: string) => string;
	export let value: FileData | null = null;
	export let show_download_button = false;
	export let handle_clear: () => void = () => {};
	/** True if the video has a previous state to revert to. */
	export let has_change_history = false;

	// -----------------
	// Internal State
	// -----------------
	/** The FFmpeg instance. */
	let ffmpeg: FFmpeg;
	/** The duration of the selected trim region. */
	let trimmedDuration: number | null = null;
	/** The start time of the trim, in seconds. */
	let dragStart = 0;
	/** The end time of the trim, in seconds. */
	let dragEnd = 0;
	/** A flag to show a loading state while the timeline generates thumbnails. */
	let loadingTimeline = false;

	/** Load the FFmpeg library when the component is first mounted. */
	onMount(async () => {
		ffmpeg = await loadFfmpeg();
	});

	/** When entering edit mode, initialize the trimmed duration to the full video duration. */
	$: if (mode === "edit" && trimmedDuration === null && videoElement)
		trimmedDuration = videoElement.duration;
	
	/** Toggles the video trimming UI on and off. */
	const toggleTrimmingMode = (): void => {
		if (mode === "edit") {
			mode = "";
			trimmedDuration = videoElement.duration;
		} else {
			mode = "edit";
		}
	};
</script>

<!-- The trimming UI, which is only visible when mode is 'edit'. -->
<div class="container" class:hidden={mode !== "edit"}>
	{#if mode === "edit"}
		<div class="timeline-wrapper">
			<VideoTimeline
				{videoElement}
				bind:dragStart
				bind:dragEnd
				bind:trimmedDuration
				bind:loadingTimeline
			/>
		</div>
	{/if}

	<div class="controls" data-testid="waveform-controls">
		{#if mode === "edit" && trimmedDuration !== null}
			<time
				aria-label="duration of selected region in seconds"
				class:hidden={loadingTimeline}>{format_time(trimmedDuration)}</time
			>
			<div class="edit-buttons">
				<button
					class:hidden={loadingTimeline}
					class="text-button"
					on:click={() => {
						mode = "";
						processingVideo = true;
						trimVideo(ffmpeg, dragStart, dragEnd, videoElement)
							.then((videoBlob) => {
								handle_trim_video(videoBlob);
							})
							.then(() => {
								processingVideo = false;
							});
					}}>Trim</button
				>
				<button
					class="text-button"
					class:hidden={loadingTimeline}
					on:click={toggleTrimmingMode}>Cancel</button
				>
			</div>
		{:else}
			<div />
		{/if}
	</div>
</div>

<!-- Standard controls like Clear, Download, Undo, and Trim. -->
<ModifyUpload
	{i18n}
	on:clear={() => handle_clear()}
	download={show_download_button ? value?.url : null}
>
	{#if showRedo && mode === ""}
		<IconButton
			Icon={Undo}
			label="Reset video to initial value"
			disabled={processingVideo || !has_change_history}
			on:click={() => {
				handle_reset_value();
				mode = "";
			}}
		/>
	{/if}

	{#if interactive && mode === ""}
		<IconButton
			Icon={Trim}
			label="Trim video to selection"
			disabled={processingVideo}
			on:click={toggleTrimmingMode}
		/>
	{/if}
</ModifyUpload>

<style>
	.container {
		width: 100%;
	}
	time {
		color: var(--color-accent);
		font-weight: bold;
		padding-left: var(--spacing-xs);
	}

	.timeline-wrapper {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 100%;
	}

	.text-button {
		border: 1px solid var(--neutral-400);
		border-radius: var(--radius-sm);
		font-weight: 300;
		font-size: var(--size-3);
		text-align: center;
		color: var(--neutral-400);
		height: var(--size-5);
		font-weight: bold;
		padding: 0 5px;
		margin-left: 5px;
	}

	.text-button:hover,
	.text-button:focus {
		color: var(--color-accent);
		border-color: var(--color-accent);
	}

	.controls {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin: var(--spacing-lg);
		overflow: hidden;
	}

	.edit-buttons {
		display: flex;
		gap: var(--spacing-sm);
	}

	@media (max-width: 320px) {
		.controls {
			flex-direction: column;
			align-items: flex-start;
		}

		.edit-buttons {
			margin-top: var(--spacing-sm);
		}

		.controls * {
			margin: var(--spacing-sm);
		}

		.controls .text-button {
			margin-left: 0;
		}
	}

	.container {
		display: flex;
		flex-direction: column;
	}

	.hidden {
		display: none;
	}
</style>