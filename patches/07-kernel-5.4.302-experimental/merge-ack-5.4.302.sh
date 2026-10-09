#!/bin/bash
# ЭКСПЕРИМЕНТ: ядро Allwinner 5.4.125 (H618-Android12-Src) -> 5.4.302 (Android Common Kernel android12-5.4).
# Ядро AW = ACK android12-5.4 (осень 2021) + BSP Allwinner, поэтому обновляем через git merge, а не патчами.
# ВНИМАНИЕ: на T95 ядро 5.4.302 работает, но после выхода из сна (standby) система виснет при
# переинициализации eMMC -> сброс watchdog. В релизную сборку НЕ вошло.
#
# Использование:
#   bash merge-ack-5.4.302.sh <чистый longan/kernel/linux-5.4 из H618-Android12-Src> <рабочая папка>
# Дерево AW должно быть ЧИСТЫМ (сразу после распаковки, без сборки), иначе ветка aw-base не совпадёт.
# Результат: <рабочая папка>/linux-5.4, ветка t95-5.4.302. Скопировать в longan/kernel/linux-5.4:
#   rsync -a --delete --exclude=.git <рабочая папка>/linux-5.4/ longan/kernel/linux-5.4/
set -euo pipefail

AW=$(realpath "$1")
WORK=$(realpath -m "$2")
HERE=$(dirname "$(realpath "$0")")

ACK_URL=${ACK_URL:-https://android.googlesource.com/kernel/common}
ACK_BASE=73e6d86c3            # коммит ACK, ближайший к ядру AW (12.10.2021)
ACK_TOP=250657e3e4fa0189d0ebf710093551ba4a1ea9c1   # android12-5.4, тег android12-5.4.302_r00 (11.12.2025)

mkdir -p "$WORK"
cd "$WORK"
if [ ! -d linux-5.4/.git ]; then
    git init -q linux-5.4
    git -C linux-5.4 remote add origin "$ACK_URL"
fi
cd linux-5.4
git config user.name  >/dev/null || git config user.name  t95
git config user.email >/dev/null || git config user.email t95@local

# ~3-4 ГБ: только история с мая 2021 (этого хватает, чтобы найти общий предок)
git fetch --shallow-since=2021-05-01 origin android12-5.4
git cat-file -e "$ACK_BASE^{commit}"
git cat-file -e "$ACK_TOP^{commit}"

# 1) ветка aw-base = коммит ACK + дерево AW как есть (контрольное дерево: e28114d7d1c9...)
git checkout -q -B aw-base "$ACK_BASE"
rsync -a --delete --exclude=.git "$AW"/ ./
git add -A
git commit -q -m "Allwinner H618 BSP kernel (Orange Pi H618-Android12-Src) на ACK android12-5.4 $ACK_BASE"
echo "aw-base tree: $(git rev-parse HEAD^{tree})"

# 2) merge ACK 5.4.302: ожидаются 11 конфликтов
git checkout -q -B t95-5.4.302 aw-base
git merge --no-edit "$ACK_TOP" || true

# 3) разрешение конфликтов (готовые файлы в resolved/):
#    sunxi-mmc.c, sun50i-cpufreq-nvmem.c, pinctrl-sunxi.c -> AW;
#    elantech.c, checkpatch.pl, f2fs/super.c, arch/arm/kernel/Makefile -> upstream;
#    f_accessory.c -> upstream (compat_ioctl = acc_ioctl, acc_compat_ioctl AW убран);
#    f_fs.c -> оба (io_wait AW + drain_workqueue upstream);
#    drivers/char/Kconfig -> текст upstream + source AW + endmenu;
#    drivers/net/can/sun4i_can.c -> остаётся удалённым (как у AW).
cp -r "$HERE"/resolved/. ./
git rm -q --ignore-unmatch drivers/net/can/sun4i_can.c
git add -A
git commit -q --no-edit

# 4) исправления после merge
git am -q "$HERE"/0001-cpufreq-nvmem-AW.patch "$HERE"/0002-mmc-core-AW.patch

echo "t95-5.4.302 tree: $(git rev-parse HEAD^{tree})  (у меня: b5b7dff5033a2b2d9438b5791b0eaed23afc0de6)"
