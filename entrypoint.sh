#!/usr/bin/env bash
set -euo pipefail

# Expect these at runtime:
#   CRD_SSH_CODE  (short-lived, from https://remotedesktop.google.com/headless → Debian)
# Build-time args already baked:
#   CRD_USERNAME, CRD_PASSWORD, CRD_PIN

# Load baked-in values by reading crd_login.txt for the PIN (optional)
CRD_PIN_FROM_FILE="$(grep '^PIN:' /root/crd_login.txt | awk '{print $2}' || true)"
if [[ -z "${CRD_PIN:-}" && -n "${CRD_PIN_FROM_FILE}" ]]; then
  export CRD_PIN="$CRD_PIN_FROM_FILE"
fi

# Validate env
if [[ -z "${CRD_SSH_CODE:-}" ]]; then
  echo "ERROR: CRD_SSH_CODE is required at runtime. Get it from https://remotedesktop.google.com/headless (Debian) and pass with -e CRD_SSH_CODE=..."
  exit 1
fi

if [[ -z "${CRD_PIN:-}" ]]; then
  echo "ERROR: CRD_PIN not found. Provide at runtime with -e CRD_PIN=..., or bake via CI variable."
  exit 1
fi

if [[ "${#CRD_PIN}" -lt 6 ]]; then
  echo "ERROR: CRD_PIN must be at least 6 digits."
  exit 1
fi

# Determine username baked at build time
CRD_USERNAME="$(awk -F: '/\/home\// {print $1; exit}' /etc/passwd)"
if id "${CRD_USERNAME}" &>/dev/null; then
  :
else
  echo "ERROR: CRD user not found. Image build may have failed."
  exit 1
fi

# Ensure group membership (idempotent)
adduser "${CRD_USERNAME}" chrome-remote-desktop || true

# Start CRD host registration as the non-root user
echo "Registering Chrome Remote Desktop host for user '${CRD_USERNAME}'..."
su - "${CRD_USERNAME}" -c "/opt/google/chrome-remote-desktop/start-host \
  --code='${CRD_SSH_CODE}' \
  --redirect-url='https://remotedesktop.google.com/_/oauthredirect' \
  --name='${HOSTNAME:-crd-container}' \
  --pin='${CRD_PIN}'" || {
    echo "ERROR: start-host failed. Check your CRD_SSH_CODE and network access."
    exit 1
  }

# Start CRD service (some builds need this; harmless if already running)
service chrome-remote-desktop start || true

echo "Chrome Remote Desktop is starting. You should see this machine at https://remotedesktop.google.com/access"
echo "To view creds stored in image: cat /root/crd_login.txt"
echo "Following CRD logs..."
# Follow general logs (CRD writes to temp/syslog variants). This is a best-effort tail.
# Try to tail the latest CRD temp log if it exists; otherwise fall back to syslog.
LATEST_TMP_LOG="$(ls -1t /tmp/chrome_remote_desktop_* 2>/dev/null | head -n1 || true)"
if [[ -n "${LATEST_TMP_LOG}" ]]; then
  tail -F "${LATEST_TMP_LOG}"
else
  # Some distros route logs to /var/log/syslog; inside containers journald/syslog may not be present.
  # Fallback to sleeping to keep the container alive if no log file is available.
  echo "(No specific CRD temp log found; keeping container alive.)"
  exec tail -f /dev/null
fi
