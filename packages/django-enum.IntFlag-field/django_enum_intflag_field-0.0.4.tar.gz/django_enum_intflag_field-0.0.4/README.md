# django-enum.IntFlag-field

This gives you a model field that takes a Python stdlib [enum.IntFlag](https://docs.python.org/3/library/enum.html#enum.IntFlag) class, stores flag combinations as an IntegerField, and allows convenient bitwise containment predicates through the Django ORM.

In other words: a bitfield in your DB, with all the conveniences of enum.IntFlag.

### What is a bitfield, even
What's a bitfield? A bitfield is a field of bits :-). Like `0110`.
You can use it to represent a bunch of booleans that in turn represent presence or absence of flags, or anything you want — perhaps sandwich toppings!

Let's say these 4 field positions represent Butter, Gouda, Rocket and Tomato. Then `0110` means we have a sandwich without Butter, but with Gouda and Rocket, but no Tomato.

A bitfield is thus a string of bits. And it just so happens that an integer is *also* a string of bits! `0110` is the number 6, look:

```pycon
>>> 0b0110
6
```

And it just so happens that both Python and databases have facilities to work with numbers-as-bitfields or bitfields-as-numbers.
A database 64-bit BigIntegerField can accommodate a Python [enum.IntFlag](https://docs.python.org/3/library/enum.html#enum.IntFlag) class
with up to 63 members. The first member gets the bit position for the number 1 (2⁰, thus bit position 0), and since the maximum positive value
of a 64-bit signed integer is 2⁶³-1, and since we need powers of 2 for our members... that leaves bits 0-62, and thus 63 members.

When you use this ModelField, a Django check will validate your associated enum.IntFlag class to make sure your values are within bounds.


## Installing
`pip install django-enum.IntFlag-field`. Or equivalent.
There's no need to add anything to your `settings.INSTALLED_APPS`.


## How do I even
Example model and parafernalia, inspired by the [test models.py](src/django_testapp_intflagfield/models.py):

```python
from enum import IntFlag, auto
from django.db import models
from enum_intflagfield import IntFlagField


class SandwichTopping(IntFlag):
    BUTTER = auto()  # becomes 1  (2**0)
    GOUDA  = auto()  # becomes 2  (2**1)
    ROCKET = auto()  # becomes 4  (2**2)
    TOMATO = auto()  # becomes 8  (2**3)
    HUMMUS = auto()  # becomes 16 (2**4)


class Sandwich(models.Model):
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(toppings__contains_noneof=IntFlagField.complement(SandwichTopping)),
                name='forbid_spurious_bits',
                violation_error_message='Field contains spurious bits (bits not representing any Topping member)',
            )
        ]
    name = models.CharField(primary_key=True)
    toppings = IntFlagField(choices=SandwichTopping, unique=True)
```

And then you'd use it like so — example adapted from the [tests](src/django_testapp_intflagfield/tests.py): 

```pycon
>>> Sandwich.objects.create(
    name='Healthy',
    toppings=SandwichTopping.ROCKET | SandwichTopping.TOMATO | SandwichTopping.HUMMUS,
)
<Sandwich: Sandwich object (Healthy)>

# gives you the sandwich you just saved — on readback, the integer value is neatly converted into an IntFlag combo.
# 28 is the numeric value that was actually stored in the database — as with all Enums, you can get at it with `.value`.
>>> Sandwich.objects.get(name='Healthy').toppings
<SandwichTopping.ROCKET|TOMATO|HUMMUS: 28>

# gives you all sandwiches that have *ONE OR MORE* of (Butter, Hummus) toppings
>>> Sandwich.objects.filter(toppings__contains_anyof=SandwichTopping.BUTTER | SandwichTopping.HUMMUS)
<QuerySet [<Sandwich: Sandwich object (Healthy)>]>

# gives you all sandwiches that have *AT LEAST ALL OF* (Rocket, Tomato) toppings
>>> Sandwich.objects.filter(toppings__contains=SandwichTopping.ROCKET | SandwichTopping.TOMATO)
<QuerySet [<Sandwich: Sandwich object (Healthy)>]>

# gives you all sandwiches that have *NONE OF* (Butter, Gouda) toppings
>>> Sandwich.objects.exclude(toppings__contains_anyof=SandwichTopping.BUTTER | SandwichTopping.GOUDA)
<QuerySet [<Sandwich: Sandwich object (Healthy)>]>
```

# This is wrong and not even in 1NF
True! It's a field with a set of values. You *can* set indices on it, but it's quite an art to match index expressions to query patterns. And you'll need to manage your Enum class wisely; deleting a member means changing over from `auto()` to hardcoded powers-of-2 as you don't want your semantics to shift, presumably! There's advantages too, in particular `CHECK` constraints are straightforward.

Alternatives:
- add a boolean column for every flag. Cons: Lots of columns, thus lots of schema changes when your set-of-booleans definition change often. Performance & efficiency suffer. Pros: Much easier to design indices for.
- use a many2many design. Cons: performance & efficiency suffer. Some queries are harder. `CHECK` constraints won't allow you to express all you would be able to express on a bitfield-containing row. Pros: You'll be doing it by the book.

Yet sometimes, you really just want a blessed bitfield. I couldn't find any ergonomic ones on PyPI (2024), so I made this one.


# Contributing
You may want to discuss your idea on the [mailinglist](https://lists.sr.ht/~nullenenenen/django-enum.IntFlag-field-discuss) first. Or just send a patch straight away, see https://git-send-email.io/ to learn how.