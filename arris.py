#!/usr/bin/env python3

import argparse, re
import http.server
import socketserver
from bs4 import BeautifulSoup
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from time import sleep

parser = argparse.ArgumentParser()
parser.add_argument('--loginurl', default='http://192.168.100.1/cgi-bin/basic_pwd_cgi')
parser.add_argument('--username', default='admin')
parser.add_argument('--password', default='password')
parser.add_argument('--listen', type=int, default=8000)
args = parser.parse_args()

def scrape():
  chrome_options = Options()
  chrome_options.add_argument("--headless")
  browser = webdriver.Chrome(options=chrome_options)
  browser.get(args.loginurl)
  sleep(2)
  user = browser.find_elements_by_xpath('//*[@id="user"]')
  user[0].send_keys(args.username)
  pwd = browser.find_elements_by_xpath('//*[@id="pwd"]')
  pwd[0].send_keys(args.password)
  submit = browser.find_elements_by_xpath('/html/body/div[1]/div[3]/form/p[3]/input[1]')
  submit[0].click()
  sleep(2)
  status = browser.page_source

  # with open('status.html') as f:
  #   status = f.read()

  soup = BeautifulSoup(status, 'html.parser')
  tds = soup.find_all('td')

  downstreams = []
  for i in range(10,10+9*16,9):
    downstreams.append({
      'name': tds[i+0].text,
      'dcid': tds[i+1].text,
      'freq': tds[i+2].text,
      'power': tds[i+3].text,
      'snr': tds[i+4].text,
      'mod': tds[i+5].text,
      'octets': tds[i+6].text,
      'corr': tds[i+7].text,
      'uncorr': tds[i+8].text,
    })
  # pprint(downstreams)

  upstreams = []
  for i in range(162,162+7*4,7):
    upstreams.append({
      'name': tds[i+0].text,
      'ucid': tds[i+1].text,
      'freq': tds[i+2].text,
      'power': tds[i+3].text,
      'chan': tds[i+4].text,
      'symb': tds[i+5].text,
      'mod': tds[i+6].text,
    })
  # pprint(upstreams)

  status = {
    'uptime': tds[192].text,
    'computers': tds[194].text.rstrip(),
    'status': tds[196].text,
    'date': tds[198].text,
  }
  # pprint(status)

  interfaces = []
  for i in range(205,205+5*5,5):
    interfaces.append({
      'name': tds[i+0].text,
      'prov': tds[i+1].text,
      'state': tds[i+2].text,
      'speed': tds[i+3].text,
      'mac': tds[i+4].text,
    })
  # pprint(interfaces)

  html = []

  for downstream in downstreams:
    html.append('arris_downstreams_dcid{{name="{}"}} {}'.format(downstream['name'], downstream['dcid']))
    freq = downstream['freq'].replace(' MHz', '')
    html.append('arris_downstreams_frequency{{name="{}"}} {}'.format(downstream['name'], freq))
    power = downstream['power'].replace(' dBmV', '')
    html.append('arris_downstreams_power{{name="{}"}} {}'.format(downstream['name'], power))
    snr = downstream['snr'].replace(' dB', '')
    html.append('arris_downstreams_snr{{name="{}"}} {}'.format(downstream['name'], snr))
    html.append('arris_downstreams_octets{{name="{}"}} {}'.format(downstream['name'], downstream['octets']))
    html.append('arris_downstreams_correcteds{{name="{}"}} {}'.format(downstream['name'], downstream['corr']))
    html.append('arris_downstreams_uncorrectables{{name="{}"}} {}'.format(downstream['name'], downstream['uncorr']))

  for upstream in upstreams:
    html.append('arris_upstreams_ucid{{name="{}"}} {}'.format(upstream['name'], upstream['ucid']))
    freq = upstream['freq'].replace(' MHz', '')
    html.append('arris_upstreams_frequency{{name="{}"}} {}'.format(upstream['name'], freq))
    power = upstream['power'].replace(' dBmV', '')
    html.append('arris_upstreams_power{{name="{}"}} {}'.format(upstream['name'], power))
    symb = upstream['symb'].replace(' kSym/s', '')
    html.append('arris_upstreams_symbolrate{{name="{}"}} {}'.format(upstream['name'], symb))

  for interface in interfaces:
    if interface['prov'] == 'Enabled':
      html.append('arris_interfaces_provisioned{{name="{}"}} {}'.format(interface['name'], 1))
    else:
      html.append('arris_interfaces_provisioned{{name="{}"}} {}'.format(interface['name'], 0))
    if interface['state'] == 'Up':
      html.append('arris_interfaces_state{{name="{}"}} {}'.format(interface['name'], 1))
    else:
      html.append('arris_interfaces_state{{name="{}"}} {}'.format(interface['name'], 0))

  # hacky garbage
  minutes = 0
  p = re.compile('(\d+)\s+d:\s+(\d+)\s+h:\s+(\d+)\s+m')
  m = p.match(status['uptime'])
  if m:
    x = list(map(int, m.groups()))
    minutes += x[0] * 1440 # days  * minutes/day
    minutes += x[1] * 60   # hours * minutes/hour
    minutes += x[2]        # minutes
    html.append('arris_uptime_minutes {}'.format(minutes))

  return('\n'.join(html)+'\n')

def serve():
  class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
      if self.path == '/':
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        html = f"<html><head></head><body><h1>arris-exporter</h1></body></html>"
        self.wfile.write(bytes(html, "utf8"))
        return
      if self.path == '/metrics':
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        html = scrape()
        self.wfile.write(bytes(html, "utf8"))
  handler_object = MyHttpRequestHandler
  PORT = args.listen
  my_server = socketserver.TCPServer(("", PORT), handler_object)
  my_server.serve_forever()

if __name__ == '__main__':
  serve()
