import argparse
from . import __version__
from .core import slugify

def main():
    parser = argparse.ArgumentParser(prog="spyronx", description="CLI mẫu cho gói spyronx")
    parser.add_argument("--version", action="store_true", help="Hiển thị phiên bản và thoát")
    sub = parser.add_subparsers(dest="cmd")

    p_slug = sub.add_parser("slugify", help="Chuyển chuỗi thành slug")
    p_slug.add_argument("text", help="Chuỗi đầu vào")

    args = parser.parse_args()

    if args.version:
        print(__version__)
        return

    if args.cmd == "slugify":
        print(slugify(args.text))
        return

    parser.print_help()

if __name__ == "__main__":
    main()