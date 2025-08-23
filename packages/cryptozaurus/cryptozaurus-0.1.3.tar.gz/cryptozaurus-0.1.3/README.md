## cryptozaurus

Decryptor for JS Crypto-encrypted timestamp tokens.

### Install

```bash
pip install cryptozaurus
```

### Usage

```python
from cryptozaurus import is_timestamp_valid

token: str = "32_symbols_unicode_as_msg+iv_hex"  
secret: str = "16symbolsunicode"  # same key used by the JS side

ts: bool = is_timestamp_valid(token, secret)
print(ts)
```

### License

MIT

