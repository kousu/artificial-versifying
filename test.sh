#!/bin/sh
# Test artificial-versifying: each check runs it through `uv run` with the
# given arguments and compares stdout and stderr, together, and the exit
# status with what's expected.
#
# Usage: ./test.sh

project=$(dirname "$0")

pass=0
fail=0

# check NAME STATUS ARGS... <<EXPECTED
check() {
	name=$1 status=$2
	shift 2
	expected=$(cat)
	actual=$(PYTHONDONTWRITEBYTECODE=1 uv run --quiet --project "$project" artificial-versifying "$@" 2>&1)
	got=$?
	# Python 3.14 quotes argparse's "choose from" errors and 3.13 doesn't.
	actual=$(printf '%s\n' "$actual" | sed "/choose from/s/'//g")
	# A traceback is always a bug, never an expected output.
	case $actual in
	*Traceback*)
		fail=$((fail + 1))
		echo "FAIL: $name (crashed)"
		printf '%s\n' "$actual"
		return
		;;
	esac
	if [ "$actual" = "$expected" ] && [ "$got" -eq "$status" ]; then
		pass=$((pass + 1))
	else
		fail=$((fail + 1))
		echo "FAIL: $name (exit $got, expected $status)"
		printf '%s\n' "$expected" > "${TMPDIR:-/tmp}/expected.$$"
		printf '%s\n' "$actual" | diff -u "${TMPDIR:-/tmp}/expected.$$" - | sed 1,2d
		rm -f "${TMPDIR:-/tmp}/expected.$$"
	fi
}

# book example 467182
check "book example 467182" 0 line 467182 <<'EOF'
Tristia fata tibi producunt sidera prava
EOF

# book examples, several lines
check "book examples, several lines" 0 lines 467182 879889 989978 <<'EOF'
Tristia fata tibi producunt sidera prava
Impia facta scio prædicunt sidera sæpe
Perfida dicta scio confirmant somnia multa
EOF

# line and lines are aliases
check "line and lines are aliases" 0 line 467182 879889 <<'EOF'
Tristia fata tibi producunt sidera prava
Impia facta scio prædicunt sidera sæpe
EOF

# every digit 9 reads index 8
check "every digit 9 reads index 8" 0 lines 999999 <<'EOF'
Perfida damna scio confirmant pocula sæpe
EOF

# revised tables, fixed typos
check "revised tables, fixed typos" 0 -m revised lines 111111 345555 444444 <<'EOF'
Lurida scorta palam prænarrant crimina nigra
Martia vincla tuis portendunt verbera acerba
Aspera vincla domi producunt lumina prava
EOF

# pentameter tables
check "pentameter tables" 0 -m pentameter lines 12345 99999 44444 <<'EOF'
Turpia conglomerant facta cruenta viris
Noxia procurant astra maligna mihi
Sordida perficiunt dicta cruenta scio
EOF

# elegiac alternates and indents
check "elegiac alternates and indents" 0 -m elegiac lines 467182 12345 879889 99999 <<'EOF'
Tristia fata tibi producunt sidera prava
    Turpia conglomerant facta cruenta viris
Impia facta scio prædicunt sidera sæpe
    Noxia procurant astra maligna mihi
EOF

# translate
check "translate" 0 --translate lines 467182 879889 <<'EOF'
Tristia fata tibi producunt sidera prava
Impia facta scio prædicunt sidera sæpe

Sad fates for you produce stars evil
Wicked deeds I know foretell stars often
EOF

# elegiac translate
check "elegiac translate" 0 -m elegiac -t lines 467182 12345 <<'EOF'
Tristia fata tibi producunt sidera prava
    Turpia conglomerant facta cruenta viris

Sad fates for you produce stars evil
    Foul heap up deeds bloody for men
EOF

# seeded poem
check "seeded poem" 0 poem --seed 1677 <<'EOF'
Aspera damna viro producunt crimina tantum
Aspera dona aliis prædicunt dogmata prava
Impia vota tibi causabunt pignora prava
Tristia dicta reor monstrabunt tempora quædam
EOF

# seeded elegiac poem, short options
check "seeded elegiac poem, short options" 0 -m elegiac -t poem -s 1677 -n 4 <<'EOF'
Aspera damna viro producunt crimina tantum
    Perfida significant arma dolosa malis
