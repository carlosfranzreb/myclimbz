from climbs import create_app


app = create_app("test_100")


if __name__ == "__main__":
    app.run(debug=True)
