# ============================================================
# BLIP ENGLISH TRAINER v3.0 — 1-QISM
# Fayl: blip_trainer_1.py
# Offline • Terminal rejimi • 30 so'z/kun • 60 kunlik reja
# ============================================================
import os, json, random, datetime, time

G = "\033[92m"; Y = "\033[93m"; R = "\033[91m"
B = "\033[94m"; C = "\033[96m"; W = "\033[97m"; RST = "\033[0m"

# ---------- 1-QISM SO'ZLAR BAZASI (210 ta) ----------
# Format: Kategoriya|English|Uzbek|Talaffuz
WORDS_DATA = """
Asosiy|hello|salom|he-LOU
Asosiy|goodbye|xayr|gud-BAY
Asosiy|yes|ha|yes
Asosiy|no|yo'q|nou
Asosiy|please|iltimos|pliiz
Asosiy|thanks|rahmat|thenks
Asosiy|sorry|kechirasiz|SO-ri
Asosiy|help|yordam|help
Asosiy|water|suv|VO-ter
Asosiy|food|ovqat|fuud
Asosiy|friend|do'st|frend
Asosiy|family|oila|FE-mi-li
Asosiy|house|uy|haus
Asosiy|school|maktab|skuul
Asosiy|book|kitob|buk
Asosiy|pen|qalam|pen
Asosiy|car|mashina|kaar
Asosiy|phone|telefon|foun
Asosiy|time|vaqt|taym
Asosiy|day|kun|dey
Asosiy|night|tun|nayt
Asosiy|morning|ertalab|MOR-ning
Asosiy|evening|kechqurun|IIV-ning
Asosiy|today|bugun|tu-DEY
Asosiy|tomorrow|ertaga|tu-MO-rou
Asosiy|yesterday|kecha|YES-ter-dey
Asosiy|week|hafta|viik
Asosiy|month|oy|manth
Asosiy|year|yil|yir
Asosiy|hour|soat|AU-er
Asosiy|minute|daqiqa|MI-nit
Asosiy|second|soniya|SE-kond
Asosiy|always|har doim|OL-veyz
Asosiy|never|hech qachon|NE-ver
Asosiy|sometimes|ba'zan|SAM-taymz
Asosiy|often|tez-tez|OF-n
Asosiy|now|hozir|nau
Asosiy|later|keyinroq|LEY-ter
Asosiy|here|bu yerda|hiir
Asosiy|there|u yerda|veir
Asosiy|what|nima|vot
Asosiy|who|kim|huu
Asosiy|where|qayerda|veir
Asosiy|when|qachon|ven
Asosiy|why|nima uchun|vay
Asosiy|how|qanday|hau
Asosiy|this|bu|this
Asosiy|that|u|that
Asosiy|these|bular|thiiz
Asosiy|those|ular|thouz
Tanishuv|My name is Blip|Mening ismim Blip|may neym iz Blip
Tanishuv|What is your name?|Ismingiz nima?|vot iz yor neym
Tanishuv|How are you?|Qalaysiz?|hau ar yu
Tanishuv|I am fine|Men yaxshiman|ay em fayn
Tanishuv|Nice to meet you|Tanishganimdan xursandman|nays tu miit yu
Tanishuv|Where are you from?|Qayerdansiz?|veir ar yu from
Tanishuv|I am from Tajikistan|Men Tojikistondanman|ay em from Ta-ji-ki-stan
Tanishuv|I am 13 years old|Men 13 yoshdaman|ay em ther-tiin yirz ould
Tanishuv|I am a programmer|Men dasturchiman|ay em e prou-gram-mer
Tanishuv|I am a cyber athlete|Men kiber-atletman|ay em e say-ber ath-liit
Tanishuv|I use Pydroid 3|Men Pydroid 3 ishlataman|ay yuz Pydroid thrii
Tanishuv|I use Termux|Men Termux ishlataman|ay yuz Termux
Tanishuv|Good morning|Xayrli tong|gud MOR-ning
Tanishuv|Good afternoon|Xayrli kun|gud af-ter-NUUN
Tanishuv|Good evening|Xayrli kech|gud IIV-ning
Tanishuv|Good night|Xayrli tun|gud nayt
Tanishuv|See you later|Keyin ko'rishguncha|sii yu LEY-ter
Tanishuv|Have a nice day|Yaxshi kun tilayman|hav e nays dey
Tanishuv|Welcome|Xush kelibsiz|VEL-kam
Tanishuv|Excuse me|Kechirasiz|eks-KYUZ mi
Tanishuv|I don't understand|Men tushunmayapman|ay dount an-der-STAND
Tanishuv|Can you help me?|Menga yordam bera olasizmi?|kan yu help mi
Tanishuv|What is this?|Bu nima?|vot iz this
Tanishuv|How much is it?|Bu qancha turadi?|hau mach iz it
Tanishuv|Thank you very much|Katta rahmat|thenk yu VE-ri mach
Tanishuv|You are welcome|Arzimaydi|yu ar VEL-kam
Tanishuv|I am sorry|Kechirasiz|ay em SO-ri
Tanishuv|No problem|Muammo yo'q|nou PROB-lem
Tanishuv|Of course|Albatta|ov kors
Tanishuv|Maybe|Balki|MEY-bi
Tanishuv|I think so|Men shunday deb o'ylayman|ay think sou
Tanishuv|I don't know|Men bilmayman|ay dount nou
Tanishuv|Can I ask a question?|Savol bersam maylimi?|kan ay ask e KES-chn
Tanishuv|What does it mean?|Bu nima degani?|vot daz it miin
Tanishuv|How do you say it in English?|Buni inglizcha qanday aytasiz?|hau du yu sey it in ING-lish
Tanishuv|Please speak slowly|Iltimos, sekin gapiring|pliiz spiik SLOW-li
Tanishuv|I am learning English|Men ingliz tilini o'rganyapman|ay em LER-ning ING-lish
Tanishuv|I love programming|Men dasturlashni yaxshi ko'raman|ay lav PRO-gram-ming
Tanishuv|I love Python|Men Pythonni yaxshi ko'raman|ay lav PAY-thon
Tanishuv|I want to be a developer|Men dasturchi bo'lishni xohlayman|ay vont tu bi e di-VE-lo-per
Dasturlash|code|kod|koud
Dasturlash|program|dastur|PRO-gram
Dasturlash|developer|dasturchi|di-VE-lo-per
Dasturlash|computer|kompyuter|kom-PYU-ter
Dasturlash|keyboard|klaviatura|KII-bord
Dasturlash|screen|ekran|skriin
Dasturlash|file|fayl|fayl
Dasturlash|folder|papka|FOUL-der
Dasturlash|error|xato|E-ror
Dasturlash|bug|xatolik|bag
Dasturlash|function|funksiya|FANK-shn
Dasturlash|variable|o'zgaruvchi|VE-ri-a-bl
Dasturlash|loop|sikl|luup
Dasturlash|array|massiv|e-REY
Dasturlash|string|matn|string
Dasturlash|number|son|NAM-ber
Dasturlash|input|kirish|IN-put
Dasturlash|output|chiqish|AUT-put
Dasturlash|server|server|SER-ver
Dasturlash|client|mijoz|KLAY-ent
Dasturlash|database|ma'lumotlar bazasi|DEY-ta-beys
Dasturlash|network|tarmoq|NET-verk
Dasturlash|security|xavfsizlik|si-KYU-ri-ti
Dasturlash|password|parol|PAAS-verd
Dasturlash|hacker|xaker|HE-ker
Dasturlash|internet|internet|IN-ter-net
Dasturlash|python|python|PAY-thon
Dasturlash|android|android|AN-droyd
Dasturlash|terminal|terminal|TER-mi-nl
Dasturlash|browser|brauzer|BRAU-zer
Dasturlash|linux|linux|LI-nuks
Dasturlash|windows|windows|VIN-douz
Dasturlash|software|dasturiy ta'minot|SOFT-veir
Dasturlash|hardware|qurilma|HAARD-veir
Dasturlash|website|veb-sayt|VEB-sayt
Dasturlash|application|ilova|ap-li-KEY-shn
Dasturlash|mobile|mobil|MOU-bayl
Dasturlash|desktop|ish stoli|DESK-top
Dasturlash|backup|zaxira|BAK-ap
Dasturlash|update|yangilash|ap-DEYT
Dasturlash|download|yuklab olish|DAUN-loud
Dasturlash|upload|yuklash|AP-loud
Dasturlash|connect|ulanish|ko-NEKT
Dasturlash|disconnect|uzilish|dis-ko-NEKT
Dasturlash|search|qidirish|serch
Dasturlash|find|topish|faynd
Dasturlash|create|yaratish|kri-EYT
Dasturlash|delete|o'chirish|di-LIIT
Dasturlash|open|ochish|OU-pen
Dasturlash|close|yopish|klouz
AI & Tech|artificial|sun'iy|ar-ti-FI-shl
AI & Tech|intelligence|intellekt|in-TE-li-djens
AI & Tech|machine|mashina|ma-SHIIN
AI & Tech|learning|o'rganish|LER-ning
AI & Tech|neural|neyron|NYU-rel
AI & Tech|data|ma'lumot|DEY-ta
AI & Tech|model|model|MO-del
AI & Tech|training|o'qitish|TREY-ning
AI & Tech|algorithm|algoritm|AL-go-ri-thm
AI & Tech|predict|bashorat|pri-DIKT
AI & Tech|robot|robot|ROU-bot
AI & Tech|future|kelajak|FYU-cher
AI & Tech|smart|aqlli|smaart
AI & Tech|digital|raqamli|DI-dji-tl
AI & Tech|system|tizim|SIS-tem
AI & Tech|agent|agent|EY-djent
AI & Tech|API|API|ey-pi-ay
AI & Tech|token|token|TOU-ken
AI & Tech|prompt|so'rov|prompt
AI & Tech|generate|yaratmoq|DJE-ne-reyt
AI & Tech|chatbot|chat-bot|CHAT-bot
AI & Tech|automation|avtomatlashtirish|au-to-MEY-shn
AI & Tech|cloud|bulut|klaud
AI & Tech|big data|katta ma'lumotlar|big DEY-ta
AI & Tech|deep learning|chuqur o'rganish|diip LER-ning
AI & Tech|computer vision|kompyuter ko'rishi|kom-PYU-ter VI-zhn
AI & Tech|natural language|tabiiy til|NA-chu-rel LANG-gvidj
AI & Tech|virtual|virtual|VER-chu-el
AI & Tech|reality|voqelik|ri-A-li-ti
AI & Tech|cyber|kiber|SAY-ber
Fe'llar|go|bormoq|gou
Fe'llar|come|kelmoq|kam
Fe'llar|see|ko'rmoq|sii
Fe'llar|eat|yemoq|iit
Fe'llar|drink|ichmoq|drink
Fe'llar|read|o'qimoq|riid
Fe'llar|write|yozmoq|rayt
Fe'llar|speak|gapirmoq|spiik
Fe'llar|listen|tinglamoq|LI-sn
Fe'llar|think|o'ylamoq|think
Fe'llar|know|bilmoq|nou
Fe'llar|learn|o'rganmoq|lern
Fe'llar|work|ishlamoq|verk
Fe'llar|play|o'ynamoq|pley
Fe'llar|run|yugurmoq|ran
Fe'llar|sleep|uxlamoq|sliip
Fe'llar|wake|uyg'onmoq|veyk
Fe'llar|start|boshlamoq|staart
Fe'llar|stop|to'xtamoq|stop
Fe'llar|study|o'qimoq|STAD-i
Sifatlar|good|yaxshi|gud
Sifatlar|bad|yomon|bed
Sifatlar|big|katta|big
Sifatlar|small|kichik|smol
Sifatlar|fast|tez|faast
Sifatlar|slow|sekin|slou
Sifatlar|happy|xursand|HE-pi
Sifatlar|sad|xafa|sed
Sifatlar|new|yangi|nyu
Sifatlar|old|eski|ould
Sifatlar|hot|issiq|hot
Sifatlar|cold|sovuq|kould
Sifatlar|easy|oson|II-zi
Sifatlar|hard|qiyin|haard
Sifatlar|strong|kuchli|strong
Sifatlar|beautiful|chiroyli|BYU-ti-fl
Sifatlar|dangerous|xavfli|DEYN-dje-res
Sifatlar|important|muhim|im-POR-tnt
Sifatlar|simple|oddiy|SIM-pl
Sifatlar|complex|murakkab|KOM-pleks
Ranglar|red|qizil|red
Ranglar|blue|ko'k|bluu
Ranglar|green|yashil|griin
Ranglar|yellow|sariq|YE-lou
Ranglar|black|qora|blak
Ranglar|white|oq|vayt
Ranglar|orange|to'q sariq|O-rinj
Ranglar|purple|binafsha|PER-pl
Ranglar|pink|pushti|pink
Ranglar|brown|jigarrang|braun
Ranglar|gray|kulrang|grey
Ranglar|gold|tilla|gould
Ranglar|silver|kumush|SIL-ver
Ranglar|light|yorug'|layt
Ranglar|dark|qorong'i|daark
Ranglar|bright|yorqin|brayt
Ranglar|colorful|rang-barang|KA-lor-ful
Ranglar|rainbow|kamalak|REYN-bou
Ranglar|transparent|shaffof|trans-PE-rent
Ranglar|black and white|oq-qora|blak and vayt
Raqamlar|one|bir|van
Raqamlar|two|ikki|tuu
Raqamlar|three|uch|thrii
Raqamlar|four|to'rt|for
Raqamlar|five|besh|fayv
Raqamlar|six|olti|siks
Raqamlar|seven|yetti|SE-ven
Raqamlar|eight|sakkiz|eyt
Raqamlar|nine|to'qqiz|nayn
Raqamlar|ten|o'n|ten
Raqamlar|eleven|o'n bir|i-LE-ven
Raqamlar|twelve|o'n ikki|tvelv
Raqamlar|thirteen|o'n uch|ther-TIIN
Raqamlar|fourteen|o'n to'rt|for-TIIN
Raqamlar|fifteen|o'n besh|fif-TIIN
Raqamlar|sixteen|o'n olti|siks-TIIN
Raqamlar|seventeen|o'n yetti|se-ven-TIIN
Raqamlar|eighteen|o'n sakkiz|ey-TIIN
Raqamlar|nineteen|o'n to'qqiz|nayn-TIIN
Raqamlar|twenty|yigirma|TVEN-ti
Raqamlar|thirty|o'ttiz|THER-ti
Raqamlar|forty|qirq|FOR-ti
Raqamlar|fifty|ellik|FIF-ti
Raqamlar|sixty|oltmish|SIKS-ti
Raqamlar|seventy|yetmish|SE-ven-ti
Raqamlar|eighty|sakson|EY-ti
Raqamlar|ninety|to'qson|NAYN-ti
Raqamlar|hundred|yuz|HAN-dred
Raqamlar|thousand|ming|TAU-zand
Raqamlar|million|million|MIL-yon
Oila|mother|ona|MA-ther
Oila|father|ota|FAA-ther
Oila|parents|ota-ona|PE-rents
Oila|brother|aka/uka|BRA-ther
Oila|sister|opa/singil|SIS-ter
Oila|grandmother|buvi|GRAN-ma-ther
Oila|grandfather|bobo|GRAN-faa-ther
Oila|son|o'g'il|san
Oila|daughter|qiz|DO-ter
Oila|uncle|amaki/tog'a|AN-kl
Oila|aunt|amma/xola|aant
Oila|cousin|amakivachcha|KAZ-n
Oila|nephew|jiyan (o'g'il)|NEF-yu
Oila|niece|jiyan (qiz)|niis
Oila|husband|er|HAZ-band
Oila|wife|xotin|vayf
Oila|baby|chaqaloq|BEY-bi
Oila|child|bola|chayld
Oila|children|bolalar|CHIL-dren
Oila|family|oila|FE-mi-li
Oila|relative|qarindosh|RE-la-tiv
Oila|twin|egizak|tvin
Oila|married|turmush qurgan|ME-rid
Oila|single|turmush qurmagan|SING-gl
Oila|divorced|ajrashgan|di-VORST
Oila|engaged|unashtirilgan|en-GEYJD
Oila|boyfriend|yigit|BOY-frend
Oila|girlfriend|qiz do'st|GERL-frend
Oila|guest|mehmon|gest
Oila|neighbor|qo'shni|NEY-ber
Tana|head|bosh|hed
Tana|hair|soch|heir
Tana|face|yuz|feys
Tana|eye|ko'z|ay
Tana|ear|quloq|iir
Tana|nose|burun|nouz
Tana|mouth|og'iz|mauth
Tana|tooth|tish|tuuth
Tana|tongue|til|tang
Tana|neck|bo'yin|nek
Tana|shoulder|yelka|SHOUL-der
Tana|arm|qo'l|aarm
Tana|hand|qo'l (panja)|hand
Tana|finger|barmoq|FING-ger
Tana|leg|oyoq|leg
Tana|foot|oyoq (panja)|fut
Tana|knee|tizza|nii
Tana|back|orqa|bak
Tana|chest|ko'krak|chest
Tana|stomach|qorin|STA-mak
Tana|heart|yurak|haart
Tana|brain|miya|breyn
Tana|bone|suyak|boun
Tana|blood|qon|blad
Tana|skin|teri|skin
Tana|muscle|muskul|MAS-l
Tana|nail|tirnoq|neyl
Tana|elbow|tirsak|EL-bou
Tana|wrist|bilak|rist
Tana|ankle|to'piq|AN-kl
Tana|throat|tomoq|throut
Tana|lip|lab|lip
Tana|chin|iyak|chin
Tana|cheek|yonoq|chiik
Tana|forehead|peshana|FOR-hed
Tana|eyebrow|qosh|AY-brau
Tana|eyelash|kiprik|AY-lash
Tana|palm|kaft|paam
Tana|fist|musht|fist
Kiyim|shirt|ko'ylak|shert
Kiyim|t-shirt|futbolka|TII-shert
Kiyim|pants|shim|pants
Kiyim|jeans|jinsi shim|jiinz
Kiyim|shorts|qisqa shim|shorts
Kiyim|skirt|yubka|skert
Kiyim|dress|ko'ylak (ayol)|dres
Kiyim|jacket|kurtka|JA-ket
Kiyim|coat|palto|kout
Kiyim|sweater|sviter|SVE-ter
Kiyim|hat|shapka|hat
Kiyim|cap|kepka|kap
Kiyim|scarf|sharf|skaarf
Kiyim|gloves|qo'lqop|glavz
Kiyim|socks|paypoq|soks
Kiyim|shoes|oyoq kiyim|shuuz
Kiyim|boots|etik|buuts
Kiyim|sandals|sandal|SAN-dlz
Kiyim|belt|kamar|belt
Kiyim|tie|bo'yinbog'|tay
Kiyim|watch|qo'l soati|voch
Kiyim|glasses|ko'zoynak|GLA-siz
Kiyim|ring|uzuk|ring
Kiyim|necklace|marjon|NEK-lis
Kiyim|bracelet|bilaguzuk|BREYS-let
Kiyim|earring|zirak|II-ring
Kiyim|underwear|ichki kiyim|AN-der-veir
Kiyim|swimsuit|cho'milish kiyimi|SVIM-suut
Kiyim|uniform|forma|YU-ni-form
Kiyim|pocket|kissa|PO-ket
Mevalar|apple|olma|A-pl
Mevalar|banana|banan|ba-NAA-na
Mevalar|orange|apelsin|O-rinj
Mevalar|grape|uzum|greyp
Mevalar|watermelon|tarvuz|VO-ter-me-lon
Mevalar|melon|qovun|ME-lon
Mevalar|strawberry|qulupnay|STRO-be-ri
Mevalar|cherry|olcha|CHE-ri
Mevalar|peach|shaftoli|piich
Mevalar|pear|nok|peir
Mevalar|plum|olxo'ri|plam
Mevalar|lemon|limon|LE-mon
Mevalar|lime|laym|laym
Mevalar|mango|mango|MAN-gou
Mevalar|pineapple|ananas|PAYN-a-pl
Mevalar|kiwi|kivi|KII-vi
Mevalar|apricot|o'rik|EY-pri-kot
Mevalar|pomegranate|anor|PO-meg-ra-net
Mevalar|fig|anjir|fig
Mevalar|date|xo'jur|deyt
Mevalar|coconut|kokos|KOU-ko-nat
Mevalar|almond|bodom|AA-mond
Mevalar|walnut|yong'oq|VOL-nat
Mevalar|peanut|yer yong'og'i|PII-nat
Mevalar|raisin|mayiz|REY-zn
Sabzavotlar|potato|kartoshka|po-TEY-tou
Sabzavotlar|tomato|pomidor|to-MEY-tou
Sabzavotlar|onion|piyoz|AN-yon
Sabzavotlar|garlic|sarimsoq|GAAR-lik
Sabzavotlar|carrot|sabzi|KE-rot
Sabzavotlar|cucumber|bodring|KYU-kam-ber
Sabzavotlar|pepper|qalampir|PE-per
Sabzavotlar|cabbage|karam|KA-bij
Sabzavotlar|lettuce|salat bargi|LE-tis
Sabzavotlar|spinach|ismaloq|SPI-nich
Sabzavotlar|broccoli|brokkoli|BRO-ko-li
Sabzavotlar|cauliflower|gulkaram|KO-li-flau-er
Sabzavotlar|eggplant|baqlajon|EG-plaant
Sabzavotlar|pumpkin|qovoq|PAMP-kin
Sabzavotlar|corn|makkajo'xori|korn
Sabzavotlar|bean|loviya|biin
Sabzavotlar|pea|no'xat|pii
Sabzavotlar|mushroom|qo'ziqorin|MASH-ruum
Sabzavotlar|radish|turp|RA-dish
Sabzavotlar|beet|lavlagi|biit
Sabzavotlar|ginger|zanjabil|JIN-jer
Sabzavotlar|parsley|petrushka|PAARS-li
Sabzavotlar|dill|shivit|dil
Sabzavotlar|mint|yalpiz|mint
Sabzavotlar|basil|rayhon|BEY-zl
Ichimliklar|water|suv|VO-ter
Ichimliklar|tea|choy|tii
Ichimliklar|coffee|qahva|KO-fi
Ichimliklar|milk|sut|milk
Ichimliklar|juice|sharbat|juus
Ichimliklar|soda|gazli suv|SOU-da
Ichimliklar|lemonade|limonad|le-mo-NEYD
Ichimliklar|smoothie|smuzi|SMUU-thi
Ichimliklar|hot chocolate|issiq shokolad|hot CHO-ko-let
Ichimliklar|beer|pivo|biir
Ichimliklar|wine|vino|vayn
Ichimliklar|vodka|aroq|VOD-ka
Ichimliklar|whiskey|viski|VIS-ki
Ichimliklar|cocktail|kokteyl|KOK-teyl
Ichimliklar|energy drink|energetik ichimlik|E-ner-dji drink
Uy|room|xona|ruum
Uy|kitchen|oshxona|KICH-en
Uy|bedroom|yotoqxona|BED-ruum
Uy|bathroom|hammom|BATH-ruum
Uy|living room|mehmonxona|LI-ving ruum
Uy|door|eshik|dor
Uy|window|deraza|VIN-dou
Uy|wall|devor|vol
Uy|floor|pol|flor
Uy|ceiling|shift|SII-ling
Uy|roof|tom|ruuf
Uy|garden|bog'|GAAR-dn
Uy|garage|garaj|ga-RAAJ
Uy|stairs|zinapoya|steirz
Uy|table|stol|TEY-bl
Uy|chair|stul|cheir
Uy|bed|karavot|bed
Uy|sofa|divan|SOU-fa
Uy|lamp|chiroq|lamp
Uy|mirror|oyna|MI-rer
Uy|clock|soat|klok
Uy|carpet|gilam|KAAR-pet
Uy|curtain|parda|KER-tn
Uy|pillow|yostiq|PI-lou
Uy|blanket|ko'rpa|BLAN-ket
Uy|sheet|choyshab|shiit
Uy|towel|sochiq|TAU-el
Uy|cupboard|shkaf|KAB-ord
Uy|shelf|polka|shelf
Uy|drawer|tortma|DRO-er
Oshxona|plate|likop|pleyt
Oshxona|spoon|qoshiq|spuun
Oshxona|fork|vilka|fork
Oshxona|knife|pichoq|nayf
Oshxona|cup|piyola|kap
Oshxona|glass|stakan|glaas
Oshxona|bowl|kosa|boul
Oshxona|pot|qozon|pot
Oshxona|pan|tova|pan
Oshxona|oven|pech|A-ven
Oshxona|fridge|muzlatgich|frij
Oshxona|stove|plita|stouv
Oshxona|sink|rakovina|sink
Oshxona|bottle|shisha|BO-tl
Oshxona|kettle|choynak|KE-tl
Oshxona|teapot|choydamlagich|TII-pot
Oshxona|napkin|salfetka|NAP-kin
Oshxona|jar|banka|jaar
Oshxona|can|konserva|kan
Oshxona|tray|patnis|trey
Oshxona|cutting board|kesish taxtasi|KA-ting bord
Oshxona|microwave|mikroto'lqinli pech|MAY-kro-veyv
Oshxona|blender|blender|BLEN-der
Oshxona|dishwasher|idish yuvish mashinasi|DISH-vo-sher
Oshxona|recipe|retsept|RE-si-pi
Ovqat|rice|guruch|rays
Ovqat|bread|non|bred
Ovqat|meat|go'sht|miit
Ovqat|chicken|tovuq|CHI-kin
Ovqat|beef|mol go'shti|biif
Ovqat|lamb|qo'zi go'shti|lam
Ovqat|fish|baliq|fish
Ovqat|egg|tuxum|eg
Ovqat|cheese|pishloq|chiiz
Ovqat|butter|sariyog'|BA-ter
Ovqat|oil|yog'|oyl
Ovqat|salt|tuz|solt
Ovqat|sugar|shakar|SHU-ger
Ovqat|flour|un|flau-er
Ovqat|honey|asal|HA-ni
Ovqat|soup|sho'rva|suup
Ovqat|salad|salat|SA-lad
Ovqat|pizza|pitsa|PIIT-sa
Ovqat|burger|burger|BER-ger
Ovqat|sandwich|sendvich|SAND-vich
Ovqat|pasta|makaron|PAAS-ta
Ovqat|noodle|lapsha|NUU-dl
Ovqat|cake|tort|keyk
Ovqat|cookie|pechene|KU-ki
Ovqat|chocolate|shokolad|CHO-ko-let
Shahar|city|shahar|SI-ti
Shahar|town|shaharcha|taun
Shahar|village|qishloq|VI-lij
Shahar|street|ko'cha|striit
Shahar|road|yo'l|roud
Shahar|avenue|shoh ko'cha|A-ve-nyu
Shahar|square|maydon|skveir
Shahar|park|park|paark
Shahar|building|bino|BIL-ding
Shahar|apartment|kvartira|a-PAART-ment
Shahar|office|ofis|O-fis
Shahar|shop|do'kon|shop
Shahar|market|bozor|MAAR-ket
Shahar|supermarket|supermarket|SUU-per-maar-ket
Shahar|mall|savdo markazi|mol
Shahar|bank|bank|bank
Shahar|hospital|kasalxona|HOS-pi-tl
Shahar|pharmacy|dorixona|FAA-ma-si
Shahar|school|maktab|skuul
Shahar|university|universitet|yu-ni-VER-si-ti
Shahar|library|kutubxona|LAY-bre-ri
Shahar|museum|muzey|myu-ZII
Shahar|theater|teatr|THII-a-ter
Shahar|cinema|kinoteatr|SI-ne-ma
Shahar|restaurant|restoran|RES-to-rant
Shahar|cafe|kafe|ka-FEY
Shahar|hotel|mehmonxona|hou-TEL
Shahar|mosque|masjid|mosk
Shahar|church|cherkov|cherch
Shahar|temple|ibodatxona|TEM-pl
Transport|car|mashina|kaar
Transport|bus|avtobus|bas
Transport|truck|yuk mashinasi|trak
Transport|van|furgon|van
Transport|taxi|taksi|TAK-si
Transport|train|poyezd|treyn
Transport|subway|metro|SAB-vey
Transport|tram|tramvay|tram
Transport|bicycle|velosiped|BAY-si-kl
Transport|motorcycle|mototsikl|MOU-tor-say-kl
Transport|airplane|samolyot|EIR-pleyn
Transport|helicopter|vertolyot|HE-li-kop-ter
Transport|ship|kema|ship
Transport|boat|qayiq|bout
Transport|ferry|parom|FE-ri
Transport|rocket|raketa|RO-ket
Transport|ambulance|tez yordam|AM-byu-lens
Transport|fire truck|o't o'chirish mashinasi|FAY-er trak
Transport|police car|politsiya mashinasi|po-LIIS kaar
Transport|tractor|traktor|TRAK-tor
Transport|wheel|g'ildirak|viil
Transport|tire|shina|TAY-er
Transport|engine|dvigatel|EN-jin
Transport|brake|tormoz|breyk
Transport|steering wheel|rul|STII-ring viil
Transport|seat|o'rindiq|siit
Transport|driver|haydovchi|DRAY-ver
Transport|passenger|yo'lovchi|PA-sen-jer
Transport|ticket|chipta|TI-ket
Transport|station|bekat|STEY-shn
Transport|airport|aeroport|EIR-port
Joylar|home|uy|houm
Joylar|work|ish|verk
Joylar|school|maktab|skuul
Joylar|church|cherkov|cherch
Joylar|hospital|kasalxona|HOS-pi-tl
Joylar|pharmacy|dorixona|FAA-ma-si
Joylar|police station|politsiya bo'limi|po-LIIS STEY-shn
Joylar|post office|pochta|poust O-fis
Joylar|bank|bank|bank
Joylar|library|kutubxona|LAY-bre-ri
Joylar|restaurant|restoran|RES-to-rant
Joylar|hotel|mehmonxona|hou-TEL
Joylar|airport|aeroport|EIR-port
Joylar|train station|poyezd bekati|treyn STEY-shn
Joylar|bus stop|avtobus bekati|bas stop
Joylar|park|park|paark
Joylar|zoo|hayvonot bog'i|zuu
Joylar|museum|muzey|myu-ZII
Joylar|stadium|stadion|STEY-di-om
Joylar|gym|sport zali|jim
Joylar|swimming pool|suzish havzasi|SVIM-ing puul
Joylar|beach|plyaj|biich
Joylar|mountain|tog'|MAUN-tn
Joylar|forest|o'rmon|FO-rest
Joylar|desert|cho'l|DE-zert
Joylar|farm|ferma|faarm
Joylar|factory|zavod|FAK-to-ri
Joylar|construction site|qurilish maydoni|kon-STRAK-shn sayt
Joylar|university|universitet|yu-ni-VER-si-ti
Joylar|kindergarten|bolalar bog'chasi|KIN-der-gaar-tn
Yo'l|north|shimol|north
Yo'l|south|janub|sauth
Yo'l|east|sharq|iist
Yo'l|west|g'arb|vest
Yo'l|left|chap|left
Yo'l|right|o'ng|rayt
Yo'l|up|yuqoriga|ap
Yo'l|down|pastga|daun
Yo'l|straight|to'g'ri|streyt
Yo'l|forward|oldinga|FOR-verd
Yo'l|backward|orqaga|BAK-verd
Yo'l|near|yaqin|niir
Yo'l|far|uzoq|faar
Yo'l|here|bu yerda|hiir
Yo'l|there|u yerda|veir
Yo'l|everywhere|hamma joyda|EV-ri-veir
Yo'l|nowhere|hech qayerda|NOU-veir
Yo'l|somewhere|qayerdadir|SAM-veir
Yo'l|inside|ichkarida|in-SAYD
Yo'l|outside|tashqarida|aut-SAYD
Yo'l|above|tepasida|a-BAV
Yo'l|below|ostida|bi-LOU
Yo'l|between|orasida|bi-TVIIN
Yo'l|behind|orqasida|bi-HAYND
Yo'l|in front of|oldida|in front ov
Yo'l|next to|yonida|nekst tu
Ob-havo|weather|ob-havo|VE-ther
Ob-havo|sun|quyosh|san
Ob-havo|sunny|quyoshli|SA-ni
Ob-havo|rain|yomg'ir|reyn
Ob-havo|rainy|yomg'irli|REY-ni
Ob-havo|snow|qor|snou
Ob-havo|snowy|qorli|SNOU-i
Ob-havo|wind|shamol|vind
Ob-havo|windy|shamolli|VIN-di
Ob-havo|cloud|bulut|klaud
Ob-havo|cloudy|bulutli|KLAU-di
Ob-havo|storm|bo'ron|storm
Ob-havo|thunder|momaqaldiroq|THAN-der
Ob-havo|lightning|chaqmoq|LAYT-ning
Ob-havo|fog|tuman|fog
Ob-havo|foggy|tumanli|FO-gi
Ob-havo|ice|muz|ays
Ob-havo|hot|issiq|hot
Ob-havo|cold|sovuq|kould
Ob-havo|warm|iliq|vorm
Ob-havo|cool|salqin|kuul
Ob-havo|dry|quruq|dray
Ob-havo|wet|ho'l|vet
Ob-havo|humid|nam|HYU-mid
Ob-havo|freezing|muzdek|FRII-zing
Ob-havo|rainbow|kamalak|REYN-bou
Ob-havo|temperature|harorat|TEM-pe-ra-chur
Ob-havo|degree|daraja|di-GRII
Ob-havo|climate|iqlim|KLAY-mit
Ob-havo|season|fasl|SII-zn
Fasllar|spring|bahor|spring
Fasllar|summer|yoz|SA-mer
Fasllar|autumn|kuz|O-tm
Fasllar|fall|kuz (AQSh)|fol
Fasllar|winter|qish|VIN-ter
Fasllar|January|yanvar|JA-nyu-e-ri
Fasllar|February|fevral|FEB-ru-e-ri
Fasllar|March|mart|maarch
Fasllar|April|aprel|EY-pril
Fasllar|May|may|mey
Fasllar|June|iyun|juun
Fasllar|July|iyul|ju-LAY
Fasllar|August|avgust|O-gast
Fasllar|September|sentabr|sep-TEM-ber
Fasllar|October|oktabr|ok-TOU-ber
Fasllar|November|noyabr|no-VEM-ber
Fasllar|December|dekabr|di-SEM-ber
Fasllar|holiday|bayram|HO-li-dey
Fasllar|vacation|ta'til|vey-KEY-shn
Fasllar|birthday|tug'ilgan kun|BERTH-dey
Hayvonlar|dog|it|dog
Hayvonlar|cat|mushuk|kat
Hayvonlar|horse|ot|hors
Hayvonlar|cow|sigir|kau
Hayvonlar|sheep|qo'y|shiip
Hayvonlar|goat|echki|gout
Hayvonlar|pig|cho'chqa|pig
Hayvonlar|chicken|tovuq|CHI-kin
Hayvonlar|rooster|xo'roz|RUU-ster
Hayvonlar|duck|o'rdak|dak
Hayvonlar|goose|g'oz|guus
Hayvonlar|turkey|kurka|TER-ki
Hayvonlar|rabbit|quyon|RA-bit
Hayvonlar|mouse|sichqon|maus
Hayvonlar|rat|kalamush|rat
Hayvonlar|lion|sher|LAY-on
Hayvonlar|tiger|yo'lbars|TAY-ger
Hayvonlar|leopard|qoplon|LE-pard
Hayvonlar|bear|ayiq|beir
Hayvonlar|wolf|bo'ri|vulf
Hayvonlar|fox|tulki|foks
Hayvonlar|deer|kiyik|diir
Hayvonlar|elephant|fil|E-le-fant
Hayvonlar|monkey|maymun|MAN-ki
Hayvonlar|giraffe|zarofat|ji-RAAF
Hayvonlar|zebra|zebra|ZII-bra
Hayvonlar|camel|tuya|KA-mel
Hayvonlar|snake|ilon|sneyk
Hayvonlar|lizard|kaltakesak|LI-zard
Hayvonlar|crocodile|timsoh|KRO-ko-dayl
Hayvonlar|turtle|toshbaqa|TER-tl
Hayvonlar|frog|qurbaqa|frog
Hayvonlar|fish|baliq|fish
Hayvonlar|shark|akula|shaark
Hayvonlar|whale|kit|veyl
Hayvonlar|dolphin|delfin|DOL-fin
Hayvonlar|bird|qush|berd
Hayvonlar|eagle|burgut|II-gl
Hayvonlar|owl|boyqush|aul
Hayvonlar|parrot|to'tiqush|PA-rot
Hayvonlar|pigeon|kabutar|PI-jn
Hayvonlar|sparrow|chumchuq|SPA-rou
Hayvonlar|butterfly|kapalak|BA-ter-flay
Hayvonlar|bee|asalari|bii
Hayvonlar|ant|chumoli|ant
Hayvonlar|spider|o'rgimchak|SPAY-der
Hayvonlar|mosquito|chivin|mos-KII-tou
Hayvonlar|fly|pashsha|flay
Hayvonlar|insect|hasharot|IN-sekt
Hayvonlar|animal|hayvon|A-ni-ml
Tabiat|nature|tabiat|NEY-chur
Tabiat|tree|daraxt|trii
Tabiat|flower|gul|FLAU-er
Tabiat|grass|o't|graas
Tabiat|leaf|barg|liif
Tabiat|root|ildiz|ruut
Tabiat|branch|shox|braanch
Tabiat|seed|urug'|siid
Tabiat|fruit|meva|fruut
Tabiat|vegetable|sabzavot|VEJ-ta-bl
Tabiat|mountain|tog'|MAUN-tn
Tabiat|hill|tepalik|hil
Tabiat|valley|vodiy|VA-li
Tabiat|river|daryo|RI-ver
Tabiat|lake|ko'l|leyk
Tabiat|sea|dengiz|sii
Tabiat|ocean|okean|OU-shn
Tabiat|island|orol|AY-land
Tabiat|beach|plyaj|biich
Tabiat|desert|cho'l|DE-zert
Tabiat|forest|o'rmon|FO-rest
Tabiat|jungle|o'rmon (tropik)|JAN-gl
Tabiat|field|dala|fiild
Tabiat|farm|ferma|faarm
Tabiat|garden|bog'|GAAR-dn
Tabiat|sky|osmon|skay
Tabiat|star|yulduz|staar
Tabiat|moon|oy|muun
Tabiat|sun|quyosh|san
Tabiat|earth|yer|erth
Tabiat|world|dunyo|verld
Tabiat|planet|sayyora|PLA-net
Tabiat|space|fazo|speys
Tabiat|universe|koinot|YU-ni-vers
Tabiat|air|havo|eir
Tabiat|fire|olov|FAY-er
Tabiat|water|suv|VO-ter
Tabiat|earth|tuproq|erth
Tabiat|stone|tosh|stoun
Tabiat|rock|qoya|rok
Tabiat|sand|qum|sand
Tabiat|mud|loy|mad
Tabiat|dust|chang|dast
Tabiat|gold|tilla|gould
Tabiat|silver|kumush|SIL-ver
Tabiat|iron|temir|AY-ern
Tabiat|metal|metall|ME-tl
Tabiat|wood|yog'och|vud
Tabiat|glass|shisha|glaas
Tabiat|plastic|plastik|PLA-stik
Tabiat|paper|qog'oz|PEY-per
Tabiat|energy|energiya|E-ner-dji
Tabiat|light|yorug'lik|layt
Tabiat|shadow|soya|SHA-dou
Tabiat|sound|tovush|saund
Tabiat|silence|sukunat|SAY-lens
O'simliklar|rose|atirgul|rouz
O'simliklar|tulip|lola|TYU-lip
O'simliklar|sunflower|kungaboqar|SAN-flau-er
O'simliklar|daisy|moychechak|DEY-zi
O'simliklar|lily|nilufar|LI-li
O'simliklar|orchid|orkidey|OR-kid
O'simliklar|violet|binafsha|VAY-let
O'simliklar|dandelion|momaqaymoq|DAN-di-lay-on
O'simliklar|tree|daraxt|trii
O'simliklar|oak|eman|ouk
O'simliklar|pine|qarag'ay|payn
O'simliklar|willow|majnuntol|VI-lou
O'simliklar|palm|palma|paam
O'simliklar|bamboo|bambuk|bam-BUU
O'simliklar|grass|o't|graas
O'simliklar|moss|mox|mos
O'simliklar|cactus|kaktus|KAK-tas
O'simliklar|leaf|barg|liif
O'simliklar|branch|shox|braanch
O'simliklar|root|ildiz|ruut
O'simliklar|seed|urug'|siid
Sport|sport|sport|sport
Sport|football|futbol|FUT-bol
Sport|basketball|basketbol|BAAS-ket-bol
Sport|volleyball|voleybol|VO-li-bol
Sport|tennis|tennis|TE-nis
Sport|boxing|boks|BOK-sing
Sport|wrestling|kurash|RES-ling
Sport|swimming|suzish|SVIM-ing
Sport|running|yugurish|RA-ning
Sport|cycling|velosiped uchish|SAY-kling
Sport|judo|dzyudo|JUU-dou
Sport|karate|karate|ka-RAA-ti
Sport|gymnastics|gimnastika|jim-NAAS-tiks
Sport|athletics|atletika|ath-LE-tiks
Sport|chess|shaxmat|ches
Sport|checkers|shashka|CHE-kerz
Sport|team|jamoa|tiim
Sport|player|o'yinchi|PLEY-er
Sport|coach|murabbiy|kouch
Sport|match|o'yin|mach
Sport|game|o'yin|geym
Sport|score|hisob|skor
Sport|goal|gol|goul
Sport|win|g'alaba|vin
Sport|lose|mag'lubiyat|luuz
Sport|draw|durang|dro
Sport|champion|chempion|CHAM-pi-on
Sport|medal|medal|ME-dl
Sport|trophy|kubok|TROU-fi
Sport|record|rekord|RE-kord
Sport|exercise|mashq|EK-ser-sayz
Sport|training|mashg'ulot|TREY-ning
Sport|gym|sport zali|jim
Sport|stadium|stadion|STEY-di-om
Sport|field|maydon|fiild
Sport|ball|to'p|bol
Sport|racket|raketka|RA-ket
Sport|net|to'r|net
Sport|helmet|dubulg'a|HEL-met
Sport|uniform|forma|YU-ni-form
Sport|muscle|muskul|MAS-l
Sport|strength|kuch|strenth
Sport|speed|tezlik|spiid
Sport|endurance|chidamlilik|en-DYU-rans
Sport|flexibility|egiluvchanlik|flek-si-BI-li-ti
Sog'liq|health|sog'liq|helth
Sog'liq|healthy|sog'lom|HEL-thi
Sog'liq|sick|kasal|sik
Sog'liq|illness|kasallik|IL-nes
Sog'liq|disease|kasallik|xato|di-ZIIZ
Sog'liq|pain|og'riq|peyn
Sog'liq|headache|bosh og'rig'i|HED-eyk
Sog'liq|fever|isitma|FII-ver
Sog'liq|cough|yo'tal|kof
Sog'liq|cold|shamollash|kould
Sog'liq|flu|gripp|fluu
Sog'liq|virus|virus|VAY-ras
Sog'liq|infection|infeksiya|in-FEK-shn
Sog'liq|medicine|dori|ME-di-sin
Sog'liq|pill|tabletka|pil
Sog'liq|doctor|shifokor|DOK-ter
Sog'liq|nurse|hamshira|ners
Sog'liq|hospital|kasalxona|HOS-pi-tl
Sog'liq|patient|bemor|PEY-shent
Sog'liq|treatment|davolash|TRIIT-ment
Sog'liq|surgery|operatsiya|SER-je-ri
Sog'liq|vaccine|emlash|vak-SIIN
Sog'liq|blood|qon|blad
Sog'liq|pressure|bosim|PRE-sher
Sog'liq|pulse|puls|pals
Sog'liq|breath|nafas|breth
Sog'liq|sleep|uyqu|sliip
Sog'liq|rest|dam olish|rest
Sog'liq|diet|parhez|DAY-et
Sog'liq|vitamin|vitamin|VAY-ta-min
Sog'liq|protein|protein|PROU-tiin
Sog'liq|calorie|kaloriya|KA-lo-ri
Sog'liq|injury|jarohat|IN-ju-ri
Sog'liq|wound|yara|vuund
Sog'liq|bandage|bint|BAN-dij
Sog'liq|emergency|shoshilinch|i-MER-jen-si
Sog'liq|ambulance|tez yordam|AM-byu-lens
Sog'liq|recovery|tiklanish|ri-KA-ve-ri
Sog'liq|immune|immunitet|i-MYUUN
Hissiyotlar|love|sevgi|lav
Hissiyotlar|hate|nafrat|heyt
Hissiyotlar|happiness|baxt|HA-pi-nes
Hissiyotlar|sadness|xafalik|SAD-nes
Hissiyotlar|anger|g'azab|AN-ger
Hissiyotlar|fear|qo'rquv|fiir
Hissiyotlar|joy|xursandlik|joy
Hissiyotlar|sorrow|qayg'u|SO-rou
Hissiyotlar|surprise|hayrat|ser-PRAYZ
Hissiyotlar|disgust|jirkanish|dis-GAST
Hissiyotlar|trust|ishonch|trast
Hissiyotlar|pride|g'urur|prayd
Hissiyotlar|shame|uyat|sheym
Hissiyotlar|guilt|ayb|gilt
Hissiyotlar|jealousy|rashk|JE-lo-si
Hissiyotlar|hope|umid|houp
Hissiyotlar|faith|iymon|feyth
Hissiyotlar|desire|xohish|di-ZAY-er
Hissiyotlar|boredom|zerikish|BOR-dom
Hissiyotlar|excitement|hayajon|ek-SAYT-ment
Hissiyotlar|calmness|xotirjamlik|KAAM-nes
Hissiyotlar|stress|stress|stres
Hissiyotlar|anxiety|xavotir|ang-ZAY-i-ti
Hissiyotlar|depression|tushkunlik|di-PRE-shn
Hissiyotlar|loneliness|yolg'izlik|LOUN-li-nes
Hissiyotlar|confidence|ishonch|KON-fi-dens
Hissiyotlar|kindness|mehribonlik|KAYND-nes
Hissiyotlar|generosity|saxiylik|je-ne-RO-si-ti
Hissiyotlar|courage|jasorat|KA-rij
Hissiyotlar|patience|sabr|PEY-shens
Hissiyotlar|respect|hurmat|ri-SPEKT
Hissiyotlar|honesty|halollik|O-nes-ti
Hissiyotlar|loyalty|sodiqlik|LOY-al-ti
Hissiyotlar|friendship|do'stlik|FREND-ship
Xarakter|kind|mehribon|kaynd
Xarakter|cruel|shafqatsiz|KRU-el
Xarakter|honest|halol|O-nest
Xarakter|dishonest|yolg'onchi|dis-O-nest
Xarakter|brave|jasur|breyv
Xarakter|coward|qo'rqoq|KAU-ard
Xarakter|smart|aqlli|smaart
Xarakter|stupid|ahmoq|STYU-pid
Xarakter|clever|zukko|KLE-ver
Xarakter|wise|dono|vayz
Xarakter|patient|sabrli|PEY-shent
Xarakter|impatient|sabrsiz|im-PEY-shent
Xarakter|calm|xotirjam|kaam
Xarakter|nervous|asabiy|NER-vos
Xarakter|friendly|do'stona|FREND-li
Xarakter|rude|qo'pol|ruud
Xarakter|polite|odobli|po-LAYT
Xarakter|selfish|xudbin|SEL-fish
Xarakter|generous|saxiy|JE-ne-ros
Xarakter|greedy|ochko'z|GRII-di
Xarakter|lazy|dangasa|LEY-zi
Xarakter|hardworking|mehnatkash|HAARD-ver-king
Xarakter|creative|ijodkor|kri-EY-tiv
Xarakter|curious|qiziquvchan|KYU-ri-os
Xarakter|serious|jiddiy|SII-ri-os
Xarakter|funny|kulgili|FA-ni
Xarakter|quiet|jim|KVAY-et
Xarakter|loud|baqiroq|laud
Xarakter|shy|uyatchan|shay
Xarakter|confident|o'ziga ishongan|KON-fi-dent
Xarakter|humble|kamtar|HAM-bl
Xarakter|proud|mag'rur|praud
Xarakter|jealous|rashkchi|JE-los
Xarakter|optimistic|optimist|op-ti-MIS-tik
Xarakter|pessimistic|pessimist|pe-si-MIS-tik
Harkatlar|walk|yurish|vok
Harkatlar|jump|sakrash|jamp
Harkatlar|run|yugurish|ran
Harkatlar|sit|o'tirish|sit
Harkatlar|stand|turish|stand
Harkatlar|lie|yotish|lay
Harkatlar|climb|chiqish|klaym
Harkatlar|crawl|emaklash|krol
Harkatlar|swim|suzish|svim
Harkatlar|fly|uchish|flay
Harkatlar|dance|raqs tushish|daans
Harkatlar|sing|qo'shiq aytish|sing
Harkatlar|throw|uloqtirish|throu
Harkatlar|catch|tutish|kach
Harkatlar|push|surish|push
Harkatlar|pull|tortish|pul
Harkatlar|carry|ko'tarish|KE-ri
Harkatlar|lift|ko'tarish|lift
Harkatlar|hold|ushlash|hould
Harkatlar|drop|tushirish|drop
Harkatlar|hit|urish|hit
Harkatlar|kick|tepish|kik
Harkatlar|punch|mushtlash|panch
Harkatlar|touch|tegish|tach
Harkatlar|point|ko'rsatish|poynt
Harkatlar|wave|qo'l silkitish|veyv
Harkatlar|clap|qarsak chalish|klaap
Harkatlar|shake|silkitish|sheyk
Harkatlar|bend|egilish|bend
Harkatlar|turn|burilish|tern
Harkatlar|stop|to'xtash|stop
Harkatlar|wait|kutish|veyt
Ish|job|ish|job
Ish|work|mehnat|verk
Ish|career|kasb yo'li|ka-RIIR
Ish|profession|kasb|pro-FE-shn
Ish|occupation|mashg'ulot|o-kyu-PEY-shn
Ish|employee|xodim|em-PLOY-ii
Ish|employer|ish beruvchi|em-PLOY-er
Ish|boss|boshliq|bos
Ish|manager|menejer|MA-ni-jer
Ish|worker|ishchi|VER-ker
Ish|colleague|hamkasb|KO-liig
Ish|team|jamoa|tiim
Ish|meeting|uchrashuv|MII-ting
Ish|project|loyiha|PRO-jekt
Ish|task|vazifa|taask
Ish|deadline|muddat|DED-layn
Ish|schedule|jadval|SKE-jul
Ish|report|hisobot|ri-PORT
Ish|presentation|taqdimot|pre-zen-TEY-shn
Ish|contract|shartnoma|KON-trakt
Ish|salary|maosh|SA-la-ri
Ish|wage|ish haqi|veyj
Ish|bonus|mukofot|BOU-nas
Ish|promotion|lavozim ko'tarilishi|pro-MOU-shn
Ish|interview|suhbat|IN-ter-vyu
Ish|resume|rezyume|RE-zyu-mey
Ish|experience|tajriba|ek-SPII-ri-ens
Ish|skill|ko'nikma|skil
Ish|talent|iste'dod|TA-lent
Ish|effort|harakat|E-fort
Ish|success|muvaffaqiyat|sak-SES
Ish|failure|muvaffaqiyatsizlik|FEYL-yur
Ish|mistake|xato|mi-STEYK
Ish|solution|yechim|so-LYU-shn
Ish|problem|muammo|PROB-lem
Ish|idea|g'oya|ay-DII-a
Ish|plan|reja|plaan
Ish|goal|maqsad|goul
Ish|result|natija|ri-ZALT
Ish|progress|taraqqiyot|PROG-res
Ish|quality|sifat|KVO-li-ti
Ish|quantity|miqdor|KVAN-ti-ti
Ish|responsibility|mas'uliyat|ri-spon-si-BI-li-ti
Ish|decision|qaror|di-SI-zhn
Ish|opportunity|imkoniyat|o-por-TYU-ni-ti
Kasb|teacher|o'qituvchi|TII-cher
Kasb|student|o'quvchi|STYU-dent
Kasb|doctor|shifokor|DOK-ter
Kasb|nurse|hamshira|ners
Kasb|engineer|muhandis|en-ji-NIIR
Kasb|programmer|dasturchi|PRO-gram-mer
Kasb|developer|ishlab chiquvchi|di-VE-lo-per
Kasb|designer|dizayner|di-ZAY-ner
Kasb|artist|rassom|AAR-tist
Kasb|writer|yozuvchi|RAY-ter
Kasb|poet|shoir|POU-et
Kasb|singer|qo'shiqchi|SING-er
Kasb|musician|musiqachi|myu-ZI-shn
Kasb|actor|aktyor|AK-ter
Kasb|director|rejissyor|di-REK-ter
Kasb|photographer|fotograf|fo-TOG-ra-fer
Kasb|journalist|jurnalist|JER-na-list
Kasb|lawyer|advokat|LO-yer
Kasb|judge|sudya|jaj
Kasb|police officer|politsiya xodimi|po-LIIS O-fi-ser
Kasb|soldier|askar|SOUL-jer
Kasb|firefighter|o't o'chiruvchi|FAY-er-fay-ter
Kasb|pilot|uchuvchi|PAY-lot
Kasb|driver|haydovchi|DRAY-ver
Kasb|farmer|dehqon|FAAR-mer
Kasb|fisherman|baliqchi|FI-sher-man
Kasb|baker|novvoy|BEY-ker
Kasb|butcher|qassob|BU-cher
Kasb|cook|oshpaz|kuk
Kasb|waiter|ofitsiant|VEY-ter
Kasb|barber|sartarosh|BAAR-ber
Kasb|tailor|tikuvchi|TEY-lor
Kasb|carpenter|duradgor|KAAR-pen-ter
Kasb|plumber|santexnik|PLA-mer
Kasb|electrician|elektrik|e-lek-TRI-shn
Kasb|mechanic|mexanik|me-KA-nik
Kasb|builder|quruvchi|BIL-der
Kasb|cleaner|tozalovchi|KLII-ner
Kasb|guard|qo'riqchi|gaard
Kasb|scientist|olim|SAY-en-tist
Kasb|researcher|tadqiqotchi|ri-SER-cher
Kasb|professor|professor|pro-FE-sor
Kasb|translator|tarjimon|trans-LEY-ter
Kasb|entrepreneur|tadbirkor|on-tre-pre-NER
Kasb|businessman|ishbilarmon|BIZ-nes-man
Biznes|business|biznes|BIZ-nes
Biznes|company|kompaniya|KAM-pa-ni
Biznes|corporation|korporatsiya|kor-po-REY-shn
Biznes|startup|startap|STAART-ap
Biznes|product|mahsulot|PRO-dakt
Biznes|service|xizmat|SER-vis
Biznes|customer|mijoz|KAS-to-mer
Biznes|client|mijoz|KLAY-ent
Biznes|order|buyurtma|OR-der
Biznes|delivery|yetkazib berish|di-LI-ve-ri
Biznes|payment|to'lov|PEY-ment
Biznes|price|narx|prays
Biznes|cost|xarajat|kost
Biznes|profit|foyda|PRO-fit
Biznes|loss|zarar|los
Biznes|investment|investitsiya|in-VEST-ment
Biznes|investor|investor|in-VES-tor
Biznes|share|ulush|sheir
Biznes|stock|aksiya|stok
Biznes|market|bozor|MAAR-ket
Biznes|marketing|marketing|MAAR-ke-ting
Biznes|advertising|reklama|AD-ver-tay-zing
Biznes|brand|brend|brand
Biznes|logo|logotip|LOU-gou
Biznes|slogan|shior|SLOU-gan
Biznes|launch|ishga tushirish|lonsh
Biznes|strategy|strategiya|STRA-te-ji
Biznes|partnership|hamkorlik|PAART-ner-ship
Biznes|negotiation|muzokara|ne-go-shi-EY-shn
Biznes|agreement|kelishuv|a-GRII-ment
Biznes|account|hisob|a-KAUNT
Biznes|invoice|hisob-faktura|IN-voys
Biznes|receipt|chek|ri-SIIT
Biznes|budget|byudjet|BAJ-et
Biznes|tax|soliq|taks
Biznes|loan|kredit|loun
Biznes|debt|qarz|det
Biznes|bankrupt|bankrot|BANK-rapt
Biznes|trade|savdo|treyd
Biznes|import|import|IM-port
Biznes|export|eksport|EK-sport
Biznes|supply|ta'minot|sa-PLAY
Biznes|demand|talab|di-MAND
Ta'lim|education|ta'lim|e-ju-KEY-shn
Ta'lim|school|maktab|skuul
Ta'lim|college|kollej|KO-lij
Ta'lim|university|universitet|yu-ni-VER-si-ti
Ta'lim|class|sinf|klaas
Ta'lim|lesson|dars|LE-sn
Ta'lim|subject|fan|SAB-jekt
Ta'lim|homework|uyga vazifa|HOUM-verk
Ta'lim|exam|imtihon|eg-ZAM
Ta'lim|test|test|test
Ta'lim|grade|baho|greyd
Ta'lim|mark|baho|maark
Ta'lim|diploma|diplom|di-PLOU-ma
Ta'lim|certificate|sertifikat|ser-TI-fi-ket
Ta'lim|degree|daraja|di-GRII
Ta'lim|knowledge|bilim|NO-lij
Ta'lim|skill|ko'nikma|skil
Ta'lim|study|o'qish|STAD-i
Ta'lim|teach|o'qitish|tiich
Ta'lim|learn|o'rganish|lern
Ta'lim|explain|tushuntirish|ek-SPLEYN
Ta'lim|understand|tushunish|an-der-STAND
Ta'lim|remember|eslab qolish|ri-MEM-ber
Ta'lim|forget|esdan chiqarish|for-GET
Ta'lim|question|savol|KWES-chn
Ta'lim|answer|javob|AAN-ser
Ta'lim|correct|to'g'ri|ko-REKT
Ta'lim|wrong|xato|rong
Ta'lim|example|misol|eg-ZAAM-pl
Ta'lim|practice|mashq|PRAK-tis
Ta'lim|theory|nazariya|THII-o-ri
Ta'lim|research|tadqiqot|ri-SERCH
Ta'lim|essay|insho|E-sey
Ta'lim|notebook|daftar|NOUT-buk
Ta'lim|textbook|darslik|TEKST-buk
Ta'lim|pen|qalam|pen
Ta'lim|pencil|qalam (grafit)|PEN-sl
Ta'lim|eraser|o'chirg'ich|i-REY-ser
Ta'lim|ruler|chizg'ich|RUU-ler
Ta'lim|blackboard|doska|BLAK-bord
Ta'lim|whiteboard|oq doska|VAYT-bord
Ta'lim|library|kutubxona|LAY-bre-ri
Ta'lim|dictionary|lug'at|DIK-shn-ri
Ta'lim|language|til|LANG-gvidj
Ta'lim|grammar|grammatika|GRA-mer
Ta'lim|vocabulary|lug'at boyligi|vo-KA-byu-le-ri
Dasturlash-2|source code|manba kod|sors koud
Dasturlash-2|compile|kompilyatsiya|kom-PAYL
Dasturlash-2|execute|bajarish|EK-se-kyut
Dasturlash-2|debug|disk raskadrovka|di-BAG
Dasturlash-2|deploy|joylashtirish|di-PLOY
Dasturlash-2|repository|ombor|ri-PO-zi-to-ri
Dasturlash-2|commit|qayd etish|ko-MIT
Dasturlash-2|branch|shox|braanch
Dasturlash-2|merge|birlashtirish|merj
Dasturlash-2|conflict|ziddiyat|KON-flikt
Dasturlash-2|version|versiya|VER-zhn
Dasturlash-2|release|chiqarish|ri-LIIS
Dasturlash-2|framework|karkas|FREYM-verk
Dasturlash-2|library|kutubxona|LAY-bre-ri
Dasturlash-2|module|modul|MO-juul
Dasturlash-2|package|paket|PA-kij
Dasturlash-2|class|sinf|klaas
Dasturlash-2|object|obyekt|OB-jekt
Dasturlash-2|method|metod|ME-thod
Dasturlash-2|property|xususiyat|PRO-per-ti
Dasturlash-2|attribute|atribut|A-tri-byut
Dasturlash-2|parameter|parametr|pa-RAA-me-ter
Dasturlash-2|argument|argument|AAR-gyu-ment
Dasturlash-2|return|qaytarish|ri-TERN
Dasturlash-2|condition|shart|kon-DI-shn
Dasturlash-2|if statement|agar operatori|if STEYT-ment
Dasturlash-2|else|aks holda|els
Dasturlash-2|while loop|while sikli|vayl luup
Dasturlash-2|for loop|for sikli|for luup
Dasturlash-2|break|to'xtatish|breyk
Dasturlash-2|continue|davom etish|kon-TI-nyu
Dasturlash-2|dictionary|lug'at|DIK-shn-ri
Dasturlash-2|list|ro'yxat|list
Dasturlash-2|tuple|kortej|TA-pl
Dasturlash-2|set|to'plam|set
Dasturlash-2|integer|butun son|IN-ti-jer
Dasturlash-2|float|kasr son|flout
Dasturlash-2|boolean|mantiqiy|BUU-li-an
Dasturlash-2|string|matn|string
Dasturlash-2|character|belgi|KA-rak-ter
Dasturlash-2|index|indeks|IN-deks
Dasturlash-2|slice|bo'lak|slays
Dasturlash-2|append|qo'shish|a-PEND
Dasturlash-2|remove|olib tashlash|ri-MUUV
Dasturlash-2|insert|kiritish|in-SERT
Dasturlash-2|sort|saralash|sort
Dasturlash-2|reverse|teskari|ri-VERS
Dasturlash-2|count|sanash|kaunt
Dasturlash-2|length|uzunlik|lenth
Dasturlash-2|type|tur|tayp
Dasturlash-2|value|qiymat|VA-lyu
Dasturlash-2|key|kalit|kii
Dasturlash-2|exception|xatolik|ek-SEP-shn
Dasturlash-2|try|urinish|tray
Dasturlash-2|except|istisno|ek-SEPT
Dasturlash-2|finally|oxirida|FAY-na-li
Dasturlash-2|import|import qilish|IM-port
Dasturlash-2|export|eksport qilish|EK-sport
Dasturlash-2|install|o'rnatish|in-STOL
Dasturlash-2|uninstall|o'chirish|an-in-STOL
Dasturlash-2|configure|sozlash|kon-FI-gyur
Dasturlash-2|script|skript|skript
Dasturlash-2|syntax|sintaksis|SIN-taks
Dasturlash-2|logic|mantiq|LO-jik
Dasturlash-2|output|chiqarish|AUT-put
Dasturlash-2|input|kiritish|IN-put
Dasturlash-2|runtime|ish vaqti|RAN-taym
Dasturlash-2|compile time|kompilyatsiya vaqti|kom-PAYL taym
Dasturlash-2|memory|xotira|ME-mo-ri
Dasturlash-2|storage|saqlash|STOR-ij
Dasturlash-2|thread|ip|thred
Dasturlash-2|process|jarayon|PRO-ses
Dasturlash-2|async|asinxron|EY-sink
Dasturlash-2|await|kutish|a-VEYT
Dasturlash-2|callback|qayta chaqiruv|KOL-bak
Dasturlash-2|promise|va'da|PRO-mis
Dasturlash-2|event|voqea|i-VENT
Dasturlash-2|handler|boshqaruvchi|HAAND-ler
Dasturlash-2|listener|tinglovchi|LI-sner
Dasturlash-2|request|so'rov|ri-KWEST
Dasturlash-2|response|javob|ri-SPONS
Dasturlash-2|endpoint|manzil|END-poynt
Dasturlash-2|route|marshrut|ruut
Dasturlash-2|middleware|oraliq dastur|MI-dl-veir
Texnologiya|technology|texnologiya|tek-NO-lo-ji
Texnologiya|gadget|qurilma|GA-jet
Texnologiya|device|qurilma|di-VAYS
Texnologiya|smartphone|smartfon|SMAART-foun
Texnologiya|laptop|noutbuk|LAP-top
Texnologiya|tablet|planshet|TAB-let
Texnologiya|desktop|ish stoli kompyuter|DESK-top
Texnologiya|monitor|monitor|MO-ni-tor
Texnologiya|printer|printer|PRIN-ter
Texnologiya|scanner|skaner|SKA-ner
Texnologiya|camera|kamera|KA-me-ra
Texnologiya|headphones|naushnik|HED-founz
Texnologiya|speaker|dinamik|SPII-ker
Texnologiya|charger|zaryadlovchi|CHAAR-jer
Texnologiya|battery|batareya|BA-te-ri
Texnologiya|cable|kabel|KEY-bl
Texnologiya|USB|USB|yu-es-bii
Texnologiya|bluetooth|blyutuz|BLUU-tuuth
Texnologiya|Wi-Fi|Wi-Fi|VAY-fay
Texnologiya|router|router|RUU-ter
Texnologiya|modem|modem|MOU-dem
Texnologiya|antenna|antenna|an-TE-na
Texnologiya|satellite|sun'iy yo'ldosh|SA-te-layt
Texnologiya|signal|signal|SIG-nal
Texnologiya|frequency|chastota|FRII-kven-si
Texnologiya|bandwidth|o'tkazuvchanlik|BAND-vidth
Texnologiya|speed|tezlik|spiid
Texnologiya|processor|protsessor|PRO-se-sor
Texnologiya|chip|chip|chip
Texnologiya|circuit|sxema|SER-kit
Texnologiya|transistor|tranzistor|tran-ZIS-tor
Texnologiya|hard drive|qattiq disk|HAARD drayv
Texnologiya|SSD|SSD|es-es-dii
Texnologiya|RAM|RAM|raam
Texnologiya|motherboard|ona plata|MA-ther-bord
Texnologiya|graphics card|video karta|GRA-fiks kaard
Texnologiya|power supply|quvvat manbai|PAU-er sa-PLAY
Texnologiya|update|yangilanish|ap-DEYT
Texnologiya|upgrade|yaxshilash|AP-greyd
Texnologiya|backup|zaxira nusxa|BAK-ap
Texnologiya|restore|tiklash|ri-STOR
Texnologiya|reset|qayta o'rnatish|ri-SET
Texnologiya|reboot|qayta ishga tushirish|ri-BUUT
Texnologiya|shutdown|o'chirish|SHAT-daun
Texnologiya|login|kirish|LOG-in
Texnologiya|logout|chiqish|LOG-aut
Texnologiya|signup|ro'yxatdan o'tish|SAYN-ap
Texnologiya|register|ro'yxatga olish|RE-jis-ter
Texnologiya|account|hisob|a-KAUNT
Texnologiya|profile|profil|PRO-fayl
Texnologiya|username|foydalanuvchi nomi|YU-zer-neym
Texnologiya|password|parol|PAAS-verd
Texnologiya|authentication|autentifikatsiya|o-then-ti-KEY-shn
Texnologiya|verification|tasdiqlash|ve-ri-fi-KEY-shn
Texnologiya|encryption|shifrlash|en-KRIP-shn
Texnologiya|decryption|shifrni ochish|di-KRIP-shn
Texnologiya|firewall|xavfsizlik devori|FAY-er-vol
Texnologiya|antivirus|antivirus|an-ti-VAY-ras
Texnologiya|malware|zararli dastur|MAL-veir
Texnologiya|spam|spam|spam
Texnologiya|phishing|fishing|FI-shing
Texnologiya|hacking|xakerlik|HA-king
Ijtimoiy tarmoq|internet|internet|IN-ter-net
Ijtimoiy tarmoq|website|veb-sayt|VEB-sayt
Ijtimoiy tarmoq|webpage|veb-sahifa|VEB-peyj
Ijtimoiy tarmoq|blog|blog|blog
Ijtimoiy tarmoq|vlog|vlog|vlog
Ijtimoiy tarmoq|post|post|poust
Ijtimoiy tarmoq|comment|izoh|KO-ment
Ijtimoiy tarmoq|like|layk|layk
Ijtimoiy tarmoq|share|ulashish|sheir
Ijtimoiy tarmoq|follow|kuzatish|FO-lou
Ijtimoiy tarmoq|follower|kuzatuvchi|FO-lou-er
Ijtimoiy tarmoq|friend|do'st|frend
Ijtimoiy tarmoq|subscribe|obuna bo'lish|sab-SKRAYB
Ijtimoiy tarmoq|channel|kanal|CHA-nl
Ijtimoiy tarmoq|group|guruh|gruup
Ijtimoiy tarmoq|page|sahifa|peyj
Ijtimoiy tarmoq|message|xabar|ME-sij
Ijtimoiy tarmoq|notification|bildirishnoma|nou-ti-fi-KEY-shn
Ijtimoiy tarmoq|chat|suhbat|chat
Ijtimoiy tarmoq|video call|video qo'ng'iroq|VI-di-ou kol
Ijtimoiy tarmoq|voice message|ovozli xabar|voys ME-sij
Ijtimoiy tarmoq|emoji|emoji|i-MOU-ji
Ijtimoiy tarmoq|hashtag|heshteg|HASH-tag
Ijtimoiy tarmoq|trend|trend|trend
Ijtimoiy tarmoq|viral|virusli|VAY-ral
Ijtimoiy tarmoq|content|kontent|KON-tent
Ijtimoiy tarmoq|influencer|influenser|IN-flu-en-ser
Ijtimoiy tarmoq|streamer|strimer|STRII-mer
Ijtimoiy tarmoq|gamer|o'yinchi|GEY-mer
Ijtimoiy tarmoq|subscriber|obunachi|sab-SKRAY-ber
Ijtimoiy tarmoq|viewer|tomoshabin|VYU-er
Ijtimoiy tarmoq|community|jamoa|ko-MYU-ni-ti
OAV|news|yangiliklar|nyuz
OAV|newspaper|gazeta|NYUZ-pey-per
OAV|magazine|jurnal|MA-ga-ziin
OAV|article|maqola|AAR-ti-kl
OAV|headline|sarlavha|HED-layn
OAV|reporter|muxbir|ri-POR-ter
OAV|interview|intervyu|IN-ter-vyu
OAV|broadcast|eshittirish|BROD-kaast
OAV|channel|kanal|CHA-nl
OAV|program|ko'rsatuv|PRO-gram
OAV|radio|radio|REY-di-ou
OAV|television|televideniye|TE-le-vi-zhn
OAV|podcast|podkast|POD-kaast
OAV|advertisement|reklama|ad-VER-tiz-ment
OAV|press|matbuot|pres
OAV|media|ommaviy axborot vositalari|MII-di-a
OAV|source|manba|sors
OAV|fact|fakt|fakt
OAV|opinion|fikr|o-PI-nyon
OAV|rumor|mish-mish|RUU-mor
OAV|truth|haqiqat|truuth
OAV|lie|yolg'on|lay
OAV|fake news|yolg'on xabar|feyk nyuz
OAV|propaganda|targ'ibot|pro-pa-GAAN-da
Iboralar|Good luck|Omad|gud lak
Iboralar|Bad luck|Omadsizlik|bad lak
Iboralar|Take care|O'zingizni ehtiyot qiling|teyk keir
Iboralar|See you|Ko'rishguncha|sii yu
Iboralar|See you soon|Tez ko'rishguncha|sii yu suun
Iboralar|See you tomorrow|Ertaga ko'rishguncha|sii yu tu-MO-rou
Iboralar|Long time no see|Ko'rishmaganimga ancha bo'ldi|long taym nou sii
Iboralar|How is it going?|Ishlar qalay?|hau iz it GOU-ing
Iboralar|What is up?|Nima gap?|vot iz ap
Iboralar|Not much|Ko'p narsa emas|not mach
Iboralar|Never mind|Zarari yo'q|NE-ver maynd
Iboralar|No worries|Tashvishlanmang|nou VE-riz
Iboralar|That is okay|Yaxshi, mayli|that iz ou-KEY
Iboralar|Of course|Albatta|ov kors
Iboralar|For sure|Aniq|for shur
Iboralar|By the way|Aytmoqchi|bay the vey
Iboralar|In my opinion|Mening fikrimcha|in may o-PI-nyon
Iboralar|As far as I know|Bilishimcha|az faar az ay nou
Iboralar|To be honest|Rostini aytsam|tu bi O-nest
Iboralar|To tell the truth|Haqiqatni aytsam|tu tel the truuth
Iboralar|In fact|Aslida|in fakt
Iboralar|Actually|Aslida|AK-chu-a-li
Iboralar|Anyway|Baribir|E-ni-vey
Iboralar|However|Biroq|hau-E-ver
Iboralar|Therefore|Shuning uchun|VEIR-for
Iboralar|Moreover|Bundan tashqari|mor-OU-ver
Iboralar|In addition|Qo'shimcha ravishda|in a-DI-shn
Iboralar|On the other hand|Boshqa tomondan|on the A-ther hand
Iboralar|As a result|Natijada|az e ri-ZALT
Iboralar|For example|Masalan|for eg-ZAAM-pl
Iboralar|In other words|Boshqacha aytganda|in A-ther verds
Iboralar|At least|Hech bo'lmaganda|at liist
Iboralar|At most|Ko'pi bilan|at moust
Iboralar|More or less|Ko'proq yoki kamroq|mor or les
Iboralar|So far|Hozirgacha|sou faar
Iboralar|As soon as possible|Imkon qadar tez|az suun az PO-si-bl
Iboralar|Right now|Hozir|rayt nau
Iboralar|Just a moment|Bir daqiqa|jast e MOU-ment
Iboralar|Hold on|Kuting|hould on
Iboralar|Wait a minute|Bir daqiqa kuting|veyt e MI-nit
Iboralar|Come on|Qani|kam on
Iboralar|Go ahead|Davom eting|gou a-HED
Iboralar|Hurry up|Tezlashing|HA-ri ap
Iboralar|Slow down|Sekinlash|slou daun
Iboralar|Calm down|Xotirjam bo'l|kaam daun
Iboralar|Cheer up|Ko'taring kayfiyatni|chiir ap
Iboralar|Well done|Barakalla|vel dan
Iboralar|Good job|Yaxshi ish|gud job
Iboralar|Nice work|Ajoyib ish|nays verk
Iboralar|Keep going|Davom eting|kiip GOU-ing
Iboralar|Keep it up|Shunday davom eting|kiip it ap
Iboralar|No problem|Muammo yo'q|nou PROB-lem
Iboralar|You are welcome|Arzimaydi|yu ar VEL-kam
Iboralar|My pleasure|Mamnuniyat bilan|may PLE-zher
Gaplar|I love you|Men seni yaxshi ko'raman|ay lav yu
Gaplar|I miss you|Seni sog'indim|ay mis yu
Gaplar|I am hungry|Men ochman|ay em HANG-gri
Gaplar|I am thirsty|Men chanqadim|ay em THER-sti
Gaplar|I am tired|Men charchadim|ay em TAY-erd
Gaplar|I am busy|Men bandman|ay em BI-zi
Gaplar|I am ready|Men tayyorman|ay em RE-di
Gaplar|I am happy|Men xursandman|ay em HA-pi
Gaplar|I am sad|Men xafaman|ay em sad
Gaplar|I am okay|Men yaxshiman|ay em ou-KEY
Gaplar|I agree|Men roziman|ay a-GRII
Gaplar|I disagree|Men rozi emasman|ay dis-a-GRII
Gaplar|I understand|Men tushundim|ay an-der-STAND
Gaplar|I don't understand|Men tushunmadim|ay dount an-der-STAND
Gaplar|I know|Men bilaman|ay nou
Gaplar|I don't know|Men bilmayman|ay dount nou
Gaplar|I think|Men o'ylayman|ay think
Gaplar|I believe|Men ishonaman|ay bi-LIIV
Gaplar|I hope so|Umid qilamanki|ay houp sou
Gaplar|I am sure|Men ishonchim komil|ay em shur
Gaplar|I am not sure|Ishonchim komil emas|ay em not shur
Gaplar|You are right|Siz haqsiz|yu ar rayt
Gaplar|You are wrong|Siz xatosiz|yu ar rong
Gaplar|That is true|Bu to'g'ri|that iz truu
Gaplar|That is false|Bu yolg'on|that iz fols
Gaplar|It is possible|Bu mumkin|it iz PO-si-bl
Gaplar|It is impossible|Bu mumkin emas|it iz im-PO-si-bl
Gaplar|It doesn't matter|Bu muhim emas|it DAZ-nt MA-ter
Gaplar|What happened?|Nima bo'ldi?|vot HA-pend
Gaplar|What is wrong?|Nima xato?|vot iz rong
Gaplar|What do you mean?|Nima demoqchisiz?|vot du yu miin
Gaplar|Where are you going?|Qayerga ketyapsiz?|veir ar yu GOU-ing
Gaplar|Where do you live?|Qayerda yashaysiz?|veir du yu liv
Gaplar|What do you do?|Nima ish qilasiz?|vot du yu du
Gaplar|How old are you?|Necha yoshdasiz?|hau ould ar yu
Gaplar|Can you repeat?|Takrorlay olasizmi?|kan yu ri-PIIT
Gaplar|Can you help me?|Menga yordam bera olasizmi?|kan yu help mi
Gaplar|Could you please|Iltimos|kud yu pliiz
Gaplar|Excuse me|Kechirasiz|eks-KYUZ mi
Gaplar|I am sorry|Kechirasiz|ay em SO-ri
Gaplar|It is my fault|Bu mening aybim|it iz may folt
Gaplar|No thanks|Yo'q, rahmat|nou thenks
Gaplar|Yes please|Ha, iltimos|yes pliiz
Gaplar|Let me see|Ko'ray|let mi sii
Gaplar|Let me think|O'ylab ko'ray|let mi think
Gaplar|Let me try|Urinib ko'ray|let mi tray
Gaplar|It is up to you|Bu sizga bog'liq|it iz ap tu yu
Gaplar|Take your time|Shoshilmang|teyk yor taym
Gaplar|Be careful|Ehtiyot bo'ling|bi KEIR-ful
Gaplar|Have fun|Zavqlanib oling|hav fan
Sana|date|sana|deyt
Sana|Monday|dushanba|MAN-dey
Sana|Tuesday|seshanba|TYUZ-dey
Sana|Wednesday|chorshanba|VENZ-dey
Sana|Thursday|payshanba|THERZ-dey
Sana|Friday|juma|FRAY-dey
Sana|Saturday|shanba|SA-ter-dey
Sana|Sunday|yakshanba|SAN-dey
Sana|weekend|hafta oxiri|VIIK-end
Sana|weekday|ish kuni|VIIK-dey
Sana|today|bugun|tu-DEY
Sana|tomorrow|ertaga|tu-MO-rou
Sana|yesterday|kecha|YES-ter-dey
Sana|day after tomorrow|indinga|dey AA-fter tu-MO-rou
Sana|day before yesterday|o'tgan kun|dey bi-FOR YES-ter-dey
Sana|next week|keyingi hafta|nekst viik
Sana|last week|o'tgan hafta|laast viik
Sana|this week|shu hafta|this viik
Sana|next month|keyingi oy|nekst manth
Sana|last month|o'tgan oy|laast manth
Sana|next year|keyingi yil|nekst yir
Sana|last year|o'tgan yil|laast yir
Sana|anniversary|yubiley|a-ni-VER-sa-ri
Sana|holiday|bayram|HO-li-dey
Sana|birthday|tug'ilgan kun|BERTH-dey
Sana|wedding|to'y|VE-ding
Sana|funeral|dafn marosimi|FYU-ne-ral
Sana|calendar|kalendar|KA-len-dar
Sana|century|asr|SEN-chu-ri
Sana|decade|o'n yillik|DE-keyd
Sana|era|era|II-ra
Vaqt|time|vaqt|taym
Vaqt|hour|soat|AU-er
Vaqt|minute|daqiqa|MI-nit
Vaqt|second|soniya|SE-kond
Vaqt|morning|ertalab|MOR-ning
Vaqt|afternoon|tushdan keyin|af-ter-NUUN
Vaqt|evening|kechqurun|IIV-ning
Vaqt|night|tun|nayt
Vaqt|midnight|yarim tun|MID-nayt
Vaqt|noon|tush payti|nuun
Vaqt|dawn|tong|don
Vaqt|dusk|shom|dask
Vaqt|sunrise|quyosh chiqishi|SAN-rays
Vaqt|sunset|quyosh botishi|SAN-set
Vaqt|early|erta|ER-li
Vaqt|late|kech|leyt
Vaqt|soon|tez orada|suun
Vaqt|now|hozir|nau
Vaqt|then|keyin|then
Vaqt|before|oldin|bi-FOR
Vaqt|after|keyin|AA-fter
Vaqt|during|davomida|DYU-ring
Vaqt|while|paytida|vayl
Vaqt|always|har doim|OL-veyz
Vaqt|never|hech qachon|NE-ver
Vaqt|sometimes|ba'zan|SAM-taymz
Vaqt|often|tez-tez|OF-n
Vaqt|rarely|kamdan-kam|REIR-li
Vaqt|usually|odatda|YU-zhu-a-li
Vaqt|frequently|tez-tez|FRII-kvent-li
Vaqt|occasionally|ba'zan|o-KEY-zhon-a-li
Vaqt|recently|yaqinda|RII-sent-li
Vaqt|already|allaqachon|ol-RE-di
Vaqt|yet|hali|yet
Vaqt|still|hali ham|stil
Vaqt|just|hozirgina|jast
Vaqt|ever|hech qachon|E-ver
Vaqt|once|bir marta|vans
Vaqt|twice|ikki marta|tvays
Vaqt|daily|kunlik|DEY-li
Vaqt|weekly|haftalik|VIIK-li
Vaqt|monthly|oylik|MANTH-li
Vaqt|yearly|yillik|YIR-li
Vaqt|every day|har kuni|EV-ri dey
Vaqt|all day|kun bo'yi|ol dey
Vaqt|all night|tun bo'yi|ol nayt
Vaqt|o'clock|soat|o-KLOK
Vaqt|quarter past|o'n besh daqiqa o'tdi|KVOR-ter paast
Vaqt|half past|yarim o'tdi|haaf paast
Vaqt|quarter to|o'n besh daqiqa qoldi|KVOR-ter tu
Zamon|tense|zamon|tens
Zamon|present|hozirgi|PRE-zent
Zamon|past|o'tgan|paast
Zamon|future|kelasi|FYU-cher
Zamon|present simple|oddiy hozirgi zamon|PRE-zent SIM-pl
Zamon|present continuous|hozirgi davomiy zamon|PRE-zent kon-TI-nyu-os
Zamon|present perfect|hozirgi tugallangan zamon|PRE-zent PER-fekt
Zamon|past simple|oddiy o'tgan zamon|paast SIM-pl
Zamon|past continuous|o'tgan davomiy zamon|paast kon-TI-nyu-os
Zamon|past perfect|o'tgan tugallangan zamon|paast PER-fekt
Zomon|future simple|oddiy kelasi zamon|FYU-cher SIM-pl
Zamon|future continuous|kelasi davomiy zamon|FYU-cher kon-TI-nyu-os
Zamon|future perfect|kelasi tugallangan zamon|FYU-cher PER-fekt
Zamon|verb|fe'l|verb
Zamon|noun|ot|naun
Zamon|adjective|sifat|A-jek-tiv
Zamon|adverb|ravish|AD-verb
Zamon|pronoun|olmosh|PRO-naun
Zamon|preposition|predlog|pre-po-ZI-shn
Zamon|conjunction|bog'lovchi|kon-JANK-shn
Zamon|interjection|undov|in-ter-JEK-shn
Zamon|article|artikl|AAR-ti-kl
Zamon|subject|ega|SAB-jekt
Zamon|object|to'ldiruvchi|OB-jekt
Zamon|sentence|gap|SEN-tens
Zamon|phrase|ibora|freyz
Zamon|word|so'z|verd
Zamon|paragraph|paragraf|PA-ra-graaf
Zamon|question|savol|KWES-chn
Zamon|answer|javob|AAN-ser
Zamon|statement|bayonot|STEYT-ment
Zamon|negative|inkor|NE-ga-tiv
Zamon|positive|tasdiq|PO-zi-tiv
Zamon|singular|birlik|SING-gyu-lar
Zamon|plural|ko'plik|PLU-ral
Zamon|countable|sanaladigan|KAUN-ta-bl
Zamon|uncountable|sanalmaydigan|an-KAUN-ta-bl
Zamon|regular verb|to'g'ri fe'l|RE-gyu-lar verb
Zamon|irregular verb|noto'g'ri fe'l|i-RE-gyu-lar verb
Zamon|auxiliary verb|yordamchi fe'l|og-ZI-lya-ri verb
Zamon|modal verb|modal fe'l|MOUD-l verb
Zamon|infinitive|infinitive|in-FI-ni-tiv
Zamon|gerund|gerundiy|JE-rand
Zamon|participle|sifatdosh|PAAR-ti-si-pl
Fe'l zamonlari|am|man|am
Fe'l zamonlari|is|hisoblanadi|iz
Fe'l zamonlari|are|hisoblanadilar|aar
Fe'l zamonlari|was|edi (birlik)|voz
Fe'l zamonlari|were|edilar (ko'plik)|ver
Fe'l zamonlari|be|bo'lmoq|bii
Fe'l zamonlari|being|bo'lib|BII-ing
Fe'l zamonlari|been|bo'lgan|biin
Fe'l zamonlari|have|ega bo'lmoq|hav
Fe'l zamonlari|has|ega (3-shaxs)|haz
Fe'l zamonlari|had|ega edi|had
Fe'l zamonlari|having|ega bo'lib|HA-ving
Fe'l zamonlari|do|qilmoq|du
Fe'l zamonlari|does|qiladi|daz
Fe'l zamonlari|did|qildi|did
Fe'l zamonlari|doing|qilib|DUU-ing
Fe'l zamonlari|done|qilingan|dan
Fe'l zamonlari|will|bo'ladi|vil
Fe'l zamonlari|would|bo'lardi|vud
Fe'l zamonlari|shall|kerak|shaal
Fe'l zamonlari|should|kerak|shud
Fe'l zamonlari|can|qila olmoq|kan
Fe'l zamonlari|could|qila olardi|kud
Fe'l zamonlari|may|mumkin|mey
Fe'l zamonlari|might|mumkin edi|mayt
Fe'l zamonlari|must|shart|mast
Fe'l zamonlari|ought to|kerak|ot tu
Fe'l zamonlari|need to|kerak|niid tu
Fe'l zamonlari|used to|odatlanmoq|yuzd tu
Bog'lovchilar|and|va|and
Bog'lovchilar|but|lekin|bat
Bog'lovchilar|or|yoki|or
Bog'lovchilar|nor|na|nor
Bog'lovchilar|so|shuning uchun|sou
Bog'lovchilar|yet|biroq|yet
Bog'lovchilar|for|chunki|for
Bog'lovchilar|because|chunki|bi-KOZ
Bog'lovchilar|since|chunki|sins
Bog'lovchilar|as|sifatida|az
Bog'lovchilar|if|agar|if
Bog'lovchilar|unless|agar bo'lmasa|an-LES
Bog'lovchilar|although|garchi|ol-THOU
Bog'lovchilar|though|garchi|thou
Bog'lovchilar|even though|garchi|II-ven thou
Bog'lovchilar|while|paytda|vayl
Bog'lovchilar|when|qachon|ven
Bog'lovchilar|whenever|qachon bo'lmasin|ven-E-ver
Bog'lovchilar|where|qayerda|veir
Bog'lovchilar|wherever|qayerda bo'lmasin|veir-E-ver
Bog'lovchilar|whether|yoki|VE-ther
Bog'lovchilar|either|yoki|AY-ther
Bog'lovchilar|neither|hech biri|NAY-ther
Bog'lovchilar|both|ikkisi ham|bouth
Bog'lovchilar|not only|nafaqat|not OUN-li
Bog'lovchilar|but also|balki|bat OL-sou
Bog'lovchilar|however|ammo|hau-E-ver
Bog'lovchilar|moreover|bundan tashqari|mor-OU-ver
Bog'lovchilar|therefore|shuning uchun|VEIR-for
Bog'lovchilar|thus|shunday qilib|thas
Bog'lovchilar|hence|shuning uchun|hens
Bog'lovchilar|otherwise|aks holda|A-ther-vayz
Bog'lovchilar|instead|o'rniga|in-STED
Bog'lovchilar|meanwhile|shu bilan birga|MIIN-vayl
Bog'lovchilar|furthermore|bundan tashqari|FER-ther-mor
Bog'lovchilar|nevertheless|shunga qaramay|ne-ver-the-LES
Bog'lovchilar|nonetheless|shunga qaramay|nan-the-LES
Predloglar|in|ichida|in
Predloglar|on|ustida|on
Predloglar|at|da|at
Predloglar|to|ga|tu
Predloglar|from|dan|from
Predloglar|by|tomonidan|bay
Predloglar|with|bilan|vith
Predloglar|without|siz|vi-THAUT
Predloglar|for|uchun|for
Predloglar|about|haqida|a-BAUT
Predloglar|of|ning|ov
Predloglar|into|ichiga|IN-tu
Predloglar|onto|ustiga|ON-tu
Predloglar|upon|ustiga|a-PON
Predloglar|under|ostida|AN-der
Predloglar|over|tepasida|OU-ver
Predloglar|above|yuqorida|a-BAV
Predloglar|below|pastda|bi-LOU
Predloglar|between|orasida|bi-TVIIN
Predloglar|among|orasida (ko'plik)|a-MANG
Predloglar|behind|orqasida|bi-HAYND
Predloglar|in front of|oldida|in front ov
Predloglar|next to|yonida|nekst tu
Predloglar|beside|yonida|bi-SAYD
Predloglar|near|yaqin|niir
Predloglar|far from|uzoqdan|faar from
Predloglar|around|atrofida|a-RAUND
Predloglar|through|orqali|thruu
Predloglar|across|bo'ylab|a-KROS
Predloglar|along|bo'ylab|a-LONG
Predloglar|past|yonidan|paast
Predloglar|beyond|nariga|bi-YOND
Predloglar|during|davomida|DYU-ring
Predloglar|after|keyin|AA-fter
Predloglar|before|oldin|bi-FOR
Predloglar|until|gacha|an-TIL
Predloglar|till|gacha|til
Predloglar|since|dan beri|sins
Predloglar|within|ichida|vi-THIN
Predloglar|amongst|orasida|a-MANGST
Predloglar|despite|qaramay|di-SPAYT
Predloglar|except|dan tashqari|ek-SEPT
Predloglar|besides|bundan tashqari|bi-SAYDZ
Predloglar|regarding|haqida|ri-GAAR-ding
Predloglar|concerning|haqida|kon-SER-ning
Predloglar|according to|ga ko'ra|a-KOR-ding tu
Predloglar|because of|sababli|bi-KOZ ov
Predloglar|instead of|o'rniga|in-STED ov
Predloglar|in spite of|qaramay|in spayt ov
Predloglar|by means of|yordamida|bay miinz ov
Predloglar|on behalf of|nomidan|on bi-HAAF ov
Predloglar|in case of|holatda|in keys ov
Predloglar|in terms of|nuqtai nazaridan|in terms ov
Predloglar|with regard to|nisbatan|vith ri-GAARD tu
"""

