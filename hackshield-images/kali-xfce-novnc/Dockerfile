FROM kalilinux/kali-rolling

ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:1
ENV USER=root
ENV TERM=xterm-256color

# --------------------------------------------------
# Base packages (NO upgrade)
# --------------------------------------------------
RUN apt update && apt install -y --no-install-recommends \
    ca-certificates \
    sudo \
    dbus-x11 \
    x11-xserver-utils \
    net-tools \
    iproute2 \
    && rm -rf /var/lib/apt/lists/*

# --------------------------------------------------
# XFCE Desktop (lightweight)
# --------------------------------------------------
RUN apt update && apt install -y --no-install-recommends \
    xfce4 \
    xfce4-goodies \
    tightvncserver \
    novnc \
    websockify \
    && rm -rf /var/lib/apt/lists/*

# --------------------------------------------------
# Core lab tools (split = stable)
# --------------------------------------------------
RUN apt update && apt install -y --no-install-recommends \
    curl wget git \
    python3 python3-pip \
    vim nano tmux \
    file unzip \
    && rm -rf /var/lib/apt/lists/*

RUN apt update && apt install -y --no-install-recommends \
    nmap \
    netcat-traditional \
    dnsutils \
    && rm -rf /var/lib/apt/lists/*

RUN apt update && apt install -y --no-install-recommends \
    nikto \
    gobuster \
    sqlmap \
    hydra \
    john \
    exploitdb \
    && rm -rf /var/lib/apt/lists/*

# --------------------------------------------------
# VNC setup
# --------------------------------------------------
RUN mkdir -p /root/.vnc && \
    echo "root" | vncpasswd -f > /root/.vnc/passwd && \
    chmod 600 /root/.vnc/passwd

RUN echo "#!/bin/sh\nunset SESSION_MANAGER\nunset DBUS_SESSION_BUS_ADDRESS\nexec startxfce4 &" \
    > /root/.vnc/xstartup && chmod +x /root/.vnc/xstartup

# --------------------------------------------------
# Expose noVNC
# --------------------------------------------------
EXPOSE 6080

# --------------------------------------------------
# Start XFCE + VNC + noVNC
# --------------------------------------------------
CMD bash -lc "\
    rm -f /tmp/.X1-lock && \
    rm -rf /tmp/.X11-unix/X1 && \
    vncserver :1 -geometry 1366x768 -depth 24 && \
    exec websockify --web=/usr/share/novnc/ 6080 localhost:5901 \
"
