from climbz import create_app


app = create_app("test_100")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--database", help="database to use", default="prod")

    args = parser.parse_args()

    app = create_app(args.database)
    app.run(debug=True)
