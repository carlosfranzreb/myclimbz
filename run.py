from climbs import create_app
import argparse


TEST = False
SHORT = False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t", "--test", help="run app in test mode", choices=["true", "false"]
    )
    parser.add_argument(
        "-s", "--short", help="run app in short test mode", choices=["true", "false"]
    )

    args = parser.parse_args()
    if args.test:
        TEST = True if args.test == "true" else False
    if args.short:
        SHORT = True if args.short == "true" else False

    app = create_app(TEST, SHORT)
    app.run(debug=True)
