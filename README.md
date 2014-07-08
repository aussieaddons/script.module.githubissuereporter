GitHub Issue Reporter Module for XBMC
=====================================

This addon provides an exported module to report issues in your addon to GitHub. 

Usage
-----

* Add `<import addon="script.module.githubissuereporter"/>` in the `<requires>` section of your addon's addon XML file
* Wrap your addon code within a try / raise block
* Import and configure your IssueReporter somewhere, for example:

```python
from issue_reporter import IssueReporter
issue_reporter = IssueReporter({
    'github_api_url': 'https://api.github.com/repos/myorg/myaddon,
    'addon_name': 'My Addon Name',
    'addon_id': 'plugin.video.myaddon',
    'addon_version': '1.2.3'
})
```

* When an exception occurs, use an XBMC dialog to ask the user for consent to report the error, and call `issue_reporter.report_issue(traceback)` where traceback is the python traceback string.

Projects using this module
--------------------------
 * [ABC iView Addon](https://github.com/andybotting/xbmc-addon-abc-iview) (planned)
 * [TenPlay Addon](https://github.com/xbmc-catchuptv-au/plugin.video.catchuptv.au.ten) (planned)
