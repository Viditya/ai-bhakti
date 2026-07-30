# Image generation notes

Mode: built-in OpenAI image generation.

## Shared style

Premium Indian devotional comic-book illustration, clean ink lines,
painterly cel shading, cinematic depth, respectful iconography, warm
gold/amber highlights balanced by luminous ocean blues. Portrait 2:3 panels.
No text, captions, logos, or watermarks inside generated art.

## Identity conditioning

Each panel prompt must include every visible recurring lock listed in
`content.json`. Exact identity invariants come from
`references/character_locks/manifest.json`.

## Environment constants

- Kshirasagara: luminous pearl-white and blue celestial ocean.
- Mandara: tall dark-gold mountain with a recognizable spiral ridge.
- Churning energy: white-gold spiral, never a modern mechanical effect.
- Devas: cream, saffron, teal and gold clothing.
- Asuras: maroon, charcoal, bronze and restrained gold clothing.
- Child-safe framing: no gore, body horror, or sexualized Mohini imagery.
