# Review: Bridgeville

## Creative calls
- 1920x1080 (HyperFrames default; the plan speaks in wide shots). No burned-in captions (not asked for).
- Flat cartoon diorama look (SPEC.md). The town on the phone is a slab of land standing on the screen.
- eBay is named only in the voice and a cartoon headline; the listing UI is generic, no real logo.
- 95526 on the mailbox is Bridgeville's ZIP code. Prices on screen are only the ones the script states
  ($5,000 start, $1,777,877 final, "about $1 million less"); the 2004 sale price is not shown.
- Music and effects are synthesized in code (tools/sound.py): HeyGen's catalog needs a sign-in and
  Hugging Face (local MusicGen) is blocked by this environment's network policy.

## Measured
- Word timings: forced alignment of the given script with pocketsphinx (tools/align.py -> tools/words.json).
- check: passes; warnings kept: small texture text (listing subtitles, bill labels, the mailbox ZIP in wide
  shots), falling bills under the read-time floor (they are a pile, not reading), two contrast notes on
  white stroked titles over sky.
- Render: 121.5 s, 1920x1080, -16.5 LUFS integrated, true peak -2.5 dBTP, no clipping. Music is silent from
  67.33 s ("But") to 70.3 s as planned. Stamp hit at 0.29 s, BID click at 71.58 s, sign thud at 119.16 s.
- Sound was measured, not heard.

## Weakest shots / next
- s02 mist reads as flat white ellipses; a softer layered fog would sell the redwoods better.
- s06 highway shows one van at a time; overlapping lanes would feel more like a rush.
- s08 empty driveway: the dashed outline of the buyer is abstract; the pushed-in camera carries it.
