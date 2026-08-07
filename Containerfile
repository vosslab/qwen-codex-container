FROM docker.io/library/node:22-bookworm-slim

RUN apt-get update \
	&& apt-get install --yes --no-install-recommends \
		ca-certificates \
		git \
		socat \
		tmux \
		wget \
	&& npm install --global @openai/codex \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

CMD ["sleep", "infinity"]
