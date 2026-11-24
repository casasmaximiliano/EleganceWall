# Temporada 1: episodios 10 a 13 (mismo formato que eps_1_5.py)

EPS_C = [
dict(n=10, slug="la-navidad-de-bombolin",
 tes="La Navidad de Bombolín", ten="Bombolín's Christmas",
 sticker="⭐", ces="¿Qué ven los renos?", cen="What can reindeer see?",
 les="compartir hace que todos estemos felices", len="sharing makes everyone happy",
 dato_es="Los renos pueden ver la luz ultravioleta, que los ojos de las personas no ven. Eso los ayuda a encontrar comida en la nieve.",
 dato_en="Reindeer can see ultraviolet light, which human eyes can't see. It helps them find food in the snow.",
 fuente="Hogg y otros (2011), Journal of Experimental Biology, «Arctic reindeer extend their visual range into the ultraviolet».",
 sum_es="Es Nochebuena y nieva en el valle. Bombolín conoce a un reno que se perdió en la nieve… y juntos comparten la noche más linda del año.",
 sum_en="It's Christmas Eve and it's snowing in the valley. Bombolín meets a reindeer who got lost in the snow… and together they share the most beautiful night of the year.",
 thumb=dict(em="🦌", t1_es="¡NAVIDAD!", t1_en="CHRISTMAS!", t2_es="¡UN RENO!", t2_en="A REINDEER!", chars=["PIPO", "LULA"]),
 shorts=[(1, 2, "¡UN RENO PERDIDO!", "A LOST REINDEER!"), (3, 4, "¿QUÉ VEN LOS RENOS?", "WHAT DO REINDEER SEE?")],
 s=[
  ("xmas", ["🎄", "❄"], "PIPO LULA:calm", [
   ("PIPO", "¡Es Nochebuena! ¡Y está nevando!", "It's Christmas Eve! And it's snowing!"),
   ("LULA", "¡Yo hice la nieve! ¡Bueno… un poquito!", "I made the snow! Well… a little bit!")]),
  ("xmas", ["🦌", "❄"], "PIPO LULA:calm G:Reno", [
   ("G:Reno", "Disculpen… me perdí en la nieve. ¿Saben dónde está el bosque grande?", "Excuse me… I got lost in the snow. Do you know where the big forest is?"),
   ("PIPO", "¡Un reno! ¡Nosotros te ayudamos!", "A reindeer! We'll help you!")]),
  ("xmas", ["🦌", "🌙"], "PIPO LULA:calm G:Reno", [
   ("G:Reno", "Tengo un poquito de hambre. Busco unas plantitas que crecen debajo de la nieve.", "I'm a little hungry. I'm looking for small plants that grow under the snow."),
   ("LULA", "Pero todo está blanco… ¿cómo las encuentras?", "But everything is white… how do you find them?")]),
  ("board", ["🦌", "👀"], "PIPO ABU", [
   ("ABU", "Los renos tienen ojos muy especiales: pueden ver la luz ultravioleta, que nosotros no vemos.", "Reindeer have very special eyes: they can see ultraviolet light, which we can't see."),
   ("ABU", "Así, en la nieve blanca, las plantitas y los líquenes se ven oscuritos y fáciles de encontrar.", "So in the white snow, plants and lichens look dark and easy to find.")]),
  ("xmas", ["🌿", "🦌"], "PIPO LULA:happy G:Reno", [
   ("G:Reno", "¡Ahí están! ¡Comida!", "There they are! Food!"),
   ("PIPO", "¡Y por allá está el bosque grande!", "And over there is the big forest!")]),
  ("xmas", ["🍪", "🥛"], "PIPO TOTO ZUMBI LULA:happy ABU G:Reno", [
   ("TOTO", "¡Uy, uy! ¿Quieres quedarte a cenar con nosotros?", "Uh-oh! Do you want to stay for dinner with us?"),
   ("G:Reno", "¡Me encantaría!", "I'd love to!"),
   ("ZUMBI", "¡Zzzí! ¡Hay galletitas para todos!", "Bzzz, yes! There are cookies for everyone!")]),
  ("xmas", ["⭐", "🎄"], "PIPO TOTO ZUMBI LULA:happy ABU G:Reno", [
   ("ABU", "La Navidad es más linda cuando la compartimos.", "Christmas is more beautiful when we share it."),
   ("ALL", "¡Feliz Navidad a todos!", "Merry Christmas, everyone!")]),
  ("night", ["⭐", "🦌"], "PIPO LULA:happy G:Reno", [
   ("G:Reno", "¡Gracias, amigos! ¡Nunca voy a olvidar esta noche!", "Thank you, friends! I'll never forget this night!"),
   ("PIPO", "¡Vuelve cuando quieras, amigo reno!", "Come back anytime, reindeer friend!")]),
 ]),

dict(n=11, slug="no-tengo-sueno",
 tes="Bombolín no tiene sueño", ten="Bombolín Isn't Sleepy",
 sticker="🌙", ces="¿Cuánto duermen los koalas?", cen="How long do koalas sleep?",
 les="dormir bien nos ayuda a crecer", len="good sleep helps us grow",
 dato_es="Los koalas duermen o descansan entre 18 y 22 horas por día. Los niños de 3 a 5 años necesitan dormir de 10 a 13 horas.",
 dato_en="Koalas sleep or rest 18 to 22 hours a day. Kids ages 3 to 5 need 10 to 13 hours of sleep.",
 fuente="Australian Koala Foundation; American Academy of Sleep Medicine (2016).",
 sum_es="Es de noche y Bombolín no quiere dormir: ¡quiere seguir jugando! Un koala dormilón y Abu Tortu le muestran por qué dormir es un superpoder.",
 sum_en="It's nighttime and Bombolín doesn't want to sleep: he wants to keep playing! A sleepy koala and Grandma Tortu show him why sleep is a superpower.",
 thumb=dict(em="🌙", t1_es="¡NO TENGO SUEÑO!", t1_en="NOT SLEEPY!", t2_es="¡A DORMIR!", t2_en="BEDTIME!", chars=["PIPO", "ABU"]),
 shorts=[(0, 1, "¡NO TENGO SUEÑO!", "I'M NOT SLEEPY!"), (2, 3, "¡DUERME 20 HORAS!", "SLEEPS 20 HOURS!")],
 s=[
  ("night", ["🌙", "🧸"], "PIPO", [
   ("PIPO", "¡No tengo sueñooo! ¡Quiero jugar un ratito más!", "I'm not sleepyyy! I want to play a little longer!"),
   ("PIPO", "Ahh… ¡No! ¡Eso no fue un bostezo!", "Yawn… No! That wasn't a yawn!")]),
  ("night", ["🌙", "⭐"], "PIPO ABU", [
   ("ABU", "Bombolín, ya es hora de dormir.", "Bombolín, it's bedtime."),
   ("PIPO", "Pero Abu, dormir es aburrido…", "But Grandma, sleeping is boring…"),
   ("ABU", "¿Aburrido? Ven, te presento a alguien que es campeón de dormir.", "Boring? Come, let me introduce you to a sleeping champion.")]),
  ("night", ["🐨", "🌳"], "PIPO ABU G:Koala", [
   ("G:Koala", "Zzz… ¿Eh? Hola… yo duermo casi todo el día…", "Zzz… Huh? Hi… I sleep almost all day…"),
   ("ABU", "Los koalas duermen o descansan hasta veintidós horas por día.", "Koalas sleep or rest up to twenty-two hours a day."),
   ("PIPO", "¡Veintidós horas! ¡Es casi todo el día!", "Twenty-two hours! That's almost all day!")]),
  ("board", ["🧒", "⏰"], "PIPO ABU", [
   ("ABU", "Los niños de tu edad necesitan dormir entre diez y trece horas.", "Kids your age need between ten and thirteen hours of sleep."),
   ("ABU", "Mientras duermes, tu cuerpo crece, y tu cabeza guarda todo lo que aprendiste hoy.", "While you sleep, your body grows, and your brain saves everything you learned today.")]),
  ("night", ["🐬", "🌊"], "PIPO ABU", [
   ("PIPO", "¿Y todos los animales duermen igual?", "Do all animals sleep the same way?"),
   ("ABU", "¡No! Los delfines duermen con la mitad del cerebro, para no olvidarse de subir a respirar.", "No! Dolphins sleep with half their brain, so they don't forget to come up for air.")]),
  ("night", ["🛏", "🧸"], "PIPO ABU", [
   ("PIPO", "Bueno… me pongo el pijama, me lavo los dientes…", "Okay… I put on my pajamas, I brush my teeth…"),
   ("ABU", "Y elegimos un cuento.", "And we pick a story."),
   ("PIPO", "Y abrazo a mi peluche…", "And I hug my teddy…")]),
  ("night", ["⭐", "🌙"], "PIPO ABU", [
   ("ABU", "Duerme, duerme, dinosaurito, que la luna te cuida un ratito.", "Sleep, sleep, little dino, the moon will keep you safe tonight."),
   ("PIPO", "Buenas noches, Abu… Zzz…", "Good night, Grandma… Zzz…")]),
 ]),

dict(n=12, slug="brocoli-no",
 tes="¡Toto no quiere probar el brócoli!", ten="Toto Won't Try Broccoli!",
 sticker="🥦", ces="¿Cuántas semillas tiene una frutilla?", cen="How many seeds does a strawberry have?",
 les="probar cosas nuevas es de valientes", len="trying new things is brave",
 dato_es="A veces hay que probar un alimento nuevo entre 8 y 15 veces para que nos guste. Y una frutilla tiene unas 200 semillitas por fuera.",
 dato_en="Sometimes we need to try a new food 8 to 15 times before we like it. And a strawberry has about 200 tiny seeds on the outside.",
 fuente="Birch y Marlin (1982), revista Appetite; California Strawberry Commission.",
 sum_es="En el picnic, Toto dice «¡puaj!» al brócoli sin probarlo. Bombolín le propone un juego de colores… y una aventura muy rica.",
 sum_en="At the picnic, Toto says 'yuck!' to broccoli without even trying it. Bombolín suggests a color game… and a yummy adventure.",
 thumb=dict(em="🥦", t1_es="¡PUAJ!", t1_en="YUCK!", t2_es="¿LO PRUEBA?", t2_en="WILL HE TRY IT?", chars=["TOTO", "PIPO"]),
 shorts=[(0, 1, "¡PUAJ! ¡UN ÁRBOL!", "YUCK! A TREE!"), (4, 5, "¡200 SEMILLAS!", "200 SEEDS!")],
 s=[
  ("meadow", ["🧺", "🥦"], "PIPO TOTO", [
   ("PIPO", "¡Picnic! Traje frutas y verduras de colores.", "Picnic time! I brought colorful fruits and veggies."),
   ("TOTO", "¡Puaj! ¡Hay un árbol en mi plato!", "Yuck! There's a tree on my plate!")]),
  ("meadow", ["🥦", "🍓"], "PIPO TOTO", [
   ("PIPO", "No es un árbol, es brócoli. ¿Lo probaste alguna vez?", "It's not a tree, it's broccoli. Have you ever tried it?"),
   ("TOTO", "No… ¡pero seguro que no me gusta!", "No… but I'm sure I don't like it!")]),
  ("board", ["🥦", "🔢"], "PIPO ABU", [
   ("ABU", "¿Sabían que a veces hay que probar un alimento muchas veces para que nos guste?", "Did you know that sometimes we need to try a food many times before we like it?"),
   ("ABU", "¡A veces diez veces, o más! El paladar también aprende.", "Sometimes ten times, or more! Our taste buds learn too.")]),
  ("meadow", ["🌈", "🍽"], "PIPO TOTO LULA:happy", [
   ("LULA", "¡Juguemos al plato arcoíris! Un bocado de cada color.", "Let's play rainbow plate! One bite of each color."),
   ("TOTO", "Rojo… ¡tomate! Naranja… ¡zanahoria! Mmm…", "Red… tomato! Orange… carrot! Mmm…")]),
  ("meadow", ["🍓", "🔍"], "PIPO TOTO ABU", [
   ("TOTO", "¿Por qué la frutilla tiene puntitos?", "Why does the strawberry have dots?"),
   ("ABU", "¡Son sus semillas! Una frutilla tiene unas doscientas semillitas por fuera.", "Those are its seeds! A strawberry has about two hundred tiny seeds on the outside."),
   ("TOTO", "¡Uy, uy, uy! ¡Doscientas!", "Uh-oh! Two hundred!")]),
  ("meadow", ["🥦", "🤞"], "PIPO TOTO LULA:happy", [
   ("PIPO", "Y verde… ¡brócoli! ¿Un mordisquito chiquito?", "And green… broccoli! Just a teeny-tiny bite?"),
   ("TOTO", "Bueno… uno chiquito… ñam… Mmm… ¡no está tan mal!", "Okay… a tiny one… nom… Mmm… it's not that bad!")]),
  ("meadow", ["🌈", "🧺"], "PIPO TOTO LULA:happy ZUMBI", [
   ("ALL", "¡Rojo, naranja, amarillo y verde, comer de colores nunca se pierde!", "Red and orange, yellow and green, the yummiest rainbow you've ever seen!"),
   ("TOTO", "¡Mañana pruebo otra vez!", "I'll try it again tomorrow!")]),
 ]),

dict(n=13, slug="feliz-ano-nuevo",
 tes="¡Feliz año nuevo, Bombolín!", ten="Happy New Year, Bombolín!",
 sticker="🎆", ces="¿Cuánto tarda la Tierra en dar la vuelta al Sol?", cen="How long does Earth take to go around the Sun?",
 les="cada día es una aventura para descubrir", len="every day is an adventure to discover",
 dato_es="La Tierra tarda unos 365 días en dar una vuelta completa alrededor del Sol: eso es un año.",
 dato_en="Earth takes about 365 days to go all the way around the Sun: that's one year.",
 fuente="NASA Space Place, «How long is a year on other planets?».",
 sum_es="¡Termina el año! Bombolín mira su Libro de Descubrimientos con todas las figuritas de sus aventuras… y espera el año nuevo con sus amigos.",
 sum_en="The year is ending! Bombolín looks through his Discovery Book full of stickers from all his adventures… and waits for the new year with his friends.",
 thumb=dict(em="🎆", t1_es="¡AÑO NUEVO!", t1_en="NEW YEAR!", t2_es="¡3, 2, 1!", t2_en="3, 2, 1!", chars=["PIPO", "ZUMBI"]),
 shorts=[(1, 2, "¿QUÉ ES UN AÑO?", "WHAT IS A YEAR?"), (5, 6, "¡3, 2, 1… FELIZ AÑO!", "3, 2, 1… HAPPY NEW YEAR!")],
 s=[
  ("night", ["📖", "⭐"], "PIPO TOTO LULA:happy ZUMBI ABU", [
   ("PIPO", "¡Miren mi Libro de Descubrimientos! ¡Tiene una figurita de cada aventura!", "Look at my Discovery Book! It has a sticker from every adventure!"),
   ("TOTO", "¡El huevo gigante! ¡La cueva de los ecos! ¡Uy, cuántas cosas!", "The giant egg! The echo cave! Wow, so many things!")]),
  ("night", ["🌍", "☀"], "PIPO ABU", [
   ("PIPO", "Abu, ¿por qué el año se termina?", "Grandma, why does the year end?"),
   ("ABU", "Porque la Tierra, nuestro planeta, viaja alrededor del Sol. ¡Y tarda unos trescientos sesenta y cinco días en dar la vuelta!", "Because Earth, our planet, travels around the Sun. And it takes about three hundred sixty-five days to go all the way around!")]),
  ("board", ["🌍", "📅"], "PIPO ABU", [
   ("ABU", "Cada vuelta completa es un año. ¡Y hoy terminamos una vuelta!", "Each full trip around is one year. And today we finish one trip!"),
   ("PIPO", "¡Wiii! ¡Viajamos alrededor del Sol sin darnos cuenta!", "Wheee! We travel around the Sun without even noticing!")]),
  ("night", ["📖", "💭"], "PIPO TOTO LULA:happy ZUMBI", [
   ("LULA", "¿Qué fue lo que más les gustó del año?", "What did you like most about this year?"),
   ("ZUMBI", "¡La carrera donde llegamos todos juntos!", "The race where we all finished together!"),
   ("TOTO", "¡Mi baño con burbujas! ¡Uy, no puedo creer que lo dije!", "My bubble bath! Uh-oh, I can't believe I said that!")]),
  ("night", ["🎆", "✨"], "PIPO TOTO LULA:happy ZUMBI ABU", [
   ("ABU", "¿Y qué quieren descubrir el año que viene?", "And what do you want to discover next year?"),
   ("PIPO", "¡Todo! ¡El mar, la selva, las estrellas!", "Everything! The sea, the jungle, the stars!")]),
  ("night", ["🎆", "🎉"], "PIPO TOTO LULA:happy ZUMBI ABU", [
   ("ALL", "¡Diez, nueve, ocho, siete, seis, cinco, cuatro, tres, dos, uno!", "Ten, nine, eight, seven, six, five, four, three, two, one!"),
   ("ALL", "¡Feliz año nuevo!", "Happy New Year!")]),
  ("night", ["🎆", "💛"], "PIPO TOTO LULA:happy ZUMBI ABU", [
   ("PIPO", "¡Gracias por acompañarnos en todas nuestras aventuras!", "Thank you for joining us on all our adventures!"),
   ("ABU", "Nos vemos el año que viene, mis amores.", "See you next year, my little loves.")]),
 ]),
]
