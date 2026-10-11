**English** · [Русский](README.ru.md) · [Italiano](README.it.md)

# Clean Android 12 for the T95 (Allwinner H616)

Android 12 (TV) for the T95 H616 TV box (mine is an iconBIT TRS2048). I built it from the official
Orange Pi Zero 3 sources (`H618-Android12-Src`, Allwinner BSP, kernel 5.4.125) and ported it to the T95.
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
  This covers the framework only; the kernel and vendor parts are Allwinner's.
- All system apps and secure boot (toc0/toc1/vbmeta) are signed with **my own keys**, not with the public
  Allwinner SDK keys that anyone can use
- **FLauncher** launcher (osrosal fork 2025.07.001), with the card highlight animation off by default. With it
  on, the launcher redraws at 60 fps and keeps one core at ~95%.
- Apps: **F-Droid**, **SmartTube**, **VLC**, **Material Files**, **Downloader** (AFTVnews) and
  **Cromite 153** as WebView (replacing the old AOSP WebView 91)
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

iconBIT TRS2048 / T95, Allwinner H616, 4 GB RAM, PMIC **AXP806**, Wi-Fi/BT **UWE5622**,
Ethernet AC200 (100 Mbit).

**Works:** boot, HDMI 1080p, Ethernet, Wi-Fi 2.4/5 GHz, Bluetooth (A2DP speaker), hardware video
decoding (SmartTube VP9, VLC H.264 4K), Mali-G31 GPU, IR remote, sleep/wake and power off/on from the
remote, FD655 display, both USB ports.
**Not tested:** HDMI audio, CEC.

> [!WARNING]
> T95 boxes ship with different RAM, PMIC and Wi-Fi chips. On another board revision this firmware may
> not boot. See [Going back](#going-back-to-stock-or-another-firmware).

## Flashing

1. **Back up your current firmware** if you have it, or find the stock firmware for your revision.
2. You need a USB A-A (male-male) cable and PhoenixSuit (Windows) or OpenixSuit (Linux).
3. Download `update.opi-t95-a12-b16-user.img.xz` from [Releases](../../releases) and decompress it
   (7-Zip on Windows, `xz -d` on Linux), then select `update.opi-t95-a12-b16-user.img` and choose a full flash (Full Erase).
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
- This is a user build: no root and no UART shell.

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
| `patches/07-kernel-5.4.302-experimental/` | **experiment, not in the release**: see [Kernel](#kernel) |
| `tools/bl31_t95_patch.py` | creates `bin/bl31_t95.bin` from `bl31.bin`: skips the H618-only "hardware check" (0x1F4C). With `--fakeoff` it also adds the old power-off workaround of b13–b15 (PSCI SYSTEM_OFF, 0x1CF0..0x1D00), not needed since b16 |
| `tools/t95_board_dts.py` | generates the t95 `board.dts` from p2 (output already in `configs/t95`) |
| `tools/t95_sys_config.py` | generates the t95 `sys_config.fex` from p2 + the stock T95 `sys_config.fex` |
| `tools/gen_app_keys.sh` | generates your own app keys (platform/media/shared/networkstack/releasekey) |

Comments inside the patches and tools are in Russian (the project was first published on 4PDA).

### Steps

Clone this repository next to the extracted `H618-Android12-Src` folder:

```sh
git clone https://github.com/well83/t95-h616-android12.git
cd H618-Android12-Src
cp -a ../t95-h616-android12/longan .                                   # board folder configs/t95
cp -a device/softwinner/apollo/apollo-p2 device/softwinner/apollo/apollo-t95
cp    device/softwinner/apollo/apollo_p2.mk device/softwinner/apollo/apollo_t95.mk
for p in 03a 03b 04 05 08 09; do git apply -p1 ../t95-h616-android12/patches/$p-*.patch; done   # or patch -p1 < ...
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

### Kernel

The release build uses the Allwinner 5.4.125 kernel from H618-Android12-Src almost as is: the only source
change is one line in the AXP806 driver (patch 09, together with the U-Boot fix). The kernel is adapted to
the T95 through the longan board configuration (`longan/device/config/chips/h618/configs/t95`):

- `linux-5.4/board.dts` (generated by `tools/t95_board_dts.py`): AXP806 instead of AXP1530, eMMC DDR52,
  gmac1/AC200 (twi3, PA10/11), LEDs PH6/7, VBUS PH8, USB0 host, IR fe02/0x40, OPP, SD card detect PI16.
  The compiled dtb was checked against the box's stock `sunxi_t95.dtb`.
- `sys_config.fex` (`tools/t95_sys_config.py`): DRAM/twi/gpio_bias from stock, AXP806 power.
- `uboot-board.dts`: boot_clock 1008, AXP806, `sdc_io_1v8=0`. `pack` does **not** merge `sys_config` into
  the U-Boot DT, so U-Boot values must be written directly in `uboot-board.dts`.
- BL31: the SDK `bl31.bin` doesn't start on H616 because of an H618-only check, so `tools/bl31_t95_patch.py`
  patches it (only the "hardware check"; `--fakeoff` is the old power-off workaround, see below).

`patches/07-kernel-5.4.302-experimental/` is an **experiment** to update the kernel to 5.4.302. The
Allwinner kernel is Android Common Kernel (ACK) android12-5.4 + the Allwinner BSP, so the update is a
`git merge` with the ACK branch, not a set of patches:

- `merge-ack-5.4.302.sh` downloads ACK (~3–4 GB, history since 05/2021), creates an `aw-base` branch
  (ACK commit 73e6d86c3, the closest to the AW kernel, + the AW tree), merges android12-5.4.302_r00
  (250657e3e), resolves 11 conflicts and applies 0001/0002.
- `resolved/` holds the files after conflict resolution.
- The result boots and everything works (eth, Wi-Fi, BT, Mali, HDMI, IR, FD655, cpufreq), **but** the
  system hangs while reinitialising the eMMC after resuming from sleep, and the watchdog resets it.
  Reverting `drivers/mmc/core` to the AW version did not help. It needs a bisect; contributions welcome.

```sh
bash patches/07-kernel-5.4.302-experimental/merge-ack-5.4.302.sh longan/kernel/linux-5.4 ~/k302
rsync -a --delete --exclude=.git ~/k302/linux-5.4/ longan/kernel/linux-5.4/
```

The AW tree must be clean (freshly extracted, never built).

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

T95 boxes exist with other PMICs (for example AXP313A/AXP1530), RAM and Wi-Fi chips. A revision is described
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

- The board folder `longan/device/config/chips/h618/configs/t95/` is derived from the Orange Pi /
  Allwinner BSP configuration (`configs/p2`) and keeps the license of those files.
- Patches to AOSP, the Allwinner BSP and device trees follow the license of the files they modify
  (mostly Apache-2.0; the kernel and the files in `patches/07-kernel-5.4.302-experimental/resolved/` are
  GPL-2.0).
- `patches/06-flauncher-v2025.07.001-t95.patch` is a change to FLauncher, which is GPL-3.0.
- The tools in `tools/` and the documentation are under Apache-2.0 (see [LICENSE](LICENSE)).
- The apps preinstalled in the image are unmodified (except FLauncher) and keep their authors' licenses
  and signatures.

## Credits

Orange Pi (H618 Android 12 sources), Allwinner BSP, osrosal (FLauncher), and the authors of SmartTube,
VLC, F-Droid, Material Files and Cromite.
