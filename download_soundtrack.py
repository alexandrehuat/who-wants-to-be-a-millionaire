import argparse
import shutil
import subprocess
import sys

from env import RSC_DIR, SOUND_DIR


def parse_tracks():
    path = RSC_DIR / "tracklist.tsv"
    tracks = []
    with open(path) as f:
        for line in f.readlines():
            track_info = line.strip(" \n").split("\t")
            tracks.append(track_info)
    return tracks


def proc_run(cmd, verbose=False):
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if verbose:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)


def ytdl_mp3(title, url, from_=-1, to=-1, reset=True, verbose=False, tmp="/tmp/out.mp3"):
    path = (SOUND_DIR / title).with_suffix(".mp3")
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or reset:
        proc_run(f'yt-dlp -x --audio-format mp3 -o {tmp} {url}', verbose=verbose)
        if sum(map(int, [from_, to])) < 0:
            proc_run(f'mv {tmp} {path}')
        else:
            from_ = f"-ss {from_}" if int(from_) > 0 else ""
            to = f"-to {to}" if int(to) > 0 else ""
            proc_run(f'ffmpeg {from_} {to} -i {tmp} -c copy {path}', verbose=verbose)

    dl = path.exists()
    print("Success" if dl else "Failure", path, sep=": ")
    return dl


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-0", "--reset", action="store_true", help="erase previous sound files")
    parser.add_argument("-v", "--verbose", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.reset:
        shutil.rmtree(SOUND_DIR, ignore_errors=True)
    for track_info in parse_tracks():
        ytdl_mp3(*track_info, reset=args.reset, verbose=args.verbose)
