"""Step 4 - build the final vertical MP4 with ffmpeg (no GPU needed).

  python assemble.py plan.json                  # clips + music + sfx + voice -> build/final.mp4
  python assemble.py plan.json --upscale        # Real-ESRGAN anime upscale first (if installed)
  python assemble.py plan.json --card "3 MONTHS LATER" --card-at 2.8

Each clip is trimmed to its shot duration, scaled to out_size (default 1080x1920), set to the plan fps,
joined with hard cuts; every voice/sfx is placed at its "t" seconds, music ducks under it, and the mix is
loudness-normalised to -14 LUFS / -1 dBTP (Shorts/Reels/TikTok standard).
"""
import argparse
import json
from pathlib import Path

from common import load_plan, run, work_dir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--out", help="output file (default build/final.mp4)")
    ap.add_argument("--card", help="optional full-screen text card, e.g. '3 MONTHS LATER'")
    ap.add_argument("--card-at", type=float, default=None)
    ap.add_argument("--card-dur", type=float, default=0.8)
    ap.add_argument("--font", default="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    a = ap.parse_args()

    plan, wd = load_plan(a.plan), work_dir(a.plan)
    W, H = plan.get("out_size", [1080, 1920])
    fps = plan.get("fps", 30)
    audio = wd / "audio"
    out = Path(a.out) if a.out else wd / "final.mp4"

    # 1) normalise + trim each shot
    norm = []
    for s in plan["shots"]:
        src, dst = wd / "clips" / f"{s['id']}.mp4", wd / "clips" / f"n_{s['id']}.mp4"
        run(["ffmpeg", "-y", "-v", "error", "-i", src, "-t", s["duration"], "-an",
             "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},"
                    f"fps={fps},setsar=1,tpad=stop_mode=clone:stop_duration=5",
             "-t", s["duration"], "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", dst])
        norm.append(dst)
    lst = wd / "clips" / "list.txt"
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in norm))
    video = wd / "video_only.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", video])
    total = sum(s["duration"] for s in plan["shots"])

    if a.card:
        at = a.card_at if a.card_at is not None else plan["shots"][0]["duration"]
        txt = a.card.replace(":", r"\:").replace("'", r"\'")
        carded = wd / "video_card.mp4"
        run(["ffmpeg", "-y", "-v", "error", "-i", video, "-vf",
             f"drawbox=x=0:y=0:w=iw:h=ih:color=black@1:t=fill:enable='between(t,{at},{at + a.card_dur})',"
             f"drawtext=fontfile={a.font}:text='{txt}':fontcolor=white:fontsize={W // 11}:"
             f"x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,{at},{at + a.card_dur})'",
             "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", carded])
        video = carded

    # 2) collect timed audio items
    items = []
    mm = audio / "mmaudio_items.json"
    if mm.exists():
        items += json.loads(mm.read_text())
    else:
        items += [{"t": s["t"], "file": str(audio / f"sfx_{i}.wav"), "vol": s.get("vol", 1.0)}
                  for i, s in enumerate(plan.get("sfx", []))]
    items += [{"t": v["t"], "file": str(audio / f"voice_{i}.wav"), "vol": v.get("vol", 1.0)}
              for i, v in enumerate(plan.get("voice", []))]
    items = [x for x in items if Path(x["file"]).exists()]
    music = audio / "music.wav"

    inputs, chains, labels = ["-i", video], [], []
    for n, x in enumerate(items, start=1):
        ms = int(x["t"] * 1000)
        inputs += ["-i", x["file"]]
        chains.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,volume={x['vol']},"
                      f"adelay={ms}|{ms}[e{n}]")
        labels.append(f"[e{n}]")
    if not labels and not music.exists():
        run(["ffmpeg", "-y", "-v", "error", "-i", video, "-c", "copy", out])
        print("done (silent):", out)
        return
    fx = None
    if labels:
        chains.append(f"{''.join(labels)}amix=inputs={len(labels)}:duration=longest:normalize=0[fx]")
        fx = "[fx]"
    if music.exists():
        m = len(items) + 1
        inputs += ["-stream_loop", "-1", "-i", music]
        vol = plan.get("music", {}).get("volume", 0.3)
        chains.append(f"[{m}:a]aresample=48000,aformat=channel_layouts=stereo,volume={vol},"
                      f"afade=t=out:st={max(0, total - 1)}:d=1[mus]")
        if fx:
            chains.append("[fx]asplit=2[fx1][key]")
            chains.append("[mus][key]sidechaincompress=threshold=0.05:ratio=6:attack=5:release=300[duck]")
            chains.append("[duck][fx1]amix=inputs=2:duration=first:normalize=0[pre]")
        else:
            chains.append("[mus]anull[pre]")
    else:
        chains.append("[fx]anull[pre]")
    chains.append(f"[pre]atrim=0:{total},apad=whole_dur={total},loudnorm=I=-14:TP=-1:LRA=11[a]")

    run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(chains),
         "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
         "-t", total, "-movflags", "+faststart", out])
    print("done:", out)


if __name__ == "__main__":
    main()
