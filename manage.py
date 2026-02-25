#!/usr/bin/env python
from pathlib import Path
from shared_backend import manage

if __name__ == '__main__':
    manage.main(Path(__file__).parent.name)
