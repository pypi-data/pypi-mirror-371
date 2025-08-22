# pydebugger

Print objects with inspection details and color.


## Installing


Install and update using `pip`

```python:

    $ pip install pydebugger
```

pydebugger supports Python 2 and newer, Python 3 and newer, and PyPy.


## Example

What does it look like? Here is an example of a simple pydebugger program:

```python:
    # hello.py

    from pydebugger.debug import debug
    
    debug(variable1="data1", debug=True)
```

And what does it look like when it's run and printed in color:

```bash

    $ python hello.py 
    2024:09:12~18:21:45:822673 C:\TEMP\hello.py -> variable1: data1 -> TYPE:<class 'str'> -> LEN:5 -> [C:\TEMP\hello.py] [3] PID:21428
```

You can set OS Environment variable DEBUG=1 or DEBUG=True to avoid having to use the parameter "debug=1" or "debug=True"

```python:

    from pydebugger.debug import debug
    
    debug(variable1="data1")
```

you can run "debug.py" to provide a debug server with client support using environment variables:

```bash:
    # on terminal 

	export DEBUG_SERVER=1
	export DEBUGGER_SERVER=127.0.0.1:50001
    # then run hello.py
```
this will send all info to debug server running on '127.0.0.1' on port 50001

You can also run the debug server on a specific port number:
```bash
$ debug.py 50005
```

[![Video Example](https://img.youtube.com/vi/XWL72_oLnJ4/0.jpg)](https://www.youtube.com/watch?v=XWL72_oLnJ4)


Support
--------

*   Python 2.7+, Python 3.x
*   Windows, Linux

## author
[Hadi Cahyadi](mailto:cumulus13@gmail.com)
    

[![Buy Me a Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/cumulus13)

[![Donate via Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/cumulus13)

[Support me on Patreon](https://www.patreon.com/cumulus13)