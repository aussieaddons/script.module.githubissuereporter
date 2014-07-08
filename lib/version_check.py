try:
  import simplejson as json
except ImportError:
  import json

import re
import issue_reporter_utils as utils
from urllib2 import Request, urlopen

VERSION = utils.get_module_version()

class VersionCheck:
  def __init__(self, config={}):
    self.config = utils.build_config(config)

    if 'logger' in self.config:
      self.log = self.config['logger']
    else:
      # Fallback logger, it is recommended to pass one in as the default
      # is pretty ugly in the XBMC logs
      self.log = utils.build_logger(__name__)

  def fetch_tags(self):
    req = Request("%s/tags" % self.config['github_api_url'], headers={
      "Authorization": "Basic %s" % self.config['github_api_auth'],
      "User-Agent": '%s/%s' % (self.config['addon_id'], self.config['addon_version'])
    })

    return json.load(urlopen(req))

  def get_versions(self):
    tags = self.fetch_tags()
    self.log.debug('Found tags: %s' % tags)
    tag_names = map(lambda tag: tag['name'], tags)
    versions = filter(lambda tag: re.match(r'v(\d+)\.(\d+)(?:\.(\d+))?', tag), tag_names)
    return map(lambda tag: map(lambda v: int(v), tag[1::].split('.')), versions)

  def get_latest_version(self):
    versions = self.get_versions()
    self.log.debug('Found versions: %s' % versions)
    return sorted(versions, reverse=True)[0]

  def is_latest_version(self, current_version):
    if current_version.startswith('v'):
      current_version = current_version[1::]
    current_version = map(lambda v: int(v), current_version.split('.'))
    latest_version = self.get_latest_version()
    self.log.info('Latest version: %s, Current version: %s' % (latest_version, current_version))
    return current_version == latest_version

