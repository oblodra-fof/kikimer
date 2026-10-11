# -*- coding: utf-8 -*-
"""
Навык «Кикимер» для Алисы — помощник мастера в НРИ (DnD).

Как пользоваться (уже внутри навыка, слово «Алиса» говорить не нужно):
  «трактирщик, добро пожаловать в Гнилой Пень»  -> скажет фразу голосом трактирщика
  «говори как гоблин» / «гоблин»                 -> сделает гоблина текущим персонажем
  «отдай мне свои сапоги»                        -> скажет текущий персонаж
  «реплика» / «реплика призрак»                  -> случайная заготовленная фраза
  «повтори»                                      -> повторить последнюю фразу
  «список»                                       -> какие персонажи есть
  «помощь»                                       -> подсказка
  «выход»                                        -> закрыть навык

ВАЖНО: эффекты голоса работают, только если в настройках навыка
выбран НЕ голос Алисы (например, мужской голос).

Чтобы добавить персонажа — скопируйте любой блок в NPCS и поменяйте его.
"""

import random
import re

# ---------------------------------------------------------------------------
# Персонажи
#   effect  — эффект Яндекса: behind_the_wall, hamster, megaphone,
#             pitch_down, psychodelic, pulse, train_announce или None
#   style   — манера речи (функции ниже, в разделе STYLES)
#   prefixes — начала слов, по которым узнаём персонажа («трактирщ» поймает
#             «трактирщик», «трактирщика», «трактирщиком»)
#   exact   — слова, которые должны совпасть целиком (для коротких имён)
# ---------------------------------------------------------------------------
NPCS = {
    "kikimer": {
        "name": "Кикимер",
        "prefixes": ["кикимер"],
        "exact": [],
        "effect": "pitch_down",
        "style": "grumble",
        "intro": "Кикимер здесь. Кикимер слушает, хотя его никто не спрашивал.",
        "lines": [
            "Опять гости. Опять грязь на коврах.",
            "Кикимер всё сделает. Кикимер всегда всё делает.",
            "Шумят, топчут, а убирать кому? Кикимеру.",
            "Хозяин велел — Кикимер исполнит. Ворча, но исполнит.",
        ],
    },
    "innkeeper": {
        "name": "Трактирщик",
        "prefixes": ["трактирщ", "корчмар", "хозяин"],
        "exact": [],
        "effect": "pitch_down",
        "style": "warm",
        "intro": "Проходите, проходите, путники! Тут тепло и эль свежий.",
        "lines": [
            "Комната на ночь — две серебряных. Завтрак за счёт заведения.",
            "Слыхали? На старом тракте опять пропал обоз.",
            "Эль, медовуха или чего покрепче? Только без драк, ладно?",
            "Если ищете работу — спросите у того хмурого в углу.",
        ],
    },
    "goblin": {
        "name": "Гоблин",
        "prefixes": ["гоблин"],
        "exact": [],
        "effect": "hamster",
        "style": "excited",
        "intro": "Блестяшки! У вас есть блестяшки? Дайте!",
        "lines": [
            "Это не я украл! Оно само ко мне в карман запрыгнуло!",
            "Большой босс будет злой. Очень злой. Вы бегите лучше!",
            "Моё! Всё моё! Кто нашёл, тот и хозяин!",
            "Не бейте! Я покажу тайный ход, честно-честно!",
        ],
    },
    "ghost": {
        "name": "Призрак",
        "prefixes": ["призрак", "дух", "привидени"],
        "exact": [],
        "effect": "behind_the_wall",
        "style": "ghostly",
        "intro": "Кто потревожил мой сон?",
        "lines": [
            "Я ждал вас сто лет. Найдите моё кольцо.",
            "Холодно. Здесь всегда холодно.",
            "Не спускайтесь в подвал. Там то, что меня убило.",
            "Уходите, пока свеча не погасла.",
        ],
    },
    "guard": {
        "name": "Стражник",
        "prefixes": ["стражник", "страж", "часов", "капитан"],
        "exact": [],
        "effect": "megaphone",
        "style": "shout",
        "intro": "Стоять! Кто такие? Назовитесь!",
        "lines": [
            "Ворота закрыты до рассвета. Приказ бургомистра.",
            "Оружие в ножны. В городе не размахивать.",
            "Пошлина — пять медяков с носа. Не нравится — обходите.",
            "Ещё раз увижу — в кандалы. Проходите.",
        ],
    },
    "wizard": {
        "name": "Безумный маг",
        "prefixes": ["волшебн", "чародe", "чароде", "колдун"],
        "exact": ["маг", "мага", "магу", "магом", "маге"],
        "effect": "psychodelic",
        "style": "mad",
        "intro": "А, вы как раз вовремя. Или слишком рано. Время такое скользкое.",
        "lines": [
            "Не трогайте этот флакон. И тот. И вообще ничего не трогайте.",
            "Звёзды сказали мне ваши имена. Правда, звёзды часто врут.",
            "Я превратил ученика в жабу. Случайно. Дважды.",
            "Портал откроется через три вдоха. Раз. Два. Ой.",
        ],
    },
    "golem": {
        "name": "Голем",
        "prefixes": ["голем", "конструкт", "автомат"],
        "exact": [],
        "effect": "pulse",
        "style": "robot",
        "intro": "Голем пробуждён. Ожидаю приказ.",
        "lines": [
            "Проход запрещён. Назовите пароль.",
            "Хозяин отсутствует. Триста лет. Ожидаю.",
            "Обнаружены нарушители. Начинаю защиту.",
            "Пароль неверен. Повторите попытку.",
        ],
    },
    "herald": {
        "name": "Глашатай",
        "prefixes": ["глашата", "вестник", "герольд"],
        "exact": [],
        "effect": "train_announce",
        "style": "announce",
        "intro": "Слушайте, слушайте, жители славного города!",
        "lines": [
            "Указом короля объявляется награда за голову разбойника по прозвищу Ворон!",
            "Ярмарка начнётся на рассвете у восточных ворот!",
            "Всем, кто видел дракона, явиться в ратушу!",
            "Турнир откладывается по причине нашествия крыс!",
        ],
    },
    "narrator": {
        "name": "Рассказчик",
        "prefixes": ["рассказчик", "летописец"],
        "exact": [],
        "effect": None,
        "style": "slow",
        "intro": "Итак, история продолжается.",
        "lines": [
            "Ночь опустилась на лес, и где-то вдалеке завыли волки.",
            "Дверь медленно приоткрылась сама собой.",
            "Тишина. Слишком тихо для таверны в базарный день.",
            "Вдруг земля под ногами дрогнула.",
        ],
    },
}

