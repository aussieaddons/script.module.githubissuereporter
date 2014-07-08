#
#   GitHub Issue Reporter Module for XBMC Addons
#
#   Copyright (c) 2014 Adam Malcontenti-Wilson
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#   THE SOFTWARE.
#

import base64
import os
import re
import sys
import urllib2
import xbmc

from datetime import datetime
from os.path import join, normpath, dirname, abspath, isfile

try:
  import simplejson as json
except ImportError:
  import json

GITHUB_API_AUTH = 'eGJtY2JvdDo1OTQxNTJjMTBhZGFiNGRlN2M0YWZkZDYwZGQ5NDFkNWY4YmIzOGFj'
GIST_API_URL = 'https://api.github.com/gists'

LOG_FILTERS = (
  ('//.+?:.+?@', '//[FILTERED_USER]:[FILTERED_PASSWORD]@'),
  ('<user>.+?</user>', '<user>[FILTERED_USER]</user>'),
  ('<pass>.+?</pass>', '<pass>[FILTERED_PASSWORD]</pass>'),
)

def get_module_version():
  """
      Try and get module version from addon.xml
  """
  try:
    addon_xml = join(normpath(join(dirname(abspath(abspath(__file__))), '..')),'addon.xml')
    with open(addon_xml, 'r') as f:
      addon_xml_data = f.read()
    return re.compile(r'<addon[^>]*version="([\d.]*)"').search(addon_xml_data).group(1)
  except:
    return None

VERSION = get_module_version()

