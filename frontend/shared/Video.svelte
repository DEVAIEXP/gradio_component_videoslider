<!--
@component
This is the foundational video component, a wrapper around the native HTML `<video>` tag.
It adds advanced functionality like HLS streaming support and compatibility with
Gradio's WebAssembly (Wasm) environment. It also forwards native video events
to parent components.
-->
<svelte:options accessors={true} />

<script lang="ts">
	import type { HTMLVideoAttributes } from "svelte/elements";
	import { createEventDispatcher } from "svelte";
	import { loaded } from "./utils";

	import { resolve_wasm_src } from "@gradio/wasm/svelte";

	import Hls from "hls.js";

	// ------------------
	// Props
	// ------------------

	// --- Standard Video Attributes ---
	export let src: HTMLVideoAttributes["src"] = undefined;
	export let muted: HTMLVideoAttributes["muted"] = undefined;
	export let playsinline: HTMLVideoAttributes["playsinline"] = undefined;
	export let preload: HTMLVideoAttributes["preload"] = undefined;
	export let autoplay: HTMLVideoAttributes["autoplay"] = undefined;
	export let controls: HTMLVideoAttributes["controls"] = undefined;
	export let loop: boolean;
	
	// --- Two-way Bound State ---
	export let currentTime: number | undefined = undefined;
	export let duration: number | undefined = undefined;
	export let paused: boolean | undefined = undefined;

	// --- Specialized Props ---
	/** A direct reference to the underlying HTML <video> element. */
	export let node: HTMLVideoElement | undefined = undefined;
	/** If true, the source is an HLS stream and will be handled by hls.js. */
	export let is_stream;
	/** If true, displays a loading overlay on the video. */
	export let processingVideo = false;

	// -----------------
	// Internal State
	// -----------------
	let resolved_src: typeof src;
	let stream_active = false;

	// This block handles resolving video sources in a WebAssembly (Wasm) environment.
	// It prevents UI flickering by showing the original `src` immediately while the
	// Wasm-compatible source is being resolved asynchronously.
	let latest_src: typeof src;
	$: {
		resolved_src = src;
		latest_src = src;
		const resolving_src = src;
		resolve_wasm_src(resolving_src).then((s) => {
			if (latest_src === resolving_src) {
				resolved_src = s;
			}
		});
	}

	const dispatch = createEventDispatcher();

	/**
	 * Initializes and attaches an HLS.js player to the video element for streaming.
	 * This is only triggered when the `is_stream` prop is true.
	 * @param src The URL of the HLS manifest (.m3u8 file).
	 * @param is_stream A flag to enable or disable this functionality.
	 * @param node The HTML video element to attach the stream to.
	 */
	function load_stream(
		src: string | null | undefined,
		is_stream: boolean,
		node: HTMLVideoElement
	): void {
		if (!src || !is_stream) return;

		if (Hls.isSupported() && !stream_active) {
			const hls = new Hls({
				// Low-latency configuration
				maxBufferLength: 1,
				maxMaxBufferLength: 1,
				lowLatencyMode: true
			});
			hls.loadSource(src);
			hls.attachMedia(node);
			hls.on(Hls.Events.MANIFEST_PARSED, function () {
				(node as HTMLVideoElement).play();
			});
			hls.on(Hls.Events.ERROR, function (event, data) {
				if (data.fatal) {
					switch (data.type) {
						case Hls.ErrorTypes.NETWORK_ERROR:
							hls.startLoad();
							break;
						case Hls.ErrorTypes.MEDIA_ERROR:
							hls.recoverMediaError();
							break;
						default:
							hls.destroy();
							break;
					}
				}
			});
			stream_active = true;
		}
	}

	/** Reset the HLS stream when the video source changes. */
	$: src, (stream_active = false);

	/** Trigger the HLS stream loader if the source is a stream. */
	$: if (node && src && is_stream) {
		load_stream(src, is_stream, node);
	}
</script>

<!--
A necessary comment explaining a Svelte-specific quirk:
The spread operator with `$$props` or `$$restProps` can't be used here
to pass props from the parent component to the <video> element
because of its unexpected behavior: https://github.com/sveltejs/svelte/issues/7404
-->
<div class:hidden={!processingVideo} class="overlay">
	<span class="load-wrap">
		<span class="loader" />
	</span>
</div>
<video
	src={resolved_src}
	{muted}
	{playsinline}
	{preload}
	{autoplay}
	{controls}
	{loop}
	
	
	on:loadeddata={dispatch.bind(null, "loadeddata")}
	on:click={dispatch.bind(null, "click")}
	on:play={dispatch.bind(null, "play")}
	on:pause={dispatch.bind(null, "pause")}
	on:ended={dispatch.bind(null, "ended")}
	on:error={dispatch.bind(null, "error", "Video not playable")}
	
	
	bind:currentTime
	bind:duration
	bind:paused
	bind:this={node}

	
	use:loaded={{ autoplay: autoplay ?? false }}

	data-testid={$$props["data-testid"]}
	crossorigin="anonymous"
>
	<slot />
</video>

<style>
	.overlay {
		position: absolute;
		background-color: rgba(0, 0, 0, 0.4);
		width: 100%;
		height: 100%;
	}

	.hidden {
		display: none;
	}

	.load-wrap {
		display: flex;
		justify-content: center;
		align-items: center;
		height: 100%;
	}

	.loader {
		display: flex;
		position: relative;
		background-color: var(--border-color-accent-subdued);
		animation: shadowPulse 2s linear infinite;
		box-shadow:
			-24px 0 var(--border-color-accent-subdued),
			24px 0 var(--border-color-accent-subdued);
		margin: var(--spacing-md);
		border-radius: 50%;
		width: 10px;
		height: 10px;
		scale: 0.5;
	}

	@keyframes shadowPulse {
		33% {
			box-shadow:
				-24px 0 var(--border-color-accent-subdued),
				24px 0 #fff;
			background: #fff;
		}
		66% {
			box-shadow:
				-24px 0 #fff,
				24px 0 #fff;
			background: var(--border-color-accent-subdued);
		}
		100% {
			box-shadow:
				-24px 0 #fff,
				24px 0 var(--border-color-accent-subdued);
			background: #fff;
		}
	}
</style>