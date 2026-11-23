# Capítulos extra para llegar a 8+ minutos. Se insertan antes de "## Cierre".
import re, sys
EXTRA = {
4: """## Preguntas que me hacen siempre
@bg sitcom
@cast moni,card
P: PREGUNTAS FRECUENTES |
MONI: Antes de cerrar, las preguntas que más me hacen sobre la tarjeta.
P: ¿PAGAR ANTES DEL CIERRE? |
MONI: ¿Conviene pagar antes del cierre? Si pagás el total antes del vencimiento, ya no pagás intereses. Pagar antes del cierre sirve para liberar límite o si te cuesta controlarte, pero no te ahorra intereses extra en la mayoría de las tarjetas.
P: ¿CANCELAR LA TARJETA? |
MONI: ¿Me conviene cancelar la tarjeta? Si no podés controlarla, puede ser lo mejor. Si la usás bien, tenerla con una historia de pagos puntuales puede ayudarte a conseguir créditos más baratos en el futuro.
TARJETÍN{sly}: ¿Viste? Me necesitás.
MONI: Te necesito bien educado, Tarjetín.
P: ¿EL MÍNIMO ME ARRUINA EL HISTORIAL? |
MONI: ¿Pagar el mínimo me arruina el historial? Pagar el mínimo a tiempo no suele contar como atraso. Lo que más perjudica es pagar tarde o no pagar. Pero el mínimo te arruina el bolsillo, que es casi peor.
P: ¿Y LOS PUNTOS? |
MONI{think}: ¿Y los puntos y millas? Son un buen beneficio solo si pagás el total. Si pagás intereses, ningún punto compensa lo que perdés. Nunca gastes para juntar puntos.
P: ¿DÉBITO O CRÉDITO? |
MONI: ¿Débito o crédito? Si te cuesta controlarte, débito: gastás solo lo que tenés. Si sos ordenado, crédito con pago total: tenés un mes de plazo, protección en compras y beneficios.
""",
5: """## La versión con $900
@bg simulador
@cast moni
P: ¿Y CON $900? |
MONI: Muchos me preguntaron: ¿y si en vez de seiscientos fueran novecientos? ¿Qué cambia? Hice la cuenta.
P: +$300 |
MONI: Con trescientos dólares más por mes, la tentación es subir todo un poco: más salidas, más delivery, ropa nueva. Y al final del mes, otra vez justa.
P: LA VERSIÓN INTELIGENTE |
MONI: La versión inteligente es otra. Primero, separar cien dólares para ahorro, automático, el día de cobro.
P: $100 · AHORRO |
MONI: En un año son mil doscientos dólares. Un fondo de emergencia completo para alguien que vive con seiscientos.
P: $100 · FONDO DE IMPREVISTOS |
MONI: Segundo, subir el sobre de imprevistos a cien. Con eso, una zapatilla rota o una consulta médica ya no te desarman el mes.
P: $100 · VIVIR MEJOR |
MONI: Y tercero, los cien restantes para vivir un poco mejor: más salidas, mejor comida, algún gusto.
MONI{think}: Fijate: con el mismo aumento podés seguir viviendo al día, o podés vivir mejor y además empezar a ahorrar. La diferencia no es la plata. Es el orden en que la repartís.
P: PRIMERO EL FUTURO |
MONI: Esa es la regla que más me cambió la vida: cuando entra plata nueva, primero el futuro y después el resto. Al revés, el futuro nunca llega.
""",
6: """## Errores con el interés compuesto
@bg sitcom
@cast moni,fomito
P: 4 ERRORES |
MONI: Antes de terminar, cuatro errores comunes que le quitan potencia al interés compuesto.
P: 1 · EMPEZAR TARDE |
MONI: Error uno: esperar a tener mucha plata para empezar. Ya viste la carrera: diez años de ventaja valen más que montos grandes después.
P: 2 · SACAR LA PLATA |
MONI: Error dos: sacar la plata cada vez que crece. Cada retiro corta la bola de nieve y la hace empezar de nuevo, más chica.
FOMITO: ¡Pero yo quiero ganar rápido! ¡Esta moneda sube veinte por ciento por semana!
P: 3 · PERSEGUIR RENDIMIENTOS |
MONI: Error tres: perseguir rendimientos enormes. El interés compuesto funciona con rendimientos razonables sostenidos en el tiempo, no con apuestas que pueden perderlo todo.
MONI{angry}: Fomito, una pérdida del cincuenta por ciento necesita una ganancia del cien por ciento para volver al punto de partida. Las pérdidas grandes son veneno para el interés compuesto.
FOMITO{worried}: Eso no me lo había dicho nadie.
P: 4 · IGNORAR LA INFLACIÓN |
MONI: Y error cuatro: mirar solo el número nominal. Si tu plata crece cinco por ciento pero la inflación es seis, en realidad perdiste poder de compra.
P: CONSTANCIA |
MONI: El secreto aburrido del interés compuesto es la constancia: aportar todos los meses, no tocarlo y dejar que el tiempo haga su trabajo.
""",
7: """## Las otras burbujas famosas
@bg novela
@cast moni
P: 1720 · MARES DEL SUR |
MONI: Los tulipanes son la burbuja más famosa, pero no la más grande. En 1720, en Inglaterra, la Compañía de los Mares del Sur prometía riquezas del comercio con América.
MONI: Sus acciones se multiplicaron varias veces en pocos meses. Y cayeron casi igual de rápido.
P: ISAAC NEWTON |
MONI{shock}: Entre los que perdieron plata estaba Isaac Newton, uno de los científicos más brillantes de la historia. Se le atribuye haber dicho que podía calcular el movimiento de los planetas, pero no la locura de la gente.
P: 2000 · PUNTO COM |
MONI: En el año 2000, cualquier empresa con punto com en el nombre subía en la bolsa, aunque no ganara plata. El índice Nasdaq cayó cerca de un ochenta por ciento entre 2000 y 2002.
P: 2008 · VIVIENDAS |
MONI: En 2008 explotó la burbuja de viviendas en Estados Unidos. Se daban créditos a gente que no podía pagarlos, porque se suponía que las casas nunca bajaban. Bajaron, y arrastraron al sistema financiero mundial.
MONI{think}: En todas aparece la misma idea: esta vez es diferente. Y en todas, el final se pareció bastante a febrero de 1637.
""",
8: """## Si ya te pasaste
@bg simulador
@cast moni,card
P: ¿YA TE PASASTE? |
MONI: ¿Y si este video te llega tarde y ya te pasaste? Tranquilo. Plan de rescate para enero.
P: 1 · LA FOTO |
MONI: Paso uno: sacá la foto completa. Cuánto quedó en la tarjeta, cuántas cuotas tomaste y cuándo vence cada cosa.
TARJETÍN{sly}: No mires, es más lindo no saber.
MONI: Es más lindo para vos, Tarjetín.
P: 2 · PAGAR EL TOTAL |
MONI: Paso dos: si podés, pagá el total del resumen aunque te duela, usando ahorros si los tenés. Los intereses de la tarjeta suelen ser mucho más altos que lo que rinde cualquier ahorro.
P: 3 · ENERO EN MODO AHORRO |
MONI: Paso tres: si no podés pagar el total, enero va en modo ahorro. Recortá salidas y compras durante un mes o dos, y todo lo que ahorres va a la tarjeta.
P: 4 · NO MÁS CUOTAS |
MONI: Paso cuatro: nada de cuotas nuevas hasta terminar de pagar las de diciembre.
MONI{think}: Y anotá cuánto gastaste en total en estas fiestas. Ese número es tu presupuesto realista para el año que viene. Empezá a apartar de a poco desde septiembre.
""",
9: """## Comprar online también tiene trucos
@bg marca
@cast moni,cart
P: ¿Y ONLINE? |
MONI: ¿Y si comprás por internet? Los trucos cambian de forma, pero son muy parecidos.
P: ENVÍO GRATIS DESDE $50 |
CARRITO: Te faltan solo cinco dólares para el envío gratis. ¿Agregás algo?
MONI: El envío gratis a partir de cierto monto es la versión online del carrito grande. Terminás agregando algo que no necesitabas para no pagar un envío que costaba menos.
P: LOS QUE COMPRARON ESTO… |
MONI: Las recomendaciones: los que compraron esto también compraron. Son el pasillo que te hace atravesar el local, pero hecho a tu medida.
P: QUEDAN 2 · 15 PERSONAS MIRANDO |
MONI{think}: Los avisos de urgencia: quedan dos unidades, quince personas están viendo este producto. Son la versión digital de la música lenta: te sacan de pensar con calma.
P: LA TARJETA GUARDADA |
MONI: Y la tarjeta guardada con compra en un clic. Cuanto menos te cuesta pagar, menos sentís que estás gastando.
P: DEFENSA ONLINE |
MONI: La defensa es la misma: lista, esperar veinticuatro horas antes de comprar lo que no planeabas, comparar precios y, si te cuesta, borrar la tarjeta guardada.
CARRITO{worried}: Me dejaste en el abandono otra vez.
""",
}
if __name__ == "__main__":
    for n, txt in EXTRA.items():
        p = f"guiones/{n:02d}.txt"; s = open(p, encoding="utf-8").read()
        if txt.splitlines()[0] in s:
            continue
        i = s.index("## Cierre")
        s = s[:i] + txt + s[i:]
        s = s.replace("## Cierre\n@bg marca\n", "## Cierre\n@bg marca\n@cast moni\n", 1) if "## Cierre\n@bg marca\n@cast" not in s else s
        open(p, "w", encoding="utf-8").write(s)
        print("ok", n)
