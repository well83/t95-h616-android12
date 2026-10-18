**English** · [Русский](README.ru.md) · [Italiano](README.it.md)

# Clean Android 12 for the T95 (Allwinner H616)

Android 12 (TV) for the T95 H616 TV box. I built it from the official
Orange Pi Zero 3 sources (`H618-Android12-Src`, Allwinner BSP) and ported it to the T95. Since b18 the kernel
is updated from 5.4.125 to **5.4.302**.
It has no bloatware and no malware, and it includes AOSP security patches.

This repository contains **the patches and tools** needed to rebuild the firmware from the sources.
The ready-to-flash image is in [Releases](../../releases).

## Why

The stock T95 firmware is infected: preinstalled software installs apps by itself and talks to remote
servers. Instead of cleaning it, I rebuilt Android 12 from scratch, starting from published sources.

## What's inside

- Android 12 (TV), 64-bit, **user / release-keys** build
- SELinux **enforcing** (stock firmware and the Allwinner SDK use permissive)
- AOSP security patches **android-security-12.0.0_r34 → r69** (January 2025) on 27 projects (Bluetooth,
  frameworks/av, frameworks/base, webp, freetype, libxml2, skia, …). Security patch level **2025-01-01**.
  This covers the framework. Since b18 the kernel is **5.4.302** (LTS fixes up to December 2025, the last 5.4
  release); the closed-source Allwinner vendor blobs (GPU, video, Wi-Fi) cannot be updated.
- All system apps and secure boot (toc0/toc1/vbmeta) are signed with **my own keys**, not with the public
  Allwinner SDK keys that anyone can use
- **FLauncher** launcher (osrosal fork 2025.07.001), with the card highlight animation off by default. With it
  on, the launcher redraws at 60 fps and keeps one core at ~95%.
- Apps: **F-Droid**, **SmartTube**, **VLC**, **Material Files**, **Downloader** (AFTVnews) and
  **Cromite 153** as WebView (replacing the old AOSP WebView 91)
- Since b19: the system file/folder picker (**DocumentsUI**), needed by backup apps such as Alpha Backup and to
  add an SD card in Material Files; apps can read the CPU temperature; the boot sound is 24 dB quieter
- IR remote (it also wakes the box from sleep), FD655 front display (clock and LAN/Wi-Fi/USB icons),
  device name `T95_h616`