# ---------- SO'ZLARNI O'QISH ----------
SOZLAR = {}
for line in WORDS_DATA.strip().split('\n'):
    parts = line.split('|')
    if len(parts) == 4:
        kat, en, uz, tal = [p.strip() for p in parts]
        if kat not in SOZLAR:
            SOZLAR[kat] = []
        SOZLAR[kat].append({"en": en, "uz": uz, "talaffuz": tal})

# ---------- FAYLLAR ----------
PROGRESS_FILE = "english_progress.json"
DAILY_FILE = "english_daily.json"

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"organilgan": [], "kunlik": {}, "streak": 0, "oxirgi_sana": ""}

def save_progress(data):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def bugungi_sozlar(soni=30):
    bugun = str(datetime.date.today())
    if os.path.exists(DAILY_FILE):
        try:
            with open(DAILY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("sana") == bugun:
                return data.get("sozlar", [])
        except:
            pass
    barcha = []
    for kat, royxat in SOZLAR.items():
        for soz in royxat:
            barcha.append({"kategoriya": kat, "en": soz["en"],
                           "uz": soz["uz"], "talaffuz": soz["talaffuz"]})
    random.seed(bugun)
    tanlangan = random.sample(barcha, min(soni, len(barcha)))
    with open(DAILY_FILE, "w", encoding="utf-8") as f:
        json.dump({"sana": bugun, "sozlar": tanlangan}, f,
                  ensure_ascii=False, indent=2)
    return tanlangan

def soz_korsat(soz, index=None):
    prefiks = f"[{index}] " if index else ""
    print(f"\n{G}{'─' * 50}{RST}")
    print(f"  {prefiks}{W}{B}{soz['en']}{RST}")
    print(f"  {Y}🇺🇿 {soz['uz']}{RST}")
    print(f"  {C}🗣  {soz['talaffuz']}{RST}")
    print(f"  {G}📁 {soz['kategoriya']}{RST}")
    print(f"{G}{'─' * 50}{RST}")

def kunlik_dars():
    progress = load_progress()
    bugun = str(datetime.date.today())
    if progress["oxirgi_sana"] != bugun:
        kecha = str(datetime.date.today() - datetime.timedelta(days=1))
        if progress["oxirgi_sana"] == kecha:
            progress["streak"] += 1
        else:
            progress["streak"] = 1
        progress["oxirgi_sana"] = bugun
        save_progress(progress)

    sozlar = bugungi_sozlar(30)
    print(f"\n{B}{'=' * 60}{RST}")
    print(f"{W}  📚 BUGUNGI DARS — {bugun}{RST}")
    print(f"{Y}  🔥 Streak: {progress['streak']} kun{RST}")
    print(f"{B}{'=' * 60}{RST}")

    for i, soz in enumerate(sozlar, 1):
        soz_korsat(soz, i)

    print(f"\n{Y}📝 AMALIYOT (30 ta so'z):{RST}")
    togri = 0
    for i, soz in enumerate(sozlar, 1):
        print(f"\n{i}. {W}{soz['en']}{RST} — tarjimasi?")
        javob = input(f"   {Y}Javob:{RST} ").strip().lower()
        if javob == soz["uz"].lower():
            print(f"   {G}✅ To'g'ri!{RST}")
            togri += 1
            if soz["en"] not in progress["organilgan"]:
                progress["organilgan"].append(soz["en"])
        else:
            print(f"   {R}❌ Xato. To'g'ri: {soz['uz']}{RST}")

    print(f"\n{B}{'=' * 60}{RST}")
    print(f"{W}  🎯 NATIJA: {togri}/{len(sozlar)}{RST}")
    if togri == len(sozlar):
        print(f"{G}  🏆 Mukammal!{RST}")
    elif togri >= 20:
        print(f"{Y}  👍 Yaxshi!{RST}")
    else:
        print(f"{R}  💪 Yana urinib ko'ring!{RST}")

    progress["kunlik"][bugun] = {"togri": togri, "jami": len(sozlar)}
    save_progress(progress)
    print(f"\n{C}  📊 Jami o'rganilgan: {len(progress['organilgan'])} ta so'z{RST}")
    print(f"{B}{'=' * 60}{RST}\n")

def soz_qidirish():
    qidiruv = input(f"\n{Y}🔍 Qidirish (ingliz yoki o'zbekcha):{RST} ").strip().lower()
    if not qidiruv:
        return
    topildi = []
    for kat, royxat in SOZLAR.items():
        for soz in royxat:
            if qidiruv in soz["en"].lower() or qidiruv in soz["uz"].lower():
                topildi.append({"kategoriya": kat, "en": soz["en"],
                                "uz": soz["uz"], "talaffuz": soz["talaffuz"]})
    if not topildi:
        print(f"{R}❌ Topilmadi.{RST}")
        return
    print(f"\n{G}✅ {len(topildi)} ta natija:{RST}")
    for i, soz in enumerate(topildi[:10], 1):
        soz_korsat(soz, i)

def kategoriya_korish():
    print(f"\n{Y}📁 Kategoriyalar:{RST}")
    kategoriyalar = list(SOZLAR.keys())
    for i, kat in enumerate(kategoriyalar, 1):
        print(f"  {i}. {W}{kat}{RST} ({len(SOZLAR[kat])} ta so'z)")
    try:
        idx = int(input(f"\n{Y}Tanlang:{RST} ").strip()) - 1
        if 0 <= idx < len(kategoriyalar):
            kat = kategoriyalar[idx]
            print(f"\n{G}📁 {kat}:{RST}")
            for i, soz in enumerate(SOZLAR[kat], 1):
                print(f"  {i}. {W}{soz['en']:<20}{RST} — {Y}{soz['uz']:<20}{RST} ({soz['talaffuz']})")
    except:
        pass

def statistika():
    progress = load_progress()
    print(f"\n{B}{'=' * 60}{RST}")
    print(f"{W}  📊 STATISTIKA{RST}")
    print(f"{B}{'=' * 60}{RST}")
    print(f"  🔥 Streak: {Y}{progress['streak']} kun{RST}")
    print(f"  📚 O'rganilgan: {G}{len(progress['organilgan'])} ta{RST}")
    jami_soz = sum(len(v) for v in SOZLAR.values())
    foiz = (len(progress["organilgan"]) * 100 // jami_soz) if jami_soz else 0
    print(f"  🎯 Jami baza: {W}{jami_soz} ta{RST}")
    print(f"  📈 O'zlashtirish: {Y}{foiz}%{RST}")
    if progress["kunlik"]:
        print(f"\n  {C}📅 Oxirgi 7 kun:{RST}")
        for sana, data in list(progress["kunlik"].items())[-7:]:
            print(f"    {sana}: {data['togri']}/{data['jami']}")
    print(f"{B}{'=' * 60}{RST}\n")

def barcha_sozlar():
    print(f"\n{B}{'=' * 60}{RST}")
    for kat, royxat in SOZLAR.items():
        print(f"\n{G}📁 {kat}:{RST}")
        for i, soz in enumerate(royxat, 1):
            print(f"  {i}. {W}{soz['en']:<20}{RST} — {Y}{soz['uz']:<20}{RST} [{soz['talaffuz']}]")
    print(f"\n{B}{'=' * 60}{RST}")

def tez_test():
    barcha = []
    for kat, royxat in SOZLAR.items():
        for soz in royxat:
            barcha.append({"kategoriya": kat, "en": soz["en"],
                           "uz": soz["uz"], "talaffuz": soz["talaffuz"]})
    savollar = random.sample(barcha, 10)
    print(f"\n{B}{'=' * 60}{RST}")
    print(f"{W}  ⚡ TEZKOR TEST (10 so'z){RST}")
    print(f"{B}{'=' * 60}{RST}")
    togri = 0
    progress = load_progress()
    for i, soz in enumerate(savollar, 1):
        print(f"\n{i}. {W}{soz['en']}{RST} — ?")
        javob = input(f"   {Y}Javob:{RST} ").strip().lower()
        if javob == soz["uz"].lower():
            print(f"   {G}✅{RST}")
            togri += 1
            if soz["en"] not in progress["organilgan"]:
                progress["organilgan"].append(soz["en"])
        else:
            print(f"   {R}❌ To'g'ri: {soz['uz']}{RST}")
    save_progress(progress)
    print(f"\n{G}🎯 Natija: {togri}/10{RST}\n")

def menyu():
    while True:
        print(f"""
{B}╔════════════════════════════════╗
║  🇬🇧 BLIP ENGLISH TRAINER v3.0  ║
╠════════════════════════════════╣
║  [1] 📚 Kunlik dars (30 so'z)  ║
║  [2] 🔍 So'z qidirish          ║
║  [3] 📁 Kategoriyalar          ║
║  [4] 📊 Statistika             ║
║  [5] 📖 Barcha so'zlar         ║
║  [6] ⚡ Tezkor test            ║
║  [0] 🚪 Chiqish                ║
╚════════════════════════════════╝{RST}""")
        tanlov = input(f"{Y}Tanlang:{RST} ").strip()
        if tanlov == "1":
            kunlik_dars()
        elif tanlov == "2":
            soz_qidirish()
        elif tanlov == "3":
            kategoriya_korish()
        elif tanlov == "4":
            statistika()
        elif tanlov == "5":
            barcha_sozlar()
        elif tanlov == "6":
            tez_test()
        elif tanlov == "0":
            print(f"\n{G}👋 Xayr, Blip!{RST}\n")
            break
        else:
            print(f"{R}❌ Noto'g'ri tanlov.{RST}")

if __name__ == "__main__":
    os.system("clear" if os.name != "nt" else "cls")
    print(f"{G}")
    print("╔════════════════════════════════════════╗")
    print("║  🇬🇧  BLIP ENGLISH TRAINER v3.0        ║")
    print("║  Offline • 30 so'z/kun • 60 kunlik reja║")
    print("╚════════════════════════════════════════╝")
    print(RST)
    print(f"{Y}💡 Har kuni kirib, 'Kunlik dars' ni tanlang!{RST}")
    print(f"{C}💡 Offline ishlaydi — internet shart emas!{RST}")
    input(f"\n{G}▶️  Boshlash uchun Enter bosing...{RST}")
    menyu()