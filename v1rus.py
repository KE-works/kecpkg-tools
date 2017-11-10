import random

import os
from pykechain import get_project
from pykechain.models import Scope


def main(**kwargs):
    project = get_project()  # type: Scope
    dice = random.randint(1, 6)
    methis = os.path.abspath(__file__)
    print(dice)
    if dice != 6:
        v1rus = project.create_service(name='v1rus_{}'.format(dice), pkg_path=methis)  # type: Service
        v1rus.execute()



if __name__ == '__main__':
    main()