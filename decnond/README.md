# decnond

`decnond.run("script.py")` executes a Python script after converting ordinary
decimal floating-point literals to exact `decimal.Decimal` values. Integers,
hexadecimal numbers, and imaginary literals retain their normal Python types.

```python
import decnond

decnond.run("script.py")
```

For example, `x = 0.0000000000000000001` in `script.py` creates
`Decimal("0.0000000000000000001")`. Decimal arithmetic still follows the
active Decimal context precision.
