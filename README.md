# myclimbz developer guide

This guide is for developers: how to run and develop the app. Information about deployment can be found in `./DEPLOY.md`.

## Index

1. [Creating forms](#creating-forms)
2. [Creating filters](#creating-filters)
3. [Updating the prod DB](#update-the-prod-database)

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
ATTACH DATABASE "instance/prod_hetzner.db" AS "OLD";
INSERT INTO climber SELECT * from OLD.climber;
```
