# Marca, personajes y continuidad

## Canal
- Nombre: **Moni Finanzas** · usuario **@moni.finanzas** en YouTube, Instagram y TikTok. La marca de agua de los videos lo muestra.
- Tono: cercano, con humor y sin vueltas. Voseo rioplatense (“tenés”, “pagá”). Nada de “hola, bienvenidos”: se arranca siempre con el gancho.
- Público: jóvenes y adultos de Latinoamérica. Montos en **dólares** para que no envejezcan con la inflación local.
- Paleta: verde marca `#0E5A40`, dorado `#F7BC2B`, crema `#FFF4E2`. Tipografías: Bricolage Grotesque (títulos), Figtree (texto) y Patrick Hand (pizarra).
- Estilo visual de los personajes: **3D suave**, con gradientes y sombra (`data-look="soft"` en el renderizador).
- Kit de marca: logo, banner y portadas en `estudio-moni/marca/`.

## Personajes (tipo en el código → voz Kokoro, semitonos, velocidad)

| Personaje | Rol | Tipo | Voz |
|---|---|---|---|
| Moni | Protagonista, moneda dorada con brote | `moni` | ef_dora +2, 1.08 |
| Narrador | Voz en off, sin personaje en pantalla | — | em_alex 0, 1.05 |
| Tarjetín | Tarjeta de crédito, villano de la T1 | `card` | em_santa −1 |
| Infla | Fantasma verde de la inflación, villano de la T2 | `ghost` | ef_dora −3 + eco |
| Préstamín | Billete vendedor, préstamos fáciles (T3) | `bill` | em_alex +2 |
| Centavito | Moneda cobre, **primo** de Moni | `centavito` | ef_dora +7 |
| Peso | Moneda plateada, **pareja** de Moni | `peso` | em_alex +1 |
| Cafecito | Taza de café, gasto hormiga | `cup` | ef_dora +5 |
| Delivy | Bolsa de delivery | `bag` | em_santa +3 |
| Capricho | Moño de regalo con cuernitos, el “me lo merezco” | `bow` | ef_dora +6 |
| Ofertín | Etiqueta de precio con megáfono | `tag` | em_alex +4 |
| Fomito | Personaje violeta con ojos en espiral, FOMO y cripto | `fomito` | em_alex +6 |
| Zombis / Gym Zombi | Suscripciones que se cobran solas | `zombi` / `gymzombi` | em_santa −4 + eco |
| Carrito | Carrito de supermercado | `cart` | em_alex +5 |
| Cajero, Snacky, Botellín, Celulín, Autito, Cuotín, Remera, Campera, Resumen | Personajes de los Shorts | ver `video/build_audio.py` | ver `VOICES` |

Para agregar un personaje: `PAL` y `BODY` en `estudio-moni/video/renderer.html`, y una entrada en `VOICES` de `estudio-moni/video/build_audio.py`.

## Series y continuidad
- **Telenovela del dinero** (Shorts, 5 temporadas): T1 Moni contra Tarjetín · T2 La inflación invisible · T3 El préstamo fácil · T4 El fondo de emergencia · T5 Suscripciones zombie. Las “películas” largas cuentan una temporada completa, con escenas nuevas y explicación.
- Otros formatos de Shorts: Pizarra express, Sitcom de gastos hormiga, ¿Y si…? (simulador), Mito o verdad.
- Números ya usados (mantener coherencia): $1.000 al 24 % pagando el mínimo (3 % o $25) → 73 meses y $1.867. Pagando el doble del mínimo → 25 meses y $1.271. Cafecito: $3 × 22 × 12 = $792 al año. $5 por día = $150 por mes, 30 años al 7 % → ≈ $183.000.
