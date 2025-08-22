<!--
[SPDX-FileCopyrightText: © 2025 Roger Wilson]
[SPDX-License-Identifier: MIT]
-->

# Yet More Functools

Summary

1. [sow and reap](#sow_and_reap). **reap** takes a function, its positional and keyword arguments, and returns a 2-tuple: (the result of a function call,  <u>**and**</u> collections of any values that **sow** is called on during the execution of that function).  **reap** may also be used to set up callbacks for values **sow** is called on.
2. [throw and catch](#throw_and_catch). **catch** takes a function, its positional and keyword arguments, and returns <u>**either**</u> the result of a function call <u>**or**</u> a 2-tuple: (tag, value) that **throw** is called on during the execution of that function.
3. [stash and grab](#stash_and_grab). **stash** takes a dict of tags and values, a function, its positional and keyword arguments and returns the result of calling that function. During the evaluation of that function the values stashed may be retrieved by a call to **grab** with the appropriate tag.  In some sense this function pair performs the opposite function to **sow** and **reap**.

---

## <a name="sow_and_reap"></a>sow and reap

These are two functions that work together to allow values to be returned from arbitrarily deep in the call hierarchy without modifying the return signatures of intermediate functions. This can be done either: by using **reap** to collect and return the values saved into collections by **sow** **<u>or</u>** by using **reap** to register callback functions that are called when **sow** is called (collections collect the values **sow** is called on, callbacks are called with the values **sow** is called on).

**sow** has a simple call signature. It takes one argument x and one keyword argument tag which defaults to None. It pushes the value x to the destination(s) identified by tag which is a hashable identifier or a sequence of them. **sow** returns the value it is called with.

```sow(x, [tag=None]) -> x```

**reap** takes a callable function **f** as its first argument; followed by **f**'s arguments, keyword-arguments and finally a keyword-argument tag which defaults to None. Tag can be a hashable identifier, a dict:{identifier: destination, ...} or a sequence of these. reap sets up destinations (collections, collection constructors or callbacks) for the values that **sow** is called on, **<u>anywhere</u>** in the call hierarchy below **f**. (See below for more information on tag).  **reap** returns a 2-tuple: (the value returned by **f**, a dict of tag:collection or tag:callback), where the collections will contain the values **sow** was called on.

```result, reaped = reap(f, *args, **kwargs, [tag=None])```

**reap** also has a context-manager equivalent called **reaper**.

---

### Tags

Most simply, tags are just hashable identifiers of destinations: collections that **sow** should append values to, or callbacks **sow** should invoke.

From the point of view of **sow**, the tag is **always** just the id of a destination for the values it is called on, that has already been set up by a call to a **reap** higher up the call hierarchy. This destination may be a collection, in which case the value is appended, or a callback function, in which case the callback is invoked on the value. If the destination is **None** then the call to **sow** does nothing. Tag may also be a sequence, in which case **sow** sends the value to all the destinations identified by that sequence.

Tags as far as **reap** is concerned can be more complicated and can take the form of:

1. A hashable id (corresponding to one in an inner **sow**).
2. A dict: {id: destination, ...}.
3. A sequence (not a tuple) of hashable ids or dicts or a mix of both.

A destination may be:

1. A zero-argument constructor for a collection with an append method.
2. An explicit collection with an "append" method.
3. A callback function (which requires **one positional argument** as **reap** will initially try to call it with no arguments to determine if it is a collection constructor).
4. **None**, which will effectively disable any corresponding **sow**(s).

The default tag of **reap** is **None**, this is also the default tag of **sow**. Within **reap**, if no destination is given for a tag, then the destination becomes the constructor "list" which then builds a list instance for each tag to hold the values **sow** is called on and return them via **reap**.

As mentioned above, if a **sow** is encountered with a tag that has not been set up by an enclosing **reap**, those values AND their tag, as a 2-tuple: (tag, value), will be pushed to the destination for the tag **None** <u>if this exists</u> and a warning emitted. If it does not, a different warning will be emitted.

### Nesting

If an outer **reap** calls a function that somewhere deeper in the call hierarchy calls an inner **reap** using the same tag, those values sown below the inner **reap** will be sent to destinations (collections or callbacks) set up by the inner **reap** on that tag. Only those values sown above that level will be sent to destinations belonging to the outer **reap**. This only applies if the tags are the same; but as the default tag is **None**, this can occur.

Internally **reap** maintains a FIFO stack of destinations for each tag. In most cases there would only be one. If there are more the one from the most deeply nested **reap** is used. As the call hierarchy is wound up, and each **reap** returns, **reap** removes the most recent destination for its tags from the stack and returns it. The stacks of destinations are held in a contextvars.ContextVar object and so should be threadsafe and async safe.

---

### Example 1 (See tests/sow_reap/example1.py) - Basic use

Imagine we are providing the function **f** to be called within another (library) function **g**. This **f** might be a function to set up a connection to an external service, or a function to be numerically optimized (see example_newton_raphson.py) or otherwise used by **g** (or still deeper calls made by **g**). We may need to know if **g ** is calling **f** at all, with what parameters, details of **f**'s internal state during execution, or how many times it is called; but we cannot modify **g**. However, within **f** we can use **sow** to save a record of those values. We can recover these values by wrapping the call to **g** with a call to **reap**.

```
def f(*args, **kwargs):
    sow((args, kwargs))
    # ... do some more stuff...
    return_value = "return value from f" 
    sow(return_value)
    return return_value
```

The function **g** we cannot change and possibly cannot easily see inside. Unknown to us, it calls **f** twice with two different values.

```
def g(f):
    # Do unknown stuff...
    a_value_g_needs = f("Unknown value 1")
    # ...more unknown stuff...
    another_value_g_needs = f("Unknown value 2")
    # ...do yet more  unknown stuff.
    return "Return value of g"
```

Calling **reap** on **g** returns a 2-tuple: (the return value of **g**, a list of the "reaped" values from **sow**). **reap** takes **g** as its first argument and then takes the arguments with which to invoke **g**.

```
print(reap(g, f))
```

This produces a 2-tuple: (the value returned by g, the dictionary returned by reap):

```
("Return value of g", {None: [(("Unknown value 1",), {}), "return value from f", (("Unknown value 2",), {}), "return value from f"]})
```

The reaped values are returned as a dictionary with the key **None**. This is because no tag has been specified in the calls to **sow** and **None** is the default tag for both **reap** and **sow**.

#### Callback alternative (See tests/sow_reap/example1_callback.py)

Instead of returning the values **sow** is called on as lists; **reap** may be used to set up callbacks that are invoked on each value **sow** is called on.

This may be achieved simply by passing the callback function into **reap**, as a 2-tuple with the relevant tag.

```
def callback(x):
    print(f"Callback called with '{x}'.")
```

```
print(reap(g, f, tag={None: callback}))
```

This will result in the callback running everytime **sow** is called, and finally **reap** returning a 2-tuple: (the return value of **g**, the dict from **reap** containing the callback).

```
Callback called with "(("Unknown value 1",), {})".
Callback called with "return value from f".
Callback called with "(("Unknown value 2",), {})".
Callback called with "return value from f".
("Return value of g", {None: <function callback at 0x0000023CC6564AE0>})
```

#### sow can be disabled from reap/reaper.

If we need to turn off the collection or callbacks of values by **sow** for a specific tag (including the default tag of **None**) we can do this by passing **None** as the collection, collection-constructor or callback in **reap** or **reaper**.

```
print(reap(g, f, tag={"input":callback_input, "return": None}))
```

This will produce:

```
Input callback called with "(("Unknown value 1",), {})".
Input callback called with "(("Unknown value 2",), {})".
("Return value of g", {"input": <function callback_input at 0x000002AB45DD4AE0>, "return": None})
```

The return **sow** has been disabled.

---

### Example 2 (See tests/sow_reap/example2.py) - as a context-manager

As an alternative to **reap**, **reaper** can be used in the guise of a context-manager...

```
with reaper() as r:
    print(g(f))
print(r())
```

This will produce:

```
Return value of g
{None: [(("Unknown value 1",), {}), "return value from f", (("Unknown value 2",), {}), "return value from f"]}
```

#### Callback alternative (See tests/sow_reap/example2_callback.py)

```
def callback(x):
    print(f"Callback called with '{x}\".")
```

```
with reaper(tag={None: callback}) as r:
    print(g(f))
print(r())
```

This will produce:

```
Callback called with "(("Unknown value 1",), {})".
Callback called with "return value from f".
Callback called with "(("Unknown value 2",), {})".
Callback called with "return value from f".
Return value of g
{None: <function callback at 0x000001F7B0D54AE0>}
```

Note: reap itself now returns the tag:callback function dictionary.

---

### Example 3 (See tests/sow_reap/example3.py) - with named tags

We can improve the separation of values in example 1 by using tags to set up different **reaps** for different values and **sow** to these different tags. Rather than everything that is passed to **sow** coming out in one big list, items will then be collected as multiple lists.

We can modify **f** so that the first **sow** uses a different tag to the second **sow**. A tag can be any hashable value. Without a tag specified a default tag of **None** is used.

```
def f(*args, **kwargs):
    sow((args, kwargs), tag="input")
    # ... do some more stuff...
    return_value = "return value from f" 
    sow(return_value, tag="return")
    return return_value
```

This will produce:

```
r() -> {input: [(("Unknown value 1",), {}), "return value from f", (("Unknown value 2",), {}), "return value from f"]}
```

If **sow** is called with a specific tag for which there is no corresponding outer **reap** a 2-tuple: (tag, value) will be pushed onto the tag=None collection (or callback) and a warning issued.

#### Callback alternative (See tests/sow_reap/example3_callback.py)

Setting up two callbacks, one for each tag.

```
def callback_input(x):
    print(f"Input callback called with '{x}'.")

def callback_return(x):
    print(f"Return callback called with '{x}'.")
```

```
print(reap(g, f, tag={"input": callback_input, "return": callback_return}))
```

This will produce:

```
Input callback called with "(("Unknown value 1",), {})".
Return callback called with "return value from f".
Input callback called with "(("Unknown value 2",), {})".
Return callback called with "return value from f".
("Return value of g", {"input": <function callback_input at 0x0000027EE6B94AE0>, "return": <function callback_return at 0x0000027EE6B956C0>})
```

---

## <a name="throw_and_catch"></a>throw and catch

**throw** and **catch** are also a pair of functions that work together to return values from deep in the call hierarchy. However, unlike **sow** and **reap**, when they do so, they immediately interrupt execution flow. As soon as **throw** throws a value the nearest encapsulating **catch**, for the same tag, will return.

**throw** has a simple call signature. It takes one argument x and one keyword argument tag which defaults to **None**. It throws the value x to the **catch** identified by tag, a hashable identifier or a sequence of them.  <u>**throw** interrupts execution flow at the point it is called.</u>  Internally **catch** sets up a conditional try...except block and **throw** conditionally raises a specific type of exception which carries the value throw was called on. If throw has been disabled by an enclosing call to catch then throw will simply return the value it was called on.

```throw(x, [tag=None]) -> x```

**catch** takes a callable function **f** as its first argument followed by **f**'s arguments and keyword-arguments and finally a keyword-argument tag which defaults to **None**. Tag can be a hashable identifier, a dict of {id: boolean, ...} or a sequence of these. The boolean in the tuple can be used to turn a **throw** below this call to **catch** on or off, for the given tag. **catch** catches values thrown by **throw** **<u>anywhere</u>** in the call hierarchy below **f**.  **catch** returns a 2-tuple: (the relevant tag, the value thrown by **throw**) or the value returned by **f** if no throws occur or none are relevant or active.

```tag, value = catch(f, *args, **kwargs, [tag=None])```

As with **sow** and **reap**, if a **throw** uses a tag for which there is no enclosing **catch** using that same tag but there is an enclosing **catch** using the default tag of None a 2-tuple (tag, value) will be received by that enclosing **catch** and a warning will be issued. If there is no enclosing catch, for the correct tag or None, then a different warning will be issued.

**catch** has a context-manager equivalent called **catcher**.

---

### Example 1 (See tests/throw_catch/example1.py)

Basic operation using the default tag of None.

```
def f(x):
    return throw(x) + 1
    
# Example A.
# The result is 2 because there is no surrounding catch so throw does nothing but return x, f returns normally.
# NOTE: Throw emits a warning as it is expecting to be called within a catch/catcher.
print(f"Example A -> {f(1)}")
flush_and_pause()

# Example B.
# The result is (None, 1`) because there is a surrounding catch so throw interrupts f.
print(f"Example B -> {catch(f, 1)}")
flush_and_pause()

# Example C.
# This exactly the same as B but with the tag and default setting.
# The result is (None, 1`) because there is a surrounding catch so throw interrupts f.
print(f"Example C -> {catch(f, 1, tag={None: True})}")
flush_and_pause()

# Example D.
# The result is 2 because although there is a surrounding catch we've turned
# the throw off for that tag (None) so throw does nothing, f returns normally.
# There is no warning because throw happens inside a catch/catcher.
print(f"Example D -> {catch(f, 1, tag={None: False})}")
flush_and_pause()

# Example E.
# The result is (None, 1) because there is a surrounding catch we've turned
# on throw for that tag (None) so throw interrupts f.
print(f"Example E -> {catch(f, 1, tag={None: True})}")
flush_and_pause()
```

produces...

```
Example A -> 2
..\yetmorefunctools\src\yet_more_functools\throw_catch\thow_catch.py:79: UserWarning: No tag None found as there is no outer catch for this tag OR tag=None.
  warnings.warn(f'No tag {tag} found as there is no outer catch for this tag OR tag=None.',


Example B -> (None, 1)


Example C -> (None, 1)


Example D -> 2


Example E -> (None, 1)
```

The call ```f(1)``` will return 2 because there is no encapsulating **catch** so the call to **throw** does nothing (throw simply returns the value it was called with but emits a warning about no encapsulating catch/catcher).

The call ```catch(f, 1)``` will return ```(None, 1)``` as within the encapsulating call to **catch** the **throw** becomes active and will interrupt the execution of **f**. The default tag is **None**.

We can control this from the **catch** using the tag keyword. The call ```catch(f, 1, tag={None: False})``` will again return 2 as this has disabled **throw** inside this **catch** using ```tag=None```. The call ```catch(f, 1, tag={None: True})``` will return ```(None, 1)```.

### Example 2 (See tests/throw_catch/example2.py) - with named tags

More advanced behaviour using different tags and the special behaviour of the None tag catching values thrown on other tags if they are not specifically being caught and catch/catcher is using the default tag=None.

```
def f(x):
    # Will try to **throw** on either of these two tags.
    return throw(x, tag=["tag0", "tag1"]) + 1
    
# Example A
# Returns (None, ("tag0", 1)), NOT the return value from f, as throw is not using the default tag=None.
# It's caught by the default tag of None (as no tag is specified in catch) which "hoovers up" anything
# thrown on another tag - with a warning.
print(f"Example A ->  {catch(f, 1)}")
flush_and_pause()

# Example A2
# Returns 2, the return value from f, as throw is not using the default tag=None.
# Disable None catching these other tags.
print(f"Example A2 ->  {catch(f, 1, tag={None: False})}")
flush_and_pause()

# Example B
# Returns ("tag0", 1) as catch is listening for one of the tags throw is using.
print(f"Example B -> {catch(f, 1, tag="tag0")}")
flush_and_pause()

# Example C
# Returns ("tag0", 1) as throw and catch are using the same tags, the first tag will be used.
print(f"Example C -> {catch(f, 1, tag=["tag0", "tag1"])}")
flush_and_pause()

# Example D
# Returns ("tag0", 1) still the first tag (in the order throw tried them) will be used."
print(f"Example D -> {catch(f, 1, tag=["tag1", "tag0"])}")
flush_and_pause()

# Example E
# "Returns ("tag1", 1) second tag as this is the only tag catch is listening for.
# Issues a warning because throw tries tag0 first and there is no catch for it.
print(f"Example E -> {catch(f, 1, tag=["tag1"])}")
flush_and_pause()

# Example F
# Returns , the return value from f, as now catch isn't listening for any tag throw is using
# and issues a warning about this in the process.
print(f"Example F -> {catch(f, 1, tag=["tag2"])}")
flush_and_pause()
```

produces...

```
Example A ->  (None, ('tag0', 1))
...\yetmorefunctools\src\yet_more_functools\throw_catch\thow_catch.py:74: UserWarning: No tag tag0 found as there is no outer catch for this specific tag.  Values will be sent to the tag=None catch which does exist as tuples of (tag, value).
  warnings.warn(


Example A2 ->  2


Example B -> ('tag0', 1)


Example C -> ('tag0', 1)


Example D -> ('tag0', 1)


Example E -> ('tag1', 1)
...\yetmorefunctools\src\yet_more_functools\throw_catch\thow_catch.py:79: UserWarning: No tag tag0 found as there is no outer catch for this tag OR tag=None.
  warnings.warn(f'No tag {tag} found as there is no outer catch for this tag OR tag=None.',


...\yetmorefunctools\src\yet_more_functools\throw_catch\thow_catch.py:79: UserWarning: No tag tag1 found as there is no outer catch for this tag OR tag=None.
  warnings.warn(f'No tag {tag} found as there is no outer catch for this tag OR tag=None.',
Example F -> 2
```

The call ```f(1)``` or the call ```catch(f, 1)``` will return ```2```. As in the first case, there is no encapsulating **catch** and in the second case **catch** will be listening for throws on the two specific tags given, not on the default tag of **None**.

The calls ```catch(f, 1, tag="tag0")```, ```catch(f, 1, tag=["tag0", "tag1"])``` and ```catch(f, 1, tag=["tag1", "tag0"])``` all return ```(tag0, 1)``` because **throw** is trying to use tag0 first.

The call ```catch(f, 1, tag=["tag1"])``` will return ```(tag1, 1)``` because **throw** is also trying to use tag1 and in this case **catch** is not listening for tag0.

The call ```catch(f, 1, tag=["tag2"])``` will return ```2``` because **throw** isn't trying to use tag2 and so **throw** will again do nothing and **f** will return normally.

### Example 3 (See tests/throw_catch/example3.py) - as a context-manager

catcher allows function calls to be wrapped in a context-manager "with" block that listens for calls to **throw** (on tags passed into catcher). catcher emits a callable (ct in the examples below) to be called after the managed block exits to pick up any value thrown during the execution of the block. If the block executes normally and nothing is thrown inside then the result of calling ct will be **None**. If anything is thrown during execution then execution of the block will be interrupted and the result of calling ct() will be a 2-tuple: (tag, thrown value).

```
def f(x):
    # Will try to throw on either of these two tags.
    return throw(x, tag=["tag0", "tag1"]) + 1
    
# Example A
# Returns (None, ("tag0", 1)) as throw is not using the default tag=None.
# And there is a warning because catch isn't using the tags throw is.
with catcher() as ct:
    print(f"Example A -> {f(1)}")  # Doesn't happen.
print(f"Example A -> ct() = {ct()}")
flush_and_pause()

# Example B
# Returns ("tag0", 1) as catch is listening for one of the tags throw is using.
with catcher(tag="tag0") as ct:
    print(f"Example B -> {f(1)}")  # Doesn't happen.
print(f"Example B -> ct() = {ct()} ")
flush_and_pause()

# Example C
# Returns ("tag0", 1) as throw and catcher are using the same tags, the first tag will be used.
with catcher(tag=["tag0", "tag1"]) as ct:
    print(f"Example C -> {f(1)}")  # Doesn't happen.
print(f"Example C -> ct() = {ct()}")
flush_and_pause()

# Example D
# Returns ("tag0", 1) still the first tag (in the order throw got them) will be used.
# Catcher is listening for both tag1 and tag0 BUT throw uses tag0 first and first wins.
with catcher(tag=["tag1", "tag0"]) as ct:
    print(f"Example D -> {f(1)}")  # Doesn't happen.
print(f"Example D -> ct() = {ct()}")
flush_and_pause()

# Example E
# Returns ("tag1", 1) second tag as this is the only tag catch is listening for.
# Catcher is only listening for tag1 and throw tries tag0 first (no catcher) and then tag1.
# There is a warning because there is no catcher for tag0.
with catcher(tag=["tag1"]) as ct:
    print(f"Example E -> {f(1)}")  # Doesn't happen.
print(f"Example E -> ct() = {ct()}")
flush_and_pause()

# Example F
# The function f actually returns because throw doesn't do anything.
# So ct() which contains the thrown value is None.
with catcher(tag=["tag2"]) as ct:
    print(f"Example F -> {f(1)}")  # This DOES happen because there is no catcher for tag0 or tag1.
print(f"Example F -> ct() = {ct()}") # So this is None.
```

produces...

```
Example A -> ct() = (None, ('tag0', 1))
...\yetmorefunctools\src\yet_more_functools\throw_catch\thow_catch.py:74: UserWarning: No tag tag0 found as there is no outer catch for this specific tag.  Values will be sent to the tag=None catch which does exist as tuples of (tag, value).
  warnings.warn(


Example B -> ct() = ('tag0', 1) 


Example C -> ct() = ('tag0', 1)


Example D -> ct() = ('tag0', 1)


Example E -> ct() = ('tag1', 1)
...\yetmorefunctools\src\yet_more_functools\throw_catch\thow_catch.py:79: UserWarning: No tag tag0 found as there is no outer catch for this tag OR tag=None.
  warnings.warn(f'No tag {tag} found as there is no outer catch for this tag OR tag=None.',


Example F -> 2
Example F -> ct() = None
...\yetmorefunctools\src\yet_more_functools\throw_catch\thow_catch.py:79: UserWarning: No tag tag1 found as there is no outer catch for this tag OR tag=None.
  warnings.warn(f'No tag {tag} found as there is no outer catch for this tag OR tag=None.',
```
---

## <a name="stash_and_grab"></a>stash and grab

These are two functions that work together to allow values to be passed deep into the call hierarchy without modifying the call signatures of intermediate functions.  **stash** takes in a dict, a function f and its positional and keyword arguments.  It makes the values of that dict available to any code executed within the call to f via calls to grab using the appropriate tags.

**grab** has a simple call signature.  It takes one argument tag which defaults to None.  It returns the value set up for that tag by an enclosing call to **stash**.

```v = grab([tag=None])```

**stash** takes a dict, setting up the tags and values for the call to f as well as f's arguments and returns the result of the call to **f**.  It makes the values in the dict **stashed** available during the evaluation of the function **f**.

```r = stash(stashed, f, *args, **kwargs)```

**stash** also has a context-manager equivalent called **stasher**.

### Example 1 (See tests/stash_grab/example1.py)

```
def f(x):
    return x+grab()
```

or functionally identical but more explicit:-

```
def f(x):
    return x+grab(tag=None)
```

Then running the following.

```
result = stash({None: 2}, f, 1)
```

The value result will be 3 which is the sum of 1 from the input and 2 from the stashed value of 2 (under the default tag of None for **grab**).

### Example 2 (See tests/stash_grab/example2.py) - as a context-manager

```
def f(x):
    return x+grab()
```

or functionally identical but more explicit:-

```
def f(x):
    return x+grab(tag=None)
```

Then running the following.

```
with stasher({None: 2}):
    result = f(1)
```

The value result will be 3 which is the sum of 1 from the input and 2 from the stashed value of 2 (under the default tag of None for **grab**).

### Example 3 (See tests/stash_grab/example3.py) - nesting

```
def f(x):
    with stasher({"Nested": 5}):
        temp = g(x)
    return temp * grab(tag="Global") + grab(tag="Nested")


def g(x):
    return x * grab(tag="Global") + grab(tag="Nested")


with stasher({"Global": 2, "Nested": 3}):
    result = f(1)
```

This will produce a result of 17.  The call to **stasher** inside **f** means that the value associated with the tag **Nested** supersedes the one set outside, so for the duration of the call to **g** it becomes 5 not 3.  Outside of this inner context managed block it reverts to the value set up by the outer context managed block of 3.

The same effect can be produced using stash but this is perhaps less clear.

```
def f(x):
    return stash({"Nested": 5}, g, x) * grab(tag="Global") + grab(tag="Nested")


result = stash({"Global": 2, "Nested": 3}, f, 1)
