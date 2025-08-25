from typing import Any, Generator, Callable

from . import themes
from .types import TreeNode, Theme


def default_render(key: str, value: Any) -> str:
    return f'{key}: {value}'


def tree(
    name: str,
    data: Any,
    theme: Theme = themes.Ascii,
    render: Callable = default_render
) -> Generator[str, None, None]:
    """
    Генератор для построения и обхода дерева данных

    Args:
        name: Название дерева
        data: Входные данные для построения дерева
        theme: Тема оформления

    Yields:
        str: Строка с информацией о текущем узле
    """
    if not isinstance(data, (dict, list, tuple)):
        raise TypeError('Data must be a dict, list, or tuple')

    def _build_tree(data: Any, parent_key: str = '') -> TreeNode:
        """Рекурсивно строит дерево TreeNode из вложенных dict/list/tuple."""
        node = TreeNode(value=parent_key or 'root')

        if isinstance(data, dict):
            for key, value in data.items():
                child = _build_tree(value, str(key))
                node.children.append(child)
        elif isinstance(data, (list, tuple)):
            for idx, item in enumerate(data):
                child = _build_tree(item, f'[{idx}]')
                node.children.append(child)
        else:
            node.value = render(parent_key, data)

        return node

    root = _build_tree(data)
    yield f'{name}:'

    def _traverse(
        node: TreeNode,
        prefix: str = '',
        is_last: bool = True
    ) -> Generator[str, None, None]:
        if prefix:
            connector = theme.corner if is_last else theme.branch
            line = prefix + connector + node.value
        else:
            line = node.value
        if line != 'root':
            yield line[4:]

        new_prefix = prefix + (theme.tab if is_last else theme.vertical)
        for i, child in enumerate(node.children):
            yield from _traverse(
                child,
                new_prefix,
                i == len(node.children) - 1
            )

    yield from _traverse(root)
