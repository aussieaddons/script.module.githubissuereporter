GITHUB_API_AUTH = 'eGJtY2JvdDo1OTQxNTJjMTBhZGFiNGRlN2M0YWZkZDYwZGQ5NDFkNWY4YmIzOGFj'
GIST_API_URL = 'https://api.github.com/gists'

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

def get_addon_data(prop):
  """
      Try and get addon info properties
  """
  try:
    import xbmcaddon
    return xbmcaddon.Addon().getAddonInfo(prop)
  except:
    return None

def build_config(config={}):
  final_config = {
    'github_api_auth': GITHUB_API_AUTH,
    'gist_api_url': GIST_API_URL,
    'addon_id': get_addon_data('id'),
    'addon_name': get_addon_data('name'),
    'addon_version': get_addon_data('version'),
  }
  final_config.update(config)

  if not 'github_api_url' in final_config:
    raise Exception('GitHub API URL must be set in configuration`')
  else:
    return final_config

def build_logger(name):
  import logging
  logging.basicConfig(level=logging.DEBUG)
  return logging.getLogger(name)
