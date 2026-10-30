"""Mācību satura karkass, atbilstošs VTDT 3. kursa 234 stundu dalījumam."""
SECTIONS = [
("5.1", "Datu bāzu pilnveidošanas un optimizēšanas metodes", 65, [
"Ievada diagnostika: relācijas un SQL pamati", "Datubāzu pārvaldības sistēmu izvēle", "PostgreSQL, MySQL un SQLite salīdzinājums", "Datu integritātes jēdziens", "PRIMARY KEY un UNIQUE", "FOREIGN KEY un relācijas", "ON DELETE un ON UPDATE darbības", "NOT NULL, CHECK un DEFAULT", "Integritātes kļūdu diagnostika", "Datu dublēšanās un normalizācijas mērķi", "Pirmā normālforma (1NF)", "Otrā normālforma (2NF)", "Trešā normālforma (3NF)", "ER diagrammas pārprojektēšana", "Datubāzes migrāciju plānošana", "Indeksu darbības principi", "Vienkāršie un saliktie indeksi", "Kad indeksu nevajag veidot", "Vaicājumu izpildes plāni", "EXPLAIN praktiskā analīze", "Sarežģītu vaicājumu lēnuma cēloņi", "JOIN optimizācijas principi", "Agregāciju optimizācija", "Transakciju pamati", "ACID īpašības", "COMMIT un ROLLBACK", "Vienlaicīgas izmaiņas un integritāte", "Datubāzes rezerves kopiju stratēģija", "Datu konsekvences audits", "Praktiska datubāzes optimizācija", "Optimizācijas rezultātu salīdzināšana", "Projekta aizstāvēšana: optimizācija", "Sadaļas vērtēšanas darbs"]),
("5.2", "Datu bāzes testēšana", 65, [
"SELECT, WHERE un ORDER BY atkārtojums", "INNER JOIN", "LEFT JOIN un NULL", "Vairāku tabulu JOIN", "GROUP BY un agregātfunkcijas", "HAVING nosacījumi", "COUNT, SUM, AVG un datu precizitāte", "Apakšvaicājumi SELECT", "IN un EXISTS", "Korelētie apakšvaicājumi", "CTE ar WITH", "Vairāku CTE kombinēšana", "CASE WHEN izteiksmes", "Datumu un teksta funkcijas", "Logu funkciju ievads", "ROW_NUMBER un RANK", "Analītisko vaicājumu veidošana", "Pareizo sagaidāmo rezultātu definēšana", "SQL testēšanas pamati", "Robežgadījumi un tukšas tabulas", "NULL kļūdas SQL vaicājumos", "Dublēti JOIN rezultāti", "Testa datu kopu projektēšana", "SQL sintakses kļūdu analīze", "Loģikas kļūdu diagnostika", "Vaicājumu kļūdu atkārtošana", "Testēšanas scenāriju dokumentēšana", "Regresijas testēšana", "Datu bāzes testu automatizācija", "Kombinēts SQL izaicinājums", "Kļūdu labošanas laboratorija", "Testēšanas rezultātu prezentācija", "Sadaļas vērtēšanas darbs"]),
("6.1", "Datu bāzes kļūdu dokumentēšana", 96, [
"Datu tipu izvēle", "INTEGER, DECIMAL un precizitāte", "VARCHAR un TEXT", "DATE, TIME un TIMESTAMP", "BOOLEAN un NULL", "Datu tipu konvertēšana", "Ievaddatu validācijas noteikumi", "Datņu apstrādes pamatprincipi", "Failu lasīšana un rakstīšana", "Failu kodējumi un UTF-8", "CSV formāta struktūra", "CSV importēšana", "CSV eksportēšana", "Datu tīrīšana pirms importa", "JSON formāta struktūra", "JSON datu validācija", "JSON importēšana un eksportēšana", "XML struktūras pamati", "CSV un JSON salīdzināšana", "Lielu datu kopu apstrāde", "Kļūdainu ierakstu atfiltrēšana", "Transakcijas datu importā", "Datu eksportu salīdzināšana", "Tīmekļa pakalpojumu jēdziens", "HTTP metodes un statusi", "REST API pamatprincipi", "API atbilde JSON formātā", "API ievaddatu pārbaude", "Datubāzes kļūdu klasifikācija", "Kļūdu reģistrēšana žurnālā", "Žurnāla ieraksta struktūra", "Kļūdas atkārtošanas soļi", "Problēmas ziņojuma (bug report) rakstīšana", "Kļūdu smagums un prioritāte", "Kopsavilkuma pārskats", "Testēšanas pierādījumi un fakti", "SQL kļūdas dokumentācijas darbs", "Datu integritātes incidenta apraksts", "Datu importa kļūdas apraksts", "API kļūdas apraksts", "Kļūdu novēršanas pārbaudes", "Regresijas scenāriji", "Dokumentācijas kvalitātes audits", "Grupas projekta sagatavošana", "Praktiskais datu apmaiņas projekts", "Kļūdu žurnāla sagatavošana", "Projekta demonstrācija", "Sadaļas vērtēšanas darbs"]),
("FIN", "Moduļa noslēguma darbs", 8, ["Noslēguma darba teorētiskā pārbaude", "Praktiska datubāzes darba izstrāde", "Testēšana un kļūdu dokumentācija", "Noslēguma darba demonstrēšana"])
]

