FROM debian:bookworm-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       latexmk texlive-latex-extra texlive-fonts-recommended \
       texlive-bibtex-extra biber python3 python3-gi python3-gi-cairo python3-cairo gir1.2-rsvg-2.0 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /source
ENTRYPOINT ["latexmk"]
