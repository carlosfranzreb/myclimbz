from climbs import create_app


DEBUG = False
app = create_app(DEBUG)


if __name__ == "__main__":
    app.run(debug=True)
