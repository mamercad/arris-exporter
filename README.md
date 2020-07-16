# arris-exporter

Prometheus exporter for my Arris SBG10. If they'd only offer SNMP, sigh. This is much hacks, but, I wanted something relatively quick (to be able to monitor correctables and uncorrectables without logging into a web browser manually). Currently using Chrome with Selenium (you'll need to install a Chrome driver).

```bash
❯ virtualenv -p python3 venv
Running virtualenv with interpreter /usr/local/bin/python3
Already using interpreter /usr/local/opt/python/bin/python3.7
Using base prefix '/usr/local/Cellar/python/3.7.7/Frameworks/Python.framework/Versions/3.7'
New python executable in /Users/mark/Code/github.com/mamercad/arris-exporter/venv/bin/python3.7
Also creating executable in /Users/mark/Code/github.com/mamercad/arris-exporter/venv/bin/python
Installing setuptools, pip, wheel...
done.

❯ source venv/bin/activate

❯ pip install -r requirements.txt
Processing /Users/mark/Library/Caches/pip/wheels/0a/9e/ba/20e5bbc1afef3a491f0b3bb74d508f99403aabe76eda2167ca/bs4-0.0.1-py3-none-any.whl
Collecting mechanize
  Using cached mechanize-0.4.5-py2.py3-none-any.whl (109 kB)
Collecting selenium
  Using cached selenium-3.141.0-py2.py3-none-any.whl (904 kB)
Collecting beautifulsoup4
  Using cached beautifulsoup4-4.9.1-py3-none-any.whl (115 kB)
Collecting html5lib>=0.999999999
  Using cached html5lib-1.1-py2.py3-none-any.whl (112 kB)
Collecting urllib3
  Using cached urllib3-1.25.9-py2.py3-none-any.whl (126 kB)
Collecting soupsieve>1.2
  Using cached soupsieve-2.0.1-py3-none-any.whl (32 kB)
Collecting six>=1.9
  Using cached six-1.15.0-py2.py3-none-any.whl (10 kB)
Collecting webencodings
  Using cached webencodings-0.5.1-py2.py3-none-any.whl (11 kB)
Installing collected packages: soupsieve, beautifulsoup4, bs4, six, webencodings, html5lib, mechanize, urllib3, selenium
Successfully installed beautifulsoup4-4.9.1 bs4-0.0.1 html5lib-1.1 mechanize-0.4.5 selenium-3.141.0 six-1.15.0 soupsieve-2.0.1 urllib3-1.25.9 webencodings-0.5.1

❯ ./arris.py --help
usage: arris.py [-h] [--loginurl LOGINURL] [--username USERNAME]
                [--password PASSWORD] [--listen LISTEN]

optional arguments:
  -h, --help           show this help message and exit
  --loginurl LOGINURL
  --username USERNAME
  --password PASSWORD
  --listen LISTEN

❯ ./arris.py --password hunter2 --listen 8000
127.0.0.1 - - [16/Jul/2020 05:35:03] "GET /metrics HTTP/1.1" 200 -

❯ curl http://localhost:8000/metrics
arris_downstreams_dcid{name="Downstream 1"} 17
arris_downstreams_frequency{name="Downstream 1"} 579.00
arris_downstreams_power{name="Downstream 1"} -1.60
arris_downstreams_snr{name="Downstream 1"} 38.61 dB
arris_downstreams_octets{name="Downstream 1"} 7042634012
arris_downstreams_correcteds{name="Downstream 1"} 41
arris_downstreams_uncorrectables{name="Downstream 1"} 0
...
```
