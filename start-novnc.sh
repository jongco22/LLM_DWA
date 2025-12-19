#!/bin/bash
export DISPLAY=:99

# Clean up old sockets
mkdir -p /tmp/.X11-unix
chmod 1777 /tmp/.X11-unix
rm -f /tmp/.X11-unix/X99 || true

# 1️⃣ Start virtual display
Xvfb :99 -screen 0 1280x800x16 &
sleep 2

# 2️⃣ Start lightweight window manager
fluxbox &

# 3️⃣ Start VNC server
x11vnc -display :99 -forever -nopw -shared &
sleep 2

# 4️⃣ Start noVNC
websockify --web=/usr/share/novnc/ 6080 localhost:5900 &
echo "✅ noVNC running at: http://localhost:6080/vnc.html"

# 5️⃣ Keep container alive
tail -f /dev/null
