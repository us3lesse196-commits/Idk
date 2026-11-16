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

## Entrar a lugares (aprobado)
Tres formas, según el lugar:
1. **Corte de fachada** (casas, tienda, lugares chicos): al cruzar la puerta la fachada se desvanece y se
   ve el interior en el mismo sitio, sin carga. La lluvia se ve por las ventanas y se oye apagada.
2. **Escena aparte** (prepa, departamentos): fundido a negro y mapa interior propio
   (pasillos, escaleras, salones, azotea).
3. **Capas de profundidad** (callejones): en ciertos huecos entre edificios el personaje camina hacia el
   fondo, a una calle trasera.
- Solo algunos lugares se pueden visitar, y cada uno tiene algo especial (personaje, momento o vista).
- Algunos abren solo a ciertas horas (tienda de día, biblioteca por la tarde).
- Botón táctil extra de **entrar** que aparece solo junto a puertas o callejones.

## Sentarse y los audífonos (aprobado en idea)
- En bancas, azoteas, parada del bus, árbol grande, etc. el estudiante puede **sentarse**.
- Sentado, se pone **audífonos** y aparecen 2 menús:
  1. **Música:** eliges música y empieza un **timelapse medianamente rápido**; puedes solo escuchar
     y ver el mundo cambiar. (Qué más se puede hacer aquí: pendiente, ver abajo.)
  2. **Clima y hora:** eliges clima y hora, confirmas y empieza un **timelapse rápido** hasta llegar ahí.
- Propuesta de Claude: tocar la pantalla salta el timelapse; la música elegida se puede mantener al
  pedir clima y hora.
- Clima natural además cambia solo, con pronósticos dentro del mundo (tele, vecinos, cielo nublándose).
- Los botones de Hora/Clima de la prueba quedan solo para pruebas.
- Abierto: si todos los climas están disponibles desde el inicio o algunos se desbloquean al vivirlos.

## Pendientes para recordar
- [ ] **Recordarle al usuario:** qué más se puede hacer en el modo música/timelapse además de escuchar
      (lo pensará después de terminar lo más importante).

## En discusión
- Personajes y diálogos; el cuaderno en pantalla; progreso y guardado; tamaño de la primera versión.

## Prototipo
- `prueba/index.html`: prueba visual 0.1 (5 zonas, ciclo de día, lluvia/charcos/goteras, aurora,
  zorro espíritu, música generada).
