app_name := 'puzzlechum'

### recipes
@default: build

# build the project
build:
    @python3 -m build

install: build
    @pipx install .

install-arch: build
    @makepkg --syncdeps --force --clean
    @sudo pacman -U puzzlechum-*-x86_64.pkg.tar.zst

uninstall:
    @pip install pip-autoremove
    @pip-autoremove puzzlechum -y
