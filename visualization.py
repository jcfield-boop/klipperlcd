#!/usr/bin/env python3
"""
Visualization helpers for KlipperLCD

Provides formatting functions to display bed mesh data, statistics,
and other calibration information on the LCD screen.
"""


def format_bed_mesh_grid(mesh_data, max_width=40):
    """
    Format bed mesh as a text grid for LCD display

    Args:
        mesh_data: Dict with 'points', 'min', 'max', 'range'
        max_width: Maximum width for grid display

    Returns:
        String with formatted grid
    """
    if not mesh_data or not mesh_data.get('points'):
        return "No mesh data available"

    points = mesh_data['points']
    mesh_min = mesh_data['min']
    mesh_max = mesh_data['max']
    mesh_range = mesh_data['range']

    rows = len(points)
    cols = len(points[0]) if points else 0

    # Build header
    output = [f"Bed Mesh ({mesh_data.get('profile_name', 'default')}):"]
    output.append("=" * min(max_width, 35))

    # Format grid - show values with color indicators
    for row in points:
        row_str = ""
        for point in row:
            # Format to 2 decimal places with + sign for positive
            if point >= 0:
                row_str += f" +{point:.2f}"
            else:
                row_str += f" {point:.2f}"
        output.append(row_str)

    # Add statistics
    output.append("=" * min(max_width, 35))
    output.append(f"Min: {mesh_min:+.3f}mm  Max: {mesh_max:+.3f}mm")
    output.append(f"Range: {mesh_range:.3f}mm")

    # Quality assessment
    if mesh_range < 0.05:
        quality = "Excellent"
    elif mesh_range < 0.1:
        quality = "Good"
    elif mesh_range < 0.2:
        quality = "Fair"
    else:
        quality = "Poor - Re-level needed"

    output.append(f"Quality: {quality}")

    return "\n".join(output)


def format_mesh_stats_compact(mesh_data):
    """
    Format mesh statistics in compact form for status display

    Args:
        mesh_data: Dict with mesh statistics

    Returns:
        String with compact stats
    """
    if not mesh_data:
        return "No mesh loaded"

    return (f"Mesh: {mesh_data.get('profile_name', 'default')} | "
            f"Range: {mesh_data.get('range', 0):.3f}mm | "
            f"Min: {mesh_data.get('min', 0):+.3f} Max: {mesh_data.get('max', 0):+.3f}")


def colorize_mesh_value(value, mesh_min, mesh_max):
    """
    Determine color code for mesh point based on deviation

    Args:
        value: The mesh point value
        mesh_min: Minimum mesh value
        mesh_max: Maximum mesh value

    Returns:
        String: 'green', 'yellow', or 'red'
    """
    # Normalize to range 0-1
    if mesh_max == mesh_min:
        return 'green'

    normalized = (value - mesh_min) / (mesh_max - mesh_min)

    # Determine color based on how close to extremes
    if abs(value - mesh_min) < 0.02 or abs(value - mesh_max) < 0.02:
        return 'red'  # Near extremes
    elif normalized < 0.3 or normalized > 0.7:
        return 'yellow'  # Moderately far from center
    else:
        return 'green'  # Near center


def format_pressure_advance_info(pa_value):
    """
    Format pressure advance value with helpful context

    Args:
        pa_value: Current PA value

    Returns:
        String with formatted PA info
    """
    lines = [
        f"Pressure Advance: {pa_value:.4f}",
        "",
        "Typical ranges:",
        "  Bowden: 0.3 - 0.7",
        "  Direct Drive: 0.02 - 0.1",
        "",
    ]

    # Give feedback on current value
    if pa_value < 0.01:
        lines.append("Status: Very low (or disabled)")
    elif pa_value < 0.15:
        lines.append("Status: Typical for direct drive")
    elif pa_value < 0.4:
        lines.append("Status: Moderate (bowden/hybrid)")
    else:
        lines.append("Status: High (long bowden)")

    return "\n".join(lines)


