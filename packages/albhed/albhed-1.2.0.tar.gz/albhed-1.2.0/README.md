# Al Bhed

Simple CLI and Library that translates Text into Al Bhed

Python:
```python
>>> from albhed import albhed
>>>
>>> albhed("Hello, World!")
'Rammu, Funmt!'
>>>
>>> albhed("Rammu, Funmt!", revert=True)
'Hello, World!'
```

Shell:
```shell
$ albhed Hello, World!
Rammu, Funmt!

$ albhed -r Rammu, Funmt!
Hello, World!
```
