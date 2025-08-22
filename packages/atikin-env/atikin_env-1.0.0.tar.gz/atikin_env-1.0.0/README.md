# Atikin Env ■
Ultra-fast, zero-dependency `.env` loader for Python with **automatic type casting**.
## ■ Features
- ■ Faster than python-dotenv
- ■ Zero Dependencies
- ■ Auto Type Casting (bool, int, float, None)
- ■ Simple API
## ■ Installation
```bash
pip install atikin-env
```
## ■ Usage
```python
from atikin_env import load_env, get
# Load environment variables
load_env(".env")
print(get("NAME")) # str -> "Atikin"
print(get("AGE")) # int -> 25
print(get("DEBUG")) # bool -> True
print(get("PI")) # float -> 3.1416
```
## ■ Run Tests
```bash
pytest
```
## ■ Publishing to PyPI (Step-by-Step)
1. **Install tools**
```bash
pip install build twine
```
2. **Build package**
```bash
python -m build
```
3. **Upload to PyPI**
```bash
twine upload dist/*
```
## ■ License
MIT License © 2025 Atikin Verse



## FOLLOW US ON For more information:

Join our social media for exciting updates, news, and insights! Follow us on :

<!--Table-->
| ACCOUNTS                 | USERNAME          |
|------------              | --------------    |
| FACEBOOK                 | atikinverse       |
| INSTAGRAM                | atikinverse       |
| LINKEDIN                 | atikinverse       |
| TWITTER (X)              | atikinverse       |
| THREADS                  | atikinverse       |
| PINTREST                 | atikinverse       |
| QUORA                    | atikinverse       |
| REDDIT                   | atikinverse       |
| TUMBLR                   | atikinverse       |
| SNAPCHAT                 | atikinverse       |
| SKYPE                    | atikinverse       |
| GITHUB                   | atikinverse       |

---

Feel free to reach out if you have any questions or suggestions!

Happy Coding! 🚀