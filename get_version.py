import git

git.Repo('.').remotes['origin'].pull()

import init_db

print('done')