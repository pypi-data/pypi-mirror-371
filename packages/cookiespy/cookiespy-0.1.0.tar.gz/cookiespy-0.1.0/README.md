# 🍪 CookieSpy

CookieSpy is a simple tool for retrieving, displaying, and exporting cookies from a URL.  
Supports colorized CLI display (via `rich`), export to JSON/CSV, and a simple web-based GUI (Flask).

---

## FLowchart

<center>
<img src="./cookiespy-diagram.drawio.png" alt="diagram business for cookiespy" />
</center>


## Installation

Clone this repository
```bash
https://github.com/fdhliakbar/CookieSpy.git
```

Install requirements
```bash
pip install -r requirements.txt
```

Install as a package (recommended):
```bash
pip install -e .
```

## CLI Usage

```bash
🔍 Mengambil cookies...

✔ Cookies ditemukan: {'_gh_sess': 
'3TLOJqcMKU9Mi5JN8EkecauN9FsSaImjhCOiKu8YDXpalofmkZbBe1xYtVDBFYf6bmbNh6MTfg8IVY2wsq%2FVN46DF2ok51y2O%2FHGYnq1X8qXX3zLmRFtZzierEp1O%2BuPy9StY3jL11vTVDNmjvX2%2Bdfy99JZ0fZOc
Dle6ZmLE0%2F8kvP6oMMB%2FGhOb0jGTwRPpEuAfmy%2BFmoGfg%2FqUZTpNk6JvPifKDVLAFwVPH08JyFwuf2YxM1tRs1S2Rx7H%2B%2Blo8mLWUKKDpVeGaONLYeNbQ%3D%3D--2bPnIxmDdV4DSGDx--L5Zjb9nicw2HqWy
0LoVW%2BQ%3D%3D', '_octo': 'GH1.1.89567047.1755552745', 'logged_in': 'no'}
``` -->

### Install Packages

```bash
pip install dist/cookiespy-0.1.0-py3-none-any.whl

Installing collected packages: cookiespy
Successfully installed cookiespy-0.1.0
```

### Run Program with CLI(Command Line Interface)
```bash
# Export with JSON
cookiespy https://youtube.com/ --export json

# Export with CSV
cookiespy https://youtube.com/ --export csv

```

### Output JSON
```bash
Fetching cookies from: https://facebook.com/
Cookies found: {'fr': '0qhvcEPszmVSmExBF..Boqw-r..AAA.0.0.Boqw-r.AWe5t84W9KkqFc6QoQPZqX7icCs', 'sb': 'qw-raOaLC5CvSSBM3qNhw0wf'}
[+] Cookies diexport ke cookies.json
Exported cookies to cookies.json
```

### Output CSV
```bash
Fetching cookies from: https://facebook.com/
Cookies found: {'fr': '0o5AyAWMjYLU5Wf8G..Boqw_G..AAA.0.0.Boqw_G.AWejVulJjL0qf-r097kKCKBqM4k', 'sb': 'xg-raIpCTxgOpbwcUJfHj7bj'}
[+] Cookies diexport ke cookies.csv
Exported cookies to cookies.csv
```

## Testing

Before testing, you must install the required packages. You can install all the required packages by

```bash
#Install requirement first
pip install -r requirements.txt


# Then you can enter the directory and run the program like this
cd test; pytest -v testing.py

# Output 

========================================================================== test session starts ==========================================================================
platform win32 -- Python 3.13.3, pytest-8.4.1, pluggy-1.6.0 -- C:\Users\USER\AppData\Local\Programs\Python\Python313\python.exe
cachedir: .pytest_cache
rootdir: E:\Github-Database\CookieSpy
configfile: pyproject.toml
plugins: anyio-4.9.0
collected 1 item                                                                                                                                                         

testing.py::test_fetch_cookies_google PASSED                                                                                                                       [100%]

=========================================================================== 1 passed in 1.25s ===========================================================================
```

---

<img src="https://i.pinimg.com/1200x/2c/be/1d/2cbe1db9099cfd8409444f5837d16afb.jpg" alt="Anime Banner" />
