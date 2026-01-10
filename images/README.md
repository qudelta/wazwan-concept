# Image Assets Guide

## Folder Structure

This directory contains all images used in the Wazwan scrolljacking website.

### Directory Layout

```
images/
├── traem/          # Copper plate images
├── rice/           # Rice images
├── gravy/          # Methi maaz (gravy) images
├── kebabs/         # Seekh kebab images
└── chicken/        # Fried chicken images
```

## Image Requirements

### Traem (Copper Plate)
**Path**: `images/traem/plate.jpg`
- A round copper plate (traem) from top view
- High resolution (min 1000x1000px)
- Should show the metallic copper texture
- Will be displayed in a circular frame

### Rice
**Path**: `images/rice/rice.png`
- Cooked basmati rice
- Top-down view preferred
- High resolution (min 800x800px)
- Will be overlaid on the traem

### Gravy (Methi Maaz)
**Path**: `images/gravy/methi-maaz.jpg`
- Methi maaz or any Kashmiri gravy
- Top-down view
- High resolution (min 800x800px)
- Will be semi-transparent to show rice beneath

### Kebabs
**Paths**: 
- `images/kebabs/kebab.png`

- Seekh kebab or similar
- Side view or angled view
- Min 400x400px
- Same image will be used for both kebabs

### Chicken
**Paths**:
- `images/chicken/chicken.jpg`

- Fried chicken piece (quarter or similar)
- Angled view
- Min 400x400px
- **Note**: Reduced to 2 pieces (was 4)

### Shank (Dani Phol)
**Path**: `images/shank/shank.png`
- Lamb shank piece
- Side or angled view
- Min 600x600px
- Center placement

### Tabakh Maaz
**Path**: `images/tabakh-maaz/tabakh-maaz.png`
- Fried rib pieces (Kashmiri style)
- Angled view
- Min 400x400px
- Same image used for 2 pieces

### Covering Plate
**Path**: `images/covering-plate/plate.png`
- Round copper/metal plate (similar to traem)
- Top-down view
- Min 1000x1000px
- Should match traem style

### Rista
**Path**: `images/rista/rista.png`
- Meatball in red gravy
- Top or angled view
- Min 300x300px
- Same image used for 4 pieces


## Supported Formats

- **JPG/JPEG** (recommended for photos)
- **PNG** (if transparency needed)
- **WebP** (for optimized loading)

## Tips for Best Results

1. **High Resolution**: Use high-res images (they'll be scaled down)
2. **Good Lighting**: Well-lit food photography works best
3. **Clean Background**: Neutral backgrounds or transparent PNGs
4. **Consistent Style**: Try to maintain similar photography style across all images
5. **File Size**: Optimize images to under 500KB each for faster loading

## Quick Start

1. Place your images in the respective folders
2. Name them as specified above (or update paths in `index.html`)
3. Refresh the website to see your images

---

**Current Status**: Placeholder images needed - website will not display images until you add them to these folders.
