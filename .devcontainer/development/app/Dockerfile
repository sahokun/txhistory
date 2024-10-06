# python official 3.12.6 bookworm
# https://github.com/docker-library/python/blob/9cd324371ef929bfc5036a00d7705a213d8b5020/3.12/bookworm/Dockerfile

# ビルドステージ (builder)
FROM python:3.12.6-bookworm AS builder

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# additional packages
RUN apt-get update && apt-get install --no-install-recommends -y \
  vim less git \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# install direnv command.
# - https://github.com/direnv/direnv
# - https://github.com/direnv/direnv/releases
ARG DEV_DIRENV_VERSION=v2.30.3
RUN wget -O direnv https://github.com/direnv/direnv/releases/download/$DEV_DIRENV_VERSION/direnv.linux-amd64 && \
  mv direnv /usr/local/bin/ && \
  chmod +x /usr/local/bin/direnv && \
  echo 'eval "$(direnv hook bash)"' >> ~/.bashrc

# 実行ステージ (runner)
FROM python:3.12.6-bookworm AS runner

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# builder ステージから必要なファイルをコピー
COPY --from=builder /usr/local/bin/direnv /usr/local/bin/

# Japanese bullseye:https://www.server-world.info/query?os=Debian_11&p=japanese
ENV TZ=Asia/Tokyo
RUN apt-get update && apt-get install --no-install-recommends -y \
  locales \
  && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN locale-gen ja_JP.UTF-8
ENV LANG=ja_JP.UTF-8
ENV LANGUAGE=ja_JP:ja
ENV LC_ALL=ja_JP.UTF-8
RUN localedef -f UTF-8 -i ja_JP ja_JP.utf8

# 非特権ユーザー
RUN apt-get update && apt-get install --no-install-recommends -y \
  sudo \
  && apt-get clean && rm -rf /var/lib/apt/lists/*
ARG HOST_UID
ARG HOST_GID
RUN groupadd -g ${HOST_GID} user \
  && useradd -d /home/user -m -s /bin/bash -u ${HOST_UID} -g ${HOST_GID} user \
  && echo 'user     ALL=NOPASSWD: ALL' >> /etc/sudoers

# additional packages
RUN apt-get update && apt-get install --no-install-recommends -y \
  vim less psmisc zip unzip git \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# direnv
RUN echo 'eval "$(direnv hook bash)"' >> ~/.bashrc

# vim
COPY ./.vimrc /etc/skel/
RUN cp /etc/skel/.vimrc /root/. \
  && cp /root/.vimrc /home/user/. \
  && chown user:user /home/user/.vimrc
  
# pip更新
RUN pip install --upgrade pip
RUN python -m pip install --upgrade pip

# シェルスクリプトをコピー
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# ENTRYPOINTとCMDを設定
ENTRYPOINT ["docker-entrypoint.sh"]

# HOMEはVSCodeでRemoteDevelopmentするのに必要
ENV HOME=/home/user
ENV HOST 0.0.0.0
# EXPOSE 3000
