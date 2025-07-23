<!-- videoslider/frontend/shared/Player.svelte -->
<script lang="ts">
	// Svelte and Gradio imports
	import { createEventDispatcher, onMount, tick } from "svelte";
	import { Play, Pause, Undo } from "@gradio/icons";
	import Video from "./Video.svelte";
	import VideoControls from "./VideoControls.svelte";
	import type { FileData, Client } from "@gradio/client";
	import { prepare_files } from "@gradio/client";
	import { format_time } from "@gradio/utils";
	import type { I18nFormatter } from "@gradio/utils";

	// ------------------
	// Props
	// ------------------
	export let root = "";
	export let src: string;
	export let subtitle: string | null = null;
	export let mirror: boolean;
	export let loop: boolean;
	export let muted = false;
	export let label = "test";
	/** If true, shows editing controls like trim. */
	export let interactive = false;
	export let handle_change: (video: FileData) => void = () => {};
	export let handle_reset_value: () => void = () => {};
	export let upload: Client["upload"];
	export let is_stream: boolean | undefined;
	export let i18n: I18nFormatter;
	export let show_download_button = false;
	export let value: FileData | null = null;
	export let handle_clear: () => void = () => {};
	export let has_change_history = false;
	export let fullscreen = false;

	const dispatch = createEventDispatcher<{
		play: undefined;
		pause: undefined;
		stop: undefined;
		end: undefined;
		clear: undefined;
		load: { top: number; left: number; width: number; height: number };
	}>();

	// -----------------
	// Internal State
	// -----------------
	/** The current playback time of the video, in seconds. */
	let time = 0;
	/** The total duration of the video, in seconds. */
	let duration: number;
	/** The paused state of the video. */
	let paused = true;
	/** A direct reference to the underlying HTML <video> element for internal use. */
	let video: HTMLVideoElement;
	/** A prop to export the video element reference to parent components. */
	export let video_el: HTMLVideoElement;
	/** A flag to show a loading state during video processing (e.g., trimming). */
	let processingVideo = false;

	// -----------------
	// Functions
	// -----------------

	/**
	 * Calculates and returns the size and relative position of the video element.
	 * @param video The HTML video element to measure.
	 */
	function get_video_size(video: HTMLVideoElement | null) {
		if (!video) {
			const container = video?.parentElement?.getBoundingClientRect() || {
				top: 0,
				left: 0,
				width: 640,
				height: 360
			};
			return {
				top: 0,
				left: 0,
				width: container.width,
				height: container.height
			};
		}
		const rect = video.getBoundingClientRect();
		const containerRect = video.parentElement?.getBoundingClientRect() || rect;
		return {
			top: rect.top - containerRect.top,
			left: rect.left - containerRect.left,
			width: rect.width,
			height: rect.height
		};
	}

	/** Handles user input on the range slider to seek the video. */
	function handleMove(e: Event): void {
		if (!duration) return;
		const input = e.currentTarget as HTMLInputElement;
		time = duration * (parseFloat(input.value) / 100);
	}

	/** Handles keyboard navigation (arrow keys) on the range slider. */
	function handleKeydown(e: KeyboardEvent): void {
		if (!duration) return;
		if (e.key === "ArrowLeft") {
			time = Math.max(0, time - 5);
		} else if (e.key === "ArrowRight") {
			time = Math.min(duration, time + 5);
		}
	}

	/** Toggles the video between playing and paused states. */
	async function play_pause(): Promise<void> {
		const isPlaying = video.currentTime > 0 && !video.paused && !video.ended && video.readyState > video.HAVE_CURRENT_DATA;
		if (!isPlaying) {
			await video.play();
		} else {
			video.pause();
		}
	}

	/** Dispatches events when the video playback ends. */
	function handle_end(): void {
		dispatch("stop");
		dispatch("end");
	}

	/** Handles the video trimming process. */
	const handle_trim_video = async (videoBlob: Blob): Promise<void> => {
		let _video_blob = new File([videoBlob], "video.mp4");
		const val = await prepare_files([_video_blob]);
		let value = ((await upload(val, root))?.filter(Boolean) as FileData[])[0];
		handle_change(value);
	};

	// -----------------
	// Reactive Logic
	// -----------------
	$: time = time || 0;
	$: duration = duration || 0;
	/** Passes the internal video element reference to the exported prop. */
	$: video_el = video;
	/** Calculates the progress value (0-100) for the range slider. */
	$: progressValue = duration ? (time / duration) * 100 : 0;

	/** When the video element is available, dispatch its size and set up a ResizeObserver. */
	onMount(() => {
		const resizer = new ResizeObserver(async () => {
			await tick();
			dispatch("load", get_video_size(video));
		});
		if (video) {
			resizer.observe(video);
		}
		return () => {
			resizer.disconnect();
		};
	});

	/** Dispatches the video size whenever the video element reference changes. */
	$: if (video) {
		dispatch("load", get_video_size(video));
	}