class IssueReporter:
  def __init__(self, config={}):
    default_config = {
      'github_api_auth': GITHUB_API_AUTH,
      'gist_api_url': GIST_API_URL,
      'addon_id': self.get_addon_data('id'),
      'addon_name': self.get_addon_data('name'),
      'addon_version': self.get_addon_data('version'),
    }
    default_config.update(config)
    self.config = default_config

    if not 'github_api_url' in self.config:
      raise Exception('GitHub API URL must be set in IssueReporter configuration`')

    if 'logger' in self.config:
      self.log = self.config['logger']
    else:
      # Fallback logger, it is recommended to pass one in as the default
      # is pretty ugly in the XBMC logs
      import logging
      logging.basicConfig(level=logging.DEBUG)
      self.log = logging.getLogger(__name__)

  def make_request(self, url):
    """
        Make our JSON request to GitHub
    """
    return urllib2.Request(url, headers={
      "Authorization": "Basic %s" % self.config['github_api_auth'],
      "Content-Type": "application/json",
      "User-Agent": '%s/%s' % (self.config['addon_id'], self.config['addon_version'])
    })

  def get_addon_data(self, prop):
    """
        Try and get addon data
    """
    try:
      import xbmcaddon
      return xbmcaddon.Addon().getAddonInfo(prop)
    except:
      return None

  def get_public_ip(self):
    """
        Try and fetch the public IP of the reporter for logging
        and reporting purposes
    """
    try:
        result = urllib2.urlopen('http://ipecho.net/plain', timeout=5)
        data = str(result.read())
    except:
        return "Unknown (lookup failure)"

    try:
        ip = re.compile(r'(\d+\.\d+\.\d+\.\d+)').search(data).group(1)
    except:
        return "Unknown (parse failure)"

    try:
        hostname = socket.gethostbyaddr(ip)[0]
        return "%s (%s)" % (ip, hostname)
    except:
        return ip


  def get_isp(self):
    """
        Try and fetch the ISP of the reporter for logging
        and reporting purposes
    """
    try:
        result = urllib2.urlopen('http://www.whoismyisp.org', timeout=5)
        data = str(result.read())
    except:
        return "Unknown (lookup failure)"

    try:
        isp = re.compile(r'<h1>(.*)</h1>').search(data).group(1)
    except:
        return "Unknown (parse failure)"

    return isp

  def get_system_time(self):
    """
        Fetch the current system time
    """
    now = datetime.utcnow()
    return "%04d-%02d-%02d %02d:%02d:%02d (UTC)" % (now.year, now.month, now.day, now.hour, now.minute, now.second)

  def get_xbmc_log(self):
    """
        Fetch and read the XBMC log
    """
    log_path = xbmc.translatePath('special://logpath')
    log_file_path = os.path.join(log_path, 'xbmc.log')
    self.log.debug("Reading log file from \"%s\"" % log_file_path)
    with open(log_file_path, 'r') as f:
      log_content = f.read()
    for pattern, repl in LOG_FILTERS:
      log_content = re.sub(pattern, repl, log_content)
    return log_content

  def get_xbmc_version(self):
    """
        Fetch the XBMC build version
    """
    try:
        return xbmc.getInfoLabel("System.BuildVersion")
    except:
        return 'Unknown'

  def format_issue(self, issue_data):
    """
        Build our formatted GitHub issue string
    """
    content = [
      "*Automatic bug report from end-user.*\n## Environment\n"
      "**Plugin Name:** %s" % self.config['addon_name'],
      "**Plugin ID:** %s" % self.config['addon_id'],
      "**Plugin Version:** %s" % self.config['addon_version'],
      "**XBMC Version:** %s" % self.get_xbmc_version(),
      "**Issue Reporter Version:** %s" % VERSION,
      "**Python Version:** %s" % sys.version.replace('\n', ''),
      "**Operating System:** [%s] %s" % (sys.platform, ' '.join(os.uname())),
      "**System Time:** %s" % self.get_system_time(),
      "**IP Address:** %s" % self.get_public_ip(),
      "**ISP:** %s" % self.get_isp(),
      "**Python Path:**\n```\n%s\n```" % '\n'.join(sys.path),
      "\n## Traceback\n```\n%s\n```" % issue_data,
    ]

    log_url = self.upload_log()
    if log_url:
      content.append("\n[Full xbmc.log](%s)" % log_url)

    return "\n".join(content)

  def get_temp_dir(self):
    """
        Make our addon working directory if it doesn't exist and return it.
    """
    filedir = os.path.join(xbmc.translatePath('special://temp/'), self.config['addon_id'])
    if not os.path.isdir(filedir):
      os.mkdir(filedir)
    return filedir

  def get_last_error_report_path(self):
    return join(self.get_temp_dir(), 'last_reported_error.txt')

  def upload_log(self):
    """
        Upload our full XBMC log as a GitHub gist
    """
    try:
      log_content = self.get_xbmc_log()
    except Exception as e:
      self.log.error("Failed to read log: %s" % e)
      return None

    self.log.debug("Uploading xbmc.log")
    try:
      response = urllib2.urlopen(self.make_request(self.config['gist_api_url']), json.dumps({
        "files": {
          "xbmc.log": {
            "content": log_content
          }
        }
      }))
    except urllib2.HTTPError as e:
      print e
      self.log.error("Failed to save log: HTTPError %s" % e.code)
      return False
    except urllib2.URLError as e:
      print e
      self.log.error("Failed to save log: URLError %s" % e.reason)
      return False
    try:
      return json.load(response)["html_url"]
    except:
      self.log.error("Failed to parse API response: %s" % response.read())

  def save_last_error_report(self, trace):
    """
        Save a copy of our last error report
    """
    try:
      rfile = self.get_last_error_report_path()
      self.log.debug("Saving error report to \"%s\"" % rfile)
      with open(rfile, 'w') as f:
        f.write(trace)
    except:
      self.log.error("Error writing error report file")

  def can_send_error(self, trace):
    """
        Check to see if our new error message is different from the last
        successful error report. If it is, or the file doesn't exist, then
        we'll return True
    """
    try:
      rfile = self.get_last_error_report_path()

      self.log.debug("Reading previous error report from \"%s\"" % rfile)

      if not isfile(rfile):
        self.log.info("No previous error report found")
        return True
      else:
        f = open(rfile, 'r')
        report = f.read()
        if report != trace:
          self.log.debug("Allowing error report as last report does not match this one")
          return True
        else:
          self.log.debug("Not allowing error report. Last report matches this one")
    except:
      self.log.error("Error checking error report file")

    return False


  def report_issue(self, trace):
    """
        Report our issue to GitHub
    """
    issue_body = self.format_issue(trace)
    self.log.debug("Issue Body: %s" % issue_body)

    try:
      response = urllib2.urlopen(self.make_request("%s/issues" % self.config['github_api_url']), json.dumps({
        "title": "End-user bug report",
        "body": issue_body
      }))
    except urllib2.HTTPError as e:
      self.log.error("Failed to report issue: HTTPError %s" % e.code)
      return False
    except urllib2.URLError as e:
      self.log.error("Failed to report issue: URLError %s" % e.reason)
      return False
    try:
      return json.load(response)["html_url"]
    except:
      self.log.error("Failed to parse API response: %s" % response.read())
