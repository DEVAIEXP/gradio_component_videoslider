<!-- videoslider/frontend/shared/VideoSliderPreview.svelte -->
<script lang="ts">
	// Svelte and Gradio imports
	import { createEventDispatcher, onMount, onDestroy, tick } from "svelte";
	import type { FileData, Client } from "@gradio/client";
	import type { I18nFormatter } from "@gradio/utils";
	import Slider from "./Slider.svelte";
	import Player from "./Player.svelte";
	import { BlockLabel, Empty, IconButton, IconButtonWrapper, FullscreenButton } from "@gradio/atoms";
	import { Video as VideoIcon, Download, Clear, VolumeMuted, VolumeHigh } from "@gradio/icons";
	import { DownloadLink } from "@gradio/wasm/svelte";

	// ------------------
	// Props
	// ------------------
	export let value: [FileData | null, FileData | null] = [null, null];
	export let label: string | undefined = undefined;
	export let show_download_button = true;
	export let show_label: boolean;
	export let i18n: I18nFormatter;
	export let position: number = 0.5;
	export let slider_color: string;
	export let show_fullscreen_button = true;
	export let show_mute_button = true;
	export let fullscreen = false;
	export let interactive = true;
	export let autoplay = false;
	export let loop = false;
	export let upload: Client["upload"];

	const dispatch = createEventDispatcher<{
		clear: void;
		fullscreen: boolean;
		load: { top: number; left: number; width: number; height: number };
	}>();

	// -----------------
	// Internal State & Element References
	// -----------------
	let video1_el: HTMLVideoElement | undefined;
	let video2_el: HTMLVideoElement | undefined;
	let main_wrapper_el: HTMLDivElement | undefined;
	let image_size = { top: 0, left: 0, width: 0, height: 0 };
	let viewport_width = 0;
	let resizeObserver: ResizeObserver | undefined;
	/** Tracks the muted state for both videos. Starts true to allow autoplay. */
	let isMuted = true;
	/** A flag to prevent the main click handler from firing when interacting with overlay buttons. */
	let isInteractingWithButtons = false;
	/** A flag to ensure the dimension initialization logic runs only once. */
	let is_initialized = false;

	// -----------------
	// Event Handlers
	// -----------------

	/** Toggles the muted state for both videos. */
	function toggleMute(event: Event) {
		event.stopPropagation();
		isInteractingWithButtons = true;
		if (video1_el && video2_el) {
			isMuted = !isMuted;
			video1_el.muted = isMuted;
			video2_el.muted = isMuted;
		}
		setTimeout(() => (isInteractingWithButtons = false), 0);
	}

	/** Clears both videos and resets the slider position. */
	function removeVideos(event: Event) {
		event.stopPropagation();
		isInteractingWithButtons = true;
		value = [null, null];
		position = 0.5;
		dispatch("clear");
		setTimeout(() => (isInteractingWithButtons = false), 0);
	}

	/** Toggles play/pause for both videos simultaneously. */
	function toggle_playback(event: Event): void {
		event.stopPropagation();
		if (!video1_el || !video2_el) return;
		const is_paused = video1_el.paused;
		if (is_paused) {
			video1_el.play().catch(() => {});
			video2_el.play().catch(() => {});
		} else {
			video1_el.pause();
			video2_el.pause();
		}
	}

	/** Handles the fullscreen event from the button, resets position, and dispatches. */
    function handle_fullscreen_toggle(event: CustomEvent<boolean>) {
		position = 0.5; // We still want to reset the position
		dispatch("fullscreen", event.detail);
	}

	/** Handles the load event from the Player component to update dimensions. */
	function handle_video_load(event: CustomEvent) {
		image_size = event.detail;
		if (main_wrapper_el) {
			viewport_width = main_wrapper_el.getBoundingClientRect().width;
		}
		position = 0.5;
		dispatch("load", image_size);
	}
	
	/** A utility function to constrain a value within a minimum and maximum range. */
	function clamp(value: number, min: number, max: number): number {
		return Math.min(Math.max(value, min), max);
	}

	/**
	 * Calculates the clipped position of the slider based on the video's
	 * dimensions and offset within the viewport.
	 */
	function get_coords_at_viewport(
		viewport_percent_x: number,
		viewportWidth: number,
		video_width: number,
		video_offset_x: number
	): number {
		const px_relative_to_video = viewport_percent_x * video_width;
		const pixel_position = px_relative_to_video + video_offset_x;
		const percent_position = pixel_position / viewportWidth;
		return clamp(percent_position, 0, 1);
	}

	/**
	 * Sets up a ResizeObserver to monitor the video and its container,
	 * updating the `image_size` state whenever their dimensions change.
	 */
	function init_video(video: HTMLVideoElement | null, wrapper: HTMLDivElement | null): void {
		if (!video || !wrapper) return;

		resizeObserver?.disconnect();
		const updateVideoDimensions = () => {
			const rect = video.getBoundingClientRect();
			const wrapperRect = wrapper.getBoundingClientRect();
			image_size = {
				top: rect.top - wrapperRect.top,
				left: rect.left - wrapperRect.left,
				width: rect.width || wrapperRect.width,
				height: rect.height || wrapperRect.height
			};
			viewport_width = wrapperRect.width;
			dispatch("load", image_size);
		};

		resizeObserver = new ResizeObserver(() => {
			updateVideoDimensions();
			position = 0.5;
		});

		video.addEventListener('loadedmetadata', updateVideoDimensions);
		resizeObserver.observe(wrapper);
		resizeObserver.observe(video);
		updateVideoDimensions();
	}

	// -----------------
	// Reactive Logic & Lifecycle
	// -----------------

	/** Calculates the coordinates for the CSS clip-path. */
	$: coords_at_viewport = get_coords_at_viewport(
		position,
		viewport_width || 640,
		image_size.width || viewport_width || 640,
		image_size.left || 0
	);
	/** A reactive CSS style to create the "reveal" effect. */
	$: style = `clip-path: inset(0 0 0 ${coords_at_viewport * 100}%)`;

	/** Initializes the video dimension tracking once the necessary elements are available. */
	$: if (main_wrapper_el && video1_el && !is_initialized) {
		init_video(video1_el, main_wrapper_el);
		is_initialized = true;
	}

	/** Synchronizes the state of the two videos (playback time and pause state). */
	$: {
		if (video1_el && autoplay && !video1_el.played.length) {
			video1_el.play().catch(() => {});
		}
		if (video1_el && video2_el) {
			if (Math.abs(video1_el.currentTime - video2_el.currentTime) > 0.1) {
				video2_el.currentTime = video1_el.currentTime;
			}
			if (video1_el.paused !== video2_el.paused) {
				if (video1_el.paused) {
					video2_el.pause();
				} else {
					video2_el.play().catch(() => {});
				}
			}
		}
	}

	/** On mount, sets initial state and cleans up the observer on destroy. */
	onMount(() => {
		position = 0.5;
		if (video1_el) video1_el.muted = true;
		if (video2_el) video2_el.muted = true;
		return () => {
			resizeObserver?.disconnect();
		};
	});
