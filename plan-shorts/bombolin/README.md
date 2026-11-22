# Bombolín y sus amigos: plan de un mes (90 shorts, 3 por día)

Canal de animación con IA para YouTube Shorts, TikTok y Reels. **Contenido creado para niños** de 3 a 8 años, en español y en inglés.

| Archivo | Qué tiene |
|---|---|
| `README.md` (este) | Qué cambió, qué aprendimos investigando, personajes, reglas, horarios y producción |
| `voces.md` | La voz de cada personaje, con descripciones listas para generarlas con IA |
| `calendario.md` | Los 90 shorts en orden, con día, hora, formato y título |
| `calendario.csv` | Lo mismo, con descripciones ES/EN y playlist, para abrir en Excel o Google Sheets y programar las subidas |
| `semana-1.md` … `semana-5.md` | Cada short completo: título, descripción, gancho, guion por escenas, canción o rima, dato y fuente, voces y prompt visual |
| `src/` | Los datos de los guiones y el script que arma todo (`python3 src/build.py`) |

> El plan anterior (Moni y el ahorro) quedó guardado en `../moni-plan-12-shorts.md` por si lo quieres usar más adelante.

---

## 1. Qué cambié y por qué

| Antes (Moni) | Ahora (Bombolín) | Por qué |
|---|---|---|
| Una moneda que ahorra | **Bombolín, un dinosaurio bebé** | A los chicos de 3 a 8 años les encantan los dinosaurios y los bebés, y un protagonista que «recién nació» descubre el mundo al mismo tiempo que ellos. |
| Tema: dinero y ahorro | **Tema: descubrir el mundo**: animales, dinosaurios, hábitos (dientes, manos, sueño, comida) y emociones | Son temas que los chicos miran solos y que los padres quieren que miren. |
| 5 formatos | **6 formatos**: agregué **F. Canción corta** | La música y la repetición son la base de los canales infantiles más grandes. |
| 4 videos por semana | **3 por día, con franjas fijas** (mañana con energía, tarde con la serie, noche tranquila) | Los chicos y los padres aprenden «a qué hora sale Bombolín». La franja de la noche es más tranquila, para la hora de dormir. |
| Una voz de narrador | **5 voces de personaje + invitados** | Cada personaje se reconoce por la voz (ver `voces.md`). |
| Solo datos | **Un dato verificable con fuente en cada video**, y además humor físico (Toto) y emociones (Lula) | Los chicos se ríen, los padres confían y YouTube Kids premia el contenido de calidad. |

---

## 2. Lo que aprendí investigando videos infantiles

