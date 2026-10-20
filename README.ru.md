[English](README.md) · **Русский** · [Italiano](README.it.md)

# Чистый Android 12 для T95 (Allwinner H616)

Android 12 (TV) для ТВ-приставки T95 H616, собранный из официальных исходников
Orange Pi Zero 3 (`H618-Android12-Src`, BSP Allwinner) и портированный на T95. С b18 ядро обновлено
с 5.4.125 до **5.4.302**.
Без мусора, без вирусов, с патчами безопасности AOSP.

В этом репозитории — **патчи и инструменты** для сборки прошивки из исходников.
Готовый образ для прошивки — в [Releases](../../releases).

## Зачем

Стоковая прошивка T95 заражена (предустановленный софт сам ставит приложения и ходит в сеть).
Поэтому я собрал Android 12 с нуля из открытых исходников.

## Что внутри

- Android 12 (TV), 64 бит, сборка **user / release-keys**
- SELinux в режиме **enforcing** (в стоке и у Allwinner — permissive)
- Патчи безопасности AOSP **android-security-12.0.0_r34 → r69** (январь 2025) на 27 проектах (Bluetooth,
  frameworks/av, frameworks/base, webp, freetype, libxml2, skia и др.). Уровень патча **2025-01-01**
  (фреймворк). С b18 ядро **5.4.302** (исправления LTS до декабря 2025, последний выпуск 5.4); закрытые
  бинарники Allwinner (GPU, видео, Wi-Fi) обновить нельзя
- Все системные приложения и secure boot (toc0/toc1/vbmeta) подписаны **моими собственными ключами**
  (вместо публичных ключей SDK Allwinner, которыми может подписать кто угодно)
- Лаунчер **Arc Launcher** 1.0.10 (с b21; GPL-форк LTvLauncher/FLauncher), пересобран без самообновления и с тёмным
  фоном по умолчанию: 0% CPU в покое, фокус пульта не теряется, если BT-мышь подключается во время загрузки. С b23
  главный экран сразу открывается со списком «All Apps» (нет «Избранного» по умолчанию, из-за которого приложения
  уходили за нижний край экрана), и рамка фокуса рисуется всегда (с некоторыми мышами, например Logitech M590, она
  пропадала, и казалось, что пульт не работает). До b19
  лаунчером был **FLauncher** (форк osrosal 2025.07.001) с выключенной анимацией подсветки карточек (иначе 60 fps и
  ~95% одного ядра постоянно). Arc пока только на английском.
- Приложения: **F-Droid**, **SmartTube**, **VLC**, **Material Files**, **Downloader** (AFTVnews),
  WebView **Cromite 153** вместо старого AOSP WebView 91
- С b19: системное окно выбора файлов/папок (**DocumentsUI**) — нужно приложениям резервного копирования
  (например Alpha Backup) и для добавления SD-карты в Material Files; приложения видят температуру процессора;
  звук при загрузке на 24 дБ тише
- С b21: анимации окон/переходов 0,5x по умолчанию (на 1x Mali/HWC даёт разорванные кадры при открытии/закрытии
  приложений), тёмный нейтральный системный фон вместо логотипа Orange Pi, **VLC из F-Droid** (теперь обновляется
  через F-Droid), Bluetooth LE privacy только на контроллерах, которые её поддерживают (на чипах BT 4.0 BLE-мыши и
  пульты снова подключаются сами после перезагрузки)