DEFAULT_NPC = "kikimer"
TTS_LIMIT = 1000  # у Алисы предел 1024 символа


# ---------------------------------------------------------------------------
# Манеры речи. sil <[мс]> — пауза; эти паузы и знаки препинания
# и создают интонацию.
# ---------------------------------------------------------------------------
def pause(ms):
    return " sil <[%d]> " % ms


def _sentences(text):
    parts = re.split(r"(?<=[.!?…])\s+", text.strip())
    return [p for p in parts if p]


def _ensure_end(s, mark="."):
    return s if s[-1:] in ".!?…" else s + mark


def style_plain(text):
    return text


def style_slow(text):
    text = text.replace(",", "," + pause(250))
    return pause(400).join(_ensure_end(s) for s in _sentences(text))


def style_warm(text):
    return "Хм." + pause(200) + style_slow(text)


def style_grumble(text):
    sents = [_ensure_end(s) for s in _sentences(text)]
    out = pause(300).join(sents)
    return "Кхм." + pause(250) + out + pause(350) + "Ворчу, ворчу."


def _stutter(word):
    m = re.match(r"([^аеёиоуыэюяАЕЁИОУЫЭЮЯ]*[аеёиоуыэюяАЕЁИОУЫЭЮЯ])", word)
    if not m or len(word) < 4:
        return word
    syl = m.group(1)
    return "%s-%s-%s" % (syl, syl.lower(), word[0].lower() + word[1:]) if word[0].isupper() \
        else "%s-%s-%s" % (syl, syl, word)


def style_excited(text):
    sents = []
    for s in _sentences(text):
        s = s.rstrip(".…") + ("!" if not s.endswith(("!", "?")) else "")
        sents.append(s)
    out = " ".join(sents)
    words = out.split(" ", 1)
    words[0] = _stutter(words[0])
    return " ".join(words)


