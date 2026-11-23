# Capítulos extra para 22, 23 y 24.
EXTRA = {
22: """## Cómo empezar en la bolsa
@bg marca
@cast moni
P: 3 PASOS |
MONI: Si querés dar el primer paso, tres pasos simples.
P: 1 · BASE ARMADA |
MONI: Uno: asegurate de tener fondo de emergencia y no tener deudas caras.
P: 2 · BRÓKER REGULADO |
MONI: Dos: elegí un bróker o banco regulado en tu país, con comisiones claras.
P: 3 · ALGO DIVERSIFICADO |
MONI{wave}: Tres: empezá con algo diversificado, como un fondo indexado, y aportá todos los meses. Simple, aburrido y efectivo.
""",
23: """## Infla en tu país
@bg simulador
@cast moni,ghost
P: INFLA EN EL MUNDO |
INFLA: No soy igual en todos lados, eh. En algunos países soy chiquito y en otros, enorme.
MONI: Es verdad. En muchos países desarrollados, la inflación suele moverse cerca del dos o tres por ciento anual. En otros, puede ser de dos cifras, y en algunos casos extremos, mucho más.
P: LA MISMA LÓGICA |
MONI: Pero la lógica es la misma en todos lados: la plata quieta pierde, los sueldos que se ajustan tarde pierden, y conviene buscar formas de que tu plata crezca al menos al ritmo de los precios.
P: CON INFLACIÓN ALTA |
MONI{think}: Con inflación alta, todo se acelera: los ahorros pierden más rápido, los precios cambian seguido y planificar se vuelve más difícil. Por eso, en esos países, la educación financiera es todavía más importante.
INFLA{sly}: Y ahí es donde más me divierto.
MONI{angry}: Por eso estamos haciendo esta telenovela, Infla.
## Escena eliminada: Infla y Tarjetín
@bg novela
@cast card,ghost
P: ESCENA ELIMINADA |
TARJETÍN{sly}: Infla, ¿sabés que juntos somos imparables?
INFLA{sly}: Contame.
TARJETÍN: Yo le presto plata a Moni para que compre ahora, porque vos le decís que mañana va a estar más caro.
INFLA: Y yo hago que su sueldo valga menos, así le cuesta más pagarte.
@cast moni,card,ghost
MONI{angry}: ¡Los escuché!
P: LA ALIANZA |
MONI: Esta escena la sacamos de los shorts, pero explica algo real: con inflación, comprar en cuotas puede tener sentido si las cuotas son fijas y sin interés. Pero si la tasa de la tarjeta es más alta que la inflación, la deuda crece más rápido que los precios.
MONI{think}: La regla: compará siempre la tasa de la deuda con la inflación esperada. Si la tasa es mayor, Tarjetín gana. Si es menor y fija, la ventaja puede ser tuya.
TARJETÍN{worried}: Nos descubrió.
INFLA{worried}: Retirada.
""",
24: """## Mitos de la plata en pareja
@bg mito
@cast moni,peso
P: ¿MITO O VERDAD? |
MONI: Juguemos un rato a mito o verdad, versión pareja.
P: “EL QUE GANA MÁS DECIDE” |
PESO: El que gana más decide en qué se gasta.
MONI{angry}: Mito. En una pareja, las decisiones comunes se toman entre los dos, sin importar quién gane más. La plata no compra el voto.
P: “HABLAR DE PLATA ES POCO ROMÁNTICO” |
PESO: Hablar de plata es poco romántico.
MONI: Mito. No hablar de plata es lo que termina con el romance. Planificar un viaje juntos puede ser lo más romántico del mundo.
P: “CUENTA CONJUNTA = MÁS AMOR” |
PESO: Si tenemos cuenta conjunta, nos queremos más.
MONI{think}: Mito. El sistema no mide el amor. Hay parejas felicísimas con todo separado, y parejas que pelean con todo junto. Lo que importa es que el sistema sea claro y acordado.
P: “CON MÁS PLATA NO HAY PELEAS” |
PESO{worried}: Bueno, pero si ganáramos más, no pelearíamos.
MONI: Mito también. Las parejas con más ingresos también pelean por plata. Lo que reduce las peleas no es la cantidad, es tener acuerdos.
## Cuando hay hijos
@bg marca
@cast moni,peso
P: CON HIJOS |
PESO: ¿Y cuando hay hijos, cambia algo?
MONI: Cambia bastante. Los gastos suben, a veces uno de los dos trabaja menos para cuidar, y los planes de largo plazo se vuelven más importantes.
P: EL QUE CUIDA |
MONI: Si uno de los dos deja de trabajar o trabaja menos para cuidar a los chicos, conviene que el sistema lo tenga en cuenta: que esa persona siga teniendo plata propia y que su futuro, como la jubilación, también esté protegido.
P: EL FONDO CRECE |
MONI{think}: Y el fondo de emergencia tiene que ser más grande, porque hay más personas que dependen de los mismos ingresos.
PESO: Mucho para pensar.
MONI{wave}: Por eso conviene empezar a hablarlo antes, no cuando ya llegó el primer pañal.
""",
}
if __name__ == "__main__":
    for n, txt in EXTRA.items():
        p = f"guiones/{n:02d}.txt"; s = open(p, encoding="utf-8").read()
        if txt.splitlines()[0] in s:
            continue
        i = s.index("## Cierre")
        s = s[:i] + txt + s[i:]
        open(p, "w", encoding="utf-8").write(s)
        print("ok", n)
