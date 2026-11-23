# Formato y escritura de guiones largos

Archivo: `estudio-moni/largos/guiones/NN.txt`, donde NN es el número del video en el plan, con dos dígitos.

```
@tipo historia|guia|simulacion|telenovela     (define música y etiqueta superior)
## Título del capítulo                          (placa de capítulo de 2,6 s y capítulo de YouTube)
@bg novela|pizarra|sitcom|simulador|mito|marca  (fondo de las escenas siguientes)
@cast moni,card                                 (personajes en escena, de izquierda a derecha; hasta 3)
P: TEXTO GRANDE | texto chico                   (panel; se mantiene hasta otro P:  ·  "P: -" lo borra)
MONI: Texto que se dice.                        (una línea = una escena con voz y subtítulos)
TARJETÍN{sly}: Texto.                           (expresión forzada: shock happy sly angry worried think wave)
```

- Los hablantes van en mayúsculas, con tildes: MONI, NARRADOR, TARJETÍN, INFLA, PRÉSTAMÍN, CENTAVITO, PESO, CAFECITO, DELIVY, CAPRICHO, OFERTÍN, FOMITO, ZOMBI, GYM ZOMBI, CARRITO, AUTITO y el resto de `VOICES`.
- El hablante tiene que estar en el `@cast` para aparecer y mover la boca. El NARRADOR no tiene personaje.
- Si el panel trae un número (“$1.867”), se anima contando hacia arriba y suena una campanita.
- En la voz, los números van **escritos en palabras** (“mil ochocientos sesenta y siete”). En el panel, en cifras.
- Cada línea hablada, idealmente de menos de 200 caracteres. Si es más larga, partila en dos líneas del mismo hablante.
- Los años pueden ir en cifras en la voz (“en 2008”).

## Estructura que funciona (de 8 a 11 capítulos)
1. **Gancho** en el primer capítulo, sin saludo: el momento más fuerte o el número sorprendente, la promesa y un motivo para quedarse hasta el final.
2. **Desarrollo** en capítulos de 60 a 120 segundos, cada uno con un cambio: fondo, personaje, número o pregunta.
3. En las historias: contexto, cómo funciona, el giro, el derrumbe y la lección para tu plata.
4. En las guías: pasos numerados, errores comunes y un capítulo de “cómo empezar esta semana”.
5. Si el video queda corto: “Preguntas frecuentes”, “Errores comunes” o “Resumen en 30 segundos”. Siempre con contenido real, nunca relleno.
6. **Cierre**: la lección en una frase y una pregunta concreta para comentar. El renderizador agrega después 20 segundos de pantalla final.

## Largo
- Unas 165 palabras habladas por minuto, más las placas y la pantalla final.
- **Mínimo 1.230 palabras habladas** para pasar los 8 minutos (anuncios a mitad del video). Ideal: 1.250 a 1.500.
- Ojo al contar: las líneas `P:` no son habladas. Usá el contador de `pipeline.md`, no un `wc`.

## Calidad
- Verificá cada cálculo con Python antes de escribirlo: interés compuesto, préstamos, deudas, inflación.
- Historias reales: solo hechos documentados, con fechas, y su fuente en `largos_data.py`. Si algo es leyenda (por ejemplo “70 % de los ganadores de la lotería quiebran” o “los holandeses se tiraban a los canales”), se aclara.
- Nada de recomendar productos o instrumentos puntuales. Siempre “depende de tu país y tu perfil”.
