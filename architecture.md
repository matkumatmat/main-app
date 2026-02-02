project : **Scallable app for multi microservices**
architecture : **Layered Modular Hexagonal pattern**
stack : **modern FastApi**
system API : **REST API**
OS and Kernel for server : **Linux and Linux Distro's**

# Company Information
Company adalah sebuah platform penyedia berbagai services, perusahaan bergerak di bidang penyedia layanan. sistem yang di gunakan adalah microservices dengan memecah beberapa service yang perusahaan miliki, perusahaan tidak berfokus kepada satu niche service dan perusahaan tidak membangun monolith sistem.
untuk saat ini ada 10 existing service yang di pegang perusahaan diantara beberapa contohnya [3dbinpacking,cvmaker,jobportal,media_information,etc], disini admin juga harus bisa mengelola service seperti menambahkan atau mengubah.

# Architecture
# 1. base information...
python : python 3.14
package manager : poetry
linter : ruff linter
persisten database : postgresql
temporary database : redis
stack : FastApi
ORM : SQLModel
validator : pydantic v2 (strict)
logging : structlog
testing : pytest
payment-gateaway : BRI Merchant

# 2. company code rules
1. Strict OOP = True
2. strict hexagonal and files placements, strictly to maximizing using project structures. example: where files was domain logic must saved on domain with separately
3. modularity is greatness. and clean code = true 
4. always create bussiness logic on domain, never create logic outside domain.
4. Never injection shared, external modules on domain like pydantic
5. separate logic with schema/interface with right placing
6. Strict use DI (dependency Injection).
7. file naming use camelcase (example: PaymentGateaway)
8. Function naming use snake case (example: payment_user)
9. Strict clean no Emoji = True
10. Srict Use custom module on shared folders if not exists, the module must created on shared/ (example: exceptions, UUID, logging)
11. strict use env/ on development or when production never hardcode anything
12. when must create documentation or plan, must created on md/ not on app/ 
13. clean code without docstring on anything code.
14. testing is run or maked when the codes was finals, not every create code must test, just test when instructed.
14. strictly using pydantic for everything can be.
15. always read pydantc documentation
16. always follow the flow domain -> application/dto -> application input|output -> infrastructure  http|database->
17. on infrastructure, never use domain or use model on application, if there must have model just create model on it.
18. tidak membuat custom exception, logging di dalam service ataupun infrastructure atau http, jika harus ada custom exception, maka buat di domain/exceptions

# 3. project structure
**read ProjectStructures.md or run "tree -I '__pycache__|*.py[cod]|*$py.class|.venv|venv|env|.env*|app/env|.mypy_cache|.ruff_cache|.pytest_cache|.coverage|htmlcov|dist|build|*.egg-info|.claude|.vscode|.idea|.DS_Store|Thumbs.db|md|CLAUDE.md|ProjectStructures*.md|history' --dirsfirst -o about/ProjectStructures.md"**

# 4. DO and Donts
# Do 
1. always strict with company rules (point 2) 
3. always ensure to check the shared/ modules, to check the custom of company modules instead create new code and hardcode anything
2. use dict, list, | instead of deprecated code like Dict, List, Optional
3. maximalize pydantic modules, if can implement the pydantic modules on documentation use it instead using native python methode.
4. always to check availabilty of modules and logic on domain, or shared folders
5. if feeling confused for application, do webfetch from official documentation about topic
6. if feeling confused also can read llms-*.md for pydantic or fastapi on /framework-reference

# Dont's
1. never use deprecated code like using Dict, List, or Optional
3. never use nested 'if', if can maximalize using pydantic, just use pydantic
4. never to write bussiness logic besides on domain
5. never create custom interface on files



# 5. type of user plan (for future)
user type is defined by database so it will be dynamically






