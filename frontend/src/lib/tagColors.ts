/**
 * Tag color utility for consistent tag badge colors across the application.
 *
 * Uses a deterministic hash function to map tag names to colors from a
 * curated HSL palette, ensuring the same tag always gets the same color.
 *
 * Feature: 007-intermediate-todo-features
 * [Task]: T006 [P]
 */

/**
 * Curated HSL color palette for tag badges.
 *
 * Colors are selected for readability and visual distinction:
 * - Lightness: 45-60% for good contrast on white backgrounds
 * - Saturation: 60-90% for vibrant but not overwhelming colors
 * - Hue: Distributed across the color spectrum for variety
 */
const COLOR_PALETTE = [
  { h: 0, s: 70, l: 60 },     // Red
  { h: 30, s: 80, l: 55 },   // Orange
  { h: 45, s: 90, l: 50 },   // Gold/Yellow
  { h: 60, s: 85, l: 45 },   // Yellow-Green
  { h: 120, s: 60, l: 50 },  // Green
  { h: 150, s: 70, l: 45 },  // Teal
  { h: 180, s: 70, l: 45 },  // Cyan
  { h: 210, s: 80, l: 55 },  // Blue
  { h: 240, s: 70, l: 55 },  // Indigo
  { h: 270, s: 70, l: 60 },  // Purple
  { h: 300, s: 75, l: 55 },  // Magenta
  { h: 340, s: 80, l: 60 },  // Pink/Rose
] as const;

/**
 * DJB2 string hash algorithm.
 *
 * A simple, fast hashing function that produces consistent hash values
 * for the same input string. Used to deterministically map tag names
 * to colors from the palette.
 *
 * @param str - The string to hash (tag name)
 * @returns A numeric hash value (always non-negative)
 */
function stringHash(str: string): number {
  let hash = 5381;
  for (let i = 0; i < str.length; i++) {
    // hash * 33 + char_code (bitwise shift for performance)
    hash = ((hash << 5) + hash) + str.charCodeAt(i);
  }
  return Math.abs(hash);
}

/**
 * Get the HSL color for a tag name.
 *
 * Uses a deterministic hash function to select a color from the palette,
 * ensuring the same tag name always gets the same color across renders
 * and sessions.
 *
 * @param tagName - The tag name to get a color for
 * @returns HSL color string (e.g., "hsl(210, 80%, 55%)")
 */
export function getTagColor(tagName: string): string {
  const hash = stringHash(tagName);
  const color = COLOR_PALETTE[hash % COLOR_PALETTE.length];
  return `hsl(${color.h}, ${color.s}%, ${color.l}%)`;
}

/**
 * Get Tailwind CSS-compatible classes for a tag badge.
 *
 * Returns both inline style (for dynamic background color) and static
 * classes for text color, padding, and rounded corners.
 *
 * @param tagName - The tag name to get styles for
 * @returns Object with className and style props for React components
 */
export function getTagBadgeStyles(tagName: string) {
  const color = getTagColor(tagName);

  return {
    // Inline style for the dynamic background color
    style: { backgroundColor: color } as React.CSSProperties,

    // Tailwind classes for text, padding, and border radius
    // White text works well with all our palette colors (lightness 45-60%)
    className: 'text-white font-medium px-2 py-1 rounded-md text-sm inline-block',
  };
}

/**
 * Get just the CSS class name portion for a tag badge.
 *
 * Utility function for cases where you only need the static classes
 * and will apply the color separately.
 *
 * @returns Tailwind CSS class string for tag badge styling
 */
export function getTagBadgeClassName(): string {
  return 'text-white font-medium px-2 py-1 rounded-md text-sm inline-block';
}

/**
 * Type definition for tag badge component props.
 */
export interface TagBadgeProps {
  name: string;
  onClick?: (name: string) => void;
}

/**
 * Default export for convenience.
 */
export default {
  getTagColor,
  getTagBadgeStyles,
  getTagBadgeClassName,
};
