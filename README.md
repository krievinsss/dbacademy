# DB Academy — datubāzu tehnoloģijas (3. kurss)

Darbojošs lokālais sākotnējais produkts ar skolotāja/skolēna lomām, 234 akadēmisko stundu tematisko plānu, stundu atvēršanu, teoriju, testiem, SQL laboratoriju un progresa statistiku.

## Palaišana

1. Instalē Python 3.10+ (nekādas ārējās bibliotēkas nav nepieciešamas).
2. Terminālī: `cd db-academy` un `python3 server.py` (Windows: `py server.py`).
3. Atver `http://localhost:8765`.
4. Demonstrācijas konti: `teacher` / `DemoTeacher123!`, `student1` / `DemoStudent123!` (ir arī student2…student8 ar to pašu paroli).
5. Dati glabājas `data/academy.sqlite3`. Lai atjaunotu demo datus, apturi serveri un izdzēs šo failu.

## Kas jau strādā
- Paroles ar PBKDF2-HMAC-SHA256 un servera sesijas žetoniem.
- Skolotājs var atvērt/aizvērt nodarbības, skatīt katra skolēna progresu, pārbaudījumu iesniegumus, sadaļu pabeigtību un atvērt CSV atskaiti.
- Skolēns redz pieejamās nodarbības, teoriju, pilda testus un SQL laboratoriju.
- SQL laboratorijā atļauti tikai SELECT un WITH ... SELECT vaicājumi izolētā, katrā pārbaudē no jauna izveidotā SQLite atmiņas datubāzē; ir izpildes laika/vaicājumu sarežģītības ierobežojums.
- Mācību plāna stundu summa: 65 + 65 + 96 + 8 = 234 akadēmiskās stundas.

## Kas vēl nav gatavs produkcijas līmenim
- Visa 234 stundu satura redakcionāla izstrāde un pedagoga pārskatīšana: tēmu un uzdevumu struktūra ir aizpildīta, taču vairākas nodarbības koplieto skaidrojumu/testu šablonus.
- Droša vairāku lietotāju SQL smilškaste ar PostgreSQL/MySQL DDL/DML, izolētiem konteineriem, atjaunojamām datubāzēm.
- SSO, audita žurnāli, paroles atiestatīšana, nodarbību kalendāra integrācija, centralizēta lietotāju pārvaldība, rezerves kopijas, GDPR izvērtējums, skolas lietojuma noslodzes testi.
- Šī ir lokālā Python/SQLite versija, **nav gatava izvietošanai Vercel**, kur datu noturībai jāizmanto PostgreSQL/Neon un citāda backend arhitektūra.

## Drošība
Demo kontu paroles pirms reālas izmantošanas nomaini. Neievieto šo versiju publiski internetā. Tā paredzēta lokālai pilota testēšanai ar izdomātiem skolēnu datiem.
