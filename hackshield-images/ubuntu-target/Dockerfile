FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y \
    openssh-server \
    apache2 \
    net-tools \
    iproute2 \
    iputils-ping \
    curl \
    && rm -rf /var/lib/apt/lists/*

# SSH setup
RUN mkdir /var/run/sshd
RUN echo 'root:root' | chpasswd
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

EXPOSE 22 80

# Start Apache + SSH properly
CMD ["/bin/bash", "-c", "service apache2 start && /usr/sbin/sshd -D"]
