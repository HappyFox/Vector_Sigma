FROM debian:trixie
RUN apt-get update
RUN apt-get install -y default-jre-headless python3 curl python3-aioconsole python3-aiosqlite
RUN mkdir /src
WORKDIR /src
COPY /vector_sigma /src/vector_sigma
ADD https://github.com/AsamK/signal-cli/releases/download/v0.13.15/signal-cli-0.13.15.tar.gz /src/
RUN tar xf signal-cli-0.13.15.tar.gz -C /opt
RUN ln -sf /opt/signal-cli-0.13.15/bin/signal-cli /usr/local/bin/