</script>

<BlockLabel {show_label} Icon={VideoIcon} label={label || "Video Slider"} />

{#if value === null || value[0] === null || value[1] === null}
	<Empty unpadded_box={true} size="large"><VideoIcon /></Empty>
{:else}
	<div class="video-container">
		<div
			class="icon-button-wrapper"
			role="group"
		>
			<IconButtonWrapper>
				{#if show_fullscreen_button}
					<FullscreenButton 
						bind:fullscreen
						on:fullscreen={handle_fullscreen_toggle} 
					/>
				{/if}
				{#if show_download_button && value[1]}
					<DownloadLink href={value[1]?.url} download={value[1]?.orig_name || "video"}>
						<IconButton Icon={Download} label={i18n("common.download")} />
					</DownloadLink>
				{/if}
				{#if show_mute_button}
					<div role="button" tabindex="0" on:mousedown|stopPropagation on:touchstart|stopPropagation>
						<IconButton
							Icon={isMuted ? VolumeMuted : VolumeHigh}
							label={isMuted ? i18n("common.unmute") : i18n("common.mute")}
							on:click={toggleMute}
							on:keydown={(event) => {
								if (event.key === "Enter" || event.key === " ") {
									toggleMute(event);
								}
							}}
						/>
					</div>
				{/if}
				{#if interactive}
					<div role="button" tabindex="0" on:mousedown|stopPropagation on:touchstart|stopPropagation>
						<IconButton
							Icon={Clear}
							label="Remove Videos"
							on:click={removeVideos}
							on:keydown={(event) => {
								if (event.key === "Enter" || event.key === " ") {
									removeVideos(event);
								}
							}}
						/>
					</div>
				{/if}
			</IconButtonWrapper>
		</div>

		<div
			class="main-wrapper"
			bind:this={main_wrapper_el}
			on:mousedown|stopPropagation={toggle_playback}
			on:touchstart|stopPropagation={toggle_playback}
			on:keydown={(event) => {
				if (event.key === "Enter" || event.key === " ") {
					toggle_playback(event);
				}
			}}
			role="button"
			tabindex="0"
		>
			<Slider bind:position {slider_color} {image_size} disabled={isInteractingWithButtons} bind:parent_el={main_wrapper_el}>
				<div class="player-wrapper">
					{#if value[0]}
						<Player
							src={value[0].meta?._base64 || value[0].url}
							bind:video_el={video1_el}
							on:load={handle_video_load}
							{loop}
							muted={isMuted}
							{i18n}
							{upload}
							mirror={false}
							is_stream={value[0].is_stream}
							interactive={false}
							{fullscreen}
						/>
					{/if}
				</div>
				<div class="player-wrapper fixed" style={style}>
					{#if value[1]}
						<Player
							src={value[1].meta?._base64 || value[1].url}
							bind:video_el={video2_el}
							{loop}
							muted={isMuted}
							{i18n}
							{upload}
							mirror={false}
							is_stream={value[1].is_stream}
							interactive={false}
							{fullscreen}
						/>
					{/if}
				</div>
			</Slider>
		</div>
	</div>
{/if}

<style>
	.video-container {
		height: 100%;
		width: 100%;
		position: relative;
		display: flex;
		align-items: center;
		justify-content: center;
		overflow: hidden;
		z-index: 1;
	}
	.main-wrapper {
		user-select: none;
		height: 100%;
		width: 100%;
		position: relative;
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 2;
	}
	.player-wrapper {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 3;
		pointer-events: none;
	}
	.player-wrapper.fixed {
		background: var(--block-background-fill);
		z-index: 4;
	}
	.player-wrapper :global(video) {
		width: 100%;
		height: 100%;
		object-fit: contain;
		z-index: 5;
		pointer-events: none;
	}
	:global(.main-wrapper > .wrap) {
		position: absolute;
		top: 0;
		left: 0;
		z-index: 10;
		cursor: default;
	}
	.icon-button-wrapper {
		z-index: 1001; /* Above slider's z-index: 1000 */
		pointer-events: auto;
		position: absolute;
		top: 10px;
		right: 10px;
	}
</style>