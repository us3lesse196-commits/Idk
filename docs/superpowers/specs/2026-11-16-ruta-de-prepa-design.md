# Ruta de Prepa: notas de diseño (borrador en discusión)

> Documento vivo. Se irá completando mientras discutimos gameplay, mapas, ambientación y visuales.
> Todavía no está aprobado para construir.

## Qué es
Juego 2D en pixel art, horizontal, de **exploración tranquila en mundo abierto**.
Eres un estudiante de prepa que recorre su colonia, la escuela, la ciudad, los campos y lugares
místicos. Todo debe sentirse relajado: la música, lo visual y el ritmo.

## Decidido
- **Plataforma:** web primero (se juega desde el navegador del celular, con controles táctiles).
  Se puede pasar a Godot más adelante.
- **Orientación:** solo horizontal.
- **Arte:** por ahora lo genera Claude con código; después se cambia por arte a mano o paquetes.
- **Sin castigo:** no hay muerte ni prisa.
- **Movimiento:** caminar, saltar, agacharse, deslizarse, rebotar en muros (parkour fluido).
- **Clima y hora cambian el mundo:** ciclo día/noche, lluvia que moja todo poco a poco
  (charcos, goteras, brillo mojado), tormenta, aurora.
- **Toques míticos o mágicos** dentro de lo cotidiano.

## Objetivo del juego: el cuaderno de momentos
- Último semestre de prepa. El estudiante encuentra un cuaderno viejo con páginas a medio dibujar
  y pistas cortas.
- **Momentos:** escenas mágicas que solo aparecen con cierta combinación de **hora + clima + lugar**
  (peces de luz en charcos de noche con lluvia, zorro espíritu en noches despejadas, puente de aurora
  entre azoteas, pétalos dorados de la jacaranda al amanecer...).
- Al encontrar uno, la página se completa con un dibujo.
- El parkour sirve para llegar a momentos en lugares altos o escondidos.
- Sin orden fijo ni presión. Cada mapa nuevo agrega páginas.
- Para después (opcional): compañeros y vecinos con diálogos cortos que dan pistas; misterio suave
  sobre quién dibujó el cuaderno antes; cámara de fotos para guardar paisajes.

## Alternativas descartadas para el objetivo
- Exploración libre sin metas: relajante pero aburre rápido.
- Historia lineal por capítulos: quita la libertad del mundo abierto.

## En discusión
- Entrar a casas, edificios, callejones y otros lugares.

## Prototipo
- `prueba/index.html`: prueba visual 0.1 (5 zonas, ciclo de día, lluvia/charcos/goteras, aurora,
  zorro espíritu, música generada).
