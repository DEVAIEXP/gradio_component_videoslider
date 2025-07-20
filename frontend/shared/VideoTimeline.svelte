<!--
@component
This component displays a visual timeline of a video, composed of generated
thumbnails. It features draggable start and end handles, allowing a user to
select a specific segment of the video for trimming.
-->
<script lang="ts">
	import { onMount, onDestroy } from "svelte";

	// ------------------
	// Props
	// ------------------
	/** A direct reference to the HTML <video> element to be analyzed. */
	export let videoElement: HTMLVideoElement;
	/** The calculated duration of the selected trim region (two-way bound). */
	export let trimmedDuration: number | null;
	/** The start time of the selection in seconds (two-way bound). */
	export let dragStart: number;
	/** The end time of the selection in seconds (two-way bound). */
	export let dragEnd: number;
	/** A flag indicating if the timeline is currently being generated (two-way bound). */
	export let loadingTimeline: boolean;

	// -----------------
	// Internal State
	// -----------------
	/** An array of base64-encoded thumbnail images. */
	let thumbnails: string[] = [];
	let numberOfThumbnails = 10;
	let videoDuration: number;
	
	/** The percentage-based position of the left and right drag handles. */
	let leftHandlePosition = 0;
	let rightHandlePosition = 100;
	
	/** The currently active drag handle ('left', 'right', or null). */
	let dragging: string | null = null;

	// -----------------
	// Functions
	// -----------------

	const startDragging = (side: string | null): void => {
		dragging = side;
	};

	const stopDragging = (): void => {
		dragging = null;
	};

	/**
	 * Handles the movement of a drag handle, updating its position and the
	 * corresponding video playback time.
	 * @param event The mouse event.
	 * @param distance Optional distance for keyboard-based movement.
	 */
	const drag = (event: { clientX: number }, distance?: number): void => {
		if (dragging) {
			const timeline = document.getElementById("timeline");
			if (!timeline) return;

			const rect = timeline.getBoundingClientRect();
			let newPercentage: number;

			if (distance) {
				// Move handle based on arrow key press.
				newPercentage =
					dragging === "left"
						? leftHandlePosition + distance
						: rightHandlePosition + distance;
			} else {
				// Move handle based on mouse drag.
				newPercentage = ((event.clientX - rect.left) / rect.width) * 100;
			}

			newPercentage = Math.max(0, Math.min(newPercentage, 100));

			if (dragging === "left") {
				leftHandlePosition = Math.min(newPercentage, rightHandlePosition);
				const newTimeLeft = (leftHandlePosition / 100) * videoDuration;
				videoElement.currentTime = newTimeLeft; // Seek video to new start time
				dragStart = newTimeLeft;
			} else if (dragging === "right") {
				rightHandlePosition = Math.max(newPercentage, leftHandlePosition);
				const newTimeRight = (rightHandlePosition / 100) * videoDuration;
				videoElement.currentTime = newTimeRight; // Seek video to new end time
				dragEnd = newTimeRight;
			}

			const startTime = (leftHandlePosition / 100) * videoDuration;
			const endTime = (rightHandlePosition / 100) * videoDuration;
			trimmedDuration = endTime - startTime;
		}
	};

	/** Handles moving the drag handles with the arrow keys for accessibility. */
	const moveHandle = (e: KeyboardEvent): void => {
		if (dragging) {
			const distance = (1 / videoDuration) * 100;

			if (e.key === "ArrowLeft") {
				drag({ clientX: 0 }, -distance);
			} else if (e.key === "ArrowRight") {
				drag({ clientX: 0 }, distance);
			}
		}
	};

	/** Generates a single thumbnail by drawing the current video frame to a canvas. */
	const generateThumbnail = (): void => {
		const canvas = document.createElement("canvas");
		const ctx = canvas.getContext("2d");
		if (!ctx) return;

		canvas.width = videoElement.videoWidth;
		canvas.height = videoElement.videoHeight;
		ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

		const thumbnail: string = canvas.toDataURL("image/jpeg", 0.7);
		thumbnails = [...thumbnails, thumbnail];
	};

	// -----------------
	// Lifecycle
	// -----------------

	/** A reactive statement that updates the loading state based on thumbnail generation. */
	$: loadingTimeline = thumbnails.length !== numberOfThumbnails;

	onMount(() => {
		/**
		 * Orchestrates the thumbnail generation process by seeking the video to
		 * different time points and capturing a frame at each point.
		 */
		const loadMetadata = (): void => {
			videoDuration = videoElement.duration;
			dragEnd = videoDuration;
			const interval = videoDuration / numberOfThumbnails;
			let captures = 0;

			const onSeeked = (): void => {
				generateThumbnail();
				captures++;

				if (captures < numberOfThumbnails) {
					videoElement.currentTime += interval;
				} else {
					videoElement.removeEventListener("seeked", onSeeked);
				}
			};

			videoElement.addEventListener("seeked", onSeeked);
			videoElement.currentTime = 0; // Start the seeking process
		};

		// Wait for the video's metadata to be loaded before starting.
		if (videoElement.readyState >= 1) {
			loadMetadata();
		} else {
			videoElement.addEventListener("loadedmetadata", loadMetadata);
		}

		// Add global event listeners for dragging.
		window.addEventListener("mousemove", drag);
		window.addEventListener("mouseup", stopDragging);
		window.addEventListener("keydown", moveHandle);
	});

	onDestroy(() => {
		// Clean up global event listeners to prevent memory leaks.
		window.removeEventListener("mousemove", drag);
		window.removeEventListener("mouseup", stopDragging);
		window.removeEventListener("keydown", moveHandle);
	});