def _stretch_last_vowel(s):
    # «погасла.» -> «погаслааа.»
    m = re.search(r"([аеёиоуыэюя])([^аеёиоуыэюя]*)([.!?…]*)$", s, re.IGNORECASE)
    if not m:
        return s
    v = m.group(1)
    return s[:m.start()] + v + v.lower() * 2 + m.group(2) + m.group(3)


def style_ghostly(text):
    text = text.replace(",", "," + pause(500))
    sents = [_stretch_last_vowel(_ensure_end(s, "…")) for s in _sentences(text)]
    return pause(800).join(sents)


def style_shout(text):
    sents = [s.rstrip(".…") + ("!" if not s.endswith(("!", "?")) else "")
             for s in _sentences(text)]
    return pause(200).join(sents)


def style_mad(text):
    sents = _sentences(text)
    out = []
    for i, s in enumerate(sents):
        s = _ensure_end(s)
        if i % 2 == 1:
            s = s.rstrip(".") + "?"
        out.append(s)
    return pause(random.choice([150, 600])).join(out) + pause(300) + "Хе-хе."


def style_robot(text):
    clean = re.sub(r"[,;:]", "", text)
    words = clean.split()
    return pause(120).join(words)


def style_announce(text):
    return "Внимание!" + pause(400) + style_slow(text)


STYLES = {
    "plain": style_plain,
    "slow": style_slow,
    "warm": style_warm,
    "grumble": style_grumble,
    "excited": style_excited,
    "ghostly": style_ghostly,
    "shout": style_shout,
    "mad": style_mad,
    "robot": style_robot,
    "announce": style_announce,
}


# ---------------------------------------------------------------------------
# Сборка речи
# ---------------------------------------------------------------------------
def sanitize(text):
    # убираем угловые скобки, чтобы фраза игрока не сломала разметку
    return re.sub(r"[<>]", "", text or "").strip()


def voice(npc_key, text):
    npc = NPCS[npc_key]
    body = STYLES.get(npc["style"], style_plain)(sanitize(text))
    if npc["effect"]:
        body = '<speaker effect="%s">%s<speaker effect="-">' % (npc["effect"], body)
    return body[:TTS_LIMIT]


def find_npc(word):
    w = word.lower().strip(",.!?")
    for key, npc in NPCS.items():
        if w in npc["exact"]:
            return key
        for p in npc["prefixes"]:
            if w.startswith(p):
                return key
    return None


def npc_list_text():
    return ", ".join(n["name"] for n in NPCS.values())


# ---------------------------------------------------------------------------
# Разбор команд
# ---------------------------------------------------------------------------
SWITCH_PHRASES = ["говори как", "говори голосом", "голос", "стань", "будь", "теперь ты", "ты"]
LINE_WORDS = {"реплика", "реплику", "фраза", "фразу", "скажи что-нибудь"}
REPEAT_WORDS = {"повтори", "еще раз", "ещё раз", "повтори пожалуйста"}
LIST_WORDS = {"список", "кто есть", "персонажи", "какие персонажи", "кто тут есть", "кто у тебя есть"}
HELP_WORDS = {"помощь", "помоги", "что ты умеешь", "справка"}
EXIT_WORDS = {"выход", "выйти", "стоп игра", "закончить", "конец игры", "хватит"}


def strip_words(original, n):
    """Убираем первые n слов из исходной фразы (чтобы сказать её с регистром и знаками)."""
    parts = (original or "").split()
    s = " ".join(parts[n:]).lstrip(" ,.:—-")
    return s[:1].upper() + s[1:]


