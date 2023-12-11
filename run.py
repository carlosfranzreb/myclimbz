from climbs import create_app


TEST = False
app = create_app(TEST)


if __name__ == "__main__":
    app.run(debug=True)
