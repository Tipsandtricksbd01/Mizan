# Bridgeville: the town sold on eBay

GOAL:    the viewer laughs at the buyer who vanished and leaves with the closing joke, "bring the money".
OUTPUT:  HyperFrames, 1920 x 1080, 30 fps.
TIME:    121.5 s x 30 = 3645 frames. Voice (`assets/voice/narration.mp3`, 119.7 s) is the clock;
         every cue is a word time from forced alignment (`tools/words.json`).
LOOK:    flat cartoon diorama, bold outlines.
         ground: daylight sky #9AD4F0 -> horizon #FBE6C2 (vertical gradient, no texture); meadow #9BCB6E,
         hills #7DB46C, redwoods #2E5B3B / #3F7A4C, bark #8E3B2A, road #5A5566 with #F6D35B dashes.
         ink #23202E: every outline 5 px (4 px on trees), round joins.
         accent red #D7263D only on SOLD / FOR SALE stamps, the struck price and the BID button.
         gold #F2B134 for money and the retreat's light.
         display: Archivo Black, 96-150 px, white fill with 8 px ink stroke and a 6 px ink drop; body: Inter 700, 40-56 px.
         light: flat; one contact shadow under hero objects, ink at 18% opacity, offset 0 / 10 px.
OBJECTS: the town (10 coloured houses, 4 log cabins, a road with dashes, redwoods), a mailbox stamped 95526,
         a phone (ink body, rounded 56 px), a rubber stamp (red border 10 px, rotated -12 deg),
         the buyer (teal shirt, red cap, paper shopping bag), the two owners (orange and blue shirts),
         news vans with roof dishes, arrow cursors, a listing card with a red BID button, newspapers,
         a wall calendar, a wooden retreat sign, repair bills (paper with red REPAIR header), a FOR SALE sign.
MOTION:  arrivals back.out(1.7) (damping ~0.5, playful) on scale/position, never on opacity;
         camera power2.inOut 0.6-2 s; exits power3.in, 40% shorter than entrances;
         stamps: 0.14 s power4.in slam from 2.4x, 2-frame squash; text: blur 8 px -> 0 in 0.2 s;
         staggers 60 ms (houses), 40 ms (cursors).
SHOTS (absolute s):
  s01  0.00-7.95   town on a giant phone; SOLD slams at 0.2; "$1.78 MILLION" at 3.7; buyer poofs at 6.76; zoom into the town
  s02  7.95-17.05  sky "2002" at 8.4; glide down into misty redwoods; BRIDGEVILLE sign 10.7; SF 260 mi highway sign 13.9
  s03 17.05-23.45  wide town; 82 ACRES boundary 17.2; 10 houses pop 18.6; 4 cabins 19.8; push to mailbox 95526 at 22.4
  s04 23.45-32.85  owners + yard sign; tumbleweed "nobody bit" 26.5; online grid: lawnmower | TOWN | baseball cards
  s05 32.85-38.85  listing card, current bid $5,000 at 34.1; pull back to a globe pinging at 36.6
  s06 38.85-47.90  news vans race 39.1; phones ring 40.6; map upside down 42.2; cursor storm on BID 44.5; last ticket 46.2
  s07 47.90-62.85  calendar month 48.2; ~250 bids 49.6; clock hits zero 53.2; price spins to $1,777,877 at 59.6; SOLD 59.9; 2x 61.0
  s08 62.85-70.30  owners cheer 63.9; headlines 65.1; music stops on "But" 67.35; push in on empty driveway
  s09 70.30-79.05  cursor clicks BID 71.6; yard sale "I'LL TAKE IT!" 73.6; empty wallet + moth 77.2
  s10 79.05-86.85  driveway day to night 80.4; empty mailbox 82.0; calendar 2003 at 83.7; owners sigh 85.3
  s11 86.85-93.60  "2004" 87.1; SOLD (for real) 88.7; $1.78M struck, "about $1M less" 91.3
  s12 93.60-99.95  golden light: retreat sign 94.6; repair bills bury the new owner 98.6-99.6
  s13 99.95-108.9  phone again, back on eBay 101.4; SOLD slams 104.6; stamp peels and falls 107.4-108.1
  s14 108.9-121.5  "20+ YEARS LATER" 110.2; mailbox 115.2; pull out wide 116; FOR SALE lands on "money" 119.16; hold to end
SOUND:   voice at -16 LUFS; synthesized music bed under it (about -14 dB below voice) that cuts dead on "But" (67.35)
         and returns sparse and minor at 70.3; effects one frame after their picture: stamp slams, poof, whooshes,
         pops on houses, cursor clicks, counter ticks, paper rustle, sign thud.
BANNED:  dark void grounds; glow, bloom, particles as decoration; purple/blue gradients; glass cards;
         corner labels; logo in a corner; everything fading and sliding up; text moving while read;
         eBay's real logo or colours (the listing UI is generic).
QA:      0.3 (thumbnail: phone, town, buyer, SOLD), 6.9 (poof), 12, 20, 30.5, 45, 60, 68.5, 74, 99.5, 107.8, 120.
