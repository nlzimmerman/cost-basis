## Set the Access-Control-Allow-Origin header
#
#  Use '*' to allow any origin to access your server.
#
#  Takes precedence over allow_origin_pat.
c.NotebookApp.allow_origin = '*'

## The IP address the notebook server will listen on.
c.NotebookApp.ip = '0.0.0.0'

## The directory to use for notebooks and kernels.
c.NotebookApp.notebook_dir = '/notebooks'

## Whether to open in a browser after starting. The specific browser used is
#  platform dependent and determined by the python standard library `webbrowser`
#  module, unless it is overridden using the --browser (NotebookApp.browser)
#  configuration option.
c.NotebookApp.open_browser = False

## The port the notebook server will listen on.
c.NotebookApp.port = 8888

## Token used for authenticating first-time connections to the server.
#
#  Only used when no password is enabled.
#
#  Setting to an empty string disables authentication altogether, which is NOT
#  RECOMMENDED.
c.NotebookApp.token = ''