- С b23: **установленные пользователем приложения могут запускаться при загрузке** (оверлеи температуры, виджеты
  погоды, опции «запуск при старте»). Менеджер фоновых процессов Allwinner (Awbms, `awbms_config`) блокировал
  `BOOT_COMPLETED` и фоновые сервисы всех приложений не из своего белого списка. Сборка теперь разделена по платам:
  имя образа, продукт Android и имя устройства указывают плату (см. [Как прошить](#как-прошить))
- ИК-пульт (включение из сна тоже), передний дисплей FD655 (часы + значки LAN/WiFi/USB),
  имя устройства `T95_h616`
- **Выключение с пульта**: долгое нажатие power → меню «Выключить / Перезагрузить» (управляется стрелками
  пульта). «Выключить» — приставка гасит HDMI и дисплей и ждёт, включение кнопкой power на пульте
  (с исходным кодом Allwinner T95 вместо выключения перезагружался; в b13–b15 — обход в BL31, в b16
  исправлена настоящая причина, см. [Выключение](#выключение))
- RTC сохраняет время и флаги перезагрузки при перезагрузке (до b16 каждый сброс их обнулял)

Google-сервисов (GApps) нет. Приложения — через F-Droid, Aurora Store (ставится из F-Droid) или Downloader.

### Что убрано

- Дыры Allwinner: ADB по сети с root **без авторизации** (порт 5555 открыт для всей локальной сети),
  `runin.sh` (выполнял команды из файла на `/sdcard` от root), `preinstall` / `preloaddata` (тихая
  установка APK при запуске), `appsdisable`, `fix_traceing`, `platform_app` с `mlstrustedsubject`
- 26 приложений: заводские тесты и демо Allwinner (Test_AD — меняет лого/анимацию загрузки, DragonBox,
  DragonAgingTV, DragonAtt, AwlogSettings, TvdFileManager, VideoPlayer, Update) и ненужное на ТВ
  (EasterEgg, Traceur, LiveTv, DeskClock, PhotoTable, WebScreensaver, Contacts, Calendar, Camera2, Music,
  SoundRecorder, ExactCalculator, QuickSearchBox, SimAppDialog, WAPPushManager, NfcNci, SecureElement)

## Проверено на

T95, Allwinner H616, 4 ГБ ОЗУ, PMIC **AXP806**, Wi-Fi/BT **UWE5622**,
Ethernet AC200 (100 Мбит).

**Работает:** загрузка, HDMI 1080p, Ethernet, Wi-Fi 2,4/5 ГГц, Bluetooth (колонка A2DP), аппаратное
декодирование видео (SmartTube VP9, VLC H.264 4K), GPU Mali-G31, ИК-пульт, сон/пробуждение и
выключение/включение пультом, дисплей FD655, обе USB.
**Не проверено:** звук через HDMI, CEC.

Вторая плата, **H616-T95MAX-AXP313A-V2.0** (PMIC **AXP313A**, Wi-Fi/BT **BCM43342**, 2 ГБ), имеет свою папку
`configs/t95-axp313`, свой продукт `apollo_t95axp313` и свой **релиз** (`axp313-final`, раньше тестовые pre-release `axp313-*`), его проверил
пользователь 4PDA на версии с **eMMC**. С axp313-test11 там тоже работают сон и пробуждение: прерывание
пробуждения Wi-Fi (host-wake) блокировало лёгкий сон s2idle, теперь оно не будит систему (ядро, `0005`). Версия
этой платы с **NAND** пока не прошивается (драйвер NAND в U-Boot из BSP не запускает микросхему).

Платы называются **T95-AXP806** (эта приставка) и **T95-AXP313** (`-eMMC` / `-NAND`). Не прошивайте образ для одной
платы на другую: в имени файла указано, для какой он платы (`T95-AXP806-…`, `T95-AXP313-eMMC-…`;
b23 и тестовые сборки: `update.T95-…`; до b22: `t95axp806` / `t95axp313`).

> [!WARNING]
> T95 бывают с разной памятью, PMIC и Wi-Fi. На другой ревизии платы прошивка может не загрузиться —
> см. [Как вернуться](#как-вернуться-на-сток-или-другую-прошивку).

## Как прошить

1. **Сохраните свою текущую прошивку**, если она у вас есть (или найдите сток для своей ревизии).
2. Нужен кабель USB A-A (папа-папа) и PhoenixSuit (Windows) или OpenixSuit (Linux).
3. Скачайте из [Releases](../../releases) образ для своей платы: `T95-AXP806-a12-b24-final-user.img.xz`
   (релиз `b24-final`) или `T95-AXP313-eMMC-a12-final-user.img.xz` (релиз `axp313-final`), для root — файл `-magisk-`
   того же релиза, и распакуйте (7-Zip в Windows, `xz -d` в Linux), затем
   выберите `.img`, режим полной прошивки (Full Erase).
4. На выключенной приставке зажмите кнопку reset (в отверстии AV), подключите USB к ПК, отпустите кнопку
   через 3–5 с — начнётся прошивка.
5. Первая загрузка ~1–2 минуты.

Альтернатива без кабеля: microSD, подготовленная в PhoenixCard (режим «Product»).
**Все данные на приставке будут стёрты.** Файл `.img` — это всегда полная прошивка, а не обновление с сохранением данных.

С b23 в имени продукта и устройства Android есть плата (`apollo_t95axp806` / `apollo_t95axp313`, раньше
`apollo_t95` для обеих), поэтому OTA-пакет одной платы не установится на другую. С b22 и старше нужно один раз
прошить полный образ.

### Как вернуться на сток или другую прошивку

Прошивка **не записывает ключи в eFuse** (rotpk не прожигается — загрузчик пишет
`don't have rotpk, skip check`). Приставка не привязывается к моим ключам: можно в любой момент прошить
сток или любую другую прошивку для T95 в формате secure (toc0/toc1) тем же способом. Режим FEL (reset +
USB) находится в ПЗУ процессора, стереть его нельзя — приставка всегда восстанавливается.

> [!IMPORTANT]
> **Secure bit.** Образ в формате secure: при прошивке загрузчик пишет `burn sboot ok, set secure bit`.
> На моей приставке (как и обычно на T95 H616 со стоковой прошивкой) процессор уже в режиме secure
> с завода — ничего не меняется. Но если ваша приставка продавалась с **не-secure** прошивкой, режим
> secure включится **навсегда**: дальше будут загружаться только прошивки secure (toc0/toc1), подписанные
> любым ключом. Проверить до прошивки: сток secure, если в образе есть `toc0.fex`/`toc1.fex` (а не только
> boot0/u-boot), или по логу UART.

## Особенности

- **ADB только по сети**: «Настройки → Настройки устройства → Об устройстве», 7 нажатий на «Сборка» →
  «Для разработчиков» → включить «Отладка по USB». После этого adbd слушает порт 5555:
  `adb connect IP-приставки:5555` и подтвердите компьютер на экране пультом. По умолчанию ADB выключен.
  По кабелю USB ADB не работает: USB0 у T95 только host (нет пина ID), кабель A-A — только для прошивки.
- Короткое нажатие power — сон, долгое — меню выключения. «Выключить» — глубокий standby (U-Boot + BL31),
  а не полное отключение питания: блок питания под напряжением, включение — с пульта. Обесточить
  полностью — только вынуть блок питания.
- При первом запуске Bluetooth может стартовать на ~5 с позже (восстанавливается сам).
- Downloader (AFTVnews) — бесплатное закрытое приложение с рекламой (AdMob/Meta); при желании удалите
  обновления/отключите.
- Arc Launcher пересобран и подписан моим ключом: обновления от автора поверх не встанут, он обновляется
  вместе с прошивкой.
- В b21 VLC заменён с APK VideoLAN на сборку F-Droid (другая подпись): если Вы обновляли VLC на b20 или раньше,
  это обновление в `/data` после прошивки b21 пропадёт.
- Сборка user: нет root, нет shell на UART. С b19 есть и вариант **Magisk** (`-magisk`): та же сборка
  с `boot.img`, пропатченным Magisk; для управления root установите приложение Magisk с его страницы на GitHub.

## Сборка из исходников

### База

Официальные исходники Orange Pi Zero 3 **H618-Android12-Src** (Google Drive Orange Pi, 13.07.2023, архив
`H618-Android12-Src.tar.gz{aa..ar}`, md5 из папки Orange Pi совпадает). Плата Zero 3 в исходниках
называется **p2** (продукт `apollo_p2`); для T95 сделаны платы **t95-axp806** и **t95-axp313** (longan) и продукты
**apollo_t95axp806** и **apollo_t95axp313** (Android) с общей частью `device/softwinner/apollo/t95-common`.
Хост сборки: Ubuntu 22.04.

**Ключей подписи в репозитории нет**: генерируйте свои (`tools/gen_app_keys.sh` для ключей приложений,
`dragonsecboot` для `toc_keys`).

### Файлы

| Файл | Содержание |
|---|---|
| `longan/device/config/chips/h618/configs/t95-axp806/` | готовая папка платы `t95-axp806` (скопировать в исходники; до b22 называлась `t95`): `configs/p2` (Zero 3) + изменения: `board.dts` ядра (AXP806, eMMC DDR52, gmac1+AC200, LED, VBUS PH8, USB0 host, ИК fe02, OPP…), `sys_config.fex` (DRAM из стока T95), `uboot-board.dts` |
| `patches/03a-device-apollo-t95-vs-p2.patch` | устройство `apollo-t95` = копия `apollo-p2` + изменения (патч 14 делит его на две платы) (BoardConfig, sepolicy, FD655, ИК-раскладка, HDMI 1080p, RRO NetworkStack, WebView overlay, `apps/Android.mk`) |
| `patches/03b-product-apollo_t95-vs-p2.patch` | `apollo_t95.mk` = копия `apollo_p2.mk` + изменения |
| `patches/04-aw-fixes-64bit-security.patch` | исправления Allwinner: сборка 64 бит (модули с 32-битными блобами → 32 бит, printf/типы, ABI-дампы, HDR10+), безопасность (ADB по сети без авторизации, `platform_app mlstrustedsubject`, `service_contexts`, `/dev/watchdog`), `AndroidProducts.mk`, `pack4dist`, уровень патча 2025-01-01 |
| `patches/05-aosp-security-r34-r69.patch` | патчи безопасности AOSP android-security-12.0.0_r34 → r69 (27 проектов), включая разрешённые конфликты и `make update-api`. Сюда же попала 1 строка T95 в `system/bt/btif/src/btif_dm.cc` (имя BT из `bluetooth.device.default_name`) |
| `patches/06-flauncher-v2025.07.001-t95.patch` | [FLauncher](https://github.com/osrosal/flauncher) (тег v2025.07.001): анимация подсветки выключена по умолчанию. Сборка: Flutter 3.24.5, JDK 17, `flutter build apk --release --split-per-abi --target-platform android-arm64` |
| `patches/08-poweroff-menu-t95.patch` | выключение и меню: долгое нажатие power = меню Выключить/Перезагрузить (overlay `apollo-t95` `config.xml`), SystemUI `GlobalActionsDialogLite`: кнопки выбираются стрелками пульта (фокус, белая рамка), FD655 гаснет при выключении (`fd655.rc` on shutdown), SELinux: audio.routing, dontaudit installd |
| `patches/09-rtc-axp806-offctl-t95.patch` | исправление сброса RTC (b16): U-Boot (`pmu_axp806.c`) и ядро (`axp2101.c`) сбрасывают бит 4 регистра AXP806 0x32 (OFF_CTL), который включает бинарный sboot. С ним каждый сброс SoC обнулял весь домен RTC. См. [Выключение](#выключение) |
| `patches/10-b19-t95-axp313.patch` | b19: DocumentsUI (его убирал override `TvdFileManager`), SELinux: приложения читают температуру процессора (`sysfs_thermal`, `sysfs_temp`). Для платы AXP313A: `PRODUCT_BOARD` из `T95_BOARD` (заменено двумя продуктами патча 14), лёгкий сон s2idle (`axp313-s2idle.rc`, `/sys/power/mem_sleep` → `sysfs_power`), BCM43342 в `libhwinfo.c`, `config.txt` AP6334 с ccode XZ/11. Только для тестовых сборок (`T95_LOGGER=1`): сборщик логов `t95log` (dmesg/logcat в `/sdcard/T95_LOG`) |
| `patches/11-b21-t95.patch` | b20/b21: анимации 0,5x по умолчанию (overlay SettingsProvider `defaults.xml`), Bluetooth LE local privacy только если контроллер умеет LL privacy (`btif_dm.cc`), Arc Launcher вместо FLauncher (`apps/Android.mk`, `apollo_t95.mk`), VLC из F-Droid. Фон создаёт `tools/t95_wallpaper.py` |
| `patches/12-arclauncher-1.0.10-t95.patch` | [Arc Launcher](https://github.com/meddouribadis/arclauncher) (тег 1.0.10): тёмный фон по умолчанию; с b23 (1.0.10-t95.4) нет «Избранного» по умолчанию (главный экран открывается на All Apps) и подсветка фокуса всегда включена (`FocusHighlightStrategy.alwaysTraditional`). Сборка: Flutter 3.41.9, `flutter build apk --release --flavor play --split-per-abi --target-platform android-arm64` (во flavor `play` нет самообновления) |
| `patches/07-kernel-5.4.302/` | ядро 5.4.125 → 5.4.302 (с b18): скрипт merge ACK, разрешённые конфликты, 0001–0003 (0003 — исправление зависания после сна), только плата AXP313A: 0004 — BCM43342 в bcmdhd, 0005 — host-wake Wi-Fi больше не будит систему (`oob_wake=0`, исправляет s2idle). См. [Ядро](#ядро) |
| `patches/13-b23-t95.patch` | b23: менеджер фоновых процессов Allwinner без блокировок (`device/softwinner/common/config/awbms_config`: `blockBroadcast`, `skipService` = false) — приложения пользователя получают `BOOT_COMPLETED` и могут запускать сервисы; комментарий Arc в `apps/Android.mk` |
| `patches/14-split-boards-t95axp806-t95axp313.patch` | b23: по продукту на плату. `apollo_t95.mk` → `t95-common/t95_product.mk` (общий), новые `apollo_t95axp806.mk` / `apollo_t95axp313.mk`, папки устройств `apollo-t95axp806` / `apollo-t95axp313` (BoardConfig, `system/`, camera); apps, overlay, sepolicy, `t95/`, `t95log/` перенесены в `t95-common`. Содержит переименования: применять через `git apply` |
| `patches/15-b24-fd655-boot.patch` | b24: передний дисплей показывает `boot` через несколько секунд после включения, как стоковая прошивка (`fd655.rc`: `on early-init`); раньше он был тёмным до запуска службы часов (10–15 с) |
| `longan/device/config/chips/h618/configs/t95-axp313/` | папка платы H616-T95MAX-AXP313A-V2.0: AXP313A (как у Zero 3), DRAM из стоковой прошивки A29, тактовая 32 кГц для AP6334, выводы NAND; создаётся двумя инструментами `t95_axp313_*` |
| `tools/bl31_t95_patch.py` | создаёт `bin/bl31_<плата>.bin` (`bl31_t95-axp806.bin`, `bl31_t95-axp313.bin`; `pack` выбирает его по имени платы) из `bl31.bin`: пропуск «hardware check» только для H618 (0x1F4C). С `--fakeoff` — ещё старый обход выключения из b13–b15 (PSCI SYSTEM_OFF, 0x1CF0..0x1D00), с b16 не нужен |
| `tools/t95_board_dts.py` | генератор `board.dts` t95-axp806 из p2 (результат уже в `configs/t95-axp806`) |
| `tools/t95_sys_config.py` | генератор `sys_config.fex` t95-axp806 из p2 + стокового `sys_config.fex` T95 |
| `tools/gen_app_keys.sh` | генерация своих ключей приложений (platform/media/shared/networkstack/releasekey) |
| `tools/t95_bootsound.py` | громкость звука загрузки в `bootanimation.zip` (b19: `-24` дБ) |
| `tools/t95_wallpaper.py` | создаёт системный фон по умолчанию (тёмный градиент, b20+) в overlay `t95-common` (нужен Pillow) |
| `tools/magisk-boot.sh` | вариант с root: патчит Magisk-ом `boot.img` из signed target files, переподписывает vbmeta своим ключом AVB; затем `pack -v` |
| `tools/t95_axp313_board_dts.py`, `tools/t95_axp313_sys_config.py` | создают `board.dts` и `sys_config.fex` для `configs/t95-axp313` из p2 (+ стоковый `sys_config.fex` этой платы) |

### Порядок

Клонируйте репозиторий рядом с распакованной папкой `H618-Android12-Src`:

```sh
git clone https://github.com/well83/t95-h616-android12.git
cd H618-Android12-Src
cp -a ../t95-h616-android12/longan .                         # папки плат configs/t95-axp806, t95-axp313
cp -a device/softwinner/apollo/apollo-p2 device/softwinner/apollo/apollo-t95
cp    device/softwinner/apollo/apollo_p2.mk device/softwinner/apollo/apollo_t95.mk
bash ../t95-h616-android12/patches/07-kernel-5.4.302/merge-ack-5.4.302.sh longan/kernel/linux-5.4 ~/k302   # ядро 5.4.302
rsync -a --delete --exclude=.git ~/k302/linux-5.4/ longan/kernel/linux-5.4/
for p in 03a 03b 04 05 08 09 10 11 13 14 15; do git apply -p1 ../t95-h616-android12/patches/$p-*.patch; done   # 14: только git apply (переименования)
B=device/softwinner/apollo/common/media/bootanimation/bootanimation.zip
python3 ../t95-h616-android12/tools/t95_bootsound.py $B $B.new -24 && mv $B.new $B   # звук загрузки -24 дБ
python3 ../t95-h616-android12/tools/t95_wallpaper.py device/softwinner/apollo/t95-common/overlay/frameworks/base/core/res/res
python3 ../t95-h616-android12/tools/bl31_t95_patch.py longan/device/config/chips/h618/bin/bl31.bin \
        longan/device/config/chips/h618/bin/bl31_t95-axp806.bin
```

APK приложений кладутся в `device/softwinner/apollo/t95-common/apps/<Имя>/`, нативные библиотеки из APK
распаковать в `apps/<Имя>/lib/arm64/` (см. `apps/Android.mk`, там же SHA-256 каждого APK): ArcLauncher
(собранный с патчем 12; до b19 FLauncher с патчем 06), MaterialFiles 1.7.5 (F-Droid), CromiteWebView 153.0.8010.37 (arm64
SystemWebView), SmartTube 32.56 stable, VLC 3.7.2 arm64 (сборка F-Droid), Downloader 2.0.4 (+ `split_config.*`),
F-Droid 2.0.1.

Ключи: свои `toc_keys` в `vendor/security/toc_keys` (secure boot, vbmeta), свои ключи приложений:

```sh
bash ../t95-h616-android12/tools/gen_app_keys.sh $PWD /надёжное/место
```

Сборка:

```sh
cd longan && ./build.sh autoconfig -o android -i h618 -b t95-axp806 -n default -k linux-5.4 -a arm64 && ./build.sh && cd ..
source build/envsetup.sh && lunch apollo_t95axp806-user && make -j10 && pack4dist -v
# образ: longan/out/h618_android12_t95-axp806_uart0_secure_v0.img
```

> [!NOTE]
> Не пускайте вывод `./build.sh` через пайп (`| grep`, `| head`): сборка зависает.

Вариант с root (после сборки выше): `bash ../t95-h616-android12/tools/magisk-boot.sh Magisk-v30.7.apk && pack -v`.

Плата AXP313A: дополнительно примените к ядру `patches/07-kernel-5.4.302/0004-*.patch` и `0005-*.patch`, скопируйте прошивки
Wi-Fi/BT этой платы из её стокового `/vendor/etc/firmware` (`fw_bcm43342_ag*.bin`, `nvram_ap6334.txt`,
`bcm43342a1.hcd`; не включены, лицензия Broadcom) в `hardware/aw/wireless/partner/ampak/firmware/ap6334/`,
создайте `bin/bl31_t95-axp313.bin` через `tools/bl31_t95_patch.py` (как для t95-axp806), затем собирайте с
`-b t95-axp313` и `lunch apollo_t95axp313-user`. Образ: `longan/out/h618_android12_t95-axp313_uart0_secure_v0.img`.

### Ядро

В релизной сборке (с b18) ядро **5.4.302**. Ядро Allwinner из H618-Android12-Src (5.4.125) = Android
Common Kernel (ACK) android12-5.4 + BSP Allwinner, поэтому обновление делается через `git merge` с веткой
ACK, а не патчами (`patches/07-kernel-5.4.302/`):

- `merge-ack-5.4.302.sh` скачивает ACK (~3–4 ГБ, история с 05.2021), создаёт ветку `aw-base` (коммит
  ACK 73e6d86c3, ближайший к ядру AW, + дерево AW), делает merge android12-5.4.302_r00 (250657e3e),
  разрешает 11 конфликтов (`resolved/` — файлы после разрешения) и применяет:
  - 0001: `sun50i-cpufreq-nvmem.c` = версия AW целиком (после merge не собирается);
  - 0002: `drivers/mmc/core` = версия AW;
  - 0003: **исправление зависания после сна** (см. ниже);
  - только плата AXP313A: 0004 (имя прошивки BCM43342) и 0005 (параметр `bcmdhd` `oob_wake`, по умолчанию 0:
    прерывание host-wake Wi-Fi по уровню срабатывало сразу при входе в s2idle и на минуты занимало CPU0).
- Дерево AW должно быть чистым (только что распакованным, ни разу не собранным). Патч 09 накладывать
  **после** копирования дерева в `longan/kernel/linux-5.4`. При смене версии ядра сначала удалить
  `longan/out/kernel/{build,staging}`, иначе clang падает на старом конфиге.

**Зависание после сна (0003).** С 5.4.302 бокс выходил из сна и через несколько секунд намертво зависал
(все CPU, прерывания выключены, в случайном месте). Bisect по истории ACK: 5.4.288 — хорошо, 5.4.290 —
плохо. В 5.4.290 пришёл upstream 2f8dea1692ee «hrtimers: Handle CPU state correctly on hotplug»: сброс
состояния hrtimer каждого CPU перенесён в callback шага hotplug `CPUHP_AP_HRTIMERS_DYING`. Но в ACK
android12-5.4 коммит, который добавляет этот шаг (5c0930ccaad5), откатили (ради ABI), и callback никогда
не вызывается: после сна вторичные CPU возвращаются со старым состоянием таймеров, и система зависает.
0003 возвращает сброс в `hrtimers_prepare_cpu()`. Это ошибка ACK: она касается любого устройства на
android12-5.4 с ядром ≥ 5.4.290, которое засыпает с отключением CPU.

Под T95 ядро адаптируется конфигурацией платы в longan (`longan/device/config/chips/h618/configs/t95-axp806`):

- `linux-5.4/board.dts` (генератор `tools/t95_board_dts.py`): AXP806 вместо AXP1530, eMMC DDR52,
  gmac1/AC200 (twi3, PA10/11), LED PH6/7, VBUS PH8, USB0 host, ИК fe02/0x40, OPP, card detect SD PI16.
  Скомпилированный dtb сверен со стоковым `sunxi_t95.dtb` бокса.
- `sys_config.fex` (`tools/t95_sys_config.py`): DRAM/twi/gpio_bias из стока, питание AXP806.
- `uboot-board.dts`: boot_clock 1008, AXP806, `sdc_io_1v8=0`. `pack` **не** сливает `sys_config` в DT
  U-Boot, поэтому значения для U-Boot надо писать прямо в `uboot-board.dts`.
- BL31: `bl31.bin` из SDK на H616 не стартует (проверка «только H618») → `tools/bl31_t95_patch.py`
  (только «hardware check»; `--fakeoff` — старый обход выключения, см. ниже).

Чтобы собрать с исходным ядром 5.4.125 (как в b16), пропустите две строки про ядро в разделе [Порядок](#порядок).

### Выключение

Схема Allwinner «fake poweroff»:

1. Ядро (`CONFIG_SUNXI_FAKE_POWEROFF`) пишет 0xe в RTC GPR[2].
2. BL31 SYSTEM_OFF меняет его на 2 и делает сброс.
3. U-Boot (`CONFIG_ATF_BOX_STANDBY`) вызывает SMC 0x8000ff14.
4. BL31 читает GPR[2]==2 и `/box_start_os0` из DT → standby с пробуждением по ИК.

До b15 на T95 это **не работало**: каждый сброс обнулял весь домен RTC (все GPR, время, ALARM0_DAY),
флаг терялся, и бокс просто перезагружался. Со стоковой прошивкой тот же бокс сохраняет GPR при сбросе —
значит, дело не в железе.

**Причина (найдена 11.10.2026):** бит 4 регистра AXP806 **0x32 (OFF_CTL)**. Его при каждой загрузке
включает sboot, собранный из SDK (код PMIC — в бинарной `spl-pub/board/h616/libsun50iw9p1_sboot.a`);
сток оставляет 0 (OFF_CTL = 0x26). С включённым битом 4 сброс SoC обнуляет домен RTC. PMIC хранит значение,
пока не отключить блок питания, поэтому после нашей прошивки GPR терялись даже со стоковой цепочкой
загрузки. Проверено бисекцией на боксе из U-Boot (`sunxi_axp pmu write 0x32 …`, `mw 0x0700010c …`,
`reset`): 0x26 и 0x24 — GPR сохраняются, 0x36 и 0x34 — обнуляются. Ядро, BL31, U-Boot и способ сброса
исключены поочерёдной заменой на стоковые sboot/BL31/U-Boot.

**Исправление (b16, `patches/09`):** U-Boot сбрасывает бит 4 сразу после определения AXP806 (до любого
возможного сброса), драйвер ядра сбрасывает его ещё раз. Штатная схема Allwinner выше работает без
изменений, время и флаги перезагрузки переживают перезагрузку.

**Старый обход (b13–b15):** `tools/bl31_t95_patch.py --fakeoff` патчит PSCI SYSTEM_OFF: при GPR[2]==0xe
BL31 сразу вызывает box standby (функция 0x1B2C с сохранённым DT) без сброса. Работает, но это патч
закрытого бинарника и больше не нужен.

Отдельного SCP нет и в стоке: standby целиком внутри BL31 (код в SRAM A2 0x20000).

## Другие ревизии платы

T95 бывают с другим PMIC (например AXP313A/AXP1530), памятью и Wi-Fi. У платы AXP313A теперь есть своя папка
`configs/t95-axp313` (см. [Проверено на](#проверено-на)). Ревизия описывается своей папкой платы,
как у Orange Pi и Radxa: `longan/device/config/chips/h618/configs/<плата>/` с `sys_config.fex` (DRAM, напряжения PMIC, GPIO),
`linux-5.4/board.dts` (DT ядра) и `uboot-board.dts`, плюс небольшой продукт Android (`apollo_t95<имя>.mk` и папка
устройства, как `apollo-t95axp806`; всё остальное общее в `t95-common`). Папка Zero 3 `p2` уже
описывает AXP1530/AXP313A — хорошая отправная точка для таких боксов.

Чтобы добавить ревизию, присылайте pull request с новой папкой `longan/device/config/chips/h618/configs/t95-<имя>/` и, если можно, стоковым
`sys_config.fex`/DTB этого бокса, фото платы и логом UART первой загрузки. Сам я могу проверить только плату
с AXP806, поэтому новая папка принимается после того, как автор подтвердит, что сборка загружается.

## Безопасность и ключи

Ключи подписи я **не публикую и никому не передаю** — это гарантия, что никто другой не сможет выпустить
«обновление» для ваших приставок. Если собираете свой образ — генерируйте свои ключи.

## Лицензии

- Папки плат `longan/device/config/chips/h618/configs/t95-axp806/` и `t95-axp313/` сделаны из конфигурации BSP Orange Pi /
  Allwinner (`configs/p2`) и остаются под лицензией этих файлов.
- Патчи к AOSP, BSP Allwinner и device tree — под лицензией изменяемых файлов (в основном Apache-2.0;
  ядро и файлы в `patches/07-kernel-5.4.302/resolved/` — GPL-2.0).
- `patches/06-flauncher-v2025.07.001-t95.patch` — изменение FLauncher, `patches/12-arclauncher-1.0.10-t95.patch` —
  изменение Arc Launcher, оба GPL-3.0.
- Инструменты в `tools/` и документация — Apache-2.0 (см. [LICENSE](LICENSE)).
- Предустановленные приложения не изменены (кроме FLauncher / Arc Launcher), лицензии и подписи — авторов.

## Благодарности

Orange Pi (исходники H618 Android 12), Allwinner BSP, osrosal (FLauncher), meddouribadis (Arc Launcher), авторы SmartTube, VLC,
F-Droid, Material Files, Cromite.