def handle(command, original, state, is_new):
    current = state.get("npc", DEFAULT_NPC)
    last_tts = state.get("last_tts")
    last_text = state.get("last_text")

    def reply(text, tts, npc=current, end=False, remember=True):
        new_state = {"npc": npc,
                     "last_tts": tts if remember else last_tts,
                     "last_text": text if remember else last_text}
        return text, tts, new_state, end

    # приветствие
    if is_new and not command:
        text = ("Кикимер здесь. Скажите имя персонажа и фразу — например: "
                "«трактирщик, добро пожаловать». Персонажи: " + npc_list_text() + ".")
        tts = voice("kikimer", "Кикимер здесь. Кого сегодня изображать?") + \
            pause(300) + "Скажите имя персонажа и фразу. Например: трактирщик, добро пожаловать."
        return reply(text, tts, npc=DEFAULT_NPC)

    if command in HELP_WORDS:
        text = ("«Гоблин, это моё!» — фраза голосом гоблина. «Говори как призрак» — сменить персонажа, "
                "дальше любую фразу скажет он. «Реплика» — заготовка. «Повтори», «список», «выход».")
        return reply(text, text, remember=False)

    if command in LIST_WORDS:
        text = "Персонажи: " + npc_list_text() + "."
        return reply(text, text, remember=False)

    if command in EXIT_WORDS:
        tts = voice("kikimer", "Наконец-то тишина. Кикимер уходит.")
        return reply("Кикимер уходит. До следующей игры!", tts, end=True)

    if command in REPEAT_WORDS:
        if last_tts:
            return reply(last_text or "Повторяю.", last_tts, remember=False)
        return reply("Пока нечего повторять.", "Пока нечего повторять.", remember=False)

    words = command.split()
    if not words:
        return reply("Скажите фразу для персонажа.", "Скажите фразу для персонажа.", remember=False)

    # «реплика» или «реплика призрак»
    if words[0] in LINE_WORDS or command in LINE_WORDS:
        key = current
        if len(words) > 1:
            key = find_npc(words[1]) or current
        line = random.choice(NPCS[key]["lines"])
        return reply("%s: %s" % (NPCS[key]["name"], line), voice(key, line), npc=key)

    # «говори как гоблин», «голос призрака», «стань магом»
    for phrase in SWITCH_PHRASES:
        if command.startswith(phrase + " "):
            rest = command[len(phrase):].split()
            if rest:
                key = find_npc(rest[0])
                if key:
                    npc = NPCS[key]
                    return reply("Теперь говорит: %s. %s" % (npc["name"], npc["intro"]),
                                 voice(key, npc["intro"]), npc=key)

    # «гоблин, отдай сапоги» или просто «гоблин»
    key = find_npc(words[0])
    if key:
        npc = NPCS[key]
        phrase = strip_words(original, 1) if len(words) > 1 else ""
        if not phrase:
            return reply("Теперь говорит: %s. %s" % (npc["name"], npc["intro"]),
                         voice(key, npc["intro"]), npc=key)
        return reply("%s: %s" % (npc["name"], phrase), voice(key, phrase), npc=key)

    # иначе — говорит текущий персонаж
    phrase = original or command
    return reply("%s: %s" % (NPCS[current]["name"], phrase), voice(current, phrase))


# ---------------------------------------------------------------------------
# Обработка запроса Алисы
# ---------------------------------------------------------------------------
def process_event(event, context=None):
    req = event.get("request", {}) or {}
    command = (req.get("command") or "").lower().strip()
    original = (req.get("original_utterance") or "").strip()
    state = ((event.get("state") or {}).get("session")) or {}
    is_new = bool((event.get("session") or {}).get("new"))

    text, tts, new_state, end = handle(command, original, state, is_new)

    return {
        "version": event.get("version", "1.0"),
        "response": {
            "text": text[:1024],
            "tts": tts[:1024],
            "end_session": end,
        },
        "session_state": new_state,
    }


# ---------------------------------------------------------------------------
# Вебхук для Vercel: адрес будет https://<ваш-проект>.vercel.app/api/alice
# ---------------------------------------------------------------------------
import json
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        # проверка в браузере
        self._send(200, "Кикимер работает. Вставьте этот адрес в Яндекс Диалоги.",
                   "text/plain; charset=utf-8")

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            event = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            result = process_event(event)
        except Exception as e:  # чтобы Алиса не молчала при ошибке
            result = {"version": "1.0",
                      "response": {"text": "Кикимер споткнулся: %s" % e,
                                   "tts": "Кикимер споткнулся. Попробуйте ещё раз.",
                                   "end_session": False}}
        self._send(200, json.dumps(result, ensure_ascii=False))
