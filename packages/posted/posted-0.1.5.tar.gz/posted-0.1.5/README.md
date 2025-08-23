
# posted
Interfacing with message-broker functionality


To install:	```pip install posted```


# Examples

## ReactiveScope

A scope that reacts to writes by computing associated functions, themselves writing in the scope, creating a chain reaction that propagates information through the scope.

Parameters
----------

* `func_nodes : Iterable[ReactiveFuncNode]`
    The functions that will be called when the scope is written to.
* `scope_factory : Callable[[], MutableMapping]`
    A factory that returns a new scope. The scope will be cleared by calling this
    factory at each call to `.clear()`.

Examples
--------

First, we need some func nodes to define the reaction relationships.
We'll stuff these func nodes in a DAG, for ease of use, but it's not necessary.

```python
>>> from meshed import FuncNode, DAG
>>>
>>> def f(a, b):
...     return a + b
>>> def g(a_plus_b, d):
...     return a_plus_b * d
>>> f_node = FuncNode(func=f, out='a_plus_b')
>>> g_node = FuncNode(func=g, bind={'d': 'b'})
>>> d = DAG((f_node, g_node))
>>>
>>> print(d.dot_digraph_ascii())
<BLANKLINE>
                a
<BLANKLINE>
            │
            │
            ▼
            ┌────────┐
    b   ──▶ │   f    │
            └────────┘
    │         │
    │         │
    │         ▼
    │
    │        a_plus_b
    │
    │         │
    │         │
    │         ▼
    │       ┌────────┐
    └─────▶ │   g_   │
            └────────┘
            │
            │
            ▼
<BLANKLINE>
                g
<BLANKLINE>
```

Now we make a scope with these func nodes.

```python
>>> s = ReactiveScope(d)
```

The scope starts empty (by default).

```python
>>> s
<ReactiveScope with .scope: {}>
```

So if we try to access any key, we'll get a KeyError.

```python
>>> s['g']  # doctest: +IGNORE_EXCEPTION_DETAIL
Traceback (most recent call last):
    ...
KeyError: 'g'
```

That's because we didn't put write anything in the scope yet.

But, if you give ``g_`` enough data to be able to compute ``g`` (namely, if you
write values of ``b`` and ``a_plus_b``), then ``g`` will automatically be computed.

```python
>>> s['b'] = 3
>>> s['a_plus_b'] = 5
>>> s
<ReactiveScope with .scope: {'b': 3, 'a_plus_b': 5, 'g': 15}>
```

So now we can access ``g``.

```python
>>> s['g']
15
```

Note though, that we first showed that ``g`` appeared in the scope before we
explicitly asked for it. This was to show that ``g`` was computed as a
side-effect of writing to the scope, not because we asked for it, triggering the
computation

Let's clear the scope and show that by specifying ``a`` and ``b``, we get all the
other values of the network.

```python
>>> s.clear()
>>> s
<ReactiveScope with .scope: {}>
>>> s['a'] = 3
>>> s['b'] = 4
>>> s
<ReactiveScope with .scope: {'a': 3, 'b': 4, 'a_plus_b': 7, 'g': 28}>
>>> s['g']  # (3 + 4) * 4 == 7 * 4 == 28
28
```
