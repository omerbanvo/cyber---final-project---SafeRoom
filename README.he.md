# SafeRoom

אפליקציית שיחות וידאו מוצפנות, עם צ'אט והעברת קבצים — עבודת גמר בסייבר, 5 יחידות.

**מצב נוכחי: שלב 1** — שרת TCP שמקבל כמה לקוחות במקביל, ולקוח טקסט שמדבר איתו בפרוטוקול שבניתי.
עדיין אין הצפנה (זה שלב 2).

🇬🇧 [English version](README.md)

## דרישות

- Python 3.11 ומעלה
- אין ספריות חיצוניות

## התקנה

```bash
git clone https://github.com/omerbanvo/cyber---final-project---SafeRoom.git
cd cyber---final-project---SafeRoom
python3 -m venv venv
source venv/bin/activate
cp config/config.example.ini config/config.ini
```

## הגדרות

עורכים את `config/config.ini`:

| מפתח             | משמעות                                    | ברירת מחדל  |
|------------------|-------------------------------------------|-------------|
| `host`           | הכתובת שהשרת מאזין עליה                   | `127.0.0.1` |
| `port`           | פורט (1024–65535)                         | `31337`     |
| `max_clients`    | כמה לקוחות יכולים להתחבר במקביל           | `4`         |
| `max_frame_size` | הגודל המקסימלי של מסגרת, בבתים            | `1048576`   |
| `hello_timeout`  | כמה שניות יש ללקוח חדש לשלוח `HELLO`      | `10`        |

## הרצה

תמיד מריצים מהתיקייה הראשית של הפרויקט, עם `-m`:

```bash
python -m server.main      # טרמינל 1
python -m client.main      # טרמינל 2, 3, ...
```

פקודות בלקוח:

| פקודה         | מה היא עושה                           |
|---------------|---------------------------------------|
| `/ping`       | שולחת PING ומקבלת PONG                |
| `/bc <text>`  | שולחת טקסט לכל שאר הלקוחות            |
| `/bye`        | מתנתקת                                |

עוצרים את השרת עם `Ctrl+C`. הוא שולח `BYE` לכל הלקוחות ונסגר בצורה מסודרת.

## בדיקות

```bash
python -m unittest discover tests
```

סקריפט "תוקף" (השרת צריך לרוץ). הוא שולח מידע שבור, ובודק שהשרת סוגר רק את החיבור הזה:

```bash
python -m tests.attacker
```

## מבנה הפרויקט

```
common/   code used by both server and client (config, framing, protocol, errors)
server/   the server
client/   the client
tests/    unit tests and the attacker script
docs/     protocol documentation
```

## תיעוד

- [פרוטוקול](docs/protocol.he.md) · [Protocol](docs/protocol.md)