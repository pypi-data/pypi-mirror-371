"""Color utilities for sping UI components with multiple palette support."""

from enum import Enum
from typing import Dict, List


class ColorPalette(Enum):
    """Available color palettes for sping UI."""

    SUNSET = "sunset"  # Default: dark greyish blue -> dusty purple -> dusty pink
    OCEAN = "ocean"  # Deep blue -> cyan -> seafoam green
    FOREST = "forest"  # Dark green -> lime -> bright yellow
    VOLCANO = "volcano"  # Dark red -> orange -> bright yellow
    GALAXY = "galaxy"  # Deep purple -> magenta -> bright pink
    ARCTIC = "arctic"  # Ice blue -> white -> pale blue
    NEON = "neon"  # Dark -> electric blue -> hot pink -> yellow
    MONOCHROME = "monochrome"  # Grayscale palette


# Color palette definitions - each palette has 10 gradient stops
PALETTE_COLORS: Dict[ColorPalette, List[str]] = {
    ColorPalette.SUNSET: [
        "grey39",  # Very low - dark greyish blue
        "grey50",
        "slate_blue3",  # Low - moving toward purple
        "slate_blue1",
        "medium_purple3",  # Medium-low - dusty purple range
        "medium_purple1",
        "plum3",  # Medium-high - toward pink
        "plum1",
        "light_pink3",  # High - dusty pink range
        "light_pink1",  # Very high - bright dusty pink
    ],
    ColorPalette.OCEAN: [
        "navy_blue",  # Deep ocean
        "blue",
        "dodger_blue3",
        "dodger_blue1",
        "deep_sky_blue3",
        "deep_sky_blue1",
        "cyan3",
        "cyan1",
        "aquamarine3",
        "aquamarine1",  # Bright seafoam
    ],
    ColorPalette.FOREST: [
        "rosy_brown",  # Brown earth
        "tan",  # Light brown/earth
        "sandy_brown",  # Sandy brown earth
        "dark_olive_green3",  # Brownish olive
        "dark_olive_green2",  # Transitional olive
        "dark_green",  # Dark green
        "green4",  # Medium dark green
        "green3",  # Medium green
        "green1",  # Bright green
        "bright_green",  # Brightest green
    ],
    ColorPalette.VOLCANO: [
        "dark_red",  # Deep volcanic
        "red3",
        "red1",
        "orange_red1",
        "dark_orange3",
        "dark_orange",
        "orange1",
        "gold3",
        "gold1",
        "bright_yellow",  # Bright lava
    ],
    ColorPalette.GALAXY: [
        "purple4",  # Deep space
        "purple3",
        "medium_purple1",  # Instead of purple1
        "magenta3",
        "magenta2",
        "magenta1",
        "hot_pink3",
        "hot_pink",  # Instead of hot_pink1
        "pink3",
        "bright_magenta",  # Bright nebula
    ],
    ColorPalette.ARCTIC: [
        "steel_blue",  # Cold depths
        "light_steel_blue3",
        "light_steel_blue1",
        "light_cyan3",
        "light_cyan1",
        "white",
        "light_sky_blue3",  # Instead of light_blue3
        "light_sky_blue1",  # Instead of light_blue1
        "sky_blue1",  # Instead of powder_blue
        "white",  # Instead of alice_blue
    ],
    ColorPalette.NEON: [
        "grey11",  # Dark base
        "grey30",
        "blue1",
        "dodger_blue1",
        "cyan1",
        "spring_green1",
        "chartreuse1",
        "yellow1",
        "hot_pink",  # Instead of hot_pink1
        "magenta1",  # Electric bright
    ],
    ColorPalette.MONOCHROME: [
        "grey7",  # Almost black
        "grey15",
        "grey23",
        "grey30",
        "grey39",
        "grey50",
        "grey62",
        "grey70",
        "grey84",
        "grey93",  # Almost white
    ],
}


