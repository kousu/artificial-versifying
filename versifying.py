#!/usr/bin/env python3
"""Generate Latin verses with John Peter's Artificial Versifying (1677).

Each number picks one verse: digit n of the number picks a word from table n.
See README.md for how the tables work.

    ./versifying.py lines 467182 879889
    ./versifying.py --translate line 467182
    ./versifying.py --mode elegiac lines 123456 12345
    ./versifying.py --mode elegiac poem --seed 1677 --lines 4
"""

import argparse
import random
import sys

# Copied from versifying.js, with spelling mistakes fixed. Each table is
# 9 words interleaved with a stride of 9; a space ends a word.
TABLES = {
    "orig": [
        "isatthtppmosuroueeprprirrsridebsrpsfairitiiii dadidamdba aaa aab b   b  ",
        "dffbivvddiaaeuoeoacctlrtrnmttalaabanaa a  a a  b bi b  ",
        "mtivmvrasiiniaielchbqrldoiiiiuoierio  a ss s brmb  b  rb  ",
        "ppmppccpcrrooraoroæonrounondcstmscdfiutaiaeuicrrbtbdcruaautuuumnnbnunnnattutntttn  n t   tbbtr brb bb  ",
        "sspfctdipioiœreouodmgdimgrcennempmguriorioailaaranrtaa  a aaa  br b   ",
        "mqctpspssuuealoreælærnalamptdttnavpeaaaue ae  m m b rrb b dbr ",
    ],
    "revised": [
        "tiphambleugeosaaufrnsrprrrfbesretbieiaiiriadrd mdaaraaaeaa  a   e  ee ",
        "fsdbvscstaiaeiiacetgmlnssolannlcttra aaalrrt e   aaaaeeeee    ",
        "sfptdpppfeoauoauaeqrtimttlruiisieoauis   t mn  sst t tsttssttt ",
        "pppppmcpprrroroarræooronuæomrmtdssnmoiieutaaunttncrbrlsatduaurgtnuunbnaartnntutnna tt n ttnt  sts  tssts sts ",
        "tppvlfacseoreuœgrimcærmdmidpulbieimeolienrnirraaraaanaa  a   a  ee eee ",
        "dsqapmdnsuæucruiiærpæealrgvaedrvtara  abaa a eema  e eee  ",
    ],
    "pentameter": [
        "tapisittneremomruotdrprpirxrufrdispiiaioiatiac dbd ia aeaaaea e e   e ",
        "ppcppccsprroreooiræænærnngosscdfsgnctcliiuliuaruccmofrbiduimmiaubunuaecnnuntnnrattnt ttan  t s  ntss ssstt ststtss ",
        "iavvdflaaucieiaarsrtnrccbmtaaabttrar   aaaa aeee    e ",
        "dppncsmsmoureruoialdofuplnloetaeeeiisnennrssgadrdtbttn avaaaarae a    a ee eeee ",
        "natvsmmvmoliiceaiivibrirldhaiiioaiei s s  ss e e ee  ",
    ],
}
# English glosses for every word in the Latin tables. The words for the
# original tables follow the English tables in versifying.js.
GLOSSES = {
    # adjectives
    "aspera": "harsh", "ardua": "arduous", "barbara": "barbarous",
    "effera": "savage", "horrida": "horrid", "ignea": "fiery",
    "impia": "wicked", "improba": "shameless", "lurida": "lurid",
    "martia": "warlike", "noxia": "harmful", "perfida": "faithless",
    "pessima": "very bad", "sordida": "sordid", "tetrica": "grim",
    "tristia": "sad", "turbida": "disordered", "turpia": "foul",
    "cruenta": "bloody", "dolosa": "deceitful", "maligna": "malignant",
    "molesta": "troublesome", "nefanda": "unspeakable",
    "proterva": "wanton", "pudenda": "shameful", "sinistra": "sinister",
    "superba": "proud",
    # nouns
    "acta": "acts", "agmina": "armies", "arma": "arms", "astra": "stars",
    "bella": "wars", "castra": "camps", "crimina": "offenses",
    "damna": "losses", "dicta": "sayings",
    "dogmata": "doctrines", "dona": "gifts", "facta": "deeds",
    "fata": "fates", "fœdera": "compacts",
    "iura": "rights", "iurgia": "quarrels", "labra": "lips",
    "lumina": "lights", "pignora": "pledges", "pocula": "cups",
    "prælia": "battles", "scorta": "harlots", "sidera": "stars",
    "signa": "signs", "sistra": "rattles", "somnia": "dreams",
    "tela": "weapons", "tempora": "times", "verba": "words",
    "verbera": "blows",
    "vincla": "chains",
    "vina": "wines", "vota": "vows",
    # pronouns, short phrases
    "aliis": "for others", "domi": "at home", "ferunt": "they say",
    "foris": "abroad", "inquam": "I say", "malis": "for the evil",
    "mihi": "for me", "palam": "openly", "pati": "to suffer",
    "patet": "it is clear", "puto": "I think", "reor": "I think",
    "scio": "I know", "sequi": "to follow", "tibi": "for you",
    "tuis": "for your own", "vides": "you see", "viris": "for men",
    "viro": "for a man", "mera": "pure", "nova": "new",
    # verbs
    "causabunt": "will cause", "concedunt": "yield",
    "concludunt": "conclude", "confirmant": "confirm",
    "conglomerant": "heap up", "consummant": "complete",
    "monstrabunt": "will show",
    "perficiunt": "accomplish", "portabunt": "will bring",
    "portendunt": "portend", "prædicunt": "foretell",
    "præmonstrant": "forewarn", "prænarrant": "foretell",
    "præscribunt": "prescribe", "præstabunt": "will provide",
    "procurant": "take care of", "producunt": "produce",
    "promittunt": "promise", "promulgant": "proclaim",
    "proritant": "provoke", "significant": "signify",
    # adverbs and final adjectives
    "certa": "sure", "dira": "dire", "dura": "hard", "multa": "many",
    "nigra": "black", "plane": "clearly", "prava": "evil",
    "quædam": "certain", "sæpe": "often", "sæva": "cruel",
    "acerba": "bitter",
    "semper": "always", "sola": "alone", "tantum": "only",
}


