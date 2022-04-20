from __future__ import print_function
import ast
import os
import praw
import subprocess

class Reddit(praw.Reddit):
    def login(self, username, password, client_id, client_secret):
        self.clear_authentication()
        self.set_oauth_app_info(client_id, client_secret, '')
        self.config.user = username
        self.config.pswd = password
        self.config.grant_type = 'password'
        self.config.api_request_delay = 1.0
        self.get_access_information('code')
        self.user = self.get_me() # praw has a bug

def deploy(force=ast.literal_eval(os.getenv('force_deploy', 'False'))):
    config = os.getenv('configfile', 'config.yaml')
    diff = subprocess.check_output(['git', 'diff',
                                    '--name-only', 'HEAD^'])
    diff = diff.split() if isinstance(diff, str) else \
        diff.decode('utf-8').split()
    update_automod = config in diff
    r = Reddit(
        os.getenv("UASTRING", "Automatic Automoderator Deployment")
    )
    r.login(
        os.getenv('username'),
        os.getenv('password'),
        os.getenv('client_id'),
        os.getenv('client_secret'),
    )
    if update_automod or force:
        with open(config, 'r') as config_file:
            config_file = config_file.read()
            for subreddit in os.getenv('subreddit').split('+'):
                config_page = r.subreddit(subreddit).wiki['config/automoderator']
                config_page.edit(config_file)

if __name__ == '__main__':
    deploy()