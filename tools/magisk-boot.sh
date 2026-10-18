#!/bin/bash
# Вариант с root: патчит Magisk-ом boot.img из signed target files (шаги assets/boot_patch.sh из Magisk,
# выполняются на ПК: magiskboot x86_64 и payload arm64), возвращает hash footer AVB и заново создаёт vbmeta.img
# своим ключом (add_img_to_target_files -a пересобирает только отсутствующие образы). Пишет boot.img и vbmeta.img
# в $OUT: после этого нужно снова выполнить "pack -v" (переподпись boot.fex для secure boot).
# использование (из корня исходников Android, после lunch + pack4dist): magisk-boot.sh <Magisk.apk>
set -euo pipefail
APK=$(realpath ${1:?Magisk.apk})
SRC=$PWD; OUT=${OUT:?lunch}
Z=$(ls -t $OUT/*signed_target_files*.zip | head -1)
AVB=$SRC/out/host/linux-x86/bin/avbtool
W=$OUT/t95-magisk; rm -rf $W; mkdir -p $W/p $W/tf
echo "target files: $Z"

# payload Magisk (те же имена, что ждёт boot_patch.sh)
cd $W/p
unzip -q -o $APK 'assets/stub.apk' 'lib/x86_64/libmagiskboot.so' 'lib/arm64-v8a/*'
cp lib/x86_64/libmagiskboot.so magiskboot
cp lib/arm64-v8a/libmagiskinit.so magiskinit
cp lib/arm64-v8a/libmagisk.so magisk
cp lib/arm64-v8a/libinit-ld.so init-ld
cp assets/stub.apk stub.apk
chmod 755 magiskboot

unzip -q -o $Z -d $W/tf
cp $W/tf/IMAGES/boot.img stock_boot.img
BOOT_SIZE=$(grep '^boot_size=' $W/tf/META/misc_info.txt | cut -d= -f2)
FOOTER_ARGS=$(grep '^avb_boot_add_hash_footer_args=' $W/tf/META/misc_info.txt | cut -d= -f2-)
cp stock_boot.img boot.img
$AVB erase_footer --image boot.img

./magiskboot unpack boot.img
./magiskboot cpio ramdisk.cpio test || { echo "ramdisk не стоковый (status $?)"; exit 1; }
SHA1=$(./magiskboot sha1 boot.img)
cp ramdisk.cpio ramdisk.cpio.orig
./magiskboot compress=xz magisk magisk.xz
./magiskboot compress=xz stub.apk stub.xz
./magiskboot compress=xz init-ld init-ld.xz
# Android 12, dm-verity и FBE: так Magisk выбирает на этих устройствах (KEEPVERITY/KEEPFORCEENCRYPT = true)
# PREINITDEVICE: на устройстве boot_patch.sh берёт `magisk --preinit-device`; без него приложение (env_check = 2)
# просит полную переустановку = перезапись boot -> AVB отказывает (зависание на логотипе). Единственный вариант здесь: metadata (ext4).
cat > config <<EOF
KEEPVERITY=true
KEEPFORCEENCRYPT=true
RECOVERYMODE=false
VENDORBOOT=false
SHA1=$SHA1
PREINITDEVICE=metadata
EOF
./magiskboot cpio ramdisk.cpio \
  "add 0750 init magiskinit" \
  "mkdir 0750 overlay.d" \
  "mkdir 0750 overlay.d/sbin" \
  "add 0644 overlay.d/sbin/magisk.xz magisk.xz" \
  "add 0644 overlay.d/sbin/stub.xz stub.xz" \
  "add 0644 overlay.d/sbin/init-ld.xz init-ld.xz" \
  "patch" \
  "backup ramdisk.cpio.orig" \
  "mkdir 000 .backup" \
  "add 000 .backup/.magisk config"
./magiskboot cpio ramdisk.cpio test && { echo "ramdisk не пропатчен"; exit 1; } || true
# ядро не трогаем (патчи ядра в boot_patch.sh только для Samsung)
rm -f kernel
./magiskboot repack boot.img new-boot.img
eval "$AVB add_hash_footer --image new-boot.img --partition_size $BOOT_SIZE --partition_name boot $FOOTER_ARGS"
$AVB info_image --image new-boot.img | grep -E 'Partition Name|Digest'

# новый vbmeta (обновлённый дескриптор boot), подписан ключом AVB сборки
cp new-boot.img $W/tf/IMAGES/boot.img
rm -f $W/tf/IMAGES/vbmeta.img
cd $SRC
PATH=$SRC/out/host/linux-x86/bin:$PATH add_img_to_target_files -a $W/tf
$AVB verify_image --image $W/tf/IMAGES/vbmeta.img --key vendor/security/toc_keys/SCPFirmwareContentCertPK.pem \
  --follow_chain_partitions 2>&1 | tail -n 15 || true
[ "${MAGISK_DRY:-}" = 1 ] && { echo "DRY: $OUT не тронут"; exit 0; }
cp $W/tf/IMAGES/boot.img $OUT/boot.img
cp $W/tf/IMAGES/vbmeta.img $OUT/vbmeta.img
echo "MAGISK OK: $(sha256sum $OUT/boot.img | cut -c1-8) boot, $(sha256sum $OUT/vbmeta.img | cut -c1-8) vbmeta"