Turpia dicta vides procurant tempora certa
    Tristia perficiunt iura molesta tibi

Harsh losses for a man produce offenses only
    Faithless signify arms deceitful for the evil
Foul sayings you see take care of times sure
    Sad accomplish rights troublesome for you
EOF

# seeded pentameter poem
check "seeded pentameter poem" 0 -m pentameter poem -s 5 -n 6 <<'EOF'
Improba concludunt astra sinistra nova
Sordida significant facta molesta tibi
Tetrica perficiunt acta maligna malis
Sordida significant dicta pudenda viris
Impia præscribunt facta molesta mera
Tetrica consummant facta sinistra vides
EOF

# debug shows the seed
check "debug shows the seed" 0 -d poem -s 1677 -n 2 <<'EOF'
seed: 1677
Aspera damna viro producunt crimina tantum
Aspera dona aliis prædicunt dogmata prava
EOF

# debug does nothing for lines
check "debug does nothing for lines" 0 --debug line 467182 <<'EOF'
Tristia fata tibi producunt sidera prava
EOF

# phonetics and translation, in that order
check "phonetics and translation" 0 -p -t -m elegiac lines 467182 12345 <<'EOF'
Tristia fata tibi producunt sidera prava
    Turpia conglomerant facta cruenta viris

TRIS-tih-ah FAH-tah TIH-bee proh-DOO-koont SEE-deh-rah PRAH-wah
    TOOR-pih-ah kon-GLOM-eh-rahnt FAHK-tah kroo-EN-tah WEE-rees

Sad fates for you produce stars evil
    Foul heap up deeds bloody for men
EOF

# number too short
check "number too short" 2 lines 12 <<'EOF'
usage: artificial-versifying lines [-h] NUMBER [NUMBER ...]
artificial-versifying lines: error: '12': need 6 digits from 1 to 9 for this verse in --mode orig
EOF

# digit 0 rejected
check "digit 0 rejected" 2 lines 467180 <<'EOF'
usage: artificial-versifying lines [-h] NUMBER [NUMBER ...]
artificial-versifying lines: error: '467180': need 6 digits from 1 to 9 for this verse in --mode orig
EOF

# wrong length for pentameter line
check "wrong length for pentameter line" 2 -m elegiac lines 123456 123456 <<'EOF'
usage: artificial-versifying lines [-h] NUMBER [NUMBER ...]
artificial-versifying lines: error: '123456': need 5 digits from 1 to 9 for this verse in --mode elegiac
EOF

# bad number stops whole run
check "bad number stops whole run" 2 lines 467182 12 <<'EOF'
usage: artificial-versifying lines [-h] NUMBER [NUMBER ...]
artificial-versifying lines: error: '12': need 6 digits from 1 to 9 for this verse in --mode orig
EOF

# poem needs at least one line
check "poem needs at least one line" 2 poem -n 0 <<'EOF'
usage: artificial-versifying poem [-h] [-s SEED] [-n LINES]
artificial-versifying poem: error: --lines must be at least 1
EOF

# no subcommand
check "no subcommand" 2 467182 <<'EOF'
usage: artificial-versifying [-h] [-m {orig,revised,pentameter,elegiac}] [-t]
                             [-p] [-d]
                             {lines,line,poem} ...
artificial-versifying: error: argument command: invalid choice: 467182 (choose from lines, line, poem)
EOF

# removed english mode
check "removed english mode" 2 -m english lines 467182 <<'EOF'
usage: artificial-versifying [-h] [-m {orig,revised,pentameter,elegiac}] [-t]
                             [-p] [-d]
                             {lines,line,poem} ...
artificial-versifying: error: argument -m/--mode: invalid choice: english (choose from orig, revised, pentameter, elegiac)
EOF

# mode after subcommand rejected
check "mode after subcommand rejected" 2 lines -m elegiac 467182 <<'EOF'
usage: artificial-versifying [-h] [-m {orig,revised,pentameter,elegiac}] [-t]
                             [-p] [-d]
                             {lines,line,poem} ...
artificial-versifying: error: unrecognized arguments: -m
EOF

echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
