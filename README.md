# myclimbz developer guide

This guide is for developers. It explains how to run and develop the app. If you are interested in contributing, please have a look at the issues. For big features, please write on the issue page first, before starting to work on them!

If you want to host the app yourself, I described my deployment in `DEPLOY.md`.

## Index

1. [Run the app locally](#run-the-app-locally)
2. [Creating forms](#creating-forms)
3. [Creating filters](#creating-filters)
4. [Updating the prod DB](#update-the-prod-database)

## Run the app locally

### Clone the repository

```bash
git clone git@github.com:carlosfranzreb/myclimbz.git
```

### Create the .env file

The `.env` file stores the environment variables required by docker compose:

```bash
FLASK_DEBUG=1  # set to 1 for hot reloading, 0 for attaching the debugger
CLIMBZ_DB_URI=sqlite:///test_100.db
DISABLE_LOGIN=1
PROD=0

RECAPTCHA_PUBLIC_KEY=1234
RECAPTCHA_PRIVATE_KEY=abcd

MAIL_USERNAME=random@mail.com
MAIL_PASSWORD=mypassword1
```

- `FLASK_DEBUG` can be set to 0 or 1, depending on whether you want to allowa hot reloading or debugging:
  - `FLASK_DEBUG=1`: changes made to the code will be loaded onto the container immediately. Attaching a debugger is not possible.
  - `FLASK_DEBUG=0`: hot reloading is disabled, but you can attach a debugger to the container. This can be done in VS Code with the launch config named `Python: Remote Attach` defined in `.vscode/launch.json`.
- `CLIMBZ_DB_URI` defines the path to the database file. The test file shown above is already part of the repository, and is the one used in the tests. You can create a new one with `scripts/db/create_db.py`. Add the flag `--test` to add mock data to the created database.
- `DISABLE_LOGIN` can be set to 0 or 1. When it's set to 1, the climber with ID 1 is automatically logged in when the app starts. This is useful for development to skip the login page.
- `PROD` can be set to 0 or 1. When it's set to 1, the app is run with gunicorn (as done in production). For local development, this variable should be set to 0.
- To get RECAPTCHA v3 keys see [the official documentation](https://developers.google.com/recaptcha/docs/v3).
- The e-mail credentials are used for password recovery. When a user clicks on "Forgot password", they are sent an e-mail with a new password from this account.

### Build and run the app

This can be done easily with docker compose: run `docker compose up --build` from the root directory of the repository.

To install Docker, visit [their installation guide](https://docs.docker.com/engine/install/)

### Run the tests

Once the app runs, all tests should pass. You can check this by running `pytest` from the root directory of the repository.

Before running the tests, you need to install the requirements for the test environment. They are written in the file `requirements-test.txt`. I usually install them in a local conda environment, like this:

```bash
conda create -p ./venv python=3.10
conda activate ./venv
pip install -r requirements-test.txt
```

Once the test environment is ready, you can run the tests with the command `pytest`.

## Creating forms

We have custom functionality that can be used when creating forms with WTForms.

### Adding datalists to input fields

HTML datalists allow you to provide a list of predefined options for an input field. They are typically used with input elements of type "text" or "search". We use them e.g. to show the user existing areas while she is typing.

To add a datalist to an input field, you need to add the list of options as a `datalist` attribute to the form object. Here is an example from the session form:

```python
self.area.datalist = [
    area.name for area in Area.query.order_by(Area.name).all()
]
```

#### Adding fields if a datalist element is chosen

If you want to hide certain fields of your form when an option from the datalist is chosen, add their IDs as a string, with each ID separated with a comma, to the `toggle_ids` attribute. This behaves similarly as the toggling with a checkbox, explained below.

### Toggling field display with a checkbox

Some fields should only be displayed if a checkbox is checked. For example, in the session form, date and conditions are only necessary when the session involves real climbing, not only adding a projects. Therefore, if the checkbox "Only adding projects" is checked, those two fields are hidden.

To hide fields when a checkbox is checked, define their IDs in the `toggle_ids` attribute of the checkbox as a string containing the IDs, separated by commas and **without spaces**. The template will then add an on change event listener to the field with the JS function `checkboxToggle`, which receives the checkbox ID and the value of the `toggle_ids` attribute.

This is how it is done for the example mentioned above:

```python
self.is_project_search.toggle_ids = "date,conditions"
```

### Toggling defined by two fields

The toggling functionlaity described above can also be applied to fields with datalists. When the value in the input field can be found in the datalist, the toggling will be performed.

Toggling can also be decided in conjunction with a related field. This is currently only being used by route names and their sectors, as together they must be unique. When the route name is part of the datalist, what happens with the toggling depends on the value of the sector field:

- If the sector field is empty, it is automatically filled with the value found in the mapping of route names to sectors. If the route name is present in multiple sectors, the last occurrence will be passed. Toggling will then take place, as the route-sector combination exists in the database.
- If the sector field is not empty and its value differs from the existing route-sector combination, it is considered a new route and hence toggling will not happen.
- If the given sector matches with the one expected by the route, toggling occurs.

The relationship is defined with two attributes that are added to the input (in our case here, the route name field):

```python
form.name.relation_field = "sector"
form.name.relation_data = [0] * len(form.name.datalist)
```

The `relation_data` list maps indices of the route name's datalist to indices of the sector's datalist. You can find this implementation in `climbz/forms/route.py`.

## Creating filters

The list of filters is defined in `filters/main.js`, in the variable `FILTERS`. When the user wants to apply some filters, the function `filter_data` of the same file is called. This function calls the method `filter_value` for each filter and climb. Besides the `filter_value` method, filter classes must have a `reset` method, where its original values are set.

You can find the currently implemented filters in the folder `filters/widgets`. The whole filter menu is constructed in the file `filters/filters.js`.

## Update the prod database

If you change the scheme of the database, you need to create a new production database and add the old data. This can be done from the sqlite CLI with `ATTACH`, which allows you to insert data from one database to another. Here is an example:

```sql
ATTACH DATABASE "instance/prod_copy.db" AS "OLD";
INSERT INTO climber SELECT * from OLD.climber;
```
