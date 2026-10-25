# Limitations and Precautions

## Centerlines Do Not Represent Stroke Order

The order of centerline paths extracted from ordinary fonts is determined by traversal of the skeleton graph. It does not guarantee conventional human stroke order or natural pen movement. Use the KanjiVG pipeline when stroke order matters for writing kanji.

## Limited Alphabet Implementation

The built-in single-line alphabet currently supports only `A B C I L O T X Y Z`. It is not a complete set of general-purpose alphanumeric glyphs.

## KanjiVG Data Is Required

Generating kanji strokes assumes that the corresponding SVG file exists in the specified directory. There is no feature that infers KanjiVG-equivalent stroke order from a font file.

## Curves Are Approximated by Polylines

Font outlines and SVG Bézier curves are converted into point sequences according to the specified subdivision count. Increasing this count improves the geometric approximation but also increases the number of points and robot commands.

## Checks Before Operating the Physical Robot

COBOTTA writing causes the physical robot to move. Verify the coordinate axes, axis swapping, signs, mirroring, writing-surface Z coordinate, pen-lift height, workspace, and speed for the actual installation. In particular, `robot_swap_xy`, `robot_x_sign`, and `robot_y_sign` directly affect the installation orientation.

## Scope of Documentation

This Pages documentation is based on the supplied implementations of font processing, KanjiVG, visualization, and the COBOTTA writer. Because the complete public APIs of `font_geometry` and `font_line_layout` were not included among the files supplied for this documentation, their full sets of internal fields are not covered in the API reference.
