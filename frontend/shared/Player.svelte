<!--
@component
This component is a self-contained video player. It wraps the base <Video>
component and adds a custom control bar for play/pause, timeline scrubbing,
and fullscreen. It also integrates with VideoControls for editing features.
-->
<script lang="ts">
	import { createEventDispatcher } from "svelte";
	import { Play, Pause, Maximise, Undo } from "@gradio/icons";
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

	const dispatch = createEventDispatcher<{
		play: undefined;
		pause: undefined;
		stop: undefined;
		end: undefined;
		clear: undefined;
		loadeddata: undefined;
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
	/** A direct reference to the underlying HTML <video> element. */
	let video: HTMLVideoElement;
	/** A prop to export the video element reference to parent components. */
	export let video_el: HTMLVideoElement;
	/** A flag to show a loading state during video processing (e.g., trimming). */
	let processingVideo = false;

	// -----------------
	// Event Handlers
	// -----------------

	/** Handles scrubbing the video timeline with a mouse or touch drag. */
	function handleMove(e: TouchEvent | MouseEvent): void {
		if (!duration) return;

		if (e.type === "click") {
			handle_click(e as MouseEvent);
			return;
		}

		if (e.type !== "touchmove" && !((e as MouseEvent).buttons & 1)) return;

		const clientX =
			e.type === "touchmove"
				? (e as TouchEvent).touches[0].clientX
				: (e as MouseEvent).clientX;
		const { left, right } = (
			e.currentTarget as HTMLProgressElement
		).getBoundingClientRect();
		time = (duration * (clientX - left)) / (right - left);
	}

	/** Toggles the video between playing and paused states. */
	async function play_pause(): Promise<void> {
		if (document.fullscreenElement != video) {
			const isPlaying =
				video.currentTime > 0 &&
				!video.paused &&
				!video.ended &&
				video.readyState > video.HAVE_CURRENT_DATA;

			if (!isPlaying) {
				await video.play();
			} else video.pause();
		}
	}

	/** Handles a single click on the progress bar to seek to a specific time. */
	function handle_click(e: MouseEvent): void {
		const { left, right } = (
			e.currentTarget as HTMLProgressElement
		).getBoundingClientRect();
		time = (duration * (e.clientX - left)) / (right - left);
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

	/** Enters fullscreen mode for the video. */
	function open_full_screen(): void {
		video.requestFullscreen();
	}

	// -----------------
	// Reactive Logic
	// -----------------
	/** Ensures `time` and `duration` are never NaN. */
	$: time = time || 0;
	$: duration = duration || 0;
	/** Passes the internal video element reference to the exported prop. */
	$: video_el = video;
</script>

<div class="wrap">
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
			on:loadeddata={() => dispatch("loadeddata")}
			on:error
			on:ended={handle_end}
			bind:currentTime={time}
			bind:duration
			bind:paused
			bind:node={video}
			data-testid={`${label}-player`}
			{processingVideo}
		>
			<track kind="captions" src={subtitle} default />
		</Video>
		
	</div>

	<!-- The custom video controls overlay -->
	<div class="controls">
		<div class="inner">
			<span
				role="button"
				tabindex="0"
				class="icon"
				aria-label="play-pause-replay-button"
				on:click={play_pause}
				on:keydown={play_pause}
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
			
			<progress
				value={time / duration || 0}
				on:mousemove={handleMove}
				on:touchmove|preventDefault={handleMove}
				on:click|stopPropagation|preventDefault={handle_click}
			/>

			<div
				role="button"
				tabindex="0"
				class="icon"
				aria-label="full-screen"
				on:click={open_full_screen}
				on:keypress={open_full_screen}
			>
				<Maximise />
			</div>
		</div>
	</div>
</div>

<!-- If in interactive mode, show the additional editing controls below the player. -->
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

	progress {
		margin-right: var(--size-3);
		border-radius: var(--radius-sm);
		width: var(--size-full);
		height: var(--size-2);
	}

	progress::-webkit-progress-bar {
		border-radius: 2px;
		background-color: rgba(255, 255, 255, 0.2);
		overflow: hidden;
	}

	progress::-webkit-progress-value {
		background-color: rgba(255, 255, 255, 0.9);
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
	}
</style>