## Pycomponents

Template engine with a focus on reusability

### Examples
```
ul(class="list"):
    for val in ["Hello", False, "World"]:
        li(class="list-item"):
            if val:
                - {val}
            else:
                - Something
```