def format_input_shaper_info(shaper_config):
    """
    Format input shaper configuration for display

    Args:
        shaper_config: Dict with shaper configuration

    Returns:
        String with formatted shaper info
    """
    if not shaper_config:
        return "Input Shaper: Not configured"

    x_type = shaper_config.get('shaper_type_x', 'none')
    x_freq = shaper_config.get('shaper_freq_x', 0.0)
    y_type = shaper_config.get('shaper_type_y', 'none')
    y_freq = shaper_config.get('shaper_freq_y', 0.0)

    # Determine if enabled
    enabled = x_freq > 0 or y_freq > 0

    lines = [
        f"Input Shaper: {'ENABLED' if enabled else 'DISABLED'}",
        "",
        f"X-axis: {x_type.upper()}",
        f"  Frequency: {x_freq:.1f} Hz" if x_freq > 0 else "  (disabled)",
        "",
        f"Y-axis: {y_type.upper()}",
        f"  Frequency: {y_freq:.1f} Hz" if y_freq > 0 else "  (disabled)",
    ]

    return "\n".join(lines)


def format_klipper_state(state_info):
    """
    Format Klipper state information for display

    Args:
        state_info: Dict with 'state' and 'message'

    Returns:
        Tuple of (status_text, color)
    """
    state = state_info.get('state', 'unknown').lower()
    message = state_info.get('message', '')

    state_map = {
        'ready': ('Ready', 'green'),
        'startup': ('Starting...', 'yellow'),
        'shutdown': ('Shutdown', 'red'),
        'error': ('Error', 'red'),
        'unknown': ('Unknown', 'yellow')
    }

    status_text, color = state_map.get(state, ('Unknown', 'yellow'))

    if message and state in ['shutdown', 'error']:
        # Truncate long error messages
        if len(message) > 100:
            message = message[:97] + "..."
        status_text = f"{status_text}: {message}"

    return status_text, color


def format_file_metadata(metadata):
    """
    Format file metadata for display before printing

    Args:
        metadata: Dict with file metadata

    Returns:
        String with formatted metadata
    """
    if not metadata:
        return "No metadata available"

    lines = []

    # Print time
    est_time = metadata.get('estimated_time', 0)
    if est_time > 0:
        hours = int(est_time // 3600)
        minutes = int((est_time % 3600) // 60)
        lines.append(f"Time: {hours}h {minutes}m")

    # Filament usage
    filament_length = metadata.get('filament_total', 0)
    filament_weight = metadata.get('filament_weight_total', 0)
    if filament_length > 0:
        lines.append(f"Filament: {filament_length / 1000:.2f}m")
    if filament_weight > 0:
        lines.append(f"Weight: {filament_weight:.1f}g")

    # Layer info
    layer_height = metadata.get('layer_height', 0)
    layer_count = metadata.get('layer_count', 0)
    first_layer = metadata.get('first_layer_height', 0)

    if layer_height > 0:
        lines.append(f"Layer: {layer_height}mm")
    if first_layer > 0 and first_layer != layer_height:
        lines.append(f"First Layer: {first_layer}mm")
    if layer_count > 0:
        lines.append(f"Layers: {int(layer_count)}")

    # Slicer info
    slicer = metadata.get('slicer', '')
    if slicer and slicer != 'Unknown':
        version = metadata.get('slicer_version', '')
        if version:
            lines.append(f"Slicer: {slicer} {version}")
        else:
            lines.append(f"Slicer: {slicer}")

    return "\n".join(lines) if lines else "Limited metadata"


def format_system_stats(mcu_stats):
    """
    Format MCU and system statistics

    Args:
        mcu_stats: Dict with MCU statistics

    Returns:
        String with formatted stats
    """
    if not mcu_stats:
        return "No system stats available"

    lines = []

    # MCU temperature
    mcu_temp = mcu_stats.get('mcu_temp')
    if mcu_temp is not None:
        lines.append(f"MCU Temp: {mcu_temp:.1f}°C")

        # Warn if temperature is high
        if mcu_temp > 70:
            lines.append("  WARNING: High MCU temp!")
        elif mcu_temp > 60:
            lines.append("  (Warm - monitor)")

    return "\n".join(lines) if lines else "Stats unavailable"


# Helper function for wizard progress
def format_wizard_progress(current_step, total_steps, step_name):
    """
    Format wizard progress indicator

    Args:
        current_step: Current step number (1-indexed)
        total_steps: Total number of steps
        step_name: Name of current step

    Returns:
        String with progress indicator
    """
    progress_bar = "=" * current_step + "-" * (total_steps - current_step)
    percentage = int((current_step / total_steps) * 100)

    return (f"Step {current_step} of {total_steps} ({percentage}%)\n"
            f"[{progress_bar}]\n"
            f"{step_name}")
