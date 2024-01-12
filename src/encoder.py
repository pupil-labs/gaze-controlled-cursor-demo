from enum import Enum

from widgets.property_widget import get_properties

from actions import Action

def create_property_dict(obj):
    prop_dict = {}
    props = get_properties(obj.__class__)
    for property_name, prop in props.items():
        value = prop.fget(obj)

        if isinstance(value, Action):
            obj = value
            value = {
                "__module__": obj.__class__.__module__,
                "__class__": obj.__class__.__name__,
                **create_property_dict(obj)
            }

        elif isinstance(value, Enum):
            value = value.name


        prop_dict[property_name] = value

    return prop_dict
