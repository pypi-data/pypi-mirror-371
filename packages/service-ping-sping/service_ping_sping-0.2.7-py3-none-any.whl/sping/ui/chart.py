"""Chart components for sping UI."""

from rich.measure import Measurement
from rich.segment import Segment
from rich.style import Style

from .colors import ColorPalette, get_latency_color, get_latency_gradient_color


class BarChart:
    """Custom Rich renderable for displaying latency data as a bar chart.

    Renders a bar chart with Y-axis labels and gradient coloring based on latency values.
    The chart automatically scales to fit the provided data range and supports multiple
    color palettes for visual customization.
    """

    def __init__(
        self,
        values,
        width: int,
        height: int,
        palette: ColorPalette = ColorPalette.SUNSET,
    ):
        """Initialize the BarChart with data and display parameters.

        Args:
            values: List of numeric values to display as bars (typically latency in ms)
            width: Total width of the chart in characters (including Y-axis labels)
            height: Height of the chart in rows
            palette: Color palette to use for gradient coloring (default: SUNSET)
        """
        self.values = values  # Raw data values to be plotted
        self.width = width  # Total chart width including labels and separators
        self.height = height  # Chart height in terminal rows
        self.palette = palette  # Color scheme for gradient visualization

    def __rich_console__(self, console, options):
        """Rich protocol method to render the chart as terminal segments.

        This is the main rendering logic that converts the chart data into
        Rich Segment objects for terminal display. Handles scaling, positioning,
        and color application.

        Args:
            console: Rich console instance (unused but required by protocol)
            options: Rich console options containing max_width constraints

        Yields:
            Rich Segment objects representing chart rows with colors and text
        """
        # Calculate available chart width respecting terminal constraints
        max_width = min(self.width, options.max_width or self.width)

        # Handle extremely narrow displays with fallback
        if max_width < 12:
            # Insufficient space for meaningful chart, render empty rows
            for _ in range(self.height):
                yield Segment(" " * max_width)
            return

        # Chart layout constants
        AXIS_W = 6  # Width reserved for Y-axis numeric labels (e.g., "123.4 ")
        SEP = " │"  # Separator between Y-axis and chart data (2 chars)
        plot_w = max(1, max_width - AXIS_W - len(SEP))  # Actual chart plotting width

        # Handle empty data case
        if not self.values:
            empty_bar = " " * plot_w  # Empty row for the chart area
            for _ in range(self.height):
                line = f"{'':>{AXIS_W}}{SEP}{empty_bar}"
                yield Segment(line[:max_width])
            return

        # Extract the most recent data that fits in the chart width
        # This implements the scrolling behavior for real-time data
        subset = self.values[-plot_w:] if len(self.values) > plot_w else self.values
        if not subset:
            empty_bar = " " * plot_w
            for _ in range(self.height):
                line = f"{'':>{AXIS_W}}{SEP}{empty_bar}"
                yield Segment(line[:max_width])
            return

        # Calculate data range for scaling (min/max values in the dataset)
        vmin, vmax = min(subset), max(subset)

        # Improve y-scale for startup: use 0 as minimum when we have limited data
        # This provides better range initialization and prevents scale compression issues
        # during the initial data collection phase
        if len(subset) <= 2:
            vmin = 0.0  # Use 0 as minimum for better initial scaling

        # Calculate the data span for normalization
        span = vmax - vmin

        # Handle flat/constant values (when all data points are identical)
        if span < 1e-9:  # Essentially zero span (flat values)
            bar_chars = "█" * len(subset)  # Solid bars for all values
            padded_bar = bar_chars.ljust(plot_w)  # Pad to full width
            label_text = f"{vmax:.1f}"[:AXIS_W].rjust(AXIS_W)  # Format Y-axis label

            # Render flat chart with consistent coloring
            for i in range(self.height):
                if i == self.height - 1:
                    # Bottom row with label and gradient bars
                    # For flat values, use consistent color since they're all identical
                    label_color = self._color_for_latency_value(vmax, vmax, vmax)
                    segments = [Segment(f"{label_text}{SEP}", Style(color=label_color))]

                    # Use value-based color for flat values (consistent across all bars)
                    bar_color = self._color_for_latency_value(vmax, vmax, vmax)
                    segments.append(Segment(bar_chars, Style(color=bar_color)))
                    segments.append(Segment(" " * (plot_w - len(bar_chars)), Style()))

                    for seg in segments:
                        yield seg
                    yield Segment.line()
                else:
                    line = f"{'':>{AXIS_W}}{SEP}{padded_bar}"
                    yield Segment(line[:max_width])
                    yield Segment.line()
            return

        # Scale values to bar heights based on chart dimensions
        # Maps data values to pixel heights within the available chart area
        scaled = []
        for v in subset:
            # Normalize value to [0,1] range, then scale to chart height
            normalized = (v - vmin) / span
            h = max(1, int(normalized * (self.height - 1)) + 1)
            scaled.append(h)

        # Initialize 2D grid to represent the chart canvas
        # Each cell will contain either a space or a colored bar character
        grid = [[" "] * plot_w for _ in range(self.height)]

        # Improved positioning logic: fill left-to-right until full, then scroll right
        # This provides intuitive startup behavior and smooth transition to scrolling mode
        if len(subset) < plot_w:
            # Filling phase: chart is not yet full, align data to left side
            start_x = 0  # Left-align when chart is not full (filling phase)
        else:
            # Scrolling phase: chart is full, subset already contains rightmost data
            start_x = (
                0  # When full, subset is already the rightmost data (scrolling phase)
            )

        # Plot each bar with height-based gradient coloring
        for idx, (val, h) in enumerate(zip(subset, scaled)):
            x = start_x + idx  # Calculate x position for this bar
            if 0 <= x < plot_w:  # Ensure bar is within plot boundaries
                # Fill bar from bottom to top with gradient colors
                for y in range(self.height - h, self.height):
                    if 0 <= y < self.height:  # Ensure y position is valid
                        # Height-based gradient calculation:
                        # y represents the row (0 = top of chart, height-1 = bottom of chart)
                        # For each bar, bottom is at (height - 1), top is at (height - h)

                        bar_bottom = self.height - 1  # Bottom row of chart
                        bar_height = h  # Height of this specific bar

                        # Calculate position within this specific bar
                        # (0.0 = bottom of bar, 1.0 = top of bar)
                        bar_position = (
                            (bar_bottom - y) / (bar_height - 1)
                            if bar_height > 1
                            else 0.0  # Single-height bars get bottom color
                        )

                        # Map bar position to gradient based on the bar's proportional height
                        # Short bars only use lower gradient colors, tall bars use full range
                        max_gradient_position = (
                            h / self.height
                        )  # How much of full gradient this bar uses (0.0 to 1.0)
                        gradient_position = bar_position * max_gradient_position

                        # Apply the gradient position to our color scheme using centralized utility
                        color = get_latency_gradient_color(
                            gradient_position, self.palette
                        )

                        # Store colored character in grid for this position
                        grid[y][x] = (color, "█")

        # Generate final output with colored Y-axis labels and chart data
        mid_val = (vmin + vmax) / 2.0  # Calculate midpoint value for middle label
        for i in range(self.height):
            # Determine Y-axis label text and value for this row
            if i == 0:
                # Top row: show maximum value
                label_val = vmax
                label_text = f"{vmax:.1f}"[:AXIS_W].rjust(AXIS_W)
            elif i == self.height - 1:
                # Bottom row: show minimum value
                label_val = vmin
                label_text = f"{vmin:.1f}"[:AXIS_W].rjust(AXIS_W)
            elif i == self.height // 2:
                # Middle row: show midpoint value
                label_val = mid_val
                label_text = f"{mid_val:.1f}"[:AXIS_W].rjust(AXIS_W)
            else:
                # Other rows: no label
                label_val = None
                label_text = "".rjust(AXIS_W)

            # Output colored Y-axis label
            if label_val is not None:
                # Color the label based on its corresponding value in the data range
                label_color = self._color_for_latency_value(label_val, vmin, vmax)
                yield Segment(f"{label_text}{SEP}", Style(color=label_color))
            else:
                # Empty label rows use default styling
                yield Segment(f"{label_text}{SEP}", Style())

            # Output bar segments with gradient colors for this row
            for x in range(plot_w):
                if x < len(grid[i]) and isinstance(grid[i][x], tuple):
                    # Cell contains colored bar character
                    color, char = grid[i][x]
                    yield Segment(char, Style(color=color))
                else:
                    # Empty cell - output space
                    yield Segment(" ", Style())

            # End the row
            yield Segment.line()

    def __rich_measure__(self, console, options):
        """Rich protocol method to specify the chart's measurement requirements.

        Returns fixed width measurement to ensure consistent chart sizing
        regardless of content. This prevents the chart from resizing as data changes.

        Args:
            console: Rich console instance (unused but required by protocol)
            options: Rich console options (unused but required by protocol)

        Returns:
            Measurement object with fixed min and max width equal to self.width
        """
        return Measurement(self.width, self.width)

    def _color_for_latency_value(self, value, min_val, max_val):
        """Get appropriate color for a latency value using the chart's palette.

        This is a convenience wrapper around the centralized color utility function.
        Maps a latency value to a color based on its position within the data range.

        Args:
            value: The latency value to get color for (in ms)
            min_val: Minimum value in the current data range
            max_val: Maximum value in the current data range

        Returns:
            Rich color string appropriate for the value and current palette
        """
        return get_latency_color(value, min_val, max_val, self.palette)