</script>

<div class="wrap">
	{#if !video?.videoWidth}
		<div class="loading-spinner">Loading video...</div>
	{/if}
	<div class="mirror-wrap" class:mirror>
		<Video
			{src}
			preload="auto"
			{loop}
			{muted}
			{is_stream}
			on:click={play_pause}
			on:play={() => dispatch("play")}
			on:pause={() => dispatch("pause")}
			on:loadeddata={() => dispatch("load", get_video_size(video))}
			on:loadedmetadata={() => dispatch("load", get_video_size(video))}
			on:error={(e) => dispatch("error", e)}
			on:ended={handle_end}
			bind:currentTime={time}
			bind:duration
			bind:paused
			bind:node={video}
			data-testid={`${label}-player`}
			{processingVideo}
			{fullscreen}
		>
			<track kind="captions" src={subtitle} default />
		</Video>
	</div>

	<div class="controls">
		<div class="inner">
			<span
				role="button"
				tabindex="0"
				class="icon"
				aria-label="play-pause-replay-button"
				on:click={play_pause}
				on:keydown={(e) => {
					if (e.key === "Enter" || e.key === " ") play_pause();
				}}
			>
				{#if time === duration}
					<Undo />
				{:else if paused}
					<Play />
				{:else}
					<Pause />
				{/if}
			</span>
			<span class="time">{format_time(time)} / {format_time(duration)}</span>
			<input
				type="range"
				min="0"
				max="100"
				step="0.1"
				value={progressValue}
				aria-label="Video progress"
				on:input={handleMove}
				on:keydown={handleKeydown}
			/>
		</div>
	</div>
</div>

{#if interactive}
	<VideoControls
		videoElement={video}
		showRedo
		{handle_trim_video}
		{handle_reset_value}
		bind:processingVideo
		{value}
		{i18n}
		{show_download_button}
		{handle_clear}
		{has_change_history}
	/>
{/if}

<style lang="postcss">
	span {
		text-shadow: 0 0 8px rgba(0, 0, 0, 0.5);
	}
	input[type="range"] {
		margin-right: var(--size-3);
		width: var(--size-full);
		height: var(--size-2);
	}
	.mirror {
		transform: scaleX(-1);
	}
	.mirror-wrap {
		position: relative;
		height: 100%;
		width: 100%;
	}
	.controls {
		position: absolute;
		bottom: 0;
		opacity: 0;
		transition: 500ms;
		margin: var(--size-2);
		border-radius: var(--radius-md);
		background: var(--color-grey-800);
		padding: var(--size-2) var(--size-1);
		width: calc(100% - var(--size-2) * 2);
	}
	.wrap:hover .controls {
		opacity: 1;
	}
	.inner {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding-right: var(--size-2);
		padding-left: var(--size-2);
		width: var(--size-full);
		height: var(--size-full);
	}
	.icon {
		display: flex;
		justify-content: center;
		cursor: pointer;
		width: var(--size-6);
		color: white;
	}
	.time {
		flex-shrink: 0;
		margin-right: var(--size-3);
		margin-left: var(--size-3);
		color: white;
		font-size: var(--text-sm);
		font-family: var(--font-mono);
	}
	.wrap {
		position: relative;
		background-color: var(--background-fill-secondary);
		height: var(--size-full);
		width: var(--size-full);
		border-radius: var(--radius-xl);
	}
	.wrap :global(video) {
		height: var(--size-full);
		width: var(--size-full);
		object-fit: contain;
	}
	.loading-spinner {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		color: white;
		background: rgba(0,0,0,0.7);
		padding: 1rem;
		border-radius: 0.5rem;
	}
</style>