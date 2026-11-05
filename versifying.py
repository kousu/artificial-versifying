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
from itertools import takewhile

# Copied from versifying.js, with spelling mistakes fixed. The pentameter
# tables are from Jeffrey M. Binder's versifying.js,
# https://jeffreymbinder.net/apps/av/versifying.js
# Each table is 9 words interleaved with a stride of 9; a space ends a word.
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


# How to say each word, respelled for English speakers, using the classical
# (restored) pronunciation: c is always "k", g is always hard, v sounds like
# "w", æ like "eye", œ like "oy". Capitals mark the stressed syllable.
# Vowels: ah as in "father", eh as in "pet", ay as in "they", ih as in "pit",
# ee as in "see", oh as in "go", oo as in "moon".
PHONETICS = {
    # adjectives
    "aspera": "AHS-peh-rah", "ardua": "AR-doo-ah", "barbara": "BAR-bah-rah",
    "effera": "EF-feh-rah", "horrida": "HOR-rih-dah", "ignea": "IG-neh-ah",
    "impia": "IM-pih-ah", "improba": "IM-proh-bah", "lurida": "LOO-rih-dah",
    "martia": "MAR-tih-ah", "noxia": "NOK-sih-ah", "perfida": "PER-fih-dah",
    "pessima": "PES-sih-mah", "sordida": "SOR-dih-dah",
    "tetrica": "TET-rih-kah", "tristia": "TRIS-tih-ah",
    "turbida": "TOOR-bih-dah", "turpia": "TOOR-pih-ah",
    "cruenta": "kroo-EN-tah", "dolosa": "doh-LOH-sah",
    "maligna": "mah-LIG-nah", "molesta": "moh-LES-tah",
    "nefanda": "neh-FAHN-dah", "proterva": "proh-TER-wah",
    "pudenda": "poo-DEN-dah", "sinistra": "sih-NIS-trah",
    "superba": "soo-PER-bah",
    # nouns
    "acta": "AHK-tah", "agmina": "AHG-mih-nah", "arma": "AR-mah",
    "astra": "AHS-trah", "bella": "BEL-lah", "castra": "KAHS-trah",
    "crimina": "KREE-mih-nah", "damna": "DAHM-nah", "dicta": "DIK-tah",
    "dogmata": "DOG-mah-tah", "dona": "DOH-nah", "facta": "FAHK-tah",
    "fata": "FAH-tah", "fœdera": "FOY-deh-rah", "iura": "YOO-rah",
    "iurgia": "YOOR-ghih-ah", "labra": "LAH-brah", "lumina": "LOO-mih-nah",
    "pignora": "PIG-noh-rah", "pocula": "POH-koo-lah",
    "prælia": "PRY-lih-ah", "scorta": "SKOR-tah", "sidera": "SEE-deh-rah",
    "signa": "SIG-nah", "sistra": "SIS-trah", "somnia": "SOM-nih-ah",
    "tela": "TAY-lah", "tempora": "TEM-poh-rah", "verba": "WER-bah",
    "verbera": "WER-beh-rah", "vincla": "WIN-klah", "vina": "WEE-nah",
    "vota": "WOH-tah",
    # pronouns, short phrases
    "aliis": "AH-lih-ees", "domi": "DOH-mee", "ferunt": "FEH-roont",
    "foris": "FOH-rees", "inquam": "IN-kwahm", "malis": "MAH-lees",
    "mihi": "MIH-hee", "palam": "PAH-lahm", "pati": "PAH-tee",
    "patet": "PAH-tet", "puto": "POO-toh", "reor": "REH-or",
    "scio": "SKIH-oh", "sequi": "SEH-kwee", "tibi": "TIH-bee",
    "tuis": "TOO-ees", "vides": "WIH-dayss", "viris": "WEE-rees",
    "viro": "WIH-roh", "mera": "MEH-rah", "nova": "NOH-wah",
    # verbs
    "causabunt": "kow-SAH-boont", "concedunt": "kon-KAY-doont",
    "concludunt": "kon-KLOO-doont", "confirmant": "kon-FEER-mahnt",
    "conglomerant": "kon-GLOM-eh-rahnt", "consummant": "kon-SOOM-mahnt",
    "monstrabunt": "mohn-STRAH-boont", "perficiunt": "per-FIH-kih-oont",
    "portabunt": "por-TAH-boont", "portendunt": "por-TEN-doont",
    "prædicunt": "pry-DEE-koont", "præmonstrant": "pry-MOHN-strahnt",
    "prænarrant": "pry-NAR-rahnt", "præscribunt": "pry-SKREE-boont",
    "præstabunt": "pry-STAH-boont", "procurant": "proh-KOO-rahnt",
    "producunt": "proh-DOO-koont", "promittunt": "proh-MIT-toont",
    "promulgant": "proh-MOOL-gahnt", "proritant": "proh-REE-tahnt",
    "significant": "sig-NIH-fih-kahnt",
    # adverbs and final adjectives
    "acerba": "ah-KER-bah", "certa": "KER-tah", "dira": "DEE-rah",
    "dura": "DOO-rah", "multa": "MOOL-tah", "nigra": "NIG-rah",
    "plane": "PLAH-nay", "prava": "PRAH-wah", "quædam": "KWY-dahm",
    "sæpe": "SY-peh", "sæva": "SY-wah", "semper": "SEM-per",
    "sola": "SOH-lah", "tantum": "TAHN-toom",
}

