# Preferencias del usuario

- Antes de empezar cualquier tarea o implementación, dime si me equivoco en algo o si tienes una mejor idea.
- El usuario trabaja desde el celular: tenlo en cuenta al proponer herramientas, flujos de trabajo y controles.
- Responder en español.
- Entregar el juego siempre como un archivo HTML independiente (un solo archivo, con `<!doctype html>`, que se abre directo en el navegador del celular) y enviarlo como archivo. No publicar como artifact/link salvo que el usuario lo pida.
- Sprites y fachadas: se harán con SpriteCook cuando el usuario pague la suscripción (assets en `warm-dreams/assets.local/`, no se suben; IDs en `assets.manifest.json`). Mientras tanto, por código solo sistemas y efectos (cielo, luz, clima, partículas, física, animaciones); no invertir mucho esfuerzo en sprites por código. No usar packs de terceros. La música del juego no se cambia salvo que el usuario lo pida.
- Armar el HTML final con `python3 -I warm-dreams/tools/build.py <versión>` → `warm-dreams/dist/` (carpeta ignorada por git) y enviarlo como archivo.
- Ahorrar uso: máximo 1-2 capturas de pantalla por tarea y solo de lo que cambió; no repetir pruebas completas (prólogo/final) si el cambio no las toca; leer solo la parte del código que se va a editar; hacer cambios pequeños y concretos. El usuario prueba en su celular y reporta. Avisar antes de una tarea grande o costosa para que el usuario decida.