def make_lessons():
    rows=[]
    for code,section,total,topics in SECTIONS:
        durations=[2]*len(topics)
        if code in ("5.1","5.2"):
            durations[0]=1  # 33 nodarbības: 1 + 32*2 = 65
        assert sum(durations)==total,(code,sum(durations),total)
        for i,(title,duration) in enumerate(zip(topics,durations),1):
            rows.append(dict(section=code,section_title=section,number=i,title=title,hours=duration))
    assert sum(r['hours'] for r in rows)==234
    return rows

QUIZ_BANK = [
("Kas ir primārās atslēgas galvenais uzdevums?", ["Unikāli identificēt tabulas ierakstu", "Nokopēt tabulas struktūru", "Paātrināt jebkuru SQL komandu", "Šifrēt datus"],0,"PRIMARY KEY unikāli identificē tabulas rindu."),
("Ko nodrošina FOREIGN KEY?", ["Automātisku visus tabulas datu šifrēšanu", "Atsauču integritāti starp tabulām", "Vienmēr ātrāku SELECT", "Jaunu kolonnu izveidi"],1,"Ārējā atslēga nodrošina atsauces uz pieļaujamu saistīto ierakstu."),
("Kādēļ izmanto INDEX?", ["Lai vienmēr samazinātu diska izmantošanu", "Lai paātrinātu konkrētas datu meklēšanas", "Lai aizstātu PRIMARY KEY", "Lai izdzēstu dublikātus"],1,"Indekss palīdz meklēt ierakstus, bet rada izmaksas atjaunināšanā."),
("Ko dara ROLLBACK?", ["Apstiprina transakciju", "Atceļ neapstiprinātas transakcijas izmaiņas", "Izveido indeksu", "Atlasīs tikai pirmās 10 rindas"],1,"ROLLBACK atsauc transakcijas vēl neapstiprinātās izmaiņas."),
("Kurai komandai izmanto GROUP BY?", ["Rindu grupēšanai agregāciju vajadzībām", "Tabulas dzēšanai", "Datu bāzes kopēšanai", "Savienojuma atvēršanai"],0,"GROUP BY grupē rindas, lai veiktu agregējošus aprēķinus."),
("Ko nozīmē LEFT JOIN?", ["Tikai sakrītošās rindas", "Visas kreisās tabulas rindas un atbilstošās labās tabulas rindas", "Tikai labās tabulas rindas", "Datu dzēšanu no kreisās tabulas"],1,"LEFT JOIN saglabā kreisās tabulas rindas arī bez pāra labajā tabulā."),
("Kā SQL pārbaudīt NULL?", ["= NULL", "IS NULL", "LIKE NULL", "!= NULL"],1,"SQL NULL pārbaudei izmanto IS NULL."),
("Kas ir SQL vaicājuma regresijas tests?", ["Pārbaude, ka labojums nav sabojājis agrāk strādājošu uzvedību", "Vaicājuma izpildes pārtraukšana", "Jaunas datu bāzes uzstādīšana", "Datu bāzes dzēšana"],0,"Regresijas tests pārbauda iepriekš pareizas funkcionalitātes saglabāšanos."),
("Kāpēc datu importā vajadzīga validācija?", ["Lai kļūdaini dati nenonāktu sistēmā", "Lai CSV būtu krāsains", "Lai izslēgtu visu žurnalēšanu", "Lai nevajadzētu kļūdu apstrādi"],0,"Validācija pirms saglabāšanas pārbauda datu pareizību."),
("Kāds ir JSON formāta raksturojums?", ["Tikai binārs attēlu fails", "Strukturēts teksta datu apmaiņas formāts", "Datu bāzu indekss", "SQL komanda"],1,"JSON izmanto strukturētu datu apmaiņai."),
("Kam nepieciešams kļūdas ziņojums?", ["Lai kļūdu varētu atkārtot, saprast un novērst", "Lai slēptu kļūdas", "Lai aizvietotu testēšanu", "Lai automātiski dzēstu datubāzi"],0,"Kvalitatīvs bug report ietver atkārtošanas soļus, sagaidāmo un faktisko rezultātu."),
("Kāda ir laba reakcija uz importa kļūdu?", ["Kļūdu ignorēt", "Piereģistrēt, norādīt kļūdaino rindu un droši turpināt vai atcelt", "Izdzēst datubāzi", "Pārrakstīt visus ierakstus bez pārbaudes"],1,"Kļūdu apstrādei jābūt paredzamai un izsekojamai."),
]

SECTION_NOTES={
"5.1":"Pēti datu integritāti, datubāzes struktūru un efektivitāti. Pirms izmaiņām pieraksti sagaidāmo efektu, pēc tām pārbaudi rezultātu. Pamato DBVS, ierobežojumu vai indeksa izvēli.",
"5.2":"Izveido komplicētu SQL vaicājumu, pārbaudi to ar vairākiem datu variantiem. Salīdzini sagaidāmo un faktisko rezultātu, diagnosticē kļūdas un fiksē testēšanas secinājumus.",
"6.1":"Atšķir datu tipus un failu formātus, veic importu vai eksportu, validē datus un sagatavo atkārtojamu kļūdas aprakstu ar žurnālu un kopsavilkumu.",
"FIN":"Parādi, ka spēj izmantot datubāzi programmā, pārbaudīt vaicājumu pareizību un dokumentēt kļūdas."
}
