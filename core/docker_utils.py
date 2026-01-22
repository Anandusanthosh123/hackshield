import docker
import time
import socket

client = docker.from_env()

# ✅ Correct images
KALI_IMAGE = "hackshield/kali-gui-lab:stable"
UBUNTU_IMAGE = "hackshield/ubuntu-target:latest"

NETWORK_NAME = "hackshield-net"
NOVNC_PORT = 6080
VNC_PORT = 5901


# -------------------------------------------------
# Ensure Docker network exists
# -------------------------------------------------
def ensure_network():
    try:
        return client.networks.get(NETWORK_NAME)
    except docker.errors.NotFound:
        return client.networks.create(NETWORK_NAME, driver="bridge")


# -------------------------------------------------
# Utility: wait for TCP port
# -------------------------------------------------
def wait_for_port(host, port, timeout=40):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=2):
                return True
        except:
            time.sleep(1)
    return False


# -------------------------------------------------
# Start Kali GUI (EXACT docker run equivalent)
# -------------------------------------------------
def start_kali(username, lab_slug):
    ensure_network()

    name = f"kali-{username}-{lab_slug}"

    # Remove old container safely
    try:
        old = client.containers.get(name)
        old.stop()
        old.remove()
    except docker.errors.NotFound:
        pass

    container = client.containers.run(
        image=KALI_IMAGE,
        name=name,
        detach=True,
        tty=True,
        stdin_open=True,
        privileged=True,
        cap_add=["ALL"],
        security_opt=[
            "seccomp=unconfined",
            "apparmor=unconfined"
        ],
        network=NETWORK_NAME,
        ports={
            "6080/tcp": NOVNC_PORT,
            "5901/tcp": VNC_PORT
        },
        environment={
            "DISPLAY": ":1",
            "TERM": "xterm-256color"
        },
        command="""
        bash -c "
        mkdir -p /run/dbus &&
        rm -f /run/dbus/pid &&
        dbus-daemon --system --fork &&
        rm -rf /tmp/.X1-lock /tmp/.X11-unix/X1 &&
        vncserver :1 -geometry 1366x768 -depth 24 &&
        websockify --web=/usr/share/novnc 6080 localhost:5901 &
        tail -f /dev/null
        "
        """
    )

    # ⏳ wait until noVNC is reachable
    if not wait_for_port("127.0.0.1", NOVNC_PORT):
        raise RuntimeError("noVNC failed to start on port 6080")

    return container.id


# -------------------------------------------------
# Start Ubuntu target (headless)
# -------------------------------------------------
def start_ubuntu(username, lab_slug):
    ensure_network()

    name = "ubuntu-target"

    try:
        old = client.containers.get(name)
        if old.status == "running":
            return old.id
        old.stop()
        old.remove()
    except docker.errors.NotFound:
        pass

    container = client.containers.run(
        image=UBUNTU_IMAGE,
        name=name,
        detach=True,
        tty=True,
        network=NETWORK_NAME,
        hostname="ubuntu-target"
    )

    return container.id


# -------------------------------------------------
# Stop lab
# -------------------------------------------------
def stop_lab(username, lab_slug):
    names = [
        f"kali-{username}-{lab_slug}",
        "ubuntu-target"
    ]
    for name in names:
        try:
            c = client.containers.get(name)
            c.stop()
            c.remove()
        except:
            pass


# -------------------------------------------------
# Get container IP
# -------------------------------------------------
def get_ip(container_id):
    c = client.containers.get(container_id)
    networks = c.attrs["NetworkSettings"]["Networks"]
    return list(networks.values())[0]["IPAddress"]


# -------------------------------------------------
# Exec command inside Kali (optional)
# -------------------------------------------------
def exec_cmd(container_id, command):
    if not command.strip():
        return ""

    exec_id = client.api.exec_create(
        container=container_id,
        cmd=["/bin/bash", "-lc", command],
        tty=True,
        environment={
            "TERM": "xterm-256color",
            "COLORTERM": "truecolor"
        }
    )

    output = client.api.exec_start(exec_id["Id"], tty=True)
    return output.decode(errors="ignore")