1. **Que los vean hasta el final es lo más importante.** En canales infantiles, cuando los chicos ven el video completo, el algoritmo se lo muestra a más gente. Por eso cada short dura 25 a 33 s, tiene un gancho en el segundo 0 y termina en la misma imagen con la que empieza, para que vuelva a arrancar solo ([caso WOA Song Spanish, AIR Media-Tech](https://air.io/en/creators-spotlight/5324-views-and-3453-revenue-woa-song-spanish-case)).
2. **La claridad visual y el ritmo sostienen la atención:** un solo personaje en foco, colores brillantes y cambios de plano cada 3 o 4 s ([AIR, caso de canal infantil](https://air.io/en/creators-spotlight/road-to-a-million-kids-channel-case-study-63-revenue-31-watch-time)).
3. **Publicar varios Shorts por día funciona en infantiles:** algunas agencias ven buen alcance en canales que suben de 2 a 10 Shorts diarios. 3 por día es un ritmo que se puede sostener ([AIR](https://air.io/en/creators-spotlight/1m-views-with-shorts-getting-on-youtube-kids)).
4. **Entrar en YouTube Kids es clave.** Si el canal no cumple las reglas de calidad y seguridad infantil, los Shorts pueden no llegar al público de YouTube Kids. Por eso no hay nada de miedo, burlas, «unboxing» ni consumismo.
5. **Canciones, repetición y colores brillantes** son lo que más atrapa a los más chiquitos (investigadores citados sobre CoComelon: [Parrot Analytics](https://www.parrotanalytics.com/insights/how-cocomelon-became-a-mass-media-juggernaut-for-preschoolers/)). Por eso hay una rima fija del canal, un estribillo en cada canción y muletillas por personaje.
6. **Lo que también disfrutan los padres hace que lo vean en familia** (es lo que pasa con Bluey: [MediaCat](https://mediacat.uk/streamings-most-reliable-audience-cant-read-yet/)). Por eso hay datos curiosos reales que sorprenden también a los adultos.
7. **Canales separados por idioma.** En un caso documentado, dividir el contenido en canales localizados multiplicó las vistas ([AIR](https://air.io/en/creators-spotlight/1140-views-and-386-revenue-kids-channel-case)). **Recomiendo un canal en español y otro en inglés**, con los mismos videos doblados.
8. **No encontré datos confiables sobre el mejor horario para contenido infantil.** Los horarios de abajo son una **hipótesis razonable** para probar: revisa YouTube Studio desde la segunda semana y ajustalos.

---

## 3. Personajes (no cambian nunca)

### Protagonista: **Bombolín**
- **Qué es:** un dinosaurio bebé verde menta que acaba de salir del huevo y **usa la mitad de su cascarón como gorrito**. El gorrito es su marca: si se le cae, siempre lo recupera.
- **Personalidad:** curioso, risueño y valiente, aunque a veces duda un poquito.
- **Frase de cabecera:** **«¡Un, dos, tres, a descubrir otra vez!»** / **"One, two, three, come discover with me!"**
- **Muletilla:** «¡Wiii!»

### Amigos (cada uno representa un problema o una emoción de los chicos)
| Personaje | Qué es | Representa | Muletilla |
|---|---|---|---|
| **Toto** | Monstruito peludo naranja, con una media pegada en el pelo | El **desorden** y la torpeza: pierde cosas, se tropieza, no quiere bañarse ni probar el brócoli | «¡Uy, uy, uy!» |
| **Lula** | Nubecita que **cambia de color según lo que siente** | Las **emociones**: miedo, tristeza, enojo y vergüenza, que se resuelven con ayuda | «¡Ay, qué lindo!» |
| **Zumbi** | Abejita con 6 zapatillas rojas | La **impaciencia**: quiere todo primero y no espera el turno | «¡Zzzí!» |
| **Abu Tortu** | Abuela tortuga con lentes y bufanda | **La calma y el saber**: es la narradora, dice los datos y cierra cada video | «Mis amores…» |

Nadie es malo. Toto, Lula y Zumbi se equivocan, y entre todos lo arreglan.

**Proporciones fijas:** Bombolín y Toto miden lo mismo, Abu Tortu mide el doble, Zumbi cabe en la mano de Bombolín y Lula es del tamaño de la cabeza de Abu.
**Paleta:** verde Bombolín `#7ED9A6`, naranja Toto `#FF9A3C`, celeste Lula `#8FD3F4`, amarillo Zumbi `#FFD23F`, verde y lavanda Abu, y fondos crema y pastel.
**Estilo:** 3D suave tipo película animada, con formas redondeadas de peluche. Las descripciones exactas para la IA están dentro de cada prompt (son siempre iguales).

---

## 4. Formatos y franjas

| Formato | Cantidad | Cuándo sale |
|---|---|---|
| A. Serie con capítulos (5 series) | 22 | Lunes a viernes, 17:00 (un capítulo por día) |
| B. Explicador en pizarra con Abu Tortu | 11 | Noches de semana (tranquilo) |
| C. Comedia de diálogo | 18 | Noches de semana y tardes de fin de semana |
| D. «¿Y si…?» (empieza por el final y rebobina) | 10 | Fines de semana (son los mejores ganchos) |
| E. Juego «¿Mito o verdad?» / «¿Cuál eliges?» con cuenta regresiva | 14 | Mañanas de semana y mediodías de fin de semana |
| F. Canción corta | 15 | Mañanas (con energía) |

**Las series del mes**
1. Semana 1: **El huevo misterioso**. Bombolín encuentra un huevo gigante… ¡y nace un avestruz!
2. Semana 2: **Lula perdió su arcoíris**. Buscan sus colores uno por uno.
3. Semana 3: **La gran carrera de Zumbi**. Aprende que llegar juntos vale más que ganar.
4. Semana 4: **El cumpleaños de Abu Tortu**. La fiesta sorpresa.
5. Días 29 y 30: **La cueva de los ecos**. Termina con final abierto para que vuelvan el mes siguiente.

### Horarios (hora local del público de cada canal)
| Día | Mañana | Mediodía/Tarde | Noche |
|---|---|---|---|
| Lunes a viernes | **07:30**: canción o juego | **17:00**: capítulo de la serie (cuando salen del colegio) | **19:30**: pizarra o comedia tranquila (antes de dormir) |
| Sábado | **09:00**: canción o baile | **12:30**: «¿Y si…?» | **18:00**: comedia |
| Domingo | **09:00**: «¿Y si…?» | **12:30**: juego | **18:00**: comedia |

- **Canal en español:** prográmalo en la hora del país con más público (por ejemplo, México o Argentina). Si después ves que viene mucho público de otro país, mueve los horarios.
- **Canal en inglés:** prográmalo en hora del este de EE. UU. (ET).
- **Empieza un lunes:** el día 1 del calendario es lunes.
- En TikTok y Reels, publica los mismos videos 1 o 2 horas después que en YouTube.

### Playlists (en contenido infantil, de acá sale el crecimiento)
1. Series de Bombolín (una playlist por serie, con los capítulos en orden)
2. Canciones de Bombolín
3. Juega con Bombolín
4. ¿Y si…? con Bombolín
5. Bombolín explica
6. Bombolín y sus amigos

Al terminar cada semana, une los 5 capítulos de la serie en **un video largo de unos 3 minutos** y súbelo los domingos a la noche. Los videos largos ayudan a que el canal crezca más allá de los Shorts.

---

## 5. Reglas de cada short (las 90 las cumplen)

1. **Segundo 0:** voz, texto grande e imagen fuerte a la vez. Nunca un saludo.
2. **Una sola idea**, de 25 a 33 s, en 5 escenas: 4 de historia y 1 de cierre.
3. **Historia:** problema, giro y solución. El «problema» es un amigo que se equivoca, nunca un villano.
4. **Cambio visual cada 3 o 4 s:** corte, zoom suave, objeto que aparece o pizarra.
5. **Subtítulos grandes palabra por palabra**, con la palabra que se dice resaltada en el color del personaje que habla.
6. **Un dato real con su fuente**, que se dice en pantalla. Cuando hay un número, el supuesto se aclara.
7. **Cierre:** «¡Hoy aprendimos que…!» + la rima del canal + una invitación a cantar o jugar otra vez. **Nunca** se piden comentarios, likes ni compras. La última imagen es igual a la primera, para que el video vuelva a empezar solo.
8. **El título cumple lo que muestra el video** y tiene menos de 60 caracteres (el script lo comprueba).
9. **Nada de miedo, violencia ni burlas.** Las tormentas, cuevas o animales grandes siempre aparecen de forma amable.

---

## 6. Cómo producir cada short (paso a paso)

1. **Imagen:** copia el «Prompt visual» del short en un generador de imágenes (Midjourney, Ideogram, Leonardo…). La primera vez, genera una **hoja de personaje** para cada uno y úsala como referencia en todos los demás. Así no cambia.
2. **Animación:** anima cada escena con un generador de video a partir de imagen (Runway, Kling, Pika, Luma…), con clips de 3 o 4 s.
3. **Voces:** genera los diálogos con las voces guardadas de `voces.md`.
4. **Edición:** en CapCut o similar, en formato vertical 9:16, con los subtítulos palabra por palabra, la canción o la rima, los efectos de sonido y el texto del gancho en el fotograma 0.
5. **Subida:** usa el título y la descripción del calendario, marca **«Sí, es contenido creado para niños»**, agrega el video a su playlist y programa la fecha y la hora.
6. **Inglés:** usa el mismo video, con voces y subtítulos en inglés. Los títulos y descripciones en inglés ya están listos. Los diálogos en inglés se traducen de los guiones en español; puedo hacerlo yo si me lo pides.

**Consejo de ritmo:** 90 videos en un mes es mucho. Produce **por lotes**: un día todas las imágenes de la semana, otro día todas las voces y otro la edición. Ten siempre **una semana de videos lista antes** de empezar a publicar.

---

## 7. Antes de publicar (checklist)

- [ ] Está marcado como «Contenido creado para niños» en YouTube, y con la configuración equivalente para menores en TikTok y Reels.
- [ ] El gancho aparece en el fotograma 0 y la voz arranca de inmediato.
- [ ] Los subtítulos se entienden sin sonido.
- [ ] El dato se dice y se ve en pantalla, y la fuente está escrita (puedes agregarla en la descripción).
- [ ] Revisé el dato en la fuente antes de publicar. Los datos vienen de fuentes conocidas (museos, zoológicos, NOAA, NASA, CDC…), pero hay que confirmarlos, porque las páginas cambian.
- [ ] El final pide cantar o jugar otra vez, y no pide comentarios ni compras.
- [ ] El personaje se ve igual que en los otros videos (gorrito de cascarón, colores y proporciones).
- [ ] La música es de uso libre o tiene licencia que permita monetizar.
