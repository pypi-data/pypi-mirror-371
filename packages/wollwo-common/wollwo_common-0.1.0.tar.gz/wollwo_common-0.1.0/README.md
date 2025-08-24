# WOLLWO COMMON

"""TEXT
Copyright (c) 2025 by Michal Perzel. All rights reserved.

License: MIT
"""

## HOW TO, WITH POETRY

### Bump package versions
```BASH
cd /path/to/project/custom_logging

poetry version patch  #: 0.1.0 -> 0.1.1
poetry version minor  #: 0.1.0 -> 0.2.0
poetry version major  #: 0.1.0 -> 1.1.0

#: check with
poetry version
poetry list
poetry config --list
```

### Build project
Before building bump version of package (see above or in `/path/to/project/custom_logging/pyproject.toml`).
After build check `/path/to/project/custom_logging/dist`
```BASH
cd /path/to/project/custom_logging
poetry build
```

### New poetry Project
```BASH
poetry init      #: in current folder initialize new poetry project
poetry new test  #: create new project
cd test
poetry env info  #: check project env info
poetry env info --path
poetry lock      #: Locks the project dependencies
```

```BASH
#: deactivate creation of ENVs
poetry config virtualenvs.create false
```

### add/remove library to dependency
```BASH
poetry add package_name
poetry add package_name@0.1.0   #: exact version
poetry add package_name@^0.1.0  #: greater version than 0.1.0, but less than next major version 1.0.0
poetry add package_name@<0.1.0  #: lesser version than specified
poetry remove package_name

poetry add --dev package       #: add package necessary only for development
```

### install project with poetry as python library
```BASH
cd /path/to/project/custom_logging
poetry install
```

### Check information about packages
```BASH
poetry show
poetry show package
poetry show | awk '{print $1"="$2}'  #: export current dependency versions
poetry show -T | awk '{print $1"="$2}'  #: Top level dependencies
```

### Activate ENV
```BASH
poetry env activate
```

## CUSTOM_LOGGING

## WOLLWO_DECORATORS