# Each mode cycles through these table sets, one per verse. Elegiac couplets
# alternate a hexameter with a pentameter; the pentameter is indented, as is
# customary in print.
MODES = {
    "orig": [("", TABLES["orig"])],
    "revised": [("", TABLES["revised"])],
    "pentameter": [("", TABLES["pentameter"])],
    "elegiac": [("", TABLES["revised"]), ("    ", TABLES["pentameter"])],
}


def start_index(digit):
    """Count from digit + 1 up to 9 (from 1 for digit 9); return the 0-based cell."""
    return 8 if digit == 9 else 8 - digit


def read_word(table, digit):
    word = []
    for letter in table[start_index(digit)::9]:
        if letter == " ":
            break
        word.append(letter)
    return "".join(word).replace("_", " ")


def make_words(tables, number):
    return [read_word(t, int(d)) for t, d in zip(tables, number)]


def capitalize(verse):
    return verse[0].upper() + verse[1:]


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("-m", "--mode", choices=MODES, default="orig",
                        help="which tables to use (default: orig); elegiac "
                        "alternates revised hexameters and pentameters")
    parser.add_argument("-t", "--translate", action="store_true",
                        help="follow the poem with a word-for-word English gloss")
    commands = parser.add_subparsers(dest="command", required=True)
    lines_cmd = commands.add_parser("lines", aliases=["line"],
                                    help="make one verse per number")
    lines_cmd.add_argument("numbers", nargs="+", metavar="NUMBER",
                           help="one number per verse, one digit 1-9 per table")
    poem_cmd = commands.add_parser("poem", help="make a poem from random numbers")
    poem_cmd.add_argument("-s", "--seed", type=int,
                          help="random seed, for a repeatable poem")
    poem_cmd.add_argument("-n", "--lines", type=int, default=4,
                          help="number of verses (default: 4)")
    args = parser.parse_args()

    cycle = MODES[args.mode]
    if args.command == "poem":
        if args.lines < 1:
            poem_cmd.error("--lines must be at least 1")
        rng = random.Random(args.seed)
        count = args.lines
    else:
        count = len(args.numbers)
    lines = [cycle[i % len(cycle)] for i in range(count)]

    if args.command == "poem":
        numbers = ["".join(rng.choice("123456789") for _ in tables)
                   for _, tables in lines]
    else:
        numbers = args.numbers
        for (_, tables), number in zip(lines, numbers):
            if len(number) != len(tables) or not all(c in "123456789" for c in number):
                lines_cmd.error(f"{number!r}: need {len(tables)} digits from 1 to 9 "
                                f"for this verse in --mode {args.mode}")

    verses = [(indent, make_words(tables, number))
              for (indent, tables), number in zip(lines, numbers)]
    for indent, words in verses:
        print(indent + capitalize(" ".join(words)))
    if args.translate:
        print()
        for indent, words in verses:
            print(indent + capitalize(" ".join(GLOSSES[w] for w in words)))


if __name__ == "__main__":
    sys.exit(main())
