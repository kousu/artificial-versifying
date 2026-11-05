# Artificial Versifying

[John Peter's *Artificial Versifying, or the School-Boy's Recreation* (London, 1677)](https://archive.org/details/bim_early-english-books-1641-1700_artificial-versifying-th_pater-john_1677)
promises that "any one of ordinary capacity, who knows the A, B, C and can count 9,
though he understands not one word of Latin" can produce "hundreds of hexameter
verses, which shall be true Latin, true verse, and good sense."

The original preface says, in wonderfully sarcasticly florid language, that the book was published to take the wind out of the sails of tradesmen who boast of their work without deeply understanding the systems they use to do it. It shows that anyone can appear to be a latinist and a poet without much effort.

## The algorithm

1. Choose six digits from 1 to 9, for example `467182`.
2. Digit *n* of the six picks one word from Table *n*.
3. Each table holds 9 words, one for each digit. The words are stored
   interleaved (see below).
4. Write the six words in order. The result is a Latin hexameter.

With six independent slots of 9 choices each, the tables yield
9⁶ = 531,441 verses.

## The obfuscation: a scytale

Each table is a plain list of 9 words written interleaved, and printed at a row width that _isn't_ 9. This makes the words run diagonally across the grid and appear random to a casual observer. There are also some stray 'b's thrown on the end as filler and further obsfucation.

Table 1 of the original, as printed (11 wide):

```
i s a t t h t p p m o
s u r o u e e p r p r
i r r s r i d e b s r
p s f a i r i t i i i
i   d a d i d a m d b
a   a a a   a a b   b
      b
```

The same table wrapped at 9:

```
i s a t t h t p p
m o s u r o u e e
p r p r i r r s r
i d e b s r p s f
a i r i t i i i i
  d a d i d a m d
b a   a a a   a a
b   b       b
```

Columns read *impia, sordida, aspera, turbida, tristia, horrida, turpia,
pessima, perfida*. The same words can be read on the diagonals of the 11-wide table: impia is the first 'i', then the 'm' in the second last column, and then the 'p' in the row below and two steps _back_, then the 'i' the row below that and two more steps back, etc.

This works like a [**scytale**](https://en.wikipedia.org/wiki/Scytale): a strip of text whose consecutive letters sit a fixed distance apart, unreadable until it's wound around a rod of the correct size. Here "count to 9" plays the part of having the correct rod.

### Reading a word out of a table

The book's rule (pp. 9–10) is 'count to 9, write the letter out you land on, repeat', but it initializes the count to the user's chosen input digit *d* so that the first index they actually land on is *9-d* -- and if they chose *d=9*, they wrap to *d=0* before starting.

In python, where we have to adjust for zero-based indexing:

```
start = (9 - d -1)%9
stride = 9
join(table[start::stride])
```

> [!warning]
> The algorithm is actually a while loop, stopping at the terminator character ■. But it's easier to understand in this vector slicing form.

Worked examples from the book:

| Digits   | Verse                                        |
|----------|----------------------------------------------|
| `467182` | Tristia fata tibi producunt sidera prava     |
| `879889` | Impia facta scio prædicunt sidera sæpe       |
| `989978` | Perfida dicta scio confirmant somnia multa   |

> [!warning]
> For `989978` the book prints *mihi* instead of *scio* as the third word.
> The tables give *scio*, and the other two 9s in that example decode as
> expected, so this is probably a misprint in the 1677 example.



## How grammar and meter are imposed

All of the poetry is in the choice of words. Every word in a table can follow
every word in the table before it, so each table is a **slot** whose 9 words
are fully interchangeable:

- **Agreement.** All words in a slot have the same grammatical form, so any
  combination agrees. In the original tables:

  | Table | Contents                                   | Example     |
  |-------|--------------------------------------------|-------------|
  | 1     | adjective, neuter plural                   | *tristia*   |
  | 2     | noun, neuter plural                        | *fata*      |
  | 3     | dative pronoun or noun, or a short verb    | *tibi*, *scio* |
  | 4     | verb, 3rd person plural                    | *producunt* |
  | 5     | noun, neuter plural                        | *sidera*    |
  | 6     | adverb, or neuter plural adjective         | *semper*, *multa* |

  Because neuter nominative and accusative plurals look the same, either
  noun (Table 2 or Table 5) can be read as the subject. Every reading comes out
  as an ominous statement about fate and the stars, so the verses
  also make loose "sense".

- **Meter.** Latin verse is quantitative: it counts long and short syllables,
  not stresses, and it doesn't rhyme. A hexameter is six feet, each a dactyl
  (long-short-short) or a spondee (long-long), with the last foot shortened.
  Every word in a slot has the same pattern of long and short syllables
  (for example *tristia*, *impia*, *pessima* are all long-short-short), so
  every combination scans.

The **Pentameter** tables apply the same method to the second line of an
elegiac couplet, so an Original hexameter can be paired with a pentameter.
They come from Jeffrey M. Binder's
[versifying.js](https://jeffreymbinder.net/apps/av/versifying.js), part of
his interactive [*Artificial Versifying*](https://jeffreymbinder.net/?p=304).

The **English** tables are word-for-word glosses of the Original Latin
tables, slot for slot. They have no meter or rhyme and keep the Latin word
order.

## References

* [John Peter. *Artificial Versifying, or the School-Boy's Recreation* (London, 1677)](https://archive.org/details/bim_early-english-books-1641-1700_artificial-versifying-th_pater-john_1677)
* [jeffreymbinder. *Artificial Versifying*. (New York, 2019)](https://jeffreymbinder.net/?p=304)
* [Jeffrey M. Binder. `versifying.js`](https://jeffreymbinder.net/apps/av/versifying.js): source of the pentameter tables

## Appendix A: The tables as printed

### Table 1

```
i s a t t h t p p m o
s u r o u e e p r p r
i r r s r i d e b s r
p s f a i r i t i i i
i   d a d i d a m d b
a   a a a   a a b   b
      b
```

### Table 2

```
d f f b i v v d d i a
a e u o e o a c c t l
r t r n m t t a l a a
b a n a a   a     a
a     b   b i   b
```

### Table 3

```
m t i v m v r a s i i
n i a i e l c h b q r
l d o i i i i u o i e
r i o     a   s s   s
  b r m b     b     r
b
```

### Table 4

```
p p m p p c c p c r r
o o r a o r o æ o n r
o u n o n d c s t m s
c d f i u t a i a e u
i c r r b t b d c r u
a a u t u u u m n n b
n u n n n a t t u t n
t t t n     n   t
  t b b t r   b r b
b b
```

### Table 5

```
s s p f c t d i p i
o i œ r e o u o d m
g d i m g r c e n n
e m p m g u r i o r
i o a i l a a r a n
r t a a     a   a a
a     b r   b
```

### Table 6

```
m q c t p s p s s u u
e a l o r e æ l æ r n
a l a m p t d t t n a
v p e a a a u e   a e
    m   m   b   r r b
  b   d b r
```

## Appendix B: Decoded Tables

| Digit | Table 1 | Table 2 | Table 3 | Table 4 | Table 5 | Table 6 |
|---|---|---|---|---|---|---|
| 1 | pessima | dona | aliis | producunt | iurgia | semper |
| 2 | turpia | verba | reor | concedunt | dogmata | prava |
| 3 | horrida | vota | vides | causabunt | tempora | sola |
| 4 | tristia | iura | malis | promittunt | crimina | plane |
| 5 | turbida | bella | viro | portabunt | fœdera | tantum |
| 6 | aspera | fata | inquam | monstrabunt | pignora | certa |
| 7 | sordida | facta | tibi | procurant | somnia | quædam |
| 8 | impia | dicta | mihi | prædicunt | sidera | multa |
| 9 | perfida | damna | scio | confirmant | pocula | sæpe |

## Appendix C: English translation

This translates the original latin words to english. It won't produce well-metered poetry but they at least produce sentences.

| Digit | Table 1 | Table 2 | Table 3 | Table 4 | Table 5 | Table 6 |
|---|---|---|---|---|---|---|
| 1 | very bad | gifts | for others | produce | quarrels | always |
| 2 | foul | words | I think | yield | doctrines | evil |
| 3 | horrid | vows | you see | will cause | times | alone |
| 4 | sad | vows | for the evil | promise | offenses | clearly |
| 5 | disordered | wars | for a man | will bring | compacts | only |
| 6 | harsh | fates | I say | will show | pledges | certain |
| 7 | sordid | deeds | for you | take care of | dreams | certain |
| 8 | wicked | words | for me | foretell | stars | many |
| 9 | faithless | losses | I know | confirm | cups | often |
