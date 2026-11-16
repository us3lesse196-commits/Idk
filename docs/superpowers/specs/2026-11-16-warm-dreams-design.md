# Warm Dreams: notas de diseño (borrador en discusión)

> Documento vivo. Se irá completando mientras discutimos gameplay, mapas, ambientación y visuales.
> Todavía no está aprobado para construir.

## Qué es
Juego 2D en pixel art, horizontal, de **exploración tranquila en mundo abierto**.
Eres un estudiante de prepa que recorre su colonia, la escuela, la ciudad, los campos y lugares
místicos. Todo debe sentirse relajado: la música, lo visual y el ritmo.

## Decidido
- **Ambientación: inspirada en Japón** (no Latinoamérica). Barrios japoneses, preparatoria japonesa,
  konbini, santuarios, cerezos, trenes, etc. El zorro espíritu encaja como kitsune.
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
1. **Casas y edificios:** el personaje hace la animación de abrir la puerta y entrar, la pantalla se
   oscurece y vuelve a aparecer ya dentro (escena interior propia). La lluvia se ve por las ventanas
   y se oye apagada.
2. **Callejones:** el personaje hace la animación de entrar al callejón, la cámara hace zoom y se
   desvanece lo que tapa, mostrando el callejón (capa de fondo propia).
- Esto implica varias capas de fondos/escenas: exterior, callejones, interiores.
- Solo algunos lugares se pueden visitar, y cada uno tiene algo especial (personaje, momento o vista).
- Algunos abren solo a ciertas horas (tienda de día, biblioteca por la tarde).
- Botón táctil extra de **entrar** que aparece solo junto a puertas o callejones.

## Sentarse y los audífonos (aprobado en idea)
- En bancas, azoteas, parada del bus, árbol grande, etc. el estudiante puede **sentarse**.
- Sentado, se pone **audífonos** y aparecen 2 menús:
  1. **Música:** eliges música y empieza un **timelapse medianamente rápido**; puedes solo escuchar
     y ver el mundo cambiar. (Qué más se puede hacer aquí: pendiente, ver abajo.)
  2. **Clima y hora:** eliges clima y hora, confirmas y empieza un **timelapse rápido** hasta llegar ahí.
- Tocar la pantalla salta el timelapse (aprobado).
- Al pedir clima y hora, la canción actual se desvanece y entra otra acorde al nuevo ambiente (aprobado).
- Clima natural además cambia solo, con pronósticos dentro del mundo (tele, vecinos, cielo nublándose).
- Los botones de Hora/Clima de la prueba quedan solo para pruebas.
- Abierto: si todos los climas están disponibles desde el inicio o algunos se desbloquean al vivirlos.

## Personajes (aprobado)
- NPC repartidos por los mapas. La mayoría son de fondo, con poco detalle y sin interacción.
- Solo algunos se pueden hablar: son importantes para el cuaderno o para secretos, y tienen más detalle.
- Hay lugares solitarios y tranquilos a propósito.
- La cantidad de gente depende de la hora y el clima con lógica: de noche y con lluvia hay poca gente.
- Propuestas de Claude: los NPC de fondo reaccionan al clima (paraguas, se refugian en la parada del bus);
  tienen rutinas según la hora (estudiantes de día, vendedores en la mañana); los NPC importantes se
  distinguen con una señal sutil y tienen horarios donde encontrarlos.

## Cerrado en gameplay (aprobado)
- Cuaderno en pantalla: libro con páginas pintadas; las incompletas muestran pista y boceto a lápiz.
- Guardado automático en el dispositivo.
- NPC: reaccionan al clima, rutinas por hora, los importantes tienen horario y señal sutil.

## Siguiente paso: prototipo 0.2 (prueba de sistemas, desechable)
3 mapas + lo básico de timelapse, hora, clima, NPC, sentarse con audífonos, entrar a un lugar.

## Audífonos v2 (aprobado)
1. **Timelapse libre:** sin elegir clima; empieza desde la hora y el clima actuales y el mundo sigue su
   curso más rápido. Aparecen 2 botones:
   - **Música:** reproductor de Spotify incrustado (pegar link de playlist/canción). Sin Premium ni login
     dentro del juego; canciones completas si hay sesión de Spotify en ese navegador, si no fragmentos de
     30 s. Alternativa: música propia del juego. (El SDK oficial de Spotify no funciona en navegadores de
     celular ni desde un archivo local.)
   - **Libro de dibujo:** cuaderno para dibujar en pixel art (paleta del juego, borrador, relleno,
     deshacer, varias páginas guardadas en el dispositivo).
2. **Clima y hora:** igual que antes.

## Demo de historia (0.4, solo prueba)
- Prólogo con franjas de cine: paneo por el barrio al atardecer, título, Haru sale de la prepa, cae un
  cuaderno brillante del cerezo, diálogo con Aoi con retratos.
- Juego libre buscando los 3 momentos.
- Final: con los 3 momentos, de noche en el santuario, el kitsune guía a Haru al torii bajo la aurora,
  se revela una página nueva y aparece "Continuará...".
- Climas todos disponibles; guardado del cuaderno, historia y dibujos en el dispositivo.

## Pendientes para recordar
- [x] Qué hacer en el modo timelapse: música (Spotify) y libro de dibujo.

## En discusión
- El cuaderno en pantalla; progreso y guardado; tamaño de la primera versión.

## Prototipo
- `warm-dreams/index.html`: prueba de sistemas 0.2 (3 mapas japoneses, casa con interior, callejón,
  NPC con rutinas y paraguas, Aoi con diálogo, banca + audífonos con 2 menús y timelapse,
  3 momentos del cuaderno, tren y paso a nivel).
- `prueba/index.html`: prueba visual 0.1 (5 zonas, ciclo de día, lluvia/charcos/goteras, aurora,
  zorro espíritu, música generada).
