# Temporada 1: episodios 6 a 9 (mismo formato que eps_1_5.py)

EPS_B = [
dict(n=6, slug="pinguinos-en-la-nieve",
 tes="¡Nieve! Bombolín conoce a los pingüinos", ten="Snow! Bombolín Meets the Penguins",
 sticker="🐧", ces="¿Cómo se calientan los pingüinos?", cen="How do penguins keep warm?",
 les="turnarse es justo para todos", len="taking turns is fair for everyone",
 dato_es="Los pingüinos emperador se amontonan y se turnan para estar en el centro, donde hace más calor. Y cada copo de nieve tiene seis puntas.",
 dato_en="Emperor penguins huddle and take turns being in the middle, where it's warmest. And every snowflake has six points.",
 fuente="BBC Earth / Gerum y otros (2013), New Journal of Physics; NOAA SciJinks, «How do snowflakes form?».",
 sum_es="¡Cayó la primera nieve! Bombolín y sus amigos juegan en el hielo, pero Zumbi no quiere esperar su turno en el trineo. Los pingüinos le enseñan un secreto.",
 sum_en="The first snow has fallen! Bombolín and his friends play on the ice, but Zumbi doesn't want to wait for his turn on the sled. The penguins teach him a secret.",
 thumb=dict(em="🐧", t1_es="¡NIEVE!", t1_en="SNOW!", t2_es="¡YO PRIMERO!", t2_en="ME FIRST!", chars=["PIPO", "ZUMBI"]),
 shorts=[(0, 1, "¡NIEVE!", "SNOW!"), (4, 5, "¿CÓMO SE CALIENTAN?", "HOW DO THEY KEEP WARM?")],
 s=[
  ("snow", ["❄", "⛄"], "PIPO ZUMBI", [
   ("PIPO", "¡Wiii! ¡Todo está blanco! ¡Nieve!", "Wheee! Everything is white! Snow!"),
   ("ZUMBI", "¡Zzz… qué frío! ¡Se me congelan las alitas!", "Bzzz… so cold! My little wings are freezing!")]),
  ("snow", ["❄", "🔍"], "PIPO ZUMBI ABU", [
   ("PIPO", "¡Mira este copo de nieve en mi mano!", "Look at this snowflake in my hand!"),
   ("ABU", "Si lo miras con lupa, vas a ver que tiene seis puntas. ¡Cada copo es como una estrellita!", "If you look with a magnifying glass, you'll see it has six points. Every snowflake is like a tiny star!")]),
  ("snow", ["🛷", "⛄"], "PIPO ZUMBI TOTO", [
   ("TOTO", "¡Traje el trineo! ¿Quién va primero?", "I brought the sled! Who goes first?"),
   ("ZUMBI", "¡Yo! ¡Yo! ¡Yo primero! ¡Y yo segundo! ¡Y yo tercero!", "Me! Me! Me first! And me second! And me third!"),
   ("TOTO", "¡Uy, uy! ¡Así no es justo!", "Uh-oh! That's not fair!")]),
  ("snow", ["🐧", "🐧"], "PIPO ZUMBI G:Pingüino", [
   ("G:Pingüino", "¡Hola, amigos! ¿Por qué discuten?", "Hello, friends! Why are you arguing?"),
   ("PIPO", "Zumbi quiere ir siempre primero.", "Zumbi always wants to go first."),
   ("G:Pingüino", "Nosotros tenemos un secreto para el frío. ¡Miren!", "We have a secret for the cold. Watch!")]),
  ("board", ["🐧", "🔄"], "PIPO ABU", [
   ("ABU", "Los pingüinos emperador se juntan todos en un grupo muy apretado para calentarse.", "Emperor penguins huddle together in a tight group to keep warm."),
   ("ABU", "Los de afuera tienen más frío, así que se van turnando. ¡Todos pasan por el centro calentito!", "The ones outside are colder, so they take turns. Everyone gets a turn in the warm middle!")]),
  ("snow", ["🛷", "🐧"], "PIPO ZUMBI TOTO", [
   ("ZUMBI", "¡Entonces turnarse es como un abrazo de pingüinos!", "So taking turns is like a penguin hug!"),
   ("ZUMBI", "Toto, ¡ve tú primero!", "Toto, you go first!"),
   ("TOTO", "¡Uy, uy, uy, gracias! ¡Wiii!", "Uh-oh, thank you! Wheee!")]),
  ("snow", ["🛷", "❄"], "PIPO ZUMBI TOTO", [
   ("PIPO", "¡Ahora me toca a mí!", "Now it's my turn!"),
   ("ZUMBI", "¡Y después a mí! ¡Zzzí, qué divertido!", "And then me! Bzzz, yes, this is fun!")]),
  ("snow", ["🐧", "💛"], "PIPO ZUMBI TOTO G:Pingüino", [
   ("ALL", "¡Abrazo de pingüino!", "Penguin hug!"),
   ("G:Pingüino", "¡Así nadie tiene frío!", "That way, nobody gets cold!")]),
 ]),

dict(n=7, slug="cumpleanos-de-abu-tortu",
 tes="¡Fiesta sorpresa para Abu Tortu!", ten="A Surprise Party for Grandma Tortu!",
 sticker="🎂", ces="¿Cuántos años tiene Abu?", cen="How old is Grandma?",
 les="los regalos hechos con amor son los mejores", len="gifts made with love are the best",
 dato_es="Jonathan, una tortuga gigante de la isla Santa Elena, nació alrededor de 1832: es el animal terrestre vivo más viejo conocido.",
 dato_en="Jonathan, a giant tortoise on the island of Saint Helena, hatched around 1832: he is the oldest known living land animal.",
 fuente="Guinness World Records, «Oldest land animal living».",
 sum_es="Es el cumpleaños de Abu Tortu y los amigos preparan una fiesta sorpresa. Pero Toto decora todo al revés y Lula hace llover sobre la torta…",
 sum_en="It's Grandma Tortu's birthday and the friends plan a surprise party. But Toto decorates everything upside down and Lula rains on the cake…",
 thumb=dict(em="🎂", t1_es="¡SORPRESA!", t1_en="SURPRISE!", t2_es="¡FIESTA!", t2_en="PARTY!", chars=["ABU", "PIPO"]),
 shorts=[(0, 1, "¡SHHH! ¡SORPRESA!", "SHHH! SURPRISE!"), (6, 7, "¡SORPRESAAA!", "SURPRIIISE!")],
 s=[
  ("meadow", ["🎈", "🤫"], "PIPO TOTO ZUMBI LULA:calm", [
   ("PIPO", "¡Shhh! Hoy es el cumpleaños de Abu Tortu. ¡Le hacemos una fiesta sorpresa!", "Shhh! Today is Grandma Tortu's birthday. Let's throw her a surprise party!"),
   ("TOTO", "¿Cuántos años cumple? ¿Cien? ¿Mil?", "How old is she? A hundred? A thousand?")]),
  ("board", ["🐢", "🦕"], "PIPO ABU", [
   ("ABU", "¿Sabían que las tortugas existen desde la época de los dinosaurios?", "Did you know turtles have been around since the time of the dinosaurs?"),
   ("PIPO", "¡Abu! ¿Nos estabas escuchando?", "Grandma! Were you listening?"),
   ("ABU", "¿Escuchar qué? Yo solo pasaba despacito…", "Listening to what? I was just slowly passing by…")]),
  ("room", ["🎈", "🧦"], "PIPO TOTO", [
   ("TOTO", "¡Yo decoro! ¡Globos, guirnaldas y medias!", "I'll decorate! Balloons, streamers and socks!"),
   ("PIPO", "¿Medias?", "Socks?"),
   ("TOTO", "¡Uy, uy, uy! Quedó todo mezclado.", "Uh-oh, uh-oh! Everything got mixed up.")]),
  ("room", ["💙", "🔵"], "PIPO TOTO G:Pájaro", [
   ("G:Pájaro", "¡Pío! Yo decoro mi casa con cosas azules. ¡Prueben con un solo color!", "Tweet! I decorate my home with blue things. Try just one color!"),
   ("TOTO", "¡Todo azul! ¡Quedó hermoso!", "All blue! It looks beautiful!")]),
  ("room", ["🎂", "🌧"], "PIPO LULA:sad", [
   ("LULA", "¡Estoy tan emocionada que… ay, no! ¡Llovió sobre la torta!", "I'm so excited that… oh no! I rained on the cake!"),
   ("PIPO", "Tranquila, Lula. Hacemos una nueva, de frutas. ¡Juntos!", "It's okay, Lula. We'll make a new one, with fruit. Together!")]),
  ("room", ["🪨", "🎨"], "PIPO ZUMBI", [
   ("ZUMBI", "No tenemos regalo… ¡pero puedo pintar una piedra con un corazón!", "We don't have a gift… but I can paint a heart on a rock!"),
   ("PIPO", "¡Los pingüinos regalan piedritas a quienes quieren!", "Penguins give pebbles to the ones they love!")]),
  ("room", ["🎉", "🎂"], "PIPO TOTO ZUMBI LULA:happy ABU", [
   ("ALL", "¡Sorpresaaa! ¡Feliz cumpleaños, Abu!", "Surpriiise! Happy birthday, Grandma!"),
   ("ABU", "¡Ay, mis amores! ¡Qué hermoso!", "Oh, my little loves! How beautiful!"),
   ("ZUMBI", "¡Esta piedra es para ti!", "This rock is for you!")]),
  ("room", ["🐢", "✨"], "PIPO TOTO ZUMBI LULA:happy ABU", [
   ("ABU", "Les cuento algo: existe una tortuga de verdad, Jonathan, que nació hace casi doscientos años.", "Let me tell you something: there's a real tortoise named Jonathan who hatched almost two hundred years ago."),
   ("TOTO", "¡Uy! ¡Esa sí que sopló muchas velitas!", "Wow! He's blown out a LOT of candles!"),
   ("ABU", "Y este es el mejor regalo del mundo, porque está hecho con amor.", "And this is the best gift in the world, because it was made with love.")]),
 ]),

dict(n=8, slug="la-cueva-de-los-ecos",
 tes="La cueva que repite todo", ten="The Cave That Repeats Everything",
 sticker="🦇", ces="¿Quién repite todo?", cen="Who repeats everything?",
 les="lo nuevo da curiosidad, y está bien explorar con amigos", len="new things make us curious, and it's good to explore with friends",
 dato_es="Muchos murciélagos usan el eco para ubicarse en la oscuridad: hacen sonidos y escuchan cómo rebotan.",
 dato_en="Many bats use echoes to find their way in the dark: they make sounds and listen to how they bounce back.",
 fuente="Bat Conservation International / Smithsonian's National Zoo, «Echolocation».",
 sum_es="Bombolín y Toto entran a una cueva brillante y algo repite todo lo que dicen. ¿Un fantasma? ¡No! Es un eco… y una amiga nueva.",
 sum_en="Bombolín and Toto enter a sparkly cave and something repeats everything they say. A ghost? No! It's an echo… and a new friend.",
 thumb=dict(em="🦇", t1_es="¿QUIÉN HABLA?", t1_en="WHO'S THERE?", t2_es="¡HOLAAA!", t2_en="HELLOOO!", chars=["PIPO", "TOTO"]),
 shorts=[(0, 1, "¡HOLAAA… HOLAAA!", "HELLOOO… HELLOOO!"), (3, 4, "¡VE CON SONIDOS!", "SHE SEES WITH SOUND!")],
 s=[
  ("cave", ["💎", "🔦"], "PIPO TOTO", [
   ("PIPO", "¡Holaaa!", "Hellooo!"),
   ("G:Eco", "¡Holaaa… holaaa…!", "Hellooo… hellooo…!"),
   ("TOTO", "¡Uy, uy, uy! ¿Quién habla?", "Uh-oh, uh-oh! Who's talking?")]),
  ("cave", ["💎", "🔦"], "PIPO TOTO", [
   ("PIPO", "Es el eco. Mi voz rebota en las paredes y vuelve.", "It's an echo. My voice bounces off the walls and comes back."),
   ("TOTO", "¡Toto es valiente!", "Toto is brave!"),
   ("G:Eco", "¡Valiente… valiente…!", "Brave… brave…!")]),
  ("cave", ["🦇", "🔦"], "PIPO TOTO G:Chispi", [
   ("G:Chispi", "¡Hola! Soy Chispi, la murciélaga. ¡Bienvenidos a mi cueva!", "Hi! I'm Sparky the bat. Welcome to my cave!"),
   ("TOTO", "¿No tienes miedo de la oscuridad?", "Aren't you scared of the dark?"),
   ("G:Chispi", "¡No! Yo veo con sonidos.", "No! I see with sounds.")]),
  ("board", ["🦇", "〰"], "PIPO ABU", [
   ("ABU", "Muchos murciélagos hacen sonidos muy agudos y escuchan el eco que vuelve.", "Many bats make very high sounds and listen to the echo that comes back."),
   ("ABU", "¡Así saben dónde están las paredes y los bichitos, aunque esté oscuro!", "That way they know where the walls and the bugs are, even in the dark!")]),
  ("cave", ["💧", "💎"], "PIPO TOTO G:Chispi", [
   ("TOTO", "¡Uy! ¡Me cayó una gotita en la nariz!", "Uh-oh! A drop landed on my nose!"),
   ("G:Chispi", "Esas gotitas forman las piedras que cuelgan del techo. ¡Tardan cientos de años en crecer!", "Those drops make the rocks that hang from the ceiling. They take hundreds of years to grow!")]),
  ("cave", ["💎", "✨"], "PIPO TOTO G:Chispi", [
   ("PIPO", "¡Qué brillante es todo!", "Everything is so shiny!"),
   ("G:Chispi", "¿Jugamos a los ecos? ¡Digan su nombre!", "Want to play echoes? Say your names!"),
   ("ALL", "¡Bombolín y sus amigos!", "Bombolín and friends!"),
   ("G:Eco", "¡Amigos… amigos…!", "Friends… friends…!")]),
  ("meadow", ["🌙", "🦇"], "PIPO TOTO G:Chispi", [
   ("TOTO", "¡Ya no me da miedo la cueva!", "I'm not scared of the cave anymore!"),
   ("G:Chispi", "¡Vuelvan cuando quieran, amigos!", "Come back anytime, friends!")]),
 ]),

dict(n=9, slug="preparando-la-navidad",
 tes="¡Bombolín prepara la Navidad!", ten="Bombolín Gets Ready for Christmas!",
 sticker="🎄", ces="¿Cuál es el mejor regalo?", cen="What's the best gift?",
 les="los regalos hechos con las manos y el corazón son especiales", len="gifts made with your hands and heart are special",
 dato_es="El pájaro glorieta decora su casa con objetos azules, y algunos pingüinos regalan piedritas para armar su nido.",
 dato_en="The bowerbird decorates its home with blue things, and some penguins give pebbles to build a nest.",
 fuente="Australian Museum, «Satin Bowerbird»; Australian Antarctic Division, pingüinos de Adelia.",
 sum_es="¡Se acerca la Navidad! Bombolín y sus amigos decoran el árbol y preparan regalos hechos a mano para todos.",
 sum_en="Christmas is coming! Bombolín and his friends decorate the tree and make handmade gifts for everyone.",
 thumb=dict(em="🎄", t1_es="¡NAVIDAD!", t1_en="CHRISTMAS!", t2_es="¡REGALOS!", t2_en="GIFTS!", chars=["PIPO", "TOTO"]),
 shorts=[(0, 1, "¡LLEGA LA NAVIDAD!", "CHRISTMAS IS COMING!"), (4, 5, "¡UN REGALO HECHO A MANO!", "A HANDMADE GIFT!")],
 s=[
  ("xmas", ["🎄", "⭐"], "PIPO TOTO", [
   ("PIPO", "¡Wiii! ¡Falta poquito para Navidad! ¡Decoremos el árbol!", "Wheee! Christmas is almost here! Let's decorate the tree!"),
   ("TOTO", "¡Yo pongo la estrella! ¡Uy, uy, uy, no llego!", "I'll put the star on top! Uh-oh, I can't reach!")]),
  ("xmas", ["🎄", "🔴"], "PIPO TOTO ZUMBI", [
   ("ZUMBI", "¡Zzzí! ¡Yo vuelo y la pongo!", "Bzzz, yes! I'll fly up and put it on!"),
   ("PIPO", "¡Trabajando en equipo es más fácil!", "Teamwork makes it easier!")]),
  ("xmas", ["🎁", "🤔"], "PIPO TOTO LULA:calm", [
   ("LULA", "Quiero hacerle un regalo a cada uno… pero no sé qué.", "I want to give everyone a gift… but I don't know what."),
   ("TOTO", "¡Uy! ¡Yo tampoco!", "Uh-oh! Me neither!")]),
  ("board", ["🐧", "🪨"], "PIPO ABU", [
   ("ABU", "Les cuento un secreto: algunos pingüinos le regalan una piedrita a quien quieren, para armar su nido.", "Let me tell you a secret: some penguins give a pebble to the ones they love, to build their nest."),
   ("ABU", "Y el pájaro glorieta decora su casa con cositas azules. ¡Los regalos no tienen que ser caros!", "And the bowerbird decorates its home with little blue things. Gifts don't have to be expensive!")]),
  ("xmas", ["🎨", "✂"], "PIPO TOTO LULA:happy ZUMBI", [
   ("PIPO", "¡Hagamos regalos con nuestras manos!", "Let's make gifts with our own hands!"),
   ("ZUMBI", "¡Yo hago una tarjeta con brillitos!", "I'll make a card with glitter!"),
   ("LULA", "¡Yo un dibujo de un arcoíris!", "I'll draw a rainbow!"),
   ("TOTO", "¡Yo… un collar de fideos!", "And I'll make… a noodle necklace!")]),
  ("xmas", ["🎁", "💛"], "PIPO TOTO LULA:happy ZUMBI ABU", [
   ("ALL", "¡Para ti, Abu!", "This is for you, Grandma!"),
   ("ABU", "¡Ay, qué hermosos! Los regalos hechos con el corazón son los más especiales.", "Oh, how beautiful! Gifts made with your heart are the most special."),
   ("TOTO", "¡Y mi collar se puede comer!", "And my necklace is edible!")]),
  ("xmas", ["🎄", "✨"], "PIPO TOTO LULA:happy ZUMBI ABU", [
   ("ALL", "¡Ya llega, ya llega la Navidad!", "It's coming, it's coming, Christmas is coming!"),
   ("PIPO", "¡Qué lindo es preparar todo juntos!", "Getting ready together is the best!")]),
 ]),
]
