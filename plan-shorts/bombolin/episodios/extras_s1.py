# Escenas extra para alargar las historias de la semana 1 a 4 o 5 minutos (solo español).
# EXTRA[n] = [(después_de_la_escena, escena), ...]  (índices de la historia original de eps_*.py)
# Escena: (fondo, [emojis], "reparto", [(personaje, texto), ...])

EXTRA = {
1: [
 (1, ("meadow", ["🥚", "🍃"], "PIPO TOTO LULA:calm ZUMBI", [
   ("ZUMBI", "¡Zzzí! ¿Qué es esa cosa redonda?"),
   ("LULA", "¡Ay, qué lindo! Es un huevo. Pero tiene frío, mírenlo."),
   ("PIPO", "Los huevos necesitan estar calentitos para que el bebé crezca."),
   ("TOTO", "¡Uy, uy, uy! ¡Le presto mi media!")])),
 (1, ("meadow", ["🍂", "🥚"], "PIPO TOTO LULA:calm ZUMBI", [
   ("PIPO", "¡Hagamos un nido de hojas suaves!"),
   ("ZUMBI", "¡Yo traigo hojas! ¡Una, dos, tres!"),
   ("LULA", "Yo traigo plumitas que encontré."),
   ("TOTO", "Y yo… ¡me acuesto al lado para darle calor!"),
   ("PIPO", "¡Así está calentito y seguro!")])),
 (4, ("board", ["🐦", "🥚"], "PIPO ABU", [
   ("ABU", "Las aves se sientan sobre sus huevos para darles calor. A eso se le dice empollar."),
   ("ABU", "El bebé crece adentro, calentito, hasta que está listo para salir."),
   ("PIPO", "¡Entonces nosotros somos los que empollamos!")])),
 (4, ("night", ["🌙", "🥚"], "PIPO TOTO LULA:calm ZUMBI", [
   ("PIPO", "Se hizo de noche. Hay que cuidar el huevo por turnos."),
   ("ZUMBI", "¡Yo primero! Bueno… no. ¡Tú primero, Lula!"),
   ("LULA", "Yo lo cuido, y después te despierto, Toto."),
   ("TOTO", "Zzz… ¿Eh? ¡Sí, sí, estoy despierto!")])),
 (4, ("night", ["⭐", "🥚"], "PIPO TOTO", [
   ("TOTO", "¡Uy! ¡Casi me siento arriba del huevo!"),
   ("PIPO", "¡Cuidado, Toto! ¡Despacito!"),
   ("TOTO", "Perdón, huevito. Te canto una canción para que duermas.")])),
],
2: [
 (2, ("meadow", ["🐦", "🪶"], "PIPO TOTO G:Pájaro", [
   ("G:Pájaro", "¡Pío! ¿Ustedes saben que los pájaros nos bañamos todos los días?"),
   ("TOTO", "¿Todos los días? ¡Uy, qué cansador!"),
   ("G:Pájaro", "¡Es divertidísimo! Salpicamos agua con las alas. ¡Splish, splash!")])),
 (2, ("meadow", ["🐷", "🟤"], "PIPO TOTO G:Gallina", [
   ("TOTO", "Pero los cerditos están siempre en el barro… ¡como yo!"),
   ("PIPO", "Sí, porque el barro los refresca cuando hace calor."),
   ("G:Gallina", "¡Cocoró! ¡Pero después se lavan!")])),
 (5, ("meadow", ["🫧", "🧼"], "PIPO TOTO LULA:happy", [
   ("LULA", "¿Saben qué hace el jabón? Les cuento: atrapa la mugre y los bichitos chiquitos."),
   ("PIPO", "¡Y el agua se los lleva!"),
   ("TOTO", "¡Bye bye, bichitos!")])),
 (6, ("room", ["🦆", "🫧"], "PIPO TOTO ZUMBI", [
   ("ZUMBI", "¡Zzzí! ¡Traje un patito de goma!"),
   ("TOTO", "¡Cuac, cuac! ¡Mi patito también se baña!"),
   ("PIPO", "¿Y si hacemos una barba de espuma?"),
   ("TOTO", "¡Jo, jo, jo! ¡Soy un abuelito!")])),
 (6, ("room", ["🧴", "🪮"], "PIPO TOTO", [
   ("PIPO", "Ahora la toalla… ¡y a peinarse!"),
   ("TOTO", "¡Uy, mi pelo está suavecito como una nube!"),
   ("PIPO", "¡Pareces otro monstruo!")])),
],
3: [
 (0, ("meadow", ["☁", "🌬"], "PIPO LULA:calm ZUMBI", [
   ("ZUMBI", "¡Zzz! ¡Qué viento! ¡Casi me lleva volando!"),
   ("PIPO", "Mira esas nubes grandes y grises allá lejos."),
   ("LULA", "Son mis primas… ¡pero están un poquito enojadas!")])),
 (2, ("room", ["📚", "🕯"], "PIPO LULA:sad TOTO", [
   ("TOTO", "¡Uy! ¡Se cortó la luz!"),
   ("PIPO", "Tranquilos, tengo una linterna. ¿Les leo un cuento?"),
   ("LULA", "Sí… un cuento ayuda a no tener miedo.")])),
 (2, ("room", ["🧸", "💛"], "PIPO LULA:sad", [
   ("LULA", "Bombolín, ¿tú nunca tienes miedo?"),
   ("PIPO", "¡Claro que sí! Todos tenemos miedo a veces."),
   ("PIPO", "Cuando tengo miedo, abrazo mi peluche y respiro despacito.")])),
 (5, ("room", ["🌧", "🪟"], "PIPO LULA:calm TOTO", [
   ("TOTO", "¡Ya casi no llueve! ¡Se escucha como música!"),
   ("LULA", "Plic, plic, plic… ¡es la canción de la lluvia!"),
   ("ALL", "¡Plic, plic, ploc, llueve despacito, plic, plic, ploc, ya sale el solcito!")])),
 (7, ("meadow", ["💧", "🥾"], "PIPO LULA:happy TOTO ZUMBI", [
   ("TOTO", "¡Charcos! ¡Saltemos en los charcos!"),
   ("ZUMBI", "¡Zzzí! ¡Splash!"),
   ("LULA", "¡Yo hago más charcos! ¡Jijiji!")])),
],
4: [
 (0, ("meadow", ["👟", "🍌"], "PIPO ZUMBI TOTO", [
   ("PIPO", "Para correr hay que estirar las piernas. ¡Arriba, abajo!"),
   ("TOTO", "¡Uy, mis piernas no llegan al piso!"),
   ("ZUMBI", "¡Y hay que comer algo rico para tener energía!")])),
 (3, ("meadow", ["🐇", "💨"], "PIPO ZUMBI G:Canguro", [
   ("G:Canguro", "¡Hola, corredores! Yo no corro: ¡salto!"),
   ("ZUMBI", "¡Qué salto tan grande!"),
   ("G:Canguro", "Uso mi cola para no caerme. ¡Hop, hop, hop!")])),
 (5, ("meadow", ["💧", "🌳"], "PIPO ZUMBI", [
   ("PIPO", "Uf… ¡qué calor! Paremos a tomar agua."),
   ("ZUMBI", "¿Y si los demás nos pasan?"),
   ("PIPO", "No importa. Primero hay que cuidar el cuerpo.")])),
 (6, ("meadow", ["🐢", "🌸"], "PIPO ZUMBI ABU TOTO", [
   ("TOTO", "¡Uy, uy! ¡Espérenme!"),
   ("ABU", "Vamos, Toto. Despacito, pero sin parar."),
   ("ZUMBI", "¡Todos juntos somos un equipo!")])),
],
5: [
 (1, ("room", ["🛏", "🧦"], "PIPO TOTO ZUMBI", [
   ("ZUMBI", "¡Zzzí! ¿Buscaron debajo de la cama?"),
   ("TOTO", "¡Uy! Hay tres medias, un tren y… ¡una manzana!"),
   ("PIPO", "¡Toto! ¿Hace cuánto está esa manzana ahí?")])),
 (2, ("meadow", ["🐶", "🦴"], "PIPO TOTO", [
   ("TOTO", "¿Y si se lo llevó un perrito?"),
   ("PIPO", "¡Los perritos no se cepillan con cepillo!"),
   ("TOTO", "¡Uy, cierto! Ellos mastican cosas para limpiarse los dientes.")])),
 (4, ("board", ["🦈", "🦷"], "PIPO ABU", [
   ("ABU", "¿Sabían que a los tiburones se les caen los dientes y les salen nuevos muchas veces?"),
   ("PIPO", "¡A mí también se me van a caer los dientes de leche!"),
   ("ABU", "Sí, y te saldrán los definitivos. ¡Por eso hay que cuidarlos desde ahora!")])),
 (7, ("night", ["🌙", "🛏"], "PIPO TOTO", [
   ("TOTO", "Ahora sí, a la cama. Buenas noches, cepillo."),
   ("PIPO", "Buenas noches, Toto. ¡Que sueñes con burbujas!")])),
],
6: [
 (0, ("snow", ["⛄", "🥕"], "PIPO ZUMBI TOTO LULA:calm", [
   ("TOTO", "¡Hagamos un muñeco de nieve!"),
   ("LULA", "Una bola grande, una mediana y una chiquita."),
   ("PIPO", "¡Y una zanahoria de nariz!"),
   ("ZUMBI", "¡Zzzí! ¡Le pongo mi bufanda!")])),
 (2, ("snow", ["🛷", "😢"], "PIPO ZUMBI TOTO", [
   ("TOTO", "Zumbi no me deja subir…"),
   ("PIPO", "Zumbi, mira la cara de Toto. Está triste."),
   ("ZUMBI", "Ay… es que tenía muchas ganas.")])),
 (4, ("snow", ["🐧", "🥚"], "PIPO ZUMBI G:Pingüino", [
   ("G:Pingüino", "Y otra cosa: los papás pingüinos cuidan el huevo encima de sus patas, ¡durante muchos días!"),
   ("ZUMBI", "¿Sin moverse?"),
   ("G:Pingüino", "¡Casi sin moverse! Esperar también es cuidar.")])),
 (7, ("room", ["☕", "🧣"], "PIPO ZUMBI TOTO LULA:happy", [
   ("LULA", "¡Qué frío! Vamos adentro a tomar algo calentito."),
   ("TOTO", "¡Uy, chocolate caliente!"),
   ("ZUMBI", "¡Y yo le sirvo primero a Toto!")])),
],
7: [
 (0, ("meadow", ["📝", "🎈"], "PIPO TOTO ZUMBI LULA:calm", [
   ("PIPO", "Hagamos una lista: globos, torta, regalo… ¡y que Abu no se entere!"),
   ("ZUMBI", "¡Zzzí! ¡Yo vigilo desde el aire!"),
   ("LULA", "Yo hago la música.")])),
 (2, ("room", ["🎵", "🎹"], "PIPO LULA:calm ZUMBI", [
   ("LULA", "Ensayemos la canción del cumpleaños. ¡Despacito, que Abu no escuche!"),
   ("ALL", "¡Que los cumpla feliz, Abu Tortu, que los cumpla feliz!"),
   ("ZUMBI", "¡Shhh! ¡Más bajito!")])),
 (4, ("room", ["🍓", "🍌"], "PIPO LULA:happy TOTO", [
   ("PIPO", "La torta nueva es de frutas: frutillas, bananas y uvas."),
   ("TOTO", "¿Puedo probar una frutilla?"),
   ("LULA", "¡Una sola, Toto!"),
   ("TOTO", "Ñam… ¡bueno, dos!")])),
 (5, ("meadow", ["👀", "🐢"], "PIPO ZUMBI", [
   ("ZUMBI", "¡Alerta! ¡Abu Tortu viene por el camino!"),
   ("PIPO", "¡Todos a sus lugares! ¡Apaguen la luz!")])),
],
}

# Shorts de cada programa: (primera escena, última escena, texto del gancho), con índices de la historia ya alargada
SHORTS = {
 1: [(0, 1, "¡UN HUEVO GIGANTE!"), (10, 12, "¡NACIÓ!")],
 2: [(0, 1, "¡NO QUIERO BAÑARME!"), (9, 10, "¡BURBUJAS!")],
 3: [(2, 3, "¡BUM!"), (10, 11, "¡UN ARCOÍRIS!")],
 4: [(2, 3, "¡EN SUS MARCAS…!"), (4, 6, "¡FIUUUM!")],
 5: [(0, 1, "¿Y MI CEPILLO?"), (8, 9, "¡CHIKI-CHIKI-BRILLA!")],
 6: [(0, 1, "¡NIEVE!"), (5, 7, "¿CÓMO SE CALIENTAN?")],
 7: [(0, 1, "¡SHHH! ¡SORPRESA!"), (9, 10, "¡SORPRESAAA!")],
}