- **Power off from the remote**: a long press on power opens a *Power off / Restart* menu, which you can
  navigate with the remote's arrow keys. *Power off* turns off HDMI and the front display and waits; press
  power on the remote to turn the box back on. With the plain Allwinner code the T95 rebooted instead of
  powering off; b13–b15 worked around it in BL31, b16 fixes the real cause (see [Power off](#power-off)).
- The RTC keeps the time and the reboot flags across a reboot (before b16 every reset cleared it).

No Google services (GApps). To install apps, use F-Droid, Aurora Store (available on F-Droid) or Downloader.

### Removed

- Allwinner security holes: **unauthenticated root ADB over the network** (port 5555 open to the whole LAN),
  `runin.sh` (ran commands from a file on `/sdcard` as root), `preinstall` / `preloaddata` (silent APK
  install at boot), `appsdisable`, `fix_traceing`, and `platform_app` with `mlstrustedsubject`
- 26 apps: Allwinner factory tests and demos (Test_AD, which changes the boot logo and animation;
  DragonBox, DragonAgingTV, DragonAtt, AwlogSettings, TvdFileManager, VideoPlayer, Update) and apps that
  are useless on a TV (EasterEgg, Traceur, LiveTv, DeskClock, PhotoTable, WebScreensaver, Contacts,
  Calendar, Camera2, Music, SoundRecorder, ExactCalculator, QuickSearchBox, SimAppDialog,
  WAPPushManager, NfcNci, SecureElement)

## Tested hardware

T95, Allwinner H616, 4 GB RAM, PMIC **AXP806**, Wi-Fi/BT **UWE5622**,
Ethernet AC200 (100 Mbit).

**Works:** boot, HDMI 1080p, Ethernet, Wi-Fi 2.4/5 GHz, Bluetooth (A2DP speaker), hardware video
decoding (SmartTube VP9, VLC H.264 4K), Mali-G31 GPU, IR remote, sleep/wake and power off/on from the
remote, FD655 display, both USB ports.
**Not tested:** HDMI audio, CEC.

A second board, **H616-T95MAX-AXP313A-V2.0** (PMIC **AXP313A**, Wi-Fi/BT **BCM43342**, 2 GB), has its own board
folder `configs/t95-axp313` and **test builds** (pre-releases `axp313-*`), tested by a 4PDA user on the **eMMC**
version. The **NAND** version of that board does not flash yet (the U-Boot NAND driver of the BSP does not start
the chip). Never flash an image made for one PMIC on the other board: the file names say which board they are
for (`t95axp806` / `t95axp313`).

> [!WARNING]
> T95 boxes ship with different RAM, PMIC and Wi-Fi chips. On another board revision this firmware may
> not boot. See [Going back](#going-back-to-stock-or-another-firmware).

## Flashing

1. **Back up your current firmware** if you have it, or find the stock firmware for your revision.
2. You need a USB A-A (male-male) cable and PhoenixSuit (Windows) or OpenixSuit (Linux).
3. Download `update.opi-t95-a12-b18-user.img.xz` from [Releases](../../releases) and decompress it
   (7-Zip on Windows, `xz -d` on Linux), then select `update.opi-t95-a12-b18-user.img` and choose a full flash (Full Erase).
   b19 (pre-release while it is being tested): `update.opi-t95axp806-a12-b19-user.img.xz`, or
   `update.opi-t95axp806-a12-b19-magisk-user.img.xz` with root (Magisk).
4. With the box off, hold the reset button (inside the AV jack), connect USB to the PC, and release the
   button after 3–5 s. Flashing starts.
5. The first boot takes about 1–2 minutes.

Without a cable, you can use a microSD card prepared with PhoenixCard (*Product* mode).
**Flashing erases all data on the box.**

### Going back to stock or another firmware

This firmware **does not burn keys into the eFuses** (no rotpk: the bootloader prints
`don't have rotpk, skip check`), so the box is not tied to my keys. You can flash stock or any other T95
firmware in secure format (toc0/toc1) the same way. FEL mode (reset button + USB) lives in the SoC ROM and
cannot be erased, so the box can always be recovered.

> [!IMPORTANT]
> **Secure bit.** The image is in secure format: while flashing, the bootloader prints
> `burn sboot ok, set secure bit`. On my box, as on most T95 H616 boxes with stock firmware, the SoC was
> already in secure mode from the factory, so nothing changes. If your box shipped with **non-secure**
> firmware, flashing turns secure mode on **permanently**. After that, the box only boots secure firmware
> (toc0/toc1), signed with any key. To check before flashing: the stock firmware is secure if its image
> contains `toc0.fex`/`toc1.fex` (not just boot0/u-boot), or check the UART log.

## Usage notes

- **ADB over the network only**. Go to *Settings → Device Preferences → About*, tap *Build* 7 times, then
  open *Developer options* and turn on *USB debugging*. `adbd` then listens on port 5555:
  `adb connect <box-ip>:5555`, then confirm the computer on screen with the remote. ADB is off by default.
  ADB does not work over USB because the T95 USB0 port is host-only (no ID pin); the A-A cable is only
  for flashing.
- A short press on power puts the box to sleep; a long press opens the power menu. *Power off* is a deep
  standby (U-Boot + BL31), not a full power cut: the power supply stays live and the remote turns the box back
  on. To cut power completely, unplug the power supply.
- On first boot, Bluetooth may start ~5 s late; it recovers by itself.
- Downloader (AFTVnews) is a free, closed-source app with ads (AdMob/Meta). Uninstall its updates or
  disable it if you don't want it.
- FLauncher is rebuilt and signed with my key, so updates from its author won't install over it. It is
  updated together with the firmware.
- This is a user build: no root and no UART shell. Since b19 there is also a **Magisk** variant (`-magisk`):
  the same build with a Magisk-patched `boot.img`; install the Magisk app from its GitHub page to manage root.

## Building from source

### Base

The official Orange Pi Zero 3 sources, **H618-Android12-Src** (Orange Pi Google Drive, 2023-07-13, archive
`H618-Android12-Src.tar.gz{aa..ar}`; the md5 from the Orange Pi folder matches).
In the sources the Zero 3 board is called **p2** (product `apollo_p2`). The patches add a new board **t95**
and a new product **apollo_t95**. Build host: Ubuntu 22.04.

**Signing keys are not included.** Generate your own (`tools/gen_app_keys.sh` for the app keys,
`dragonsecboot` for `toc_keys`).

### Files

| File | Contents |
|---|---|
| `longan/device/config/chips/h618/configs/t95/` | ready board folder `t95` (copy it into the sources): `configs/p2` (Zero 3) + changes: kernel `board.dts` (AXP806, eMMC DDR52, gmac1 + AC200, LEDs, VBUS PH8, USB0 host, IR fe02, OPP…), `sys_config.fex` (DRAM from stock T95), `uboot-board.dts` |
| `patches/03a-device-apollo-t95-vs-p2.patch` | device `apollo-t95` = copy of `apollo-p2` + changes (BoardConfig, sepolicy, FD655, IR keymap, HDMI 1080p, NetworkStack RRO, WebView overlay, `apps/Android.mk`) |
| `patches/03b-product-apollo_t95-vs-p2.patch` | `apollo_t95.mk` = copy of `apollo_p2.mk` + changes |
| `patches/04-aw-fixes-64bit-security.patch` | Allwinner fixes: 64-bit build (modules depending on 32-bit blobs → 32-bit, printf/types, ABI dumps, HDR10+), security (unauthenticated network ADB, `platform_app mlstrustedsubject`, `service_contexts`, `/dev/watchdog`), `AndroidProducts.mk`, `pack4dist`, patch level 2025-01-01 |
| `patches/05-aosp-security-r34-r69.patch` | AOSP security patches android-security-12.0.0_r34 → r69 (27 projects), including resolved conflicts and `make update-api`. Also contains one T95 line in `system/bt/btif/src/btif_dm.cc` (BT name from `bluetooth.device.default_name`) |
| `patches/06-flauncher-v2025.07.001-t95.patch` | [FLauncher](https://github.com/osrosal/flauncher) (tag v2025.07.001): highlight animation off by default. Build: Flutter 3.24.5, JDK 17, `flutter build apk --release --split-per-abi --target-platform android-arm64` |
| `patches/08-poweroff-menu-t95.patch` | power off and menu: long press on power opens Power off / Restart (`apollo-t95` overlay `config.xml`); SystemUI `GlobalActionsDialogLite` buttons selectable with the remote arrows (focus, white frame); FD655 turns off at shutdown (`fd655.rc` on shutdown); SELinux: audio.routing, dontaudit installd |
| `patches/09-rtc-axp806-offctl-t95.patch` | fix for the RTC reset (b16): U-Boot (`pmu_axp806.c`) and the kernel (`axp2101.c`) clear bit 4 of AXP806 register 0x32 (OFF_CTL), which the binary sboot sets. With it set, every SoC reset cleared the whole RTC domain. See [Power off](#power-off) |
| `patches/10-b19-t95-axp313.patch` | b19: DocumentsUI (the `TvdFileManager` override removed it), SELinux: apps read the CPU temperature (`sysfs_thermal`, `sysfs_temp`). For the AXP313A board: `PRODUCT_BOARD` from `T95_BOARD`, light sleep s2idle (`axp313-s2idle.rc`, `/sys/power/mem_sleep` → `sysfs_power`), BCM43342 in `libhwinfo.c`, AP6334 `config.txt` with ccode XZ/11. Test builds only (`T95_LOGGER=1`): log collector `t95log` (dmesg/logcat to `/sdcard/T95_LOG`) |
| `patches/07-kernel-5.4.302/` | kernel 5.4.125 → 5.4.302 (since b18): ACK merge script, resolved conflicts, 0001–0003 (0003 = fix for the hang after sleep), 0004 = BCM43342 in bcmdhd (AXP313A board only). See [Kernel](#kernel) |
| `longan/device/config/chips/h618/configs/t95-axp313/` | board folder for H616-T95MAX-AXP313A-V2.0: AXP313A (as on the Zero 3), DRAM from the stock A29 firmware, AP6334 32 kHz clock, NAND pins; generated by the two `t95_axp313_*` tools |
| `tools/bl31_t95_patch.py` | creates `bin/bl31_t95.bin` from `bl31.bin`: skips the H618-only "hardware check" (0x1F4C). With `--fakeoff` it also adds the old power-off workaround of b13–b15 (PSCI SYSTEM_OFF, 0x1CF0..0x1D00), not needed since b16 |
| `tools/t95_board_dts.py` | generates the t95 `board.dts` from p2 (output already in `configs/t95`) |
| `tools/t95_sys_config.py` | generates the t95 `sys_config.fex` from p2 + the stock T95 `sys_config.fex` |
| `tools/gen_app_keys.sh` | generates your own app keys (platform/media/shared/networkstack/releasekey) |
| `tools/t95_bootsound.py` | sets the boot sound volume in `bootanimation.zip` (b19: `-24` dB) |
| `tools/magisk-boot.sh` | root variant: patches `boot.img` of the signed target files with Magisk, re-signs vbmeta with your AVB key; then run `pack -v` |
| `tools/t95_axp313_board_dts.py`, `tools/t95_axp313_sys_config.py` | generate `board.dts` and `sys_config.fex` of `configs/t95-axp313` from p2 (+ the stock `sys_config.fex` of that board) |

Comments inside the patches and tools are in Russian (the project was first published on 4PDA).

### Steps

Clone this repository next to the extracted `H618-Android12-Src` folder:

```sh
git clone https://github.com/well83/t95-h616-android12.git
cd H618-Android12-Src
cp -a ../t95-h616-android12/longan .                                   # board folder configs/t95
cp -a device/softwinner/apollo/apollo-p2 device/softwinner/apollo/apollo-t95
cp    device/softwinner/apollo/apollo_p2.mk device/softwinner/apollo/apollo_t95.mk
bash ../t95-h616-android12/patches/07-kernel-5.4.302/merge-ack-5.4.302.sh longan/kernel/linux-5.4 ~/k302   # kernel 5.4.302
rsync -a --delete --exclude=.git ~/k302/linux-5.4/ longan/kernel/linux-5.4/
for p in 03a 03b 04 05 08 09 10; do git apply -p1 ../t95-h616-android12/patches/$p-*.patch; done   # or patch -p1 < ...
B=device/softwinner/apollo/common/media/bootanimation/bootanimation.zip
python3 ../t95-h616-android12/tools/t95_bootsound.py $B $B.new -24 && mv $B.new $B   # boot sound -24 dB
python3 ../t95-h616-android12/tools/bl31_t95_patch.py longan/device/config/chips/h618/bin/bl31.bin \
        longan/device/config/chips/h618/bin/bl31_t95.bin
```

App APKs go in `device/softwinner/apollo/apollo-t95/apps/<Name>/`. Extract the native libraries from
each APK into `apps/<Name>/lib/arm64/`; see `apps/Android.mk`, which also lists the SHA-256 of each APK:
FLauncher (built with patch 06), MaterialFiles 1.7.5 (F-Droid), CromiteWebView 153.0.8010.37 (arm64
SystemWebView), SmartTube 32.56 stable, VLC 3.7.1 arm64, Downloader 2.0.4 (+ `split_config.*`),
F-Droid 2.0.1.

Keys: put your own `toc_keys` in `vendor/security/toc_keys` (secure boot, vbmeta) and generate your own
app keys:

```sh
bash ../t95-h616-android12/tools/gen_app_keys.sh $PWD /a/safe/place
```

Build:

```sh
cd longan && ./build.sh autoconfig -o android -i h618 -b t95 -n default -k linux-5.4 -a arm64 && ./build.sh && cd ..
source build/envsetup.sh && lunch apollo_t95-user && make -j10 && pack4dist -v
# image: longan/out/h618_android12_t95_uart0_secure_v0.img
```

> [!NOTE]
> Don't pipe the output of `./build.sh` (`| grep`, `| head`): the build hangs.

Root variant (after the build above): `bash ../t95-h616-android12/tools/magisk-boot.sh Magisk-v30.7.apk && pack -v`.

AXP313A board: apply also `patches/07-kernel-5.4.302/0004-*.patch` to the kernel, copy the Wi-Fi/BT firmware of
that board from its stock `/vendor/etc/firmware` (`fw_bcm43342_ag*.bin`, `nvram_ap6334.txt`, `bcm43342a1.hcd`;
not included, Broadcom license) into `hardware/aw/wireless/partner/ampak/firmware/ap6334/`, create
`bin/bl31_t95-axp313.bin` with `tools/bl31_t95_patch.py` (as for t95), then build with `-b t95-axp313` and
`export T95_BOARD=t95-axp313` before `lunch`. Image: `longan/out/h618_android12_t95-axp313_uart0_secure_v0.img`.

### Kernel

The release build (since b18) uses kernel **5.4.302**. The Allwinner kernel from H618-Android12-Src (5.4.125)
is Android Common Kernel (ACK) android12-5.4 + the Allwinner BSP, so the update is a `git merge` with the
ACK branch, not a set of patches (`patches/07-kernel-5.4.302/`):

- `merge-ack-5.4.302.sh` downloads ACK (~3–4 GB, history since 05/2021), creates an `aw-base` branch
  (ACK commit 73e6d86c3, the closest to the AW kernel, + the AW tree), merges android12-5.4.302_r00
  (250657e3e), resolves 11 conflicts (`resolved/` holds the files after resolution) and applies:
  - 0001: `sun50i-cpufreq-nvmem.c` = the whole AW version (the merged file does not build);
  - 0002: `drivers/mmc/core` = the AW version;
  - 0003: **fix for the hang after sleep** (see below).
- The AW tree must be clean (freshly extracted, never built). Apply patch 09 **after** copying the merged
  tree into `longan/kernel/linux-5.4`. When switching between kernel versions, delete
  `longan/out/kernel/{build,staging}` first, otherwise clang crashes on the old config.

**The hang after sleep (0003).** With 5.4.302 the box resumed from sleep and hard-locked a few seconds later
(all CPUs, interrupts off, at a random point). A bisect over the ACK history found it: 5.4.288 good,
5.4.290 bad. 5.4.290 brought upstream 2f8dea1692ee "hrtimers: Handle CPU state correctly on hotplug",
which moves the reset of the per-CPU hrtimer state into a callback on the `CPUHP_AP_HRTIMERS_DYING`
hotplug step. ACK android12-5.4 had reverted the commit that adds that step (5c0930ccaad5, for ABI
reasons), so the callback never runs: after suspend the secondary CPUs come back with stale timer state
and the system locks up. 0003 restores the reset in `hrtimers_prepare_cpu()`. This is an ACK bug and
affects any android12-5.4 device with kernel ≥ 5.4.290 that suspends with CPU hotplug.

The kernel is adapted to the T95 through the longan board configuration
(`longan/device/config/chips/h618/configs/t95`):

- `linux-5.4/board.dts` (generated by `tools/t95_board_dts.py`): AXP806 instead of AXP1530, eMMC DDR52,
  gmac1/AC200 (twi3, PA10/11), LEDs PH6/7, VBUS PH8, USB0 host, IR fe02/0x40, OPP, SD card detect PI16.
  The compiled dtb was checked against the box's stock `sunxi_t95.dtb`.
- `sys_config.fex` (`tools/t95_sys_config.py`): DRAM/twi/gpio_bias from stock, AXP806 power.
- `uboot-board.dts`: boot_clock 1008, AXP806, `sdc_io_1v8=0`. `pack` does **not** merge `sys_config` into
  the U-Boot DT, so U-Boot values must be written directly in `uboot-board.dts`.
- BL31: the SDK `bl31.bin` doesn't start on H616 because of an H618-only check, so `tools/bl31_t95_patch.py`
  patches it (only the "hardware check"; `--fakeoff` is the old power-off workaround, see below).

To build the original 5.4.125 kernel instead (as in b16), skip the two kernel lines in [Steps](#steps).

### Power off

Allwinner's *fake poweroff* scheme works like this:

1. The kernel (`CONFIG_SUNXI_FAKE_POWEROFF`) writes 0xe to RTC GPR[2].
2. BL31 SYSTEM_OFF changes it to 2 and resets the SoC.
3. U-Boot (`CONFIG_ATF_BOX_STANDBY`) calls SMC 0x8000ff14.
4. BL31 reads GPR[2]==2 and `/box_start_os0` from the DT, then enters standby with IR wake-up.

Up to b15 this did not work on the T95: every reset cleared the whole RTC domain (all GPRs, the time,
ALARM0_DAY), so the flag was lost and the box simply rebooted. With the stock firmware the same box keeps
the GPRs across a reset, so it was not the hardware.

**Cause (found on 11.10.2026):** bit 4 of AXP806 register **0x32 (OFF_CTL)**. The sboot built from the
SDK (its PMIC code is in the binary `spl-pub/board/h616/libsun50iw9p1_sboot.a`) sets it at every boot; the
stock firmware leaves it at 0 (OFF_CTL = 0x26). With bit 4 set, a SoC reset clears the RTC domain. The PMIC
keeps the value until the power supply is unplugged, so even the stock boot chain lost the GPRs after our
firmware had run. Tested by bisection on the box, from U-Boot (`sunxi_axp pmu write 0x32 …`,
`mw 0x0700010c …`, `reset`): 0x26 and 0x24 keep the GPRs, 0x36 and 0x34 clear them. The kernel, BL31,
U-Boot and the reset method were ruled out by swapping in the stock sboot/BL31/U-Boot one at a time.

**Fix (b16, `patches/09`):** U-Boot clears bit 4 right after detecting the AXP806 (before any reset can
happen) and the kernel driver clears it again. The standard Allwinner scheme above now works unchanged, and
the time and reboot flags survive a reboot.

**Old workaround (b13–b15):** `tools/bl31_t95_patch.py --fakeoff` patches PSCI SYSTEM_OFF so that with
GPR[2]==0xe BL31 calls box standby (function 0x1B2C with the saved DT) right away, without a reset. It
still works, but it is a patch to a closed binary and is no longer needed.

There is no separate SCP, not even in stock firmware: standby runs entirely inside BL31 (code in SRAM A2 at
0x20000).

## Other board revisions

T95 boxes exist with other PMICs (for example AXP313A/AXP1530), RAM and Wi-Fi chips. The AXP313A board now has
its own folder, `configs/t95-axp313` (see [Tested hardware](#tested-hardware)). A revision is described
by its own board folder, like Orange Pi and Radxa do: `longan/device/config/chips/h618/configs/<board>/` with `sys_config.fex`
(DRAM, PMIC voltages, GPIOs), `linux-5.4/board.dts` (kernel DT) and `uboot-board.dts`. The Android patches
stay the same. The Zero 3 folder `p2` already describes an AXP1530/AXP313A, so it is a good starting point
for those boxes.

To add a revision, open a pull request with a new folder `longan/device/config/chips/h618/configs/t95-<name>/` and, if you can, the stock
`sys_config.fex`/DTB of that box, photos of the board and a UART log of the first boot. I can only test the
AXP806 board myself, so a new folder is merged after its author confirms that the build boots.

## Security and keys

I **don't publish or share my signing keys**. This ensures no one else can ship an "update" for boxes
running this firmware. If you build your own image, generate your own keys.

## Licenses

- The board folders `longan/device/config/chips/h618/configs/t95/` and `t95-axp313/` are derived from the Orange Pi /
  Allwinner BSP configuration (`configs/p2`) and keep the license of those files.
- Patches to AOSP, the Allwinner BSP and device trees follow the license of the files they modify
  (mostly Apache-2.0; the kernel and the files in `patches/07-kernel-5.4.302/resolved/` are
  GPL-2.0).
- `patches/06-flauncher-v2025.07.001-t95.patch` is a change to FLauncher, which is GPL-3.0.
- The tools in `tools/` and the documentation are under Apache-2.0 (see [LICENSE](LICENSE)).
- The apps preinstalled in the image are unmodified (except FLauncher) and keep their authors' licenses
  and signatures.

## Credits

Orange Pi (H618 Android 12 sources), Allwinner BSP, osrosal (FLauncher), and the authors of SmartTube,
VLC, F-Droid, Material Files and Cromite.
