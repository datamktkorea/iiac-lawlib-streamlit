"""한국어 자동 띄어쓰기를 위한 커맨드 라인 인터페이스(CLI) 스크립트.

이 스크립트는 파일이나 표준 입력을 통해 텍스트를 받아 띄어쓰기를 교정한 후 출력합니다.
"""

# -*- coding: utf-8 -*-
import argparse
import sys

from pykospacing import Spacing


def get_parser():
    """커맨드 라인 인자 파서를 생성합니다.

    Returns:
        argparse.ArgumentParser: 설정된 인자 파서 객체.
    """
    parser = argparse.ArgumentParser(description="Python script for automatic Korean word spacing")

    parser.add_argument("infile", type=argparse.FileType("r"), default=sys.stdin)
    parser.add_argument("outfile", type=argparse.FileType("w"), nargs="?", default=sys.stdout)
    parser.add_argument(
        "-o",
        dest="overwrite",
        action="store_true",
        default=False,
        help="Overwrite the result itself",
    )

    return parser


def main(args=sys.argv[1:]):
    """메인 실행 함수.

    Args:
        args (list, optional): 커맨드 라인 인자 리스트. Defaults to sys.argv[1:].

    Returns:
        int: 성공 시 0, 변경 사항이 있을 시 1 (diff 스타일).
    """
    args = get_parser().parse_args(args)

    source = args.infile.read()

    result = "\n"
    spacing = Spacing()
    for line in source.splitlines():
        result += spacing(line)
        result += "\n"

    if args.overwrite:
        args.infile.close()
        with open(args.infile.name, "w", encoding=args.infile.encoding) as f:
            f.write(result)
    else:
        args.outfile.write(result)

    return 0 if (source == result) else 1


if __name__ == "__main__":
    sys.exit(main())
