#!/bin/bash
# T95: генерирует СВОИ app_keys (подпись системных APK + OTA + payload APEX) вместо публичных ключей SDK AW.
# Использование:  bash gen_app_keys.sh /путь/H618-Android12-Src /путь/надёжная-копия-ключей
# - оригинальные ключи AW сохраняются один раз в <надёжная-копия>/app_keys_allwinner
# - резервная копия новых ключей в <надёжная-копия>/app_keys
# - toc_keys НЕ трогаются (createkeys.sh AW перегенерировал бы их: не используйте его)
# Ключи без пароля (их использует pack4dist / sign_target_files_apks в неинтерактивном режиме).
set -euo pipefail
SRC=${1:?использование: gen_app_keys.sh <H618-Android12-Src> <папка-надёжной-копии>}
SAFE=${2:?использование: gen_app_keys.sh <H618-Android12-Src> <папка-надёжной-копии>}
OUT=$SRC/vendor/security/app_keys
ORIG=$SAFE/app_keys_allwinner
BACKUP=$SAFE/app_keys
SUBJ=${SUBJ:-'/C=XX/O=T95 H616/OU=Android/CN=T95 H616 Android'}

mkdir -p "$SAFE"
if [ ! -d "$ORIG" ]; then cp -a "$OUT" "$ORIG"; echo "оригиналы AW -> $ORIG"; fi
if [ -d "$BACKUP" ]; then echo "ОШИБКА: $BACKUP уже существует (ключи уже сгенерированы?): не перезаписываю"; exit 1; fi

TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
cd "$TMP"
export OPENSSL_CONF=$SRC/vendor/security/openssl.cnf
for k in platform media shared networkstack releasekey; do
    # make_key ВСЕГДА завершается с кодом 1 (trap EXIT): проверяем созданные файлы
    printf '\n' | bash "$SRC/development/tools/make_key" "$k" "$SUBJ" >/dev/null || true
    [ -s "$k.pk8" ] && [ -s "$k.x509.pem" ] || { echo "ОШИБКА: make_key $k не создал ключи"; exit 1; }
    openssl pkcs8 -inform DER -nocrypt -in "$k.pk8" -out "$k.pem"     # как в SDK AW (также .pem)
done
openssl genrsa -out product_apex_payload.pem 4096 2>/dev/null

rm -rf "$OUT"; mkdir -p "$OUT"; cp -a "$TMP"/* "$OUT"/
mkdir -p "$BACKUP"; cp -a "$TMP"/* "$BACKUP"/; chmod 700 "$BACKUP"; chmod 600 "$BACKUP"/*
echo "новые app_keys в $OUT (копия в $BACKUP):"
for k in platform media shared networkstack releasekey; do
    printf '  %-13s ' "$k"; openssl x509 -in "$OUT/$k.x509.pem" -noout -subject -fingerprint -sha256 | tr '\n' ' '; echo
done
