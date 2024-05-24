# myclimbz developer guide

This guide is for developers: how to run and develop the app.

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
