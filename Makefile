.PHONY: all install package tikz-history.tex

all: history.pdf

install:
	install -m 755 git-log-to-tikz.py $(prefix)/bin/git-log-to-tikz
	ln -s $(prefix)/bin/git-log-to-tikz $(prefix)/bin/git-tikzgraph

package: git-log-to-tikz-git--1-any.pkg.tar.xz

tikz-history.tex:
	./git-log-to-tikz.py --testfile ./testfile.json master feature1 feature2 > tikz-history.tex

history.dvi: history.tex tikz-history.tex
	latex history.tex

history.pdf: history.tex tikz-history.tex
	pdflatex history.tex

git-log-to-tikz-git--1-any.pkg.tar.xz: PKGBUILD
	makepkg --sign --clean --force
