from argparse import ArgumentParser
from pathlib import Path
from pprint import pprint
from subprocess import run

from ._internal import convert_to_transform, write_pipeline


def main() -> None:
    script, pipeline, update, tag = parse_args()
    transform = convert_to_transform(script, tag)
    if pipeline:
        write_pipeline(pipeline, transform)
        if update:
            run(["pachctl", "update", "pipeline", "-f", str(pipeline), "--reprocess"])
    else:
        pprint(transform, indent=2)


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("script", type=Path, metavar="FILE")
    parser.add_argument("--pipeline", default=None, type=Path)
    parser.add_argument("--tag", default=None, type=str)
    parser.add_argument("--update", action="store_true")
    args = parser.parse_args()
    if not args.script.exists():
        raise FileNotFoundError(args.script)
    return args.script, args.pipeline, args.update, args.tag


if __name__ == "__main__":
    main()
