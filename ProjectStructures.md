.
├── KAuthApp
│   ├── backend
│   │   ├── application
│   │   │   └── __init__.py
│   │   ├── domain
│   │   │   └── __init__.py
│   │   ├── infrastructure
│   │   │   ├── __init__.py
│   │   │   └── router.py
│   │   └── __init__.py
│   └── frontend
│       └── package.json
├── KSysAdmin
│   ├── backend
│   │   ├── application
│   │   │   └── __init__.py
│   │   ├── domain
│   │   │   └── __init__.py
│   │   ├── infrastructure
│   │   │   ├── __init__.py
│   │   │   └── router.py
│   │   └── __init__.py
│   └── frontend
│       └── package.json
├── KSysPayment
│   ├── backend
│   │   ├── application
│   │   │   └── __init__.py
│   │   ├── domain
│   │   │   └── __init__.py
│   │   ├── infrastructure
│   │   │   ├── __init__.py
│   │   │   └── router.py
│   │   └── __init__.py
│   └── frontend
│       └── package.json
├── docker-images
│   └── postgres
│       └── init
│           └── 01_init.sql
├── nginx
│   ├── client_body_temp
│   ├── fastcgi_temp
│   ├── logs
│   │   ├── access.log
│   │   └── error.log
│   ├── proxy_temp
│   ├── scgi_temp
│   ├── uwsgi_temp
│   ├── mime.types
│   └── nginx.conf
├── scripts
│   ├── gen_structures.sh
│   ├── start_nginx.sh
│   └── testFactories.sh
├── security
├── shared
│   ├── backend
│   │   ├── config
│   │   │   └── settings.py
│   │   ├── database
│   │   │   └── engine.py
│   │   ├── redis
│   │   │   └── client.py
│   │   ├── cryptoFactory.py
│   │   └── loggingFactory.py
│   └── rust-crypto
│       ├── src
│       │   └── lib.rs
│       ├── Cargo.toml
│       └── pyproject.toml
├── Dockerfile
├── FACTORY_SETUP_PLAN.md
├── ProjectStructures.json
├── ProjectStructures.md
├── README.md
├── admin_server.py
├── architecture.md
├── compose.yml
├── poetry.lock
├── public_server.py
├── pyproject.toml
└── typing.txt

38 directories, 46 files
