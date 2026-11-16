# Preferencias del usuario

- Antes de empezar cualquier tarea o implementación, dime si me equivoco en algo o si tienes una mejor idea.
- El usuario trabaja desde el celular: tenlo en cuenta al proponer herramientas, flujos de trabajo y controles.
- Responder en español.
- Entregar el juego siempre como un archivo HTML independiente (un solo archivo, con `<!doctype html>`, que se abre directo en el navegador del celular) y enviarlo como archivo. No publicar como artifact/link salvo que el usuario lo pida.
- Assets de terceros (sprites, fondos): van en `warm-dreams/assets.local/` (no se suben; el repo es público y sus licencias prohíben redistribuir). Generarlos con `python3 -I warm-dreams/tools/make_assets.py <carpeta_packs>` y armar el HTML final con `python3 -I warm-dreams/tools/build.py <versión>` → `warm-dreams/dist/`. Mantener créditos en Ajustes.
