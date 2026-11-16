# Guía para integrar sprites de SpriteCook en Warm Dreams

Referencia para cuando se generen todos los sprites con SpriteCook. Resume cómo funciona el juego hoy y qué hay que cuidar para que todo combine.

## Escalas del juego
- El mundo se mide en **unidades**; en pantalla **1 unidad = 2 píxeles** (`Z=2`). La vista muestra 120 unidades de alto (240 px).
- **Haru mide 16 unidades (32 px)**. Los NPC miden igual.
- Suelo de la calle: `y = 150`. Meseta del santuario: `y = 126`.
- Puertas: unos **48 px** de alto (24 unidades). Máquina expendedora: unos 40 px.
- Edificios de un piso: unos 130–160 px de ancho. De dos pisos: unos 140–160 px de alto.

## Cómo se procesan las imágenes
1. Generar con `generate_game_art`, modelo `gpt-image-2.5-flare`, calidad `medium`, 1K cuadrado (8 créditos).
2. **No usar la versión "pixel" de SpriteCook**: su ajuste automático deforma los edificios (los deja angostos). Descargar el **raw** (`check_job_status` con `verbose:true` → `raw_url`).
3. Reducir el raw de 1024 px con filtro **BOX** a la escala del juego (edificios: 160–190 px; hoja de objetos: unos 102 px), endurecer el alfa (`>140`) y recortar al contenido.
4. Las hojas con varios objetos se separan por componentes conectados del alfa.
5. Todo se guarda en `warm-dreams/assets.local/assets.js` como `window.WD_ASSETS = {buildings:{...}, props:{...}}`. Esa carpeta **no se sube** (el repo es público). Los IDs quedan en `warm-dreams/assets.manifest.json`.
6. `tools/build.py <versión>` incrusta `assets.js` en el HTML final (`dist/`).

## Cómo se colocan en el juego
- En el constructor del mapa exterior (`OUT`), bloque `if(window.WD_ASSETS&&WD_ASSETS.buildings)`:
  - `place(src, x, w, h, escala, brillo, base)` dibuja la imagen sobre el nivel con la base en el suelo.
  - `bld(nombre, x)` además crea la **plataforma del techo** (oneway), las **luces** y las **goteras** de los aleros.
  - Antes de colocar, se borra el dibujo viejo de esa zona (`clearRect` en `L` y `E`) y se quitan sus luces, plataformas y goteras.
- **Brillo de noche:** los píxeles cálidos y brillantes (ventanas, farolillos) se copian a la capa emisiva `E`, que se enciende cuando oscurece.
- **Luces:** se buscan manchas de píxeles cálidos y se agregan como fuentes de luz (`lights`) que abren huecos en la oscuridad.

## Problema conocido: luz "pintada" en las imágenes
Las imágenes generadas traen **la iluminación del atardecer pintada** (cielo cálido reflejado en techos, ventanas encendidas, sombras fijas). Por eso de noche los techos siguen iluminados aunque no haya sol, y de día las ventanas se ven encendidas.

**Cómo resolverlo cuando se generen los sprites definitivos:**
1. **Pedir iluminación neutra** en el prompt: *"flat even neutral daylight lighting, no cast light, no glow, no sunset tint, windows dark/unlit, lanterns unlit"*. La hora y el clima los pone el juego.
2. **Generar una segunda imagen de "luces"** para cada edificio con `edit_asset_id`: *"same image, only the lit parts at night: glowing windows, lanterns and signs on black"*. El juego la usaría como capa emisiva exacta, en lugar de adivinarla por color.
3. Opcional, para luz inteligente: un **mapa de alturas o normales** por edificio ("grayscale height map of this facade"), para que las luces del juego iluminen y sombreen cada pared según su forma.
4. Mientras tanto, el juego puede **quitar el tinte cálido** de las imágenes ya generadas (desaturar los tonos naranja del techo) para que funcionen mejor de noche.

## Prompt base usado (mantener para que todo combine)
- Inicio: *"Front elevation (flat orthographic side-scroller view, no perspective) of …"*
- Final: *"Building only, standing on a flat baseline, no ground, no sky, no people."*
- Estilo: *"cozy lo-fi pixel art, … soft shading, 2D side-scroller game background asset"* (cambiar "warm lantern light" por la iluminación neutra del punto 1).
- Cada imagen de referencia cuesta 8 créditos extra; si hay presupuesto, usar `style_asset_ids` con 1 o 2 edificios aprobados para mantener el estilo.
