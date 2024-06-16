pkgname=puzzlechum
pkgver=0.0.1
pkgrel=1
arch=('x86_64')

makedepends=(python-build python-installer python-wheel python-hatchling)
optdepends=('hyperfine: benchmarking support')

package() {
    cd ..
    python3 -m installer --destdir="$pkgdir" dist/$pkgname-$pkgver-py3-none-any.whl
}
