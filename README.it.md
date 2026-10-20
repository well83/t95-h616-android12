[English](README.md) · [Русский](README.ru.md) · **Italiano**

# Android 12 pulito per il T95 (Allwinner H616)

Android 12 (TV) per il TV box T95 H616, compilato dai sorgenti ufficiali
Orange Pi Zero 3 (`H618-Android12-Src`, BSP Allwinner) e portato sul T95. Dalla b18 il kernel è aggiornato
da 5.4.125 a **5.4.302**.
Niente app inutili, niente malware, con le patch di sicurezza AOSP.

Questo repository contiene **le patch e gli strumenti** per ricompilare il firmware dai sorgenti.
L'immagine pronta da flashare è nelle [Releases](../../releases).

## Perché

Il firmware originale del T95 è infetto: il software preinstallato installa app da solo e si collega a
server remoti. Invece di ripulirlo, ho ricompilato Android 12 da zero partendo da sorgenti
pubblici.

## Cosa contiene

- Android 12 (TV), 64 bit, build **user / release-keys**
- SELinux **enforcing** (il firmware originale e l'SDK Allwinner usano permissive)
- Patch di sicurezza AOSP **android-security-12.0.0_r34 → r69** (gennaio 2025) su 27 progetti (Bluetooth,
  frameworks/av, frameworks/base, webp, freetype, libxml2, skia, …). Livello patch **2025-01-01**: vale
  per il framework. Dalla b18 il kernel è **5.4.302** (correzioni LTS fino a dicembre 2025, l'ultima 5.4);
  i binari chiusi di Allwinner (GPU, video, Wi-Fi) non si possono aggiornare.
- Tutte le app di sistema e il secure boot (toc0/toc1/vbmeta) sono firmati con **le mie chiavi**, non con
  le chiavi pubbliche dell'SDK Allwinner che chiunque può usare
- Launcher **Arc Launcher** 1.0.10 (dalla b21; fork GPL di LTvLauncher/FLauncher), ricompilato senza
  auto-aggiornamento e con sfondo scuro di default: 0% di CPU a riposo e il focus del telecomando non si perde se un
  mouse Bluetooth si collega durante l'avvio. Dalla b23 la home si apre con *All Apps* già visibile (niente barra
  Preferiti di default, che spingeva le app sotto il bordo dello schermo) e il riquadro del focus si vede sempre (con
  alcuni mouse collegati, per esempio un Logitech M590, spariva e il telecomando sembrava non funzionare). Fino alla b19 il launcher era **FLauncher** (fork osrosal 2025.07.001)
  con l'animazione di evidenziazione delle schede spenta (se accesa ridisegna a 60 fps e tiene un core al ~95%).
  Arc per ora è solo in inglese.
- App: **F-Droid**, **SmartTube**, **VLC**, **Material Files**, **Downloader** (AFTVnews) e
  **Cromite 153** come WebView (al posto del vecchio WebView AOSP 91)
- Dalla b19: il selettore di file/cartelle di sistema (**DocumentsUI**), che serve alle app di backup come Alpha
  Backup e per aggiungere una scheda SD in Material Files; le app leggono la temperatura della CPU; la musica
  di avvio è 24 dB più bassa
- Dalla b21: animazioni di finestre/transizioni a 0,5x di default (a 1x Mali/HWC mostra fotogrammi spezzati
  all'apertura/chiusura delle app), sfondo di sistema scuro neutro al posto del logo Orange Pi, **VLC da F-Droid**
  (ora si aggiorna da F-Droid), privacy Bluetooth LE solo sui controller che la supportano (sui chip BT 4.0 mouse e
  telecomandi BLE si ricollegano da soli dopo il riavvio)
- Dalla b23: **le app installate dall'utente possono partire all'avvio** (overlay della temperatura, widget meteo,
  opzioni "avvia all'accensione"). Il gestore delle app in background di Allwinner (Awbms, `awbms_config`) bloccava
  `BOOT_COMPLETED` e i servizi in background di tutte le app fuori dalla sua whitelist. La build ora è divisa per
  scheda: il nome dell'immagine, il prodotto Android e il nome del dispositivo dicono per quale scheda sono (vedi
  [Come flashare](#come-flashare))
- Telecomando IR (accende anche il box dalla sospensione), display frontale FD655 (orologio e icone
  LAN/Wi-Fi/USB), nome dispositivo `T95_h616`
- **Spegnimento dal telecomando**: la pressione lunga di power apre il menu *Spegni / Riavvia*, che si
  naviga con le frecce del telecomando. *Spegni* spegne HDMI e display e mette il box in attesa; si riaccende
  col tasto power del telecomando. Con il codice Allwinner originale il T95 si riavviava invece di
  spegnersi; le b13–b15 lo aggiravano nel BL31, la b16 corregge la causa vera (vedi [Spegnimento](#spegnimento)).
- L'RTC conserva l'ora e i flag di riavvio quando si riavvia (prima della b16 ogni reset li azzerava).

Niente servizi Google (GApps). Le app si installano da F-Droid, Aurora Store (disponibile su F-Droid)
o Downloader.

### Cosa è stato tolto

- Falle Allwinner: **adb root in rete senza autorizzazione** (porta 5555 aperta a tutta la rete locale),
  `runin.sh` (eseguiva come root comandi da un file su `/sdcard`), `preinstall` / `preloaddata`
  (installazione silenziosa di APK all'avvio), `appsdisable`, `fix_traceing` e `platform_app` con
  `mlstrustedsubject`
- 26 app: test di fabbrica e demo Allwinner (Test_AD, che cambia logo e animazione di avvio; DragonBox,
  DragonAgingTV, DragonAtt, AwlogSettings, TvdFileManager, VideoPlayer, Update) e app inutili su una TV
  (EasterEgg, Traceur, LiveTv, DeskClock, PhotoTable, WebScreensaver, Contacts, Calendar, Camera2, Music,
  SoundRecorder, ExactCalculator, QuickSearchBox, SimAppDialog, WAPPushManager, NfcNci, SecureElement)

## Hardware provato

T95, Allwinner H616, 4 GB RAM, PMIC **AXP806**, Wi-Fi/BT **UWE5622**,
Ethernet AC200 (100 Mbit).

**Funziona:** avvio, HDMI 1080p, Ethernet, Wi-Fi 2,4/5 GHz, Bluetooth (cassa A2DP), decodifica video
hardware (SmartTube VP9, VLC H.264 4K), GPU Mali-G31, telecomando IR, sospensione/risveglio e
spegnimento/accensione dal telecomando, display FD655, entrambe le USB.
**Non provato:** audio via HDMI, CEC.

Una seconda scheda, **H616-T95MAX-AXP313A-V2.0** (PMIC **AXP313A**, Wi-Fi/BT **BCM43342**, 2 GB), ha la sua
cartella `configs/t95-axp313`, il suo prodotto `apollo_t95axp313` e **build di prova** (pre-release `axp313-*`),
provate da un utente 4PDA sulla versione **eMMC**. Dalla axp313-test11 anche lì sospensione e risveglio funzionano:
l'interrupt di risveglio del Wi-Fi (host-wake) bloccava la sospensione leggera s2idle, ora non sveglia più il
sistema (kernel `0005`). La versione **NAND** di quella scheda per ora non si flasha (il driver NAND di U-Boot del
BSP non avvia il chip).

Le due schede si chiamano **T95-AXP806** (questo box) e **T95-AXP313** (`-eMMC` / `-NAND`). Non flashare mai
un'immagine fatta per una scheda sull'altra: il nome del file dice per quale scheda è (`update.T95-AXP806-…`,
`update.T95-AXP313-eMMC-…`; fino alla b22: `t95axp806` / `t95axp313`).

> [!WARNING]
> I T95 escono con RAM, PMIC e chip Wi-Fi diversi. Su un'altra revisione della scheda questo firmware
> potrebbe non avviarsi. Vedi [Tornare indietro](#tornare-al-firmware-originale-o-a-un-altro).

## Come flashare

1. **Salva il firmware attuale**, se ce l'hai, oppure trova quello originale della tua revisione.
2. Servono un cavo USB A-A (maschio-maschio) e PhoenixSuit (Windows) o OpenixSuit (Linux).
3. Scarica `update.T95-AXP806-a12-b23-user.img.xz` dalle [Releases](../../releases) (oppure
   `update.T95-AXP806-a12-b23-magisk-user.img.xz` con root) e decomprimilo (7-Zip su Windows, `xz -d` su Linux),
   poi seleziona il `.img` e scegli il flash completo (Full Erase).
4. A box spento tieni premuto il tasto reset (dentro il jack AV), collega l'USB al PC e rilascia il tasto
   dopo 3–5 s: il flash parte.
5. Il primo avvio richiede circa 1–2 minuti.

Senza cavo si può usare una microSD preparata con PhoenixCard (modalità *Product*).
**Il flash cancella tutti i dati del box.**

Dalla b23 il nome del prodotto e del dispositivo Android contiene la scheda (`apollo_t95axp806` / `apollo_t95axp313`,
prima `apollo_t95` per entrambe), quindi un pacchetto OTA di una scheda viene rifiutato sull'altra. Se arrivi dalla
b22 o precedenti, flasha una volta l'immagine completa.

### Tornare al firmware originale o a un altro

Questo firmware **non scrive chiavi negli eFuse** (niente rotpk: il bootloader stampa
`don't have rotpk, skip check`), quindi il box non resta legato alle mie chiavi. Puoi flashare in qualsiasi
momento il firmware originale o un altro firmware T95 in formato secure (toc0/toc1) nello stesso modo.
La modalità FEL (tasto reset + USB) sta nella ROM del SoC e non si può cancellare, quindi il box si può
sempre recuperare.

> [!IMPORTANT]
> **Secure bit.** L'immagine è in formato secure: durante il flash il bootloader stampa
> `burn sboot ok, set secure bit`. Sul mio box, come sulla maggior parte dei T95 H616 col firmware
> originale, il SoC era già in modalità secure di fabbrica, quindi non cambia nulla. Se però il tuo box è
> stato venduto con un firmware **non secure**, il flash attiva la modalità secure **per sempre**: da quel
> momento il box avvia solo firmware secure (toc0/toc1), firmati con qualsiasi chiave. Per verificarlo
> prima del flash: il firmware originale è secure se la sua immagine contiene `toc0.fex`/`toc1.fex` (e non
> solo boot0/u-boot), oppure guarda il log UART.

## Note d'uso

- **adb solo in rete**. Vai in *Impostazioni → Preferenze dispositivo → Info*, premi 7 volte *Build*, poi
  apri *Opzioni sviluppatore* e attiva *Debug USB*. `adbd` ascolta allora sulla porta 5555:
  `adb connect <ip-del-box>:5555`, poi conferma il computer sullo schermo col telecomando. adb è spento
  di default. Via cavo USB adb non funziona perché la porta USB0 del T95 è solo host (manca il pin ID);
  il cavo A-A serve solo per il flash.
- La pressione breve di power mette il box in sospensione, quella lunga apre il menu di spegnimento.
  *Spegni* è uno standby profondo (U-Boot + BL31), non un distacco completo dell'alimentazione: l'alimentatore
  resta sotto tensione e il box si riaccende dal telecomando. Per togliere del tutto la corrente, stacca
  l'alimentatore.
- Al primo avvio il Bluetooth può partire con ~5 s di ritardo; si riprende da solo.
- Downloader (AFTVnews) è un'app gratuita a codice chiuso con pubblicità (AdMob/Meta). Se non la vuoi,
  disinstalla gli aggiornamenti o disattivala.
- Arc Launcher è ricompilato e firmato con la mia chiave, quindi gli aggiornamenti del suo autore non si
  installano sopra. Si aggiorna insieme al firmware.
- Nella b21 VLC è passato dall'APK VideoLAN alla build F-Droid (firma diversa): se avevi aggiornato VLC sulla b20 o
  prima, l'aggiornamento in `/data` sparisce dopo il flash della b21.
- È una build user: niente root e niente shell sulla UART. Dalla b19 c'è anche una variante **Magisk**
  (`-magisk`): la stessa build con il `boot.img` patchato da Magisk; per gestire il root installa l'app Magisk
  dalla sua pagina GitHub.

## Compilare dai sorgenti

### Base

I sorgenti ufficiali Orange Pi Zero 3 **H618-Android12-Src** (Google Drive di Orange Pi, 13/07/2023,
archivio `H618-Android12-Src.tar.gz{aa..ar}`; l'md5 della cartella Orange Pi coincide).
Nei sorgenti la scheda Zero 3 si chiama **p2** (prodotto `apollo_p2`). Il repository aggiunge le schede
**t95-axp806** e **t95-axp313** (longan) e i prodotti **apollo_t95axp806** e **apollo_t95axp313** (Android), che
condividono `device/softwinner/apollo/t95-common`. Macchina di compilazione: Ubuntu 22.04.

**Le chiavi di firma non sono incluse.** Generane di tue (`tools/gen_app_keys.sh` per le chiavi delle app,
`dragonsecboot` per le `toc_keys`).

### File

| File | Contenuto |
|---|---|
| `longan/device/config/chips/h618/configs/t95-axp806/` | cartella pronta della scheda `t95-axp806` (da copiare nei sorgenti; fino alla b22 si chiamava `t95`): `configs/p2` (Zero 3) + modifiche: `board.dts` del kernel (AXP806, eMMC DDR52, gmac1 + AC200, LED, VBUS PH8, USB0 host, IR fe02, OPP…), `sys_config.fex` (DRAM dal T95 originale), `uboot-board.dts` |
| `patches/03a-device-apollo-t95-vs-p2.patch` | dispositivo `apollo-t95` = copia di `apollo-p2` + modifiche (diviso nelle due schede dalla patch 14) (BoardConfig, sepolicy, FD655, mappa tasti IR, HDMI 1080p, RRO NetworkStack, overlay WebView, `apps/Android.mk`) |
| `patches/03b-product-apollo_t95-vs-p2.patch` | `apollo_t95.mk` = copia di `apollo_p2.mk` + modifiche |
| `patches/04-aw-fixes-64bit-security.patch` | correzioni Allwinner: build a 64 bit (moduli che dipendono da blob a 32 bit → 32 bit, printf/tipi, dump ABI, HDR10+), sicurezza (adb in rete senza autorizzazione, `platform_app mlstrustedsubject`, `service_contexts`, `/dev/watchdog`), `AndroidProducts.mk`, `pack4dist`, livello patch 2025-01-01 |
| `patches/05-aosp-security-r34-r69.patch` | patch di sicurezza AOSP android-security-12.0.0_r34 → r69 (27 progetti), con i conflitti risolti e `make update-api`. Contiene anche una riga T95 in `system/bt/btif/src/btif_dm.cc` (nome BT da `bluetooth.device.default_name`) |
| `patches/06-flauncher-v2025.07.001-t95.patch` | [FLauncher](https://github.com/osrosal/flauncher) (tag v2025.07.001): animazione di evidenziazione spenta di default. Build: Flutter 3.24.5, JDK 17, `flutter build apk --release --split-per-abi --target-platform android-arm64` |
| `patches/08-poweroff-menu-t95.patch` | spegnimento e menu: pressione lunga di power = menu Spegni/Riavvia (overlay `apollo-t95` `config.xml`); pulsanti di SystemUI `GlobalActionsDialogLite` selezionabili con le frecce del telecomando (focus, bordo bianco); FD655 spento allo spegnimento (`fd655.rc` on shutdown); SELinux: audio.routing, dontaudit installd |
| `patches/09-rtc-axp806-offctl-t95.patch` | correzione dell'azzeramento dell'RTC (b16): U-Boot (`pmu_axp806.c`) e il kernel (`axp2101.c`) spengono il bit 4 del registro 0x32 (OFF_CTL) dell'AXP806, che lo sboot binario accende. Con quel bit acceso ogni reset del SoC azzerava tutto il dominio RTC. Vedi [Spegnimento](#spegnimento) |
| `patches/10-b19-t95-axp313.patch` | b19: DocumentsUI (lo toglieva l'override di `TvdFileManager`), SELinux: le app leggono la temperatura della CPU (`sysfs_thermal`, `sysfs_temp`). Per la scheda AXP313A: `PRODUCT_BOARD` da `T95_BOARD` (sostituito dai due prodotti della patch 14), sospensione leggera s2idle (`axp313-s2idle.rc`, `/sys/power/mem_sleep` → `sysfs_power`), BCM43342 in `libhwinfo.c`, `config.txt` AP6334 con ccode XZ/11. Solo build di prova (`T95_LOGGER=1`): raccoglitore di log `t95log` (dmesg/logcat in `/sdcard/T95_LOG`) |
| `patches/11-b21-t95.patch` | b20/b21: animazioni 0,5x di default (overlay SettingsProvider `defaults.xml`), privacy locale Bluetooth LE solo se il controller ha la LL privacy (`btif_dm.cc`), Arc Launcher al posto di FLauncher (`apps/Android.mk`, `apollo_t95.mk`), VLC da F-Droid. Lo sfondo lo crea `tools/t95_wallpaper.py` |
| `patches/12-arclauncher-1.0.10-t95.patch` | [Arc Launcher](https://github.com/meddouribadis/arclauncher) (tag 1.0.10): sfondo scuro di default; dalla b23 (1.0.10-t95.4) niente Preferiti di default (la home si apre su All Apps) ed evidenziazione del focus sempre attiva (`FocusHighlightStrategy.alwaysTraditional`). Build: Flutter 3.41.9, `flutter build apk --release --flavor play --split-per-abi --target-platform android-arm64` (il flavor `play` non ha l'auto-aggiornamento) |
| `patches/07-kernel-5.4.302/` | kernel 5.4.125 → 5.4.302 (dalla b18): script di merge ACK, conflitti risolti, 0001–0003 (0003 = correzione del blocco dopo la sospensione), solo scheda AXP313A: 0004 = BCM43342 nel bcmdhd, 0005 = l'host-wake del Wi-Fi non sveglia più il sistema (`oob_wake=0`, corregge s2idle). Vedi [Kernel](#kernel) |
| `patches/13-b23-t95.patch` | b23: gestore Allwinner delle app in background senza blocchi (`device/softwinner/common/config/awbms_config`: `blockBroadcast`, `skipService` a false), così le app dell'utente ricevono `BOOT_COMPLETED` e possono avviare servizi; commento di Arc in `apps/Android.mk` |
| `patches/14-split-boards-t95axp806-t95axp313.patch` | b23: un prodotto per scheda. `apollo_t95.mk` → `t95-common/t95_product.mk` (comune), nuovi `apollo_t95axp806.mk` / `apollo_t95axp313.mk`, cartelle dispositivo `apollo-t95axp806` / `apollo-t95axp313` (BoardConfig, `system/`, camera); apps, overlay, sepolicy, `t95/`, `t95log/` spostati in `t95-common`. Contiene rinomine: va applicata con `git apply` |
| `longan/device/config/chips/h618/configs/t95-axp313/` | cartella della scheda H616-T95MAX-AXP313A-V2.0: AXP313A (come lo Zero 3), DRAM dal firmware stock A29, clock 32 kHz per l'AP6334, pin NAND; generata dai due strumenti `t95_axp313_*` |
| `tools/bl31_t95_patch.py` | crea `bin/bl31_<scheda>.bin` (`bl31_t95-axp806.bin`, `bl31_t95-axp313.bin`; `pack` lo sceglie in base al nome della scheda) da `bl31.bin`: salta il "hardware check" che accetta solo H618 (0x1F4C). Con `--fakeoff` aggiunge anche il vecchio aggiramento dello spegnimento delle b13–b15 (PSCI SYSTEM_OFF, 0x1CF0..0x1D00), non più necessario dalla b16 |
| `tools/t95_board_dts.py` | genera il `board.dts` t95-axp806 da quello p2 (il risultato è già in `configs/t95-axp806`) |
| `tools/t95_sys_config.py` | genera il `sys_config.fex` t95-axp806 da quello p2 + il `sys_config.fex` del T95 originale |
| `tools/gen_app_keys.sh` | genera le tue chiavi delle app (platform/media/shared/networkstack/releasekey) |
| `tools/t95_bootsound.py` | regola il volume della musica di avvio in `bootanimation.zip` (b19: `-24` dB) |
| `tools/t95_wallpaper.py` | crea lo sfondo di sistema di default (gradiente scuro, b20+) nell'overlay `t95-common` (serve Pillow) |
| `tools/magisk-boot.sh` | variante root: patcha con Magisk il `boot.img` dei signed target files e rifirma vbmeta con la tua chiave AVB; poi `pack -v` |
| `tools/t95_axp313_board_dts.py`, `tools/t95_axp313_sys_config.py` | generano `board.dts` e `sys_config.fex` di `configs/t95-axp313` da p2 (+ il `sys_config.fex` stock di quella scheda) |

I commenti dentro patch e strumenti sono in russo (il progetto è stato pubblicato prima su 4PDA).

### Procedura

Clona il repository accanto alla cartella estratta `H618-Android12-Src`:

```sh
git clone https://github.com/well83/t95-h616-android12.git
cd H618-Android12-Src
cp -a ../t95-h616-android12/longan .                         # cartelle delle schede configs/t95-axp806, t95-axp313
cp -a device/softwinner/apollo/apollo-p2 device/softwinner/apollo/apollo-t95
cp    device/softwinner/apollo/apollo_p2.mk device/softwinner/apollo/apollo_t95.mk
bash ../t95-h616-android12/patches/07-kernel-5.4.302/merge-ack-5.4.302.sh longan/kernel/linux-5.4 ~/k302   # kernel 5.4.302
rsync -a --delete --exclude=.git ~/k302/linux-5.4/ longan/kernel/linux-5.4/
for p in 03a 03b 04 05 08 09 10 11 13 14; do git apply -p1 ../t95-h616-android12/patches/$p-*.patch; done   # 14: solo git apply (rinomine)
B=device/softwinner/apollo/common/media/bootanimation/bootanimation.zip
python3 ../t95-h616-android12/tools/t95_bootsound.py $B $B.new -24 && mv $B.new $B   # musica di avvio -24 dB
python3 ../t95-h616-android12/tools/t95_wallpaper.py device/softwinner/apollo/t95-common/overlay/frameworks/base/core/res/res
python3 ../t95-h616-android12/tools/bl31_t95_patch.py longan/device/config/chips/h618/bin/bl31.bin \
        longan/device/config/chips/h618/bin/bl31_t95-axp806.bin
```

Gli APK delle app vanno in `device/softwinner/apollo/t95-common/apps/<Nome>/`. Estrai le librerie native
di ogni APK in `apps/<Nome>/lib/arm64/`; vedi `apps/Android.mk`, che riporta anche lo SHA-256 di ogni APK:
ArcLauncher (compilato con la patch 12; fino alla b19 FLauncher con la patch 06), MaterialFiles 1.7.5 (F-Droid),
CromiteWebView 153.0.8010.37 (arm64 SystemWebView), SmartTube 32.56 stable, VLC 3.7.2 arm64 (build F-Droid), Downloader 2.0.4 (+ `split_config.*`),
F-Droid 2.0.1.

Chiavi: metti le tue `toc_keys` in `vendor/security/toc_keys` (secure boot, vbmeta) e genera le tue chiavi
delle app:

```sh
bash ../t95-h616-android12/tools/gen_app_keys.sh $PWD /un/posto/sicuro
```

Compilazione:

```sh
cd longan && ./build.sh autoconfig -o android -i h618 -b t95-axp806 -n default -k linux-5.4 -a arm64 && ./build.sh && cd ..
source build/envsetup.sh && lunch apollo_t95axp806-user && make -j10 && pack4dist -v
# immagine: longan/out/h618_android12_t95-axp806_uart0_secure_v0.img
```

> [!NOTE]
> Non mandare l'output di `./build.sh` in una pipe (`| grep`, `| head`): la compilazione si blocca.

Variante root (dopo la build qui sopra): `bash ../t95-h616-android12/tools/magisk-boot.sh Magisk-v30.7.apk && pack -v`.

Scheda AXP313A: applica al kernel anche `patches/07-kernel-5.4.302/0004-*.patch` e `0005-*.patch`, copia i firmware Wi-Fi/BT di
quella scheda dal suo `/vendor/etc/firmware` stock (`fw_bcm43342_ag*.bin`, `nvram_ap6334.txt`, `bcm43342a1.hcd`;
non inclusi, licenza Broadcom) in `hardware/aw/wireless/partner/ampak/firmware/ap6334/`, crea
`bin/bl31_t95-axp313.bin` con `tools/bl31_t95_patch.py` (come per t95-axp806), poi compila con `-b t95-axp313` e
`lunch apollo_t95axp313-user`. Immagine: `longan/out/h618_android12_t95-axp313_uart0_secure_v0.img`.

### Kernel

La build di rilascio (dalla b18) usa il kernel **5.4.302**. Il kernel Allwinner di H618-Android12-Src
(5.4.125) è Android Common Kernel (ACK) android12-5.4 + il BSP Allwinner, quindi l'aggiornamento si fa con
`git merge` del ramo ACK, non con delle patch (`patches/07-kernel-5.4.302/`):

- `merge-ack-5.4.302.sh` scarica ACK (~3–4 GB, storia da 05/2021), crea il ramo `aw-base` (commit ACK
  73e6d86c3, il più vicino al kernel AW, + albero AW), fa il merge di android12-5.4.302_r00 (250657e3e),
  risolve 11 conflitti (`resolved/` contiene i file risolti) e applica:
  - 0001: `sun50i-cpufreq-nvmem.c` = versione AW intera (il file unito non compila);
  - 0002: `drivers/mmc/core` = versione AW;
  - 0003: **correzione del blocco dopo la sospensione** (vedi sotto);
  - solo scheda AXP313A: 0004 (nome del firmware BCM43342) e 0005 (parametro `oob_wake` del `bcmdhd`, default 0:
    l'interrupt host-wake del Wi-Fi, a livello, scattava appena iniziava s2idle e teneva bloccata la CPU0 per minuti).
- L'albero AW deve essere pulito (appena estratto, mai compilato). La patch 09 va applicata **dopo** aver
  copiato l'albero in `longan/kernel/linux-5.4`. Quando si cambia versione del kernel, cancellare prima
  `longan/out/kernel/{build,staging}`, altrimenti clang va in crash sulla vecchia configurazione.

**Il blocco dopo la sospensione (0003).** Col 5.4.302 il box usciva dalla sospensione e pochi secondi dopo
si bloccava del tutto (tutte le CPU, interrupt spenti, in un punto casuale). Una bisezione sulla storia ACK
l'ha trovato: 5.4.288 buono, 5.4.290 cattivo. Il 5.4.290 ha portato l'upstream 2f8dea1692ee "hrtimers:
Handle CPU state correctly on hotplug", che sposta l'azzeramento dello stato hrtimer di ogni CPU in una
callback della fase di hotplug `CPUHP_AP_HRTIMERS_DYING`. ACK android12-5.4 però aveva annullato il commit
che aggiunge quella fase (5c0930ccaad5, per l'ABI), quindi la callback non viene mai chiamata: dopo la
sospensione le CPU secondarie ripartono con lo stato dei timer vecchio e il sistema si blocca. 0003 rimette
l'azzeramento in `hrtimers_prepare_cpu()`. È un errore di ACK: riguarda ogni dispositivo android12-5.4 con
kernel ≥ 5.4.290 che va in sospensione spegnendo le CPU.

Il kernel si adatta al T95 con la configurazione della scheda in longan
(`longan/device/config/chips/h618/configs/t95-axp806`):

- `linux-5.4/board.dts` (generato da `tools/t95_board_dts.py`): AXP806 al posto di AXP1530, eMMC DDR52,
  gmac1/AC200 (twi3, PA10/11), LED PH6/7, VBUS PH8, USB0 host, IR fe02/0x40, OPP, rilevamento SD su PI16.
  Il dtb compilato è stato confrontato con il `sunxi_t95.dtb` originale del box.
- `sys_config.fex` (`tools/t95_sys_config.py`): DRAM/twi/gpio_bias dall'originale, alimentazione AXP806.
- `uboot-board.dts`: boot_clock 1008, AXP806, `sdc_io_1v8=0`. `pack` **non** unisce `sys_config` nel DT di
  U-Boot, quindi i valori per U-Boot vanno scritti direttamente in `uboot-board.dts`.
- BL31: il `bl31.bin` dell'SDK non parte su H616 per un controllo che accetta solo H618, quindi
  `tools/bl31_t95_patch.py` lo modifica (solo il "hardware check"; `--fakeoff` è il vecchio aggiramento
  dello spegnimento, vedi sotto).

Per compilare invece col kernel originale 5.4.125 (come nella b16), salta le due righe del kernel nella
[Procedura](#procedura).

### Spegnimento

Lo schema *fake poweroff* di Allwinner funziona così:

1. Il kernel (`CONFIG_SUNXI_FAKE_POWEROFF`) scrive 0xe in RTC GPR[2].
2. BL31 SYSTEM_OFF lo cambia in 2 e resetta il SoC.
3. U-Boot (`CONFIG_ATF_BOX_STANDBY`) chiama SMC 0x8000ff14.
4. BL31 legge GPR[2]==2 e `/box_start_os0` dal DT, poi entra in standby con risveglio da IR.

Fino alla b15 sul T95 questo **non funzionava**: ogni reset azzerava tutto il dominio RTC (tutti i GPR,
l'ora, ALARM0_DAY), il flag si perdeva e il box si riavviava. Con il firmware originale lo stesso box
conserva i GPR al reset, quindi non era colpa dell'hardware.

**Causa (trovata l'11.10.2026):** il bit 4 del registro **0x32 (OFF_CTL)** dell'AXP806. Lo accende a ogni
avvio lo sboot compilato dall'SDK (il suo codice PMIC sta nella libreria binaria
`spl-pub/board/h616/libsun50iw9p1_sboot.a`); il firmware originale lo lascia a 0 (OFF_CTL = 0x26). Con il
bit 4 acceso un reset del SoC azzera il dominio RTC. Il PMIC conserva il valore finché non si stacca
l'alimentatore, per questo dopo il nostro firmware i GPR si perdevano anche con la catena di avvio originale.
Verificato per bisezione sul box, da U-Boot (`sunxi_axp pmu write 0x32 …`, `mw 0x0700010c …`, `reset`):
con 0x26 e 0x24 i GPR restano, con 0x36 e 0x34 si azzerano. Kernel, BL31, U-Boot e modo di reset sono stati
esclusi sostituendo uno alla volta sboot, BL31 e U-Boot con quelli originali.

**Correzione (b16, `patches/09`):** U-Boot spegne il bit 4 appena riconosce l'AXP806 (prima di qualsiasi
reset) e il driver del kernel lo spegne di nuovo. Lo schema standard Allwinner qui sopra ora funziona senza
modifiche, e ora e flag di riavvio sopravvivono al riavvio.

**Vecchio aggiramento (b13–b15):** `tools/bl31_t95_patch.py --fakeoff` modifica PSCI SYSTEM_OFF: con
GPR[2]==0xe BL31 chiama subito il box standby (funzione 0x1B2C con il DT salvato), senza reset. Funziona
ancora, ma è una patch a un binario chiuso e non serve più.

Non c'è un SCP separato, nemmeno nel firmware originale: lo standby gira tutto dentro BL31 (codice in SRAM A2
a 0x20000).

## Altre revisioni della scheda

Esistono T95 con altri PMIC (per esempio AXP313A/AXP1530), altra RAM e altro Wi-Fi. La scheda AXP313A ora ha la
sua cartella, `configs/t95-axp313` (vedi [Hardware provato](#hardware-provato)). Una revisione si descrive
con la sua cartella della scheda, come fanno Orange Pi e Radxa: `longan/device/config/chips/h618/configs/<scheda>/` con `sys_config.fex`
(DRAM, tensioni del PMIC, GPIO), `linux-5.4/board.dts` (DT del kernel) e `uboot-board.dts`, più un piccolo
prodotto Android (`apollo_t95<nome>.mk` e una cartella dispositivo come `apollo-t95axp806`; tutto il resto è in comune
in `t95-common`). La cartella `p2` dello Zero 3 descrive già un AXP1530/AXP313A, quindi è un buon
punto di partenza per quei box.

Per aggiungere una revisione, apri una pull request con una nuova cartella `longan/device/config/chips/h618/configs/t95-<nome>/` e, se puoi,
il `sys_config.fex`/DTB originale di quel box, foto della scheda e un log UART del primo avvio. Io posso
provare solo la scheda con AXP806, quindi una nuova cartella viene accettata dopo che il suo autore ha
confermato che la build si avvia.

## Sicurezza e chiavi

**Non pubblico e non condivido le mie chiavi di firma.** In questo modo nessun altro può distribuire un
"aggiornamento" per i box che usano questo firmware. Se compili una tua immagine, genera chiavi tue.

## Licenze

- Le cartelle delle schede `longan/device/config/chips/h618/configs/t95-axp806/` e `t95-axp313/` derivano dalla configurazione del
  BSP Orange Pi / Allwinner (`configs/p2`) e mantengono la licenza di quei file.
- Le patch ad AOSP, al BSP Allwinner e ai device tree seguono la licenza dei file che modificano
  (soprattutto Apache-2.0; il kernel e i file in `patches/07-kernel-5.4.302/resolved/` sono
  GPL-2.0).
- `patches/06-flauncher-v2025.07.001-t95.patch` è una modifica a FLauncher e `patches/12-arclauncher-1.0.10-t95.patch`
  una modifica ad Arc Launcher, entrambi GPL-3.0.
- Gli strumenti in `tools/` e la documentazione sono sotto Apache-2.0 (vedi [LICENSE](LICENSE)).
- Le app preinstallate nell'immagine non sono modificate (tranne FLauncher / Arc Launcher) e mantengono licenze e firme
  dei loro autori.

## Ringraziamenti

Orange Pi (sorgenti H618 Android 12), BSP Allwinner, osrosal (FLauncher), meddouribadis (Arc Launcher) e gli autori di SmartTube, VLC,
F-Droid, Material Files e Cromite.
