

# DTree: Python Library for Building and Traversing Trees

DTree is a Python library for building and traversing trees. It provides a simple and efficient way to create and manipulate tree data structures.

## Features

* Create trees from dictionaries, lists, and tuples
* Traverse trees using generators
* Support for different tree themes (ASCII, Unicode)
* Customizable tree rendering and themes

## Installation

To install DTree, run the following command:
```bash
pip install pydtree
```

## Usage

Here is an example of how to create and traverse a tree using DTree:
```python
from dtree import tree

# Create a tree from a dictionary
data = {
    'root': {
        'child1': 'value1',
        'child2': 'value2',
        'child3': {
            'grandchild1': 'value3',
            'grandchild2': 'value4'
        }
    }
}

# Traverse the tree using a generator
for line in tree('my_tree', data):
    print(line)
```
This will output the following tree structure:
```
my_tree:
`-- root
    +-- child1: value1
    +-- child2: value2
    `-- child3
        +-- grandchild1: value3
        `-- grandchild2: value4
```

## Themes

DTree supports different tree themes, including ASCII and Unicode. You can customize the theme by passing a `theme` parameter to the `tree` function:
```python
from dtree import tree, themes

for line in tree(
        'my_tree',
        data,
        theme=themes.Unicode
):
    print(line)
```
This will output the following tree structure using Unicode characters:
```
my_tree:
└── root
    ├── child1: value1
    ├── child2: value2
    └── child3
        ├── grandchild1: value3
        └── grandchild2: value4
```

## Custom Themes

You can also create your own custom themes by defining a Theme object. Here is an example:

```python
from dtree.types import Theme
from dtree import tree

MyTheme = Theme(
    vertical='|   ',
    branch='+-- ',
    corner='`-- ',
    tab='    '
)

data = {...}

for line in tree(
        'my_tree',
        data,
        theme=MyTheme
):
    print(line)
```
This will output the tree structure using your custom theme.

## Customization

You can customize the tree rendering by passing a `render` function to the `tree` function:
```python
from dtree import tree

def custom_render(key, value):
    return f"{key} ({value})"

for line in tree(
        'my_tree',
        data,
        render=custom_render
):
    print(line)
```
This will output the following tree structure with custom rendering:
```
my_tree:
+-- child1 (value1)
+-- child2 (value2)
`-- child3 (value3)
```

## Contributing

If you'd like to contribute to DTree, please fork the repository and submit a pull request.

## License

DTree is licensed under the MIT License.