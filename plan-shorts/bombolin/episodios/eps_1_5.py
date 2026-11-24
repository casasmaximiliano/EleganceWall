# Temporada 1 «Bombolín descubre el mundo»: episodios 1 a 5.
# Escena: (fondo, [emojis de utilería], "reparto en escena", [(personaje, ES, EN), ...])
# Personajes: PIPO (= Bombolín), TOTO, LULA[:ánimo], ZUMBI, ABU, ALL (todos), G:<invitado>.
# El inicio (presentación), el cierre (álbum + «Hoy aprendimos» + rima) y el anticipo se agregan solos.

EPS_A = [
dict(n=1, slug="huevo-gigante",
 tes="Bombolín encuentra un huevo gigante", ten="Bombolín Finds a Giant Egg",
 sticker="🥚", ces="¿Qué hay dentro del huevo?", cen="What's inside the egg?",
 les="todos los bebés necesitan cuidado", len="every baby needs care",
 dato_es="El avestruz pone el huevo más grande de todas las aves: pesa alrededor de 1,4 kg.",
 dato_en="The ostrich lays the biggest egg of any bird: about 1.4 kg (3 lb).",
 fuente="San Diego Zoo Wildlife Alliance, «Ostrich».",
 sum_es="Bombolín encuentra un huevo enorme en el bosque. Con Toto y Abu Tortu buscan a su mamá… ¡y descubren quién estaba adentro!",
 sum_en="Bombolín finds a huge egg in the forest. With Toto and Grandma Tortu he looks for its mom… and finds out who was inside!",
 thumb=dict(em="🥚", t1_es="¡HUEVO GIGANTE!", t1_en="GIANT EGG!", t2_es="¿QUIÉN ESTÁ ADENTRO?", t2_en="WHO'S INSIDE?", chars=["PIPO", "TOTO"]),
 shorts=[(0, 1, "¡UN HUEVO GIGANTE!", "A GIANT EGG!"), (6, 7, "¡NACIÓ!", "IT HATCHED!")],
 s=[
  ("meadow", ["🥚", "🌳"], "PIPO", [
   ("PIPO", "¡Wiii! ¡Miren! ¡Un huevo gigante!", "Wheee! Look! A giant egg!"),
   ("PIPO", "¡Es más grande que yo!", "It's bigger than me!")]),
  ("meadow", ["🥚", "🌸"], "PIPO TOTO", [
   ("TOTO", "¡Uy, uy, uy! ¿Es una pelota? ¡Juguemos!", "Uh-oh, uh-oh! Is it a ball? Let's play!"),
   ("PIPO", "¡No, Toto! Es un huevo. Hay que tratarlo con cuidado.", "No, Toto! It's an egg. We have to be careful with it."),
   ("TOTO", "¿Y de quién es?", "And whose is it?"),
   ("PIPO", "No sé… ¡pero su mamá debe estar buscándolo!", "I don't know… but its mom must be looking for it!")]),
  ("meadow", ["🥚", "🏡"], "PIPO TOTO G:Gallina", [
   ("PIPO", "Doña Gallina, ¿este huevo es suyo?", "Mrs. Hen, is this egg yours?"),
   ("G:Gallina", "¡Cocoró! ¡No, no! Mis huevitos son chiquititos.", "Cluck, cluck! No, no! My eggs are teeny-tiny."),
   ("TOTO", "¡Uy! Uno chiquito… ¡y uno enorme!", "Uh-oh! One tiny egg… and one HUGE egg!")]),
  ("meadow", ["🥚", "💧"], "PIPO TOTO G:Mamá_Cocodrilo", [
   ("PIPO", "Señora Cocodrilo, ¿este huevo es suyo?", "Mrs. Crocodile, is this egg yours?"),
   ("G:Mamá_Cocodrilo", "No, pequeño. Mis huevos están en mi nido, y yo los cuido.", "No, little one. My eggs are in my nest, and I take care of them."),
   ("PIPO", "Entonces… ¿de quién será?", "Then… whose could it be?")]),
  ("board", ["🥚", "🦕"], "PIPO ABU", [
   ("PIPO", "¡Abu Tortu! Encontramos un huevo y nadie sabe de quién es.", "Grandma Tortu! We found an egg and nobody knows whose it is."),
   ("ABU", "Mis amores, ¡qué hallazgo! Los dinosaurios también nacían de huevos, como tú, Bombolín.", "My little loves, what a find! Dinosaurs hatched from eggs too, just like you, Bombolín."),
   ("ABU", "Pero este es tan grande… que solo puede ser de un ave muy, muy grande.", "But this one is so big… it can only belong to a very, very big bird.")]),
  ("meadow", ["🥚"], "PIPO TOTO ABU", [
   ("TOTO", "¡Escuchen! ¡El huevo hace pip, pip!", "Listen! The egg goes peep, peep!"),
   ("PIPO", "¡Se está moviendo!", "It's moving!"),
   ("ALL", "¡Uno, dos, tres!", "One, two, three!")]),
  ("meadow", ["🐣", "✨"], "PIPO TOTO ABU G:Avestruz_bebé", [
   ("G:Avestruz_bebé", "¿Pío?", "Peep?"),
   ("PIPO", "¡Hola, amiguito! ¡Bienvenido al mundo!", "Hello, little friend! Welcome to the world!"),
   ("TOTO", "¡Uy, qué patas tan largas!", "Uh-oh, what long legs!")]),
  ("meadow", ["🪶", "💛"], "PIPO TOTO ABU G:Mamá_Avestruz", [
   ("G:Mamá_Avestruz", "¡Mi bebé! ¡Gracias por cuidarlo!", "My baby! Thank you for looking after it!"),
   ("ABU", "¡Es un avestruz! El avestruz pone el huevo más grande de todas las aves: pesa como veinticuatro huevos de gallina.", "It's an ostrich! The ostrich lays the biggest egg of any bird: it weighs as much as twenty-four chicken eggs."),
   ("PIPO", "¡Cuidar a otros me hace muy feliz!", "Taking care of others makes me so happy!")]),
 ]),

dict(n=2, slug="no-quiero-banarme",
 tes="¡Toto no quiere bañarse!", ten="Toto Doesn't Want a Bath!",
 sticker="🛁", ces="¿Quién se baña en barro?", cen="Who takes a mud bath?",
 les="bañarnos nos mantiene limpios y sanos", len="taking a bath keeps us clean and healthy",
 dato_es="Los elefantes se cubren de barro para protegerse del sol y de los insectos.",
 dato_en="Elephants cover themselves in mud to protect their skin from the sun and bugs.",
 fuente="Smithsonian's National Zoo, «Asian elephant».",
 sum_es="Toto está lleno de manchas, pero no quiere bañarse. Un elefante le muestra su baño favorito… ¡de barro!",
 sum_en="Toto is covered in messy spots, but he doesn't want a bath. An elephant shows him his favorite bath… a mud bath!",
 thumb=dict(em="🛁", t1_es="¡NO AL BAÑO!", t1_en="NO BATH!", t2_es="¡BAÑO DE BARRO!", t2_en="MUD BATH!", chars=["TOTO", "PIPO"]),
 shorts=[(0, 1, "¡NO QUIERO BAÑARME!", "NO BATH!"), (4, 5, "¡BAÑO DE BARRO!", "MUD BATH!")],
 s=[
  ("room", ["🧽", "🫧"], "TOTO", [
   ("TOTO", "¡Uy, uy, uy! ¡Una esponja! ¡No quiero bañarme!", "Uh-oh, uh-oh! A sponge! I don't want a bath!"),
   ("TOTO", "¡Me escondo debajo de la cama!", "I'll hide under the bed!")]),
  ("room", ["🍝", "🧦"], "PIPO TOTO", [
   ("PIPO", "Toto, tienes salsa en el pelo… y una media pegada.", "Toto, you have sauce in your fur… and a sock stuck on you."),
   ("TOTO", "¡Así estoy bien! El agua moja.", "I'm fine like this! Water is wet."),
   ("PIPO", "Jaja, ¡claro que moja!", "Ha ha, of course it's wet!")]),
  ("meadow", ["🪰", "🍝"], "PIPO TOTO", [
   ("TOTO", "Uy… ¿por qué me siguen las moscas?", "Uh-oh… why are flies following me?"),
   ("PIPO", "¡Porque hueles a fideos con salsa!", "Because you smell like spaghetti!"),
   ("TOTO", "¡Mmm, fideos!", "Mmm, spaghetti!")]),
  ("meadow", ["🌊", "🌴"], "PIPO TOTO", [
   ("PIPO", "Vamos al río. Quizás te guste bañarte con amigos.", "Let's go to the river. Maybe you'll like a bath with friends."),
   ("TOTO", "Bueno… pero solo a mirar.", "Okay… but just to look.")]),
  ("meadow", ["🐘", "🟤"], "PIPO TOTO G:Elefante", [
   ("G:Elefante", "¡Hola! ¡Hoy me toca mi baño favorito!", "Hello! It's time for my favorite bath!"),
   ("TOTO", "¿Tú también te bañas?", "You take baths too?"),
   ("G:Elefante", "¡Claro! ¡Me tiro barro con la trompa! ¡Splash!", "Of course! I spray mud with my trunk! Splash!")]),
  ("board", ["🐘", "☀"], "PIPO ABU", [
   ("ABU", "Los elefantes se cubren de barro para protegerse del sol y de los bichitos. Es su manera de cuidarse.", "Elephants cover themselves in mud to protect their skin from the sun and bugs. It's how they take care of themselves."),
   ("PIPO", "¡Y nosotros nos cuidamos con agua y jabón!", "And we take care of ourselves with soap and water!")]),
  ("room", ["🛁", "🫧"], "PIPO TOTO", [
   ("TOTO", "Bueno… voy a probar. ¡Pero con muchas burbujas!", "Okay… I'll try it. But with lots of bubbles!"),
   ("ALL", "¡Burbujas, burbujas, qué lindo es bañarse!", "Bubbles, bubbles, bath time is fun!"),
   ("TOTO", "¡Uy, uy, uy! ¡Me encanta!", "Uh-oh, uh-oh! I love it!")]),
  ("room", ["✨", "🧦"], "PIPO TOTO", [
   ("PIPO", "¡Toto, estás brillante!", "Toto, you're so shiny!"),
   ("TOTO", "¡Y encontré mi otra media!", "And I found my other sock!")]),
 ]),

dict(n=3, slug="lula-y-la-tormenta",
 tes="Lula tiene miedo de la tormenta", ten="Lula Is Scared of the Storm",
 sticker="🌈", ces="¿Cómo se hace un arcoíris?", cen="How is a rainbow made?",
 les="cuando tenemos miedo, ayuda estar con alguien", len="when we're scared, it helps to be with someone",
 dato_es="El sonido del trueno tarda unos 3 segundos en recorrer 1 kilómetro. Contando los segundos se sabe si la tormenta se aleja.",
 dato_en="Thunder takes about 3 seconds to travel 1 kilometer. Counting the seconds tells you if the storm is moving away.",
 fuente="NOAA National Weather Service, «Lightning safety».",
 sum_es="Se acerca una tormenta y Lula se asusta mucho. Bombolín le enseña un truco para contar los truenos… ¡y al final aparece un arcoíris!",
 sum_en="A storm is coming and Lula gets very scared. Bombolín teaches her a trick to count the thunder… and at the end a rainbow appears!",
 thumb=dict(em="⚡", t1_es="¡QUÉ MIEDO!", t1_en="SO SCARY!", t2_es="¡ARCOÍRIS!", t2_en="RAINBOW!", chars=["LULA", "PIPO"]),
 shorts=[(1, 3, "¡BUM!", "BOOM!"), (6, 7, "¡UN ARCOÍRIS!", "A RAINBOW!")],
 s=[
  ("meadow", ["🪁", "☀"], "PIPO LULA", [
   ("PIPO", "¡Lula, mira cómo vuela mi cometa!", "Lula, look how high my kite flies!"),
   ("LULA", "¡Qué lindo día!", "What a lovely day!")]),
  ("night", ["⚡", "🌧"], "PIPO LULA:sad", [
   ("LULA", "¡Ay! ¿Qué fue esa luz?", "Oh! What was that light?"),
   ("PIPO", "Es un rayo. Ahora va a sonar el trueno.", "It's lightning. Now the thunder will rumble."),
   ("LULA", "¡Bum! ¡Ay, me asusté mucho!", "Boom! Oh, that scared me so much!")]),
  ("room", ["🪟", "🧸"], "PIPO LULA:sad", [
   ("PIPO", "Vamos adentro. Aquí estamos seguros.", "Let's go inside. We're safe in here."),
   ("LULA", "Me tiemblan las gotitas…", "My little raindrops are shaking…"),
   ("PIPO", "Tranquila, Lula. Yo estoy contigo.", "It's okay, Lula. I'm right here with you.")]),
  ("room", ["⚡", "🔢"], "PIPO LULA:sad", [
   ("PIPO", "Te enseño un truco. Cuando veas la luz, contamos.", "Let me teach you a trick. When you see the light, we count."),
   ("ALL", "¡Uno… dos… tres… cuatro… cinco…!", "One… two… three… four… five…!"),
   ("LULA", "¡Bum! Pero sonó más bajito.", "Boom! But it sounded quieter.")]),
  ("board", ["⚡", "📏"], "PIPO ABU", [
   ("ABU", "¡Muy bien! El sonido del trueno tarda unos tres segundos en recorrer un kilómetro.", "Very good! The sound of thunder takes about three seconds to travel one kilometer."),
   ("ABU", "Si cada vez cuentan más números, la tormenta se está yendo.", "If you count higher each time, the storm is going away."),
   ("ABU", "Y recuerden: con tormenta, nos quedamos adentro.", "And remember: in a storm, we stay inside.")]),
  ("room", ["⚡", "🧸"], "PIPO LULA:calm", [
   ("ALL", "¡Uno, dos, tres, cuatro, cinco, seis, siete, ocho!", "One, two, three, four, five, six, seven, eight!"),
   ("LULA", "¡Se está yendo! ¡Ya casi no tengo miedo!", "It's going away! I'm hardly scared anymore!")]),
  ("meadow", ["🌈", "☀"], "PIPO LULA:happy", [
   ("PIPO", "¡Salió el sol! ¡Miren el cielo!", "The sun came out! Look at the sky!"),
   ("LULA", "¡Un arcoíris! ¿Cómo se hace?", "A rainbow! How is it made?"),
   ("ABU", "La luz del sol entra en las gotitas de agua y se separa en colores.", "Sunlight goes into tiny drops of water and splits into colors.")]),
  ("meadow", ["🌈", "🪁"], "PIPO LULA:happy", [
   ("LULA", "¡Entonces mis gotitas ayudan a hacer arcoíris!", "So my little drops help make rainbows!"),
   ("PIPO", "¡Eres una nube muy especial, Lula!", "You're a very special cloud, Lula!")]),
 ]),

dict(n=4, slug="la-gran-carrera",
 tes="La gran carrera de Zumbi", ten="Zumbi's Big Race",
 sticker="🏁", ces="¿Quién gana la carrera?", cen="Who wins the race?",
 les="llegar juntos es el mejor premio", len="getting there together is the best prize",
 dato_es="El guepardo es el animal terrestre más rápido: puede superar los 90 km/h, pero solo en carreras cortas.",
 dato_en="The cheetah is the fastest land animal: it can run faster than 90 km/h (55 mph), but only for short sprints.",
 fuente="Smithsonian's National Zoo, «Cheetah».",
 sum_es="Zumbi quiere ganar la Gran Carrera de las Flores a toda costa. Pero en el camino aprende que ayudar a un amigo vale más que una medalla.",
 sum_en="Zumbi wants to win the Great Flower Race no matter what. But along the way he learns that helping a friend is worth more than a medal.",
 thumb=dict(em="🏁", t1_es="¡A CORRER!", t1_en="READY, GO!", t2_es="¿QUIÉN GANA?", t2_en="WHO WINS?", chars=["ZUMBI", "ABU"]),
 shorts=[(1, 2, "¡EN SUS MARCAS…!", "ON YOUR MARKS…!"), (3, 4, "¡FIUUUM!", "WHOOOSH!")],
 s=[
  ("meadow", ["🏁", "🌸"], "PIPO ZUMBI", [
   ("ZUMBI", "¡Zzzí! ¡Hoy es la Gran Carrera de las Flores! ¡Voy a ganar!", "Bzzz, yes! Today is the Great Flower Race! I'm going to win!"),
   ("PIPO", "¡Yo también voy a correr!", "I'm going to run too!")]),
  ("meadow", ["🏁", "🐞"], "PIPO ZUMBI ABU", [
   ("ABU", "En sus marcas… listos…", "On your marks… get set…"),
   ("ZUMBI", "¡Fiuuum!", "Whoooosh!"),
   ("PIPO", "¡Zumbi! ¡Todavía no dijeron «ya»!", "Zumbi! She didn't say go yet!"),
   ("ZUMBI", "Ups… perdón. Vuelvo a la línea.", "Oops… sorry. I'll go back to the line.")]),
  ("meadow", ["🏁", "🌼"], "PIPO ZUMBI ABU TOTO", [
   ("ABU", "En sus marcas, listos… ¡ya!", "On your marks, get set… go!"),
   ("TOTO", "¡Uy, uy, uy! ¡Mis pies se enredaron!", "Uh-oh, uh-oh! My feet got tangled!")]),
  ("meadow", ["🐆", "💨"], "PIPO ZUMBI G:Guepardo", [
   ("G:Guepardo", "¡Permiso! ¡Fiuuum!", "Excuse me! Whoosh!"),
   ("ZUMBI", "¿Quién fue ese? ¡Corre rapidísimo!", "Who was that? He runs super fast!"),
   ("G:Guepardo", "Soy el guepardo. Corro muy rápido… ¡pero me canso enseguida!", "I'm the cheetah. I run really fast… but I get tired quickly!")]),
  ("board", ["🐆", "🚗"], "PIPO ABU", [
   ("ABU", "El guepardo es el animal terrestre más rápido. ¡Puede correr más rápido que un auto en la ciudad!", "The cheetah is the fastest land animal. It can run faster than a car in the city!"),
   ("ABU", "Pero solo un ratito. Después necesita descansar.", "But only for a little while. Then it needs to rest.")]),
  ("meadow", ["🐞", "🍃"], "PIPO ZUMBI", [
   ("ZUMBI", "¡Ahí voy, voy a ganar!", "Here I go, I'm going to win!"),
   ("ZUMBI", "Esperen… ¿Quién llora? ¡Es una mariquita que se cayó!", "Wait… Who's crying? It's a ladybug who fell down!"),
   ("ZUMBI", "¡Te ayudo, mariquita! ¡Arriba!", "I'll help you, ladybug! Up you go!")]),
  ("meadow", ["🐢", "🍃"], "PIPO ZUMBI ABU", [
   ("ZUMBI", "Ahora voy a llegar último…", "Now I'm going to come in last…"),
   ("ABU", "Yo siempre llego última… ¡y siempre llego! Vamos juntos, paso a paso.", "I always come in last… and I always get there! Let's go together, step by step."),
   ("PIPO", "¡Juntos!", "Together!")]),
  ("meadow", ["🏁", "🎉"], "PIPO ZUMBI ABU TOTO LULA:happy", [
   ("ALL", "¡Llegamos!", "We made it!"),
   ("LULA", "¡Llegaron todos juntos!", "You all finished together!"),
   ("ZUMBI", "¡Zzzí! ¡Es la mejor carrera de todas!", "Bzzz, yes! It's the best race ever!")]),
 ]),

dict(n=5, slug="el-cepillo-perdido",
 tes="¿Dónde está el cepillo de Toto?", ten="Where Is Toto's Toothbrush?",
 sticker="🪥", ces="¿Dónde estaba el cepillo?", cen="Where was the toothbrush?",
 les="cepillarse los dientes los mantiene fuertes", len="brushing keeps our teeth strong",
 dato_es="Se recomienda cepillarse los dientes dos veces al día, durante dos minutos. Los niños tienen 20 dientes de leche.",
 dato_en="Brush your teeth twice a day for two minutes. Kids have 20 baby teeth.",
 fuente="American Dental Association, «Brushing your teeth» y «Baby teeth».",
 sum_es="Es hora de dormir, pero Toto no encuentra su cepillo de dientes. Juntos lo buscan por toda la casa… ¡y cantan la canción del cepillo!",
 sum_en="It's bedtime, but Toto can't find his toothbrush. Together they search the whole house… and sing the toothbrush song!",
 thumb=dict(em="🪥", t1_es="¿Y MI CEPILLO?", t1_en="MY TOOTHBRUSH?", t2_es="¡A CEPILLARSE!", t2_en="BRUSH TIME!", chars=["TOTO", "PIPO"]),
 shorts=[(0, 1, "¿Y MI CEPILLO?", "WHERE'S MY TOOTHBRUSH?"), (6, 7, "¡CHIKI-CHIKI-BRILLA!", "SCRUB-A-DUB-SHINE!")],
 s=[
  ("room", ["🪥", "🌙"], "PIPO TOTO", [
   ("PIPO", "¡Hora de cepillarse los dientes!", "Time to brush our teeth!"),
   ("TOTO", "¡Uy, uy, uy! ¿Dónde está mi cepillo?", "Uh-oh, uh-oh! Where's my toothbrush?")]),
  ("room", ["🧸", "🧦"], "PIPO TOTO", [
   ("PIPO", "¿Lo dejaste en tu caja de juguetes?", "Did you leave it in your toy box?"),
   ("TOTO", "Mmm… aquí hay un auto, un peluche, una media… ¡pero no el cepillo!", "Hmm… here's a car, a teddy, a sock… but no toothbrush!")]),
  ("room", ["🍪", "🥛"], "PIPO TOTO", [
   ("PIPO", "¿Y en la cocina?", "What about the kitchen?"),
   ("TOTO", "¡Encontré una galletita!", "I found a cookie!"),
   ("PIPO", "¡Toto! ¡Antes de dormir no se comen galletitas!", "Toto! No cookies right before bed!")]),
  ("room", ["🦷", "🔢"], "PIPO TOTO ABU", [
   ("ABU", "¿Qué buscan, mis amores?", "What are you looking for, my little loves?"),
   ("TOTO", "Mi cepillo. Mis dientes quieren brillar.", "My toothbrush. My teeth want to shine."),
   ("ABU", "¿Sabían que los niños tienen veinte dientes de leche? ¡Hay que cuidar cada uno!", "Did you know kids have twenty baby teeth? We need to take care of every one!")]),
  ("board", ["🦷", "⏳"], "PIPO ABU", [
   ("ABU", "Hay que cepillarse dos veces al día: a la mañana y a la noche.", "Brush twice a day: in the morning and at night."),
   ("ABU", "¡Y durante dos minutos! Como dos canciones cortitas.", "And for two minutes! Like two short songs.")]),
  ("room", ["🪥", "🧦"], "PIPO TOTO", [
   ("PIPO", "Toto… ¿qué tienes ahí en el pelo?", "Toto… what's that in your fur?"),
   ("TOTO", "¡Mi cepillo! ¡Estaba pegado al lado de mi media!", "My toothbrush! It was stuck next to my sock!"),
   ("PIPO", "¡Jajaja!", "Ha ha ha!")]),
  ("room", ["🪥", "🫧"], "PIPO TOTO", [
   ("ALL", "Arriba, abajo, chiki-chiki-brilla, dos minutos, ¡sí!, mañana y noche, ¡sí!", "Up and down, scrub-a-dub-shine, two minutes, yes! Morning and night, yes!"),
   ("TOTO", "¡Uy, uy, cuántas burbujas!", "Uh-oh, so many bubbles!")]),
  ("night", ["✨", "🦷"], "PIPO TOTO", [
   ("TOTO", "¡Mira qué sonrisa brillante!", "Look at my shiny smile!"),
   ("PIPO", "Y ahora tu cepillo va en su vasito, ¡para encontrarlo mañana!", "And now your toothbrush goes in its cup, so you can find it tomorrow!")]),
 ]),
]
