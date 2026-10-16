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
- Лаунчер **FLauncher** (форк osrosal 2025.07.001), анимация подсветки карточек выключена по умолчанию
  (иначе 60 fps и ~95% одного ядра постоянно)
- Приложения: **F-Droid**, **SmartTube**, **VLC**, **Material Files**, **Downloader** (AFTVnews),
  WebView **Cromite 153** вместо старого AOSP WebView 91
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

> [!WARNING]
> T95 бывают с разной памятью, PMIC и Wi-Fi. На другой ревизии платы прошивка может не загрузиться —
> см. [Как вернуться](#как-вернуться-на-сток-или-другую-прошивку).

## Как прошить

1. **Сохраните свою текущую прошивку**, если она у вас есть (или найдите сток для своей ревизии).
2. Нужен кабель USB A-A (папа-папа) и PhoenixSuit (Windows) или OpenixSuit (Linux).
3. Скачайте `update.opi-t95-a12-b18-user.img.xz` из [Releases](../../releases) и распакуйте
   (7-Zip в Windows, `xz -d` в Linux), затем выберите `update.opi-t95-a12-b18-user.img`, режим полной прошивки (Full Erase).
4. На выключенной приставке зажмите кнопку reset (в отверстии AV), подключите USB к ПК, отпустите кнопку
   через 3–5 с — начнётся прошивка.
5. Первая загрузка ~1–2 минуты.

Альтернатива без кабеля: microSD, подготовленная в PhoenixCard (режим «Product»).
**Все данные на приставке будут стёрты.**

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
- FLauncher пересобран и подписан моим ключом: обновления от автора поверх не встанут, он обновляется
  вместе с прошивкой.
- Сборка user: нет root, нет shell на UART.

## Сборка из исходников

### База

Официальные исходники Orange Pi Zero 3 **H618-Android12-Src** (Google Drive Orange Pi, 13.07.2023, архив
`H618-Android12-Src.tar.gz{aa..ar}`, md5 из папки Orange Pi совпадает). Плата Zero 3 в исходниках
называется **p2** (продукт `apollo_p2`); для T95 сделаны новая плата **t95** и продукт **apollo_t95**.
Хост сборки: Ubuntu 22.04.

**Ключей подписи в репозитории нет**: генерируйте свои (`tools/gen_app_keys.sh` для ключей приложений,
`dragonsecboot` для `toc_keys`).

### Файлы

| Файл | Содержание |
|---|---|
| `longan/device/config/chips/h618/configs/t95/` | готовая папка платы `t95` (скопировать в исходники): `configs/p2` (Zero 3) + изменения: `board.dts` ядра (AXP806, eMMC DDR52, gmac1+AC200, LED, VBUS PH8, USB0 host, ИК fe02, OPP…), `sys_config.fex` (DRAM из стока T95), `uboot-board.dts` |
| `patches/03a-device-apollo-t95-vs-p2.patch` | устройство `apollo-t95` = копия `apollo-p2` + изменения (BoardConfig, sepolicy, FD655, ИК-раскладка, HDMI 1080p, RRO NetworkStack, WebView overlay, `apps/Android.mk`) |
| `patches/03b-product-apollo_t95-vs-p2.patch` | `apollo_t95.mk` = копия `apollo_p2.mk` + изменения |
| `patches/04-aw-fixes-64bit-security.patch` | исправления Allwinner: сборка 64 бит (модули с 32-битными блобами → 32 бит, printf/типы, ABI-дампы, HDR10+), безопасность (ADB по сети без авторизации, `platform_app mlstrustedsubject`, `service_contexts`, `/dev/watchdog`), `AndroidProducts.mk`, `pack4dist`, уровень патча 2025-01-01 |
| `patches/05-aosp-security-r34-r69.patch` | патчи безопасности AOSP android-security-12.0.0_r34 → r69 (27 проектов), включая разрешённые конфликты и `make update-api`. Сюда же попала 1 строка T95 в `system/bt/btif/src/btif_dm.cc` (имя BT из `bluetooth.device.default_name`) |
| `patches/06-flauncher-v2025.07.001-t95.patch` | [FLauncher](https://github.com/osrosal/flauncher) (тег v2025.07.001): анимация подсветки выключена по умолчанию. Сборка: Flutter 3.24.5, JDK 17, `flutter build apk --release --split-per-abi --target-platform android-arm64` |
| `patches/08-poweroff-menu-t95.patch` | выключение и меню: долгое нажатие power = меню Выключить/Перезагрузить (overlay `apollo-t95` `config.xml`), SystemUI `GlobalActionsDialogLite`: кнопки выбираются стрелками пульта (фокус, белая рамка), FD655 гаснет при выключении (`fd655.rc` on shutdown), SELinux: audio.routing, dontaudit installd |
| `patches/09-rtc-axp806-offctl-t95.patch` | исправление сброса RTC (b16): U-Boot (`pmu_axp806.c`) и ядро (`axp2101.c`) сбрасывают бит 4 регистра AXP806 0x32 (OFF_CTL), который включает бинарный sboot. С ним каждый сброс SoC обнулял весь домен RTC. См. [Выключение](#выключение) |
| `patches/07-kernel-5.4.302/` | ядро 5.4.125 → 5.4.302 (с b18): скрипт merge ACK, разрешённые конфликты, 0001–0003 (0003 — исправление зависания после сна). См. [Ядро](#ядро) |
| `tools/bl31_t95_patch.py` | создаёт `bin/bl31_t95.bin` из `bl31.bin`: пропуск «hardware check» только для H618 (0x1F4C). С `--fakeoff` — ещё старый обход выключения из b13–b15 (PSCI SYSTEM_OFF, 0x1CF0..0x1D00), с b16 не нужен |
| `tools/t95_board_dts.py` | генератор `board.dts` t95 из p2 (результат уже в `configs/t95`) |
| `tools/t95_sys_config.py` | генератор `sys_config.fex` t95 из p2 + стокового `sys_config.fex` T95 |
| `tools/gen_app_keys.sh` | генерация своих ключей приложений (platform/media/shared/networkstack/releasekey) |

### Порядок

Клонируйте репозиторий рядом с распакованной папкой `H618-Android12-Src`:

```sh
git clone https://github.com/well83/t95-h616-android12.git
cd H618-Android12-Src
cp -a ../t95-h616-android12/longan .                                   # папка платы configs/t95
cp -a device/softwinner/apollo/apollo-p2 device/softwinner/apollo/apollo-t95
cp    device/softwinner/apollo/apollo_p2.mk device/softwinner/apollo/apollo_t95.mk
bash ../t95-h616-android12/patches/07-kernel-5.4.302/merge-ack-5.4.302.sh longan/kernel/linux-5.4 ~/k302   # ядро 5.4.302
rsync -a --delete --exclude=.git ~/k302/linux-5.4/ longan/kernel/linux-5.4/
for p in 03a 03b 04 05 08 09; do git apply -p1 ../t95-h616-android12/patches/$p-*.patch; done   # или patch -p1 < ...
python3 ../t95-h616-android12/tools/bl31_t95_patch.py longan/device/config/chips/h618/bin/bl31.bin \
        longan/device/config/chips/h618/bin/bl31_t95.bin
```

APK приложений кладутся в `device/softwinner/apollo/apollo-t95/apps/<Имя>/`, нативные библиотеки из APK
распаковать в `apps/<Имя>/lib/arm64/` (см. `apps/Android.mk`, там же SHA-256 каждого APK): FLauncher
(собранный с патчем 06), MaterialFiles 1.7.5 (F-Droid), CromiteWebView 153.0.8010.37 (arm64
SystemWebView), SmartTube 32.56 stable, VLC 3.7.1 arm64, Downloader 2.0.4 (+ `split_config.*`),
F-Droid 2.0.1.

Ключи: свои `toc_keys` в `vendor/security/toc_keys` (secure boot, vbmeta), свои ключи приложений:

```sh
bash ../t95-h616-android12/tools/gen_app_keys.sh $PWD /надёжное/место
```

Сборка:

```sh
cd longan && ./build.sh autoconfig -o android -i h618 -b t95 -n default -k linux-5.4 -a arm64 && ./build.sh && cd ..
source build/envsetup.sh && lunch apollo_t95-user && make -j10 && pack4dist -v
# образ: longan/out/h618_android12_t95_uart0_secure_v0.img
```

> [!NOTE]
> Не пускайте вывод `./build.sh` через пайп (`| grep`, `| head`): сборка зависает.

### Ядро

В релизной сборке (с b18) ядро **5.4.302**. Ядро Allwinner из H618-Android12-Src (5.4.125) = Android
Common Kernel (ACK) android12-5.4 + BSP Allwinner, поэтому обновление делается через `git merge` с веткой
ACK, а не патчами (`patches/07-kernel-5.4.302/`):

- `merge-ack-5.4.302.sh` скачивает ACK (~3–4 ГБ, история с 05.2021), создаёт ветку `aw-base` (коммит
  ACK 73e6d86c3, ближайший к ядру AW, + дерево AW), делает merge android12-5.4.302_r00 (250657e3e),
  разрешает 11 конфликтов (`resolved/` — файлы после разрешения) и применяет:
  - 0001: `sun50i-cpufreq-nvmem.c` = версия AW целиком (после merge не собирается);
  - 0002: `drivers/mmc/core` = версия AW;
  - 0003: **исправление зависания после сна** (см. ниже).
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

Под T95 ядро адаптируется конфигурацией платы в longan (`longan/device/config/chips/h618/configs/t95`):

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

T95 бывают с другим PMIC (например AXP313A/AXP1530), памятью и Wi-Fi. Ревизия описывается своей папкой платы,
как у Orange Pi и Radxa: `longan/device/config/chips/h618/configs/<плата>/` с `sys_config.fex` (DRAM, напряжения PMIC, GPIO),
`linux-5.4/board.dts` (DT ядра) и `uboot-board.dts`. Патчи Android остаются общими. Папка Zero 3 `p2` уже
описывает AXP1530/AXP313A — хорошая отправная точка для таких боксов.

Чтобы добавить ревизию, присылайте pull request с новой папкой `longan/device/config/chips/h618/configs/t95-<имя>/` и, если можно, стоковым
`sys_config.fex`/DTB этого бокса, фото платы и логом UART первой загрузки. Сам я могу проверить только плату
с AXP806, поэтому новая папка принимается после того, как автор подтвердит, что сборка загружается.

## Безопасность и ключи

Ключи подписи я **не публикую и никому не передаю** — это гарантия, что никто другой не сможет выпустить
«обновление» для ваших приставок. Если собираете свой образ — генерируйте свои ключи.

## Лицензии

- Папка платы `longan/device/config/chips/h618/configs/t95/` сделана из конфигурации BSP Orange Pi /
  Allwinner (`configs/p2`) и остаётся под лицензией этих файлов.
- Патчи к AOSP, BSP Allwinner и device tree — под лицензией изменяемых файлов (в основном Apache-2.0;
  ядро и файлы в `patches/07-kernel-5.4.302/resolved/` — GPL-2.0).
- `patches/06-flauncher-v2025.07.001-t95.patch` — изменение FLauncher, GPL-3.0.
- Инструменты в `tools/` и документация — Apache-2.0 (см. [LICENSE](LICENSE)).
- Предустановленные приложения не изменены (кроме FLauncher), лицензии и подписи — авторов.

## Благодарности

Orange Pi (исходники H618 Android 12), Allwinner BSP, osrosal (FLauncher), авторы SmartTube, VLC,
F-Droid, Material Files, Cromite.
