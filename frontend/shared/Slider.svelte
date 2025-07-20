<!--
@component
A general-purpose draggable slider component that can be laid over other content.
It uses d3-drag for robust drag handling and is designed to differentiate
between a "drag" action and a "click" action.
-->
<script lang="ts">
    import { onMount, createEventDispatcher } from "svelte";
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
    /** Layout-related props, typically bound from the parent, used for calculating pixel positions. */
    export let image_size: {
        top: number;
        left: number;
        width: number;
        height: number;
    } = { top: 0, left: 0, width: 0, height: 0 };
    export let el: HTMLDivElement | undefined = undefined;
    export let parent_el: HTMLDivElement | undefined = undefined;
    
    /** Dispatches a 'click' event ONLY if the user clicks the handle without dragging. */
    const dispatch = createEventDispatcher<{ click: MouseEvent }>();

    // -----------------
    // Internal State
    // -----------------
    let inner: Element;
    /** The slider's horizontal position in pixels. */
    let px = 0;
    /** True while the user is actively dragging the handle. */
    let active = false;
    let container_width = 0;
    
    let drag_start_x: number;
    /** A flag to determine if a drag action actually moved, differentiating it from a simple click. */
    let was_dragged = false;

    // -----------------
    // Functions
    // -----------------

    /** Calculates the slider's pixel position based on its container's dimensions. */
    function set_position(width: number): void {
        container_width = parent_el?.getBoundingClientRect().width || 0;
        if (width === 0) {
            image_size.width = el?.getBoundingClientRect().width || 0;
        }
        px = clamp(
            image_size.width * position + image_size.left,
            0,
            container_width
        );
    }

    function round(n: number, points: number): number {
        const mod = Math.pow(10, points);
        return Math.round((n + Number.EPSILON) * mod) / mod;
    }

    /** Updates the internal state based on the drag's x-coordinate. */
    function update_position(x: number): void {
        px = clamp(x, 0, container_width);
        position = round((x - image_size.left) / image_size.width, 5);
    }

    // --- D3 Drag Event Handlers ---

    function drag_start(event: any): void {
        if (disabled) return;
        active = true;
        update_position(event.x);
        drag_start_x = event.x;
        was_dragged = false;
    }

    function drag_move(event: any): void {
        if (disabled) return;
        update_position(event.x);
        if (Math.abs(event.x - drag_start_x) > 3) {
            was_dragged = true;
        }
    }

    function drag_end(event: any): void {
        if (disabled) return;
        active = false;
        if (!was_dragged) {
            dispatch("click", event.sourceEvent);
        }
    }

    /** Updates the pixel position when the `position` prop changes from the parent. */
    function update_position_from_pc(pc: number): void {
        px = clamp(image_size.width * pc + image_size.left, 0, container_width);
    }

    // -----------------
    // Lifecycle & Reactive Logic
    // -----------------
    $: set_position(image_size.width);
    $: update_position_from_pc(position);

    onMount(() => {
        set_position(image_size.width);
        const drag_handler = drag()
            .on("start", drag_start)
            .on("drag", drag_move)
            .on("end", drag_end);
        select(inner).call(drag_handler);
    });
</script>

<!-- Recalculate position on window resize. -->
<svelte:window on:resize={() => set_position(image_size.width)} />

<div class="wrap" role="none" bind:this={parent_el}>
    <!-- The content from the parent component is placed here. -->
    <div class="content" bind:this={el}>
        <slot />
    </div>

    <!-- This is the draggable handle area. -->
    <div
        class="outer"
        class:disabled
        bind:this={inner}
        role="none"
        style="transform: translateX({px}px)"
        class:grab={active}
		on:click={(event) => event.stopPropagation()}
    >
        <span class="icon-wrap" class:active class:disabled>
			<span class="icon left">◢</span>
			<span class="icon center" style:--color={slider_color}></span>
			<span class="icon right">◢</span>
		</span>
        <!-- This is the visible vertical line of the slider. -->
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
        display: block;
        position: absolute;
        top: 50%;
        transform: translate(-20.5px, -50%);
        left: 10px;
        width: 40px;
        transition: 0.2s;
        color: var(--body-text-color);
        height: 30px;
        border-radius: 5px;
        background-color: var(--color-accent);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: var(--layer-3);
        box-shadow: 0px 0px 5px 2px rgba(0, 0, 0, 0.3);
        font-size: 12px;
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
        opacity: 0.1;
    }

    .icon-wrap.active {
        opacity: 0;
    }

    .icon-wrap.disabled {
        opacity: 0;
    }

    .outer {
        width: 20px;
        height: 100%;
        position: absolute;
        cursor: grab;
        top: 0;
        left: -10px;
        pointer-events: auto;
        z-index: var(--layer-2);
    }
    .grab {
        cursor: grabbing;
    }

    .inner {
        width: 1px;
        height: 100%;
        background: var(--color);
        position: absolute;
        left: calc((100% - 2px) / 2);
    }

    .disabled {
        cursor: auto;
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