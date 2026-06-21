#!/bin/bash

# التأكد من تشغيل السكربت بصلاحيات الروت
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root: sudo ./install.sh"
  exit 1
fi

echo "Starting Focus Lock installation..."

# 1. نقل ملفات السكربت والواجهة إلى المسار المعتمد للنظام
mkdir -p /usr/local/bin
cp focus_lock.py /usr/local/bin/
cp focus_lock_ui.py /usr/local/bin/

# 2. إعطاء صلاحيات التشغيل
chmod +x /usr/local/bin/focus_lock.py

# 3. إنشاء ملف خدمة systemd
cat << 'EOF' > /etc/systemd/system/focus-lock.service
[Unit]
Description=Focus Lock System Daemon
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/focus_lock.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 4. تحديث الخدمات وتفعيل الخدمة في الخلفية
systemctl daemon-reload
systemctl enable focus-lock.service

# 5. استخراج اسم المستخدم الحقيقي لإضافة الـ Alias في ملفه الشخصي
REAL_USER=${SUDO_USER:-$USER}
USER_HOME=$(getent passwd "$REAL_USER" | cut -d: -f6)

if [ -f "$USER_HOME/.bashrc" ]; then
    if ! grep -q "alias holylock=" "$USER_HOME/.bashrc"; then
        echo "alias holylock='sudo /usr/local/bin/focus_lock.py'" >> "$USER_HOME/.bashrc"
        echo "Added 'holylock' alias to .bashrc"
    fi
fi

if [ -f "$USER_HOME/.zshrc" ]; then
    if ! grep -q "alias holylock=" "$USER_HOME/.zshrc"; then
        echo "alias holylock='sudo /usr/local/bin/focus_lock.py'" >> "$USER_HOME/.zshrc"
        echo "Added 'holylock' alias to .zshrc"
    fi
fi

echo "Installation complete successfully. Please reopen your terminal and type 'holylock' to use it."