</script>

<div class="container">
	<!-- Show a loader while thumbnails are being generated. -->
	{#if loadingTimeline}
		<div class="load-wrap">
			<span aria-label="loading timeline" class="loader" />
		</div>
	<!-- Once loaded, display the timeline. -->
	{:else}
		<div id="timeline" class="thumbnail-wrapper">
			<!-- The left (start) drag handle. -->
			<button
				aria-label="start drag handle for trimming video"
				class="handle left"
				on:mousedown={() => startDragging("left")}
				on:blur={stopDragging}
				on:keydown={(e) => {
					if (e.key === 'ArrowLeft' || e.key == 'ArrowRight') {
						startDragging("left");
					}
				}}
				style="left: {leftHandlePosition}%;"
			/>

			<!-- The colored overlay indicating the selected region. -->
			<div
				class="opaque-layer"
				style="left: {leftHandlePosition}%; right: {100 - rightHandlePosition}%"
			/>

			<!-- The generated video frame thumbnails. -->
			{#each thumbnails as thumbnail, i (i)}
				<img src={thumbnail} alt={`frame-${i}`} draggable="false" />
			{/each}

			<!-- The right (end) drag handle. -->
			<button
				aria-label="end drag handle for trimming video"
				class="handle right"
				on:mousedown={() => startDragging("right")}
				on:blur={stopDragging}
				on:keydown={(e) => {
					if (e.key === 'ArrowLeft' || e.key == 'ArrowRight') {
						startDragging("right");
					}
				}}
				style="left: {rightHandlePosition}%;"
			/>
		</div>
	{/if}
</div>

<style>
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

	.container {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		margin: var(--spacing-lg) var(--spacing-lg) 0 var(--spacing-lg);
	}

	#timeline {
		display: flex;
		height: var(--size-10);
		flex: 1;
		position: relative;
	}

	img {
		flex: 1 1 auto;
		min-width: 0;
		object-fit: cover;
		height: var(--size-12);
		border: 1px solid var(--block-border-color);
		user-select: none;
		z-index: 1;
	}

	.handle {
		width: 3px;
		background-color: var(--color-accent);
		cursor: ew-resize;
		height: var(--size-12);
		z-index: 3;
		position: absolute;
	}

	.opaque-layer {
		background-color: rgba(230, 103, 40, 0.25);
		border: 1px solid var(--color-accent);
		height: var(--size-12);
		position: absolute;
		z-index: 2;
	}
</style>