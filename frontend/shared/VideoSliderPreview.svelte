<!--
@component
This component provides the display-only view for the VideoSlider. It shows two
videos side-by-side, with a draggable slider to reveal one over the other. It
also handles synchronized play/pause functionality for both videos.
-->
<script lang="ts">
	import { createEventDispatcher } from "svelte";
	import type { FileData, Client } from "@gradio/client";
	import type { I18nFormatter } from "@gradio/utils";

	import Slider from "./Slider.svelte";
	import Player from "./Player.svelte";

	import { BlockLabel, Empty, IconButton, IconButtonWrapper, FullscreenButton } from "@gradio/atoms";
	import { Video as VideoIcon, Download, Clear } from "@gradio/icons";
	import { DownloadLink } from "@gradio/wasm/svelte";

	// ------------------
	// Props
	// ------------------
	export let value: [FileData | null, FileData | null] = [null, null];
	export let label: string | undefined = undefined;
	export let show_download_button = true;
	export let show_label: boolean;
	export let i18n: I18nFormatter;
	/** The normalized (0-1) position of the slider. */
	export let position: number;
	export let slider_color: string;
	export let show_fullscreen_button = true;
	export let fullscreen = false;
	export let interactive = true;
	export let autoplay = false;
	export let loop = false;
	export let upload: Client["upload"];

	const dispatch = createEventDispatcher<{ clear: void }>();

	// -----------------
	// Internal State
	// -----------------
	/** A direct reference to the master HTML <video> element. */
	let video1_el: HTMLVideoElement;
	/** A direct reference to the slave HTML <video> element. */
	let video2_el: HTMLVideoElement;
	
	/** A flag that becomes true once the master video has loaded its data. */
	let video_is_ready = false;
	/** A flag to ensure the initial autoplay logic runs only once. */
	let initial_autoplay_done = false;

	/** A reactive CSS style to create the "reveal" effect based on the slider's position. */
	$: style = `clip-path: inset(0 0 0 ${position * 100}%)`;

	// -----------------
	// Event Handlers
	// -----------------

	/** Sets a flag to true when the master video signals it's ready to play. */
	function handle_video_ready(): void {
		video_is_ready = true;
	}

	/** Toggles play/pause for both videos simultaneously when the user interacts. */
	function toggle_playback(): void {
		if (!video1_el || !video2_el) {
			return;
		}

		const is_paused = video1_el.paused;

		if (is_paused) {
			video1_el.play().catch(() => {});
			video2_el.play().catch(() => {});
		} else {
			video1_el.pause();
			video2_el.pause();
		}
	}

	// -----------------
	// Reactive Logic
	// -----------------
	$: {
		// This block handles initial autoplay once all conditions are met, preventing race conditions.
		if (video1_el && video_is_ready && autoplay && !initial_autoplay_done) {
			video1_el.play().catch(() => {});
			initial_autoplay_done = true;
		}

		// This block continuously synchronizes the slave video to the master video.
		if (video1_el && video2_el) {
			// Sync playback time.
			if (Math.abs(video1_el.currentTime - video2_el.currentTime) > 0.1) {
				video2_el.currentTime = video1_el.currentTime;
			}

			// Sync play/pause state.
			if (video1_el.paused !== video2_el.paused) {
				if (video1_el.paused) {
					video2_el.pause();
				} else {
					video2_el.play().catch(() => {});
				}
			}
		}
	}
</script>

<BlockLabel {show_label} Icon={VideoIcon} label={label || "Video Slider"} />

<!-- Show an empty state if no videos are provided. -->
{#if value === null || value[0] === null || value[1] === null}
	<Empty unpadded_box={true} size="large"><VideoIcon /></Empty>
{:else}
	<div class="video-container">
		<IconButtonWrapper>
            {#if show_fullscreen_button}
                <FullscreenButton {fullscreen} on:fullscreen />
            {/if}

            {#if show_download_button && value[1]}
                <DownloadLink href={value[1].meta?._base64 || value[1].url} download={value[1].orig_name || "video"}>
                    <IconButton Icon={Download} label={i18n("common.download")} />
                </DownloadLink>
            {/if}
			
            {#if interactive}
                <IconButton
                    Icon={Clear}
                    label="Remove Videos"
                    on:click={(event) => {
                        value = [null, null];
                        dispatch("clear");
                        event.stopPropagation();
                    }}
                />
            {/if}
		</IconButtonWrapper>

		<!-- This main wrapper handles clicks for the entire area and makes it accessible. -->
		<div
			class="main-wrapper"
			on:click={toggle_playback}
			on:keydown={(event) => {
				if (event.key === 'Enter' || event.key === ' ') {
					toggle_playback();
				}
			}}
			role="button"
			tabindex="0"
		>
			<!-- The first (bottom) video player. -->
			<div class="player-wrapper">
				{#if value[0]}
					<Player
						src={value[0].meta?._base64 || value[0].url}
						bind:video_el={video1_el}
						on:loadeddata={handle_video_ready}
						{loop}
						muted={true}
						{i18n}
						{upload}
						mirror={false}
						is_stream={value[0].is_stream}
						interactive={false}
					/>
				{/if}
			</div>

			<!-- The second (top, clipped) video player. -->
			<div class="player-wrapper fixed" {style}>
				{#if value[1]}
					<Player
						src={value[1].meta?._base64 || value[1].url}
						bind:video_el={video2_el} 
						{loop}
						muted={true}
						{i18n}
						{upload}
						mirror={false}
						is_stream={value[1].is_stream}
						interactive={false}
					/>
				{/if}
			</div>

			<!-- The slider is an overlay for dragging, but does not handle clicks. -->
			<Slider 
				bind:position 
				{slider_color}
			/>
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
	}

	.main-wrapper {
		position: relative;
		width: 100%;
		height: 100%;
		cursor: pointer;
	}

	.player-wrapper {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
	}

	.player-wrapper.fixed {
		background: var(--block-background-fill);
	}

	/* Ensure the Slider component is layered on top of the video players. */
	:global(.main-wrapper > .wrap) {
		position: absolute;
		top: 0;
		left: 0;
		z-index: 10;
		cursor: default;
	}
</style>