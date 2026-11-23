# Quinta tanda: resumen en 30 segundos para los videos que todavía quedan justos.
EXTRA = {
14: "Fondo de emergencia: de tres a seis meses de gastos esenciales. Disponible en días, seguro y separado de la cuenta diaria. Primera meta, quinientos dólares o un mes de gastos, en automático. Primero un mini fondo, después las deudas caras y después el fondo completo. Y cuando llega una emergencia de verdad, se usa sin culpa y se repone.",
15: "Blockbuster rechazó comprar Netflix por cincuenta millones en el año 2000 porque su negocio funcionaba, internet era lento y cambiar dolía. Reaccionó tarde y quebró en 2010. La lección para tu plata: revisá lo que hacés por costumbre, diversificá y aprendé cosas nuevas antes de que sea urgente.",
16: "Para salir de deudas: hacé la foto completa, pagá el mínimo de todas y poné todo el extra en una sola. Avalancha, la tasa más alta primero, para pagar menos intereses. Bola de nieve, la más chica primero, para ganar motivación. Cuando cancelás una, su pago pasa a la siguiente. Y para no volver: fondo de emergencia y tarjeta solo con pago total.",
17: "Las siete trampas: el ancla del precio tachado, el miedo a perder la oferta, la plata extra que se siente de juguete, el me lo merezco, el efecto manada, el costo hundido y el sesgo del presente. La defensa general: reglas decididas de antemano, esperar antes de comprar y automatizar el ahorro.",
18: "La inflación es la suba generalizada de precios. Se mide con una canasta de productos, la causan la demanda, los costos, la emisión y las expectativas, y le pega más a los ahorros quietos y a los sueldos que se ajustan tarde. Para protegerte: no dejes la plata quieta, buscá instrumentos que ajusten, invertí a largo plazo, negociá tu sueldo y comprá mejor.",
19: "FTX era una plataforma de cripto valuada en treinta y dos mil millones. Usó plata de sus clientes en otra empresa del mismo dueño, y cuando todos quisieron retirar, no estaba. Se declaró en quiebra en noviembre de 2022 y su fundador fue condenado a veinticinco años. Antes de confiar tu plata, preguntá si está regulada, quién la guarda, de dónde sale el rendimiento, si es transparente, y no pongas todo en un solo lugar.",
20: "Alquilar o comprar: comprar cuesta mucho más que la cuota, porque suma intereses, impuestos, mantenimiento y el rendimiento perdido del anticipo. Con algunos supuestos gana el que alquila e invierte la diferencia; con otros, gana el que compra. La clave es si de verdad vas a invertir la diferencia, cuántos años te vas a quedar y que la cuota no supere un tercio de tus ingresos.",
21: "Sesenta y seis dólares por mes de café, invertidos cuarenta años al siete por ciento, son unos ciento setenta y tres mil dólares. Pero la inflación achica ese número, el café puede valer la pena, y los gastos grandes pesan mucho más. Empezar temprano multiplica el resultado, y el equilibrio, como el café de los sábados, también se capitaliza.",
}
if __name__ == "__main__":
    for n, txt in EXTRA.items():
        p = f"guiones/{n:02d}.txt"; s = open(p, encoding="utf-8").read()
        head = "## Resumen en 30 segundos"
        if head in s:
            continue
        block = f"{head}\n@bg pizarra\n@cast moni\nP: RESUMEN |\n" + "\n".join(f"MONI: {x.strip()}." if not x.strip().endswith(".") else f"MONI: {x.strip()}" for x in txt.split(". ") if x.strip()) + "\n"
        i = s.index("## Cierre")
        s = s[:i] + block + s[i:]
        open(p, "w", encoding="utf-8").write(s)
        print("ok", n)