# Each mode cycles through these table sets, one per verse. Elegiac couplets
# alternate a hexameter with a pentameter; the pentameter is indented, as is
# customary in print.
MODES = {
    "orig": [("", TABLES["orig"])],
    "revised": [("", TABLES["revised"])],
    "pentameter": [("", TABLES["pentameter"])],
    "elegiac": [("", TABLES["orig"]), ("    ", TABLES["pentameter"])],
}


def read_word(table, digit):
    """Count on from digit to 9 (wrapping after 9), then read every 9th cell up to a blank."""
    i = 9 - digit  # steps taken: digit+1, ..., 9; digit 9 wraps round to 9 steps
    start = (i - 1) % 9  # 0-based column
    return "".join(takewhile(lambda c: c != " ", table[start::9]))


def make_words(tables, number):
    return [read_word(t, int(d)) for t, d in zip(tables, number)]


def capitalize(verse):
    return verse[0].upper() + verse[1:]


def layout(mode, count):
    """Return (indent, tables) for each of count verses, cycling through the mode."""
    cycle = MODES[mode]
    return [cycle[i % len(cycle)] for i in range(count)]


def lines(mode, numbers):
    """Make one verse per number. Raise ValueError if a number doesn't fit."""
    verses = []
    for (indent, tables), number in zip(layout(mode, len(numbers)), numbers):
        if len(number) != len(tables) or not all(c in "123456789" for c in number):
            raise ValueError(f"{number!r}: need {len(tables)} digits from 1 to 9 "
                             f"for this verse in --mode {mode}")
        verses.append((indent, make_words(tables, number)))
    return verses


def poem(mode, count, seed=None):
    """Make count verses from random digits; the same seed gives the same poem."""
    rng = random.Random(seed)
    return [(indent, make_words(tables, [rng.randint(1, 9) for _ in tables]))
            for indent, tables in layout(mode, count)]


def print_verses(verses, translate=False, phonetics=False):
    for indent, words in verses:
        print(indent + capitalize(" ".join(words)))
    if phonetics:
        print()
        for indent, words in verses:
            print(indent + " ".join(PHONETICS[w] for w in words))
    if translate:
        print()
        for indent, words in verses:
            print(indent + capitalize(" ".join(GLOSSES[w] for w in words)))


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("-m", "--mode", choices=MODES, default="orig",
                        help="which tables to use (default: orig); elegiac "
                        "alternates original hexameters and pentameters")
    parser.add_argument("-t", "--translate", action="store_true",
                        help="follow the poem with a word-for-word English gloss")
    parser.add_argument("-p", "--phonetics", action="store_true",
                        help="follow the poem with how to pronounce it")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="print debugging to stderr")
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

    if args.command == "poem":
        if args.lines < 1:
            poem_cmd.error("--lines must be at least 1")
        # Pick the seed here, not inside random, so --debug can show it.
        seed = random.randrange(2**32) if args.seed is None else args.seed
        if args.debug:
            print(f"seed: {seed}", file=sys.stderr)
        verses = poem(args.mode, args.lines, seed)
    elif args.command in ("lines", "line"):
        try:
            verses = lines(args.mode, args.numbers)
        except ValueError as e:
            lines_cmd.error(str(e))

    print_verses(verses, args.translate, args.phonetics)


if __name__ == "__main__":
    sys.exit(main())