def get_latency_gradient_color(
    position: float, palette: ColorPalette = ColorPalette.SUNSET
) -> str:
    """Get color based on position in latency range.

    Args:
        position: Normalized position (0.0 = min latency, 1.0 = max latency)
        palette: Color palette to use

    Returns:
        Rich color name for the gradient position
    """
    colors = PALETTE_COLORS[palette]

    if position <= 0.1:
        return colors[0]
    elif position <= 0.2:
        return colors[1]
    elif position <= 0.3:
        return colors[2]
    elif position <= 0.4:
        return colors[3]
    elif position <= 0.5:
        return colors[4]
    elif position <= 0.6:
        return colors[5]
    elif position <= 0.7:
        return colors[6]
    elif position <= 0.8:
        return colors[7]
    elif position <= 0.9:
        return colors[8]
    else:
        return colors[9]


def calculate_position(value: float, min_val: float, max_val: float) -> float:
    """Calculate normalized position (0.0-1.0) for a value in range.

    Args:
        value: The value to normalize
        min_val: Minimum value in range
        max_val: Maximum value in range

    Returns:
        Normalized position between 0.0 and 1.0
    """
    if max_val <= min_val:
        return 0.0
    return (value - min_val) / (max_val - min_val)


def get_latency_color(
    value: float,
    min_val: float,
    max_val: float,
    palette: ColorPalette = ColorPalette.SUNSET,
) -> str:
    """Get color for a latency value based on its position in the range.

    Args:
        value: Latency value
        min_val: Minimum latency in current range
        max_val: Maximum latency in current range
        palette: Color palette to use

    Returns:
        Rich color name for the latency value
    """
    if max_val <= min_val:
        # Fallback for flat data - use middle color of palette
        colors = PALETTE_COLORS[palette]
        return colors[4]  # Middle color

    position = calculate_position(value, min_val, max_val)
    return get_latency_gradient_color(position, palette)


def get_height_based_gradient_color(y_position: int, total_height: int) -> str:
    """Get color based on absolute position in container (alternative gradient).

    Args:
        y_position: Position from bottom (0 = bottom, total_height-1 = top)
        total_height: Total height of container

    Returns:
        Rich color name for height-based gradient (blue to green)
    """
    height_ratio = y_position / (total_height - 1) if total_height > 1 else 0.0

    if height_ratio <= 0.15:
        return "slate_blue1"  # Very bottom - gray-blue
    elif height_ratio <= 0.30:
        return "blue"  # Low - standard blue
    elif height_ratio <= 0.45:
        return "dodger_blue1"  # Lower middle - brighter blue
    elif height_ratio <= 0.60:
        return "deep_sky_blue1"  # Middle - sky blue
    elif height_ratio <= 0.75:
        return "cyan"  # Upper middle - cyan
    elif height_ratio <= 0.90:
        return "spring_green1"  # High - spring green
    else:
        return "bright_green"  # Top - bright neon green


def get_palette_from_string(palette_name: str) -> ColorPalette:
    """Convert string palette name to ColorPalette enum.

    Args:
        palette_name: String name of the palette

    Returns:
        ColorPalette enum value

    Raises:
        ValueError: If palette name is not recognized
    """
    try:
        return ColorPalette(palette_name.lower())
    except ValueError:
        available = [p.value for p in ColorPalette]
        raise ValueError(
            f"Unknown palette '{palette_name}'. Available palettes: {', '.join(available)}"
        )


def get_available_palettes() -> List[str]:
    """Get list of available palette names.

    Returns:
        List of palette names as strings
    """
    return [palette.value for palette in ColorPalette]


def get_palette_description(palette: ColorPalette) -> str:
    """Get a description of the color palette.

    Args:
        palette: ColorPalette enum value

    Returns:
        Human-readable description of the palette
    """
    descriptions = {
        ColorPalette.SUNSET: "Dark greyish blue → dusty purple → dusty pink (default)",
        ColorPalette.OCEAN: "Deep blue → cyan → seafoam green",
        ColorPalette.FOREST: "Dark green → lime → bright yellow",
        ColorPalette.VOLCANO: "Dark red → orange → bright yellow",
        ColorPalette.GALAXY: "Deep purple → magenta → bright pink",
        ColorPalette.ARCTIC: "Ice blue → white → pale blue",
        ColorPalette.NEON: "Dark → electric blue → hot pink → yellow",
        ColorPalette.MONOCHROME: "Grayscale from dark to light",
    }
    return descriptions.get(palette, "Unknown palette")
