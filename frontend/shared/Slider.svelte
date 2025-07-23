<!-- videoslider/frontend/shared/Slider.svelte -->
<script lang="ts">
	// Svelte and D3 imports
	import { onMount, tick } from "svelte";
	import { drag } from "d3-drag";
	import { select } from "d3-selection";

	/** A utility function to constrain a value within a minimum and maximum range. */
	function clamp(value: number, min: number, max: number): number {
		return Math.min(Math.max(value, min), max);
	}

	// ------------------
	// Props
	// ------------------
	/** The slider's position as a normalized value (0 to 1). Can be two-way bound. */
	export let position = 0.5;
	/** If true, disables all dragging and interaction. */
	export let disabled = false;
	/** The color of the vertical slider line. */
	export let slider_color = "var(--border-color-primary)";
	/** The dimensions of the content being compared. */
	export let image_size: { top: number; left: number; width: number; height: number };
	/** A reference to the content element. */
	export let el: HTMLDivElement | undefined = undefined;
	/** A reference to the main wrapper element. */
	export let parent_el: HTMLDivElement | undefined = undefined;

	// -----------------
	// Internal State
	// -----------------
	/** A reference to the draggable handle element. */
	let inner: HTMLDivElement | undefined;
	/** The slider's horizontal position in pixels. */
	let px = 0;
	/** True while the user is actively dragging the handle. */
	let active = false;
	let container_width = 0;

	/**
	 * Calculates and sets the slider's pixel position based on its container's dimensions.
	 * This is called reactively and by the ResizeObserver.
	 */
	function set_position(): void {
		if (!parent_el) return;
		const rect = parent_el.getBoundingClientRect();
		container_width = rect.width;
		px = clamp(container_width * position, 0, container_width);
	}

	/** A utility function to round a number to a specific number of decimal points. */
	function round(n: number, points: number): number {
		const mod = Math.pow(10, points);
		return Math.round((n + Number.EPSILON) * mod) / mod;
	}

	/** Updates the internal state based on the drag's x-coordinate in pixels. */
	function update_position(x: number): void {
		if (!parent_el || !image_size?.width) return;
		container_width = parent_el.getBoundingClientRect().width;
		px = clamp(x, 0, container_width);
		position = round((px - image_size.left) / image_size.width, 5);
	}

	// -----------------
	// D3 Drag Handlers
	// -----------------

	/** Handles the start of a drag action. */
	function drag_start(event: any): void {
		if (disabled) return;
		active = true;
		update_position(event.x);
	}

	/** Handles the movement during a drag action. */
	function drag_move(event: any): void {
		if (disabled) return;
		update_position(event.x);
	}

	/** Handles the end of a drag action. */
	function drag_end(): void {
		if (disabled) return;
		active = false;
	}

	// -----------------
	// Reactive Logic & Lifecycle
	// -----------------

	/** Reactively updates the slider's pixel position whenever the normalized `position` changes. */
	$: set_position();

	/** Reactively applies the calculated pixel position to the handle's style. */
	$: if (inner) {
		inner.style.transform = `translateX(${px}px)`;
	}

	/** On mount, sets up the d3-drag handler and a ResizeObserver to keep the layout correct. */
	onMount(() => {
		if (!inner) return;

		const drag_handler = drag()
			.on("start", drag_start)
			.on("drag", drag_move)
			.on("end", drag_end)
			.touchable(() => true);

		select(inner).call(drag_handler);

		const resizeObserver = new ResizeObserver(() => {
			tick().then(() => set_position());
		});

		if (parent_el) {
			resizeObserver.observe(parent_el);
		}

		return () => {
			resizeObserver.disconnect();
		};
	});
</script>

<svelte:window on:resize={() => {
	tick().then(() => set_position());
}} />

<div class="wrap" role="none" bind:this={parent_el}>
	<div class="content" bind:this={el}>
		<slot />
	</div>
	<div
		class="outer"
		class:disabled
		bind:this={inner}
		role="none"
		class:grab={active}
		on:click|stopPropagation
	>
		<span class="icon-wrap" class:active class:disabled>
			<span class="icon left">◢</span>
			<span class="icon center" style:--color={slider_color}></span>
			<span class="icon right">◢</span>
		</span>
		<div class="inner" style:--color={slider_color}></div>
	</div>
</div>

<style>
	.wrap {
		position: relative;
		width: 100%;
		height: 100%;
		z-index: var(--layer-1);
		overflow: hidden;
	}
	.icon-wrap {
		display: flex;
		position: absolute;
		top: 50%;
		transform: translate(-50%, -50%);
		left: 50%;
		width: 40px;
		transition: 0.2s;
		color: var(--body-text-color);
		height: 30px;
		border-radius: 5px;
		background-color: var(--color-accent);
		align-items: center;
		justify-content: center;
		z-index: var(--layer-3);
		box-shadow: 0px 0px 5px 2px rgba(0, 0, 0, 0.3);
		font-size: 12px;
		pointer-events: auto;
	}
	.icon.left {
		transform: rotate(135deg);
		text-shadow: -1px -1px 1px rgba(0, 0, 0, 0.1);
	}
	.icon.right {
		transform: rotate(-45deg);
		text-shadow: -1px -1px 1px rgba(0, 0, 0, 0.1);
	}
	.icon.center {
		display: block;
		width: 1px;
		height: 100%;
		background-color: var(--color);
		opacity: 0.5;
	}
	.outer {
		width: 40px;
		height: 100%;
		position: absolute;
		cursor: grab;
		top: 0;
		left: -20px;
		pointer-events: auto;
		z-index: 1000;
	}
	.grab {
		cursor: grabbing;
	}
	.inner {
		width: 1px;
		height: 100%;
		background: var(--color);
		position: absolute;
		left: calc((100% - 1px) / 2);
	}
	.disabled {
		cursor: not-allowed;
		opacity: 0.5;
	}
	.disabled .inner {
		box-shadow: none;
	}
	.content {
		width: 100%;
		height: 100%;
		display: flex;
		justify-content: center;
		align-items: center;
	}
</style>