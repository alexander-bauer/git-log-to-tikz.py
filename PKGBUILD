# Maintainer: Alexander Bauer <sasha@crofter.org>
pkgname=git-log-to-tikz-git
pkgrel=1
pkgdesc="Create a TIKZ graph from a Git repository"
url="https://github.com/ProjectMeshnet/nodeatlas"
arch=('any')
license=('MIT')
depends=('python' 'python-jinja')
conflicts=('git-log-to-tikz')
provides=('git-log-to-tikz')
source=("$pkgname"::'git+https://github.com/alexander-bauer/git-log-to-tikz.py.git#branch=master')
md5sums=('SKIP')


pkgver() {
  cd "$srcdir/$pkgname"
  # Use the tag of the last commit
  git describe --long | sed -E 's/([^-]*-g)/r\1/;s/-/./g'
}

install() {
  cd "${srcdir}/${pkgname}"
  prefix="/usr" make install
}

# vim:set ts=2 sw=2 et:
