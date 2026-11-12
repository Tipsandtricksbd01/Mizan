import json, re, sys, os, wave
import pocketsphinx
from pocketsphinx import Decoder
wav, txt, out = sys.argv[1:4]
md = os.path.join(os.path.dirname(pocketsphinx.__file__), "model", "en-us")
dic = os.path.join(md, "cmudict-en-us.dict")
known = set()
for line in open(dic):
    known.add(line.split()[0])
raw = open(txt).read()
words = re.findall(r"[a-z']+", raw.lower().replace("-", " ").replace("...", " "))
extra = {"ebay": "IY B EY", "bridgeville": "B R IH JH V IH L", "lawnmowers": "L AO N M OW ER Z"}
oov = sorted({w for w in words if w not in known})
print("OOV:", oov, file=sys.stderr)
d = Decoder(hmm=os.path.join(md, "en-us"), dict=dic, lm=None)
for w in oov:
    if w in extra:
        d.add_word(w, extra[w], True)
    else:
        sys.exit(f"no pron for {w}")
d.set_align_text(" ".join(words))
with wave.open(wav) as f:
    data = f.readframes(f.getnframes())
d.start_utt(); d.process_raw(data, full_utt=True); d.end_utt()
print('hyp:', (d.hyp().hypstr[:120] if d.hyp() else None), file=sys.stderr)
res = []
for sg in d.seg():
    if sg.word in ("<s>", "</s>", "<sil>") or sg.word.startswith('['): continue
    res.append({"w": re.sub(r'\(\d+\)$','',sg.word), "s": round(sg.start_frame / 100, 2), "e": round((sg.end_frame+1) / 100, 2)})
json.dump(res, open(out, "w"), indent=0)
print(len(res), "words aligned of", len(words), file=sys.stderr)
