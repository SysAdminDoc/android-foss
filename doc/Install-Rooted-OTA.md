# OTA Update on a Rooted Device

Installing an ***OTA*** update often fails if the device has been **rooted**. You can still complete the update without losing data. This guide shows how to do it with ***TWRP*** and ***Magisk***.

**Warning:** Back up anything important before you start. These steps modify system partitions, so proceed at your own risk.

## Table of Contents

* [Prerequisite](#prerequisite)
* [Short Version](#short-version)
* [Long Version](#long-version)
    * [Step 1: Preparation](#step-1-preparation)
    * [Step 2: Flash System Images](#step-2-flash-system-images)
    * [Step 3: Install *OTA*](#step-3-install-ota)
    * [Step 4: Install *TWRP*](#step-4-install-twrp)
    * [Step 5: Install *Magisk*](#step-5-install-magisk)
    * [Step 6: Done](#step-6-done)
* [Further information](#further-information)

-------------------------------------

## Prerequisite

1. The update file for the version *already running* on the device, not the version you want to install
1. [**TWRP**](https://twrp.me/) for your device
1. [**Magisk**](https://forum.xda-developers.com/apps/magisk/official-magisk-v7-universal-systemless-t3473445)
1. ***ADB*** and ***Fastboot***, with *Developer Mode* and *USB Debugging* enabled on the device

Verify the checksums of every downloaded file before flashing it.

The process resets selected system partitions, installs the ***OTA*** update, and restores ***TWRP*** and ***Magisk***. The *short version* is a checklist. The *long version* explains each step and includes the necessary commands.

-------------------------------------

## Short Version

1. Download the update for the currently installed version
1. Enable USB Debugging
1. Boot into the bootloader
1. Flash *recovery*, *system* and *boot* images
1. Reboot
1. Install the OTA update
1. Flash ***TWRP***
1. Boot into recovery
1. Install ***Magisk***
1. Reboot

-------------------------------------

## Long Version

Double-check your backups and the prerequisites listed above before continuing.

### Step 1: Preparation

#### Copy *Magisk* to your device

Copy or download the ***Magisk*** ZIP to your device. Internal storage and an SD card both work. Put the file somewhere you can find it later.

#### Get the stock files for the current version

Download the update file for the version already running on your device, *not* the version you want to install. If you're running v1.2.3 and want to update to v1.2.4, you need the v1.2.3 file.

Unpack the downloaded file. You'll need `recovery.img`, `system.img`, and `boot.img`.

#### Enable USB Debugging

Connect the device to your computer through USB and enable *USB Debugging* on the device.

### Step 2: Flash System Images

Open a terminal and use these commands to flash the necessary partitions:

```sh
# Check if device is recognized
adb devices

# Boot into bootloader
adb reboot bootloader

# Check device again in Bootloader
fastboot devices

# Flash recovery image
fastboot flash recovery recovery.img

# Flash system image
fastboot flash system system.img

# Flash boot image
fastboot flash boot boot.img

# Reboot device
fastboot reboot
```

### Step 3: Install *OTA*

Install the ***OTA*** update as usual on the device. It will reboot automatically. When it finishes, confirm that the installed version is correct and the system reports that it's up to date.

### Step 4: Install *TWRP*

Flash ***TWRP*** using ***ADB*** and ***Fastboot***. The image usually has a device-specific name, such as `twrp-[version]-[device].img`. The example below uses `TWRP.img` for readability.

```sh
# Check if device is recognized
adb devices

# Boot into bootloader
adb reboot bootloader

# Check device again in Bootloader
fastboot devices

# Flash TWRP
fastboot flash recovery TWRP.img

# Reboot device
fastboot reboot
```

#### Boot into *TWRP*

When the last command restarts the device, use the volume keys to navigate. Choose *Recovery* to open ***TWRP***.

### Step 5: Install *Magisk*

From the ***TWRP*** menu, choose *Install* and select the ***Magisk*** ZIP. Reboot when installation finishes.

**Note:** *This is a good time to clear the Dalvik cache, but it's optional.*

### Step 6: Done

Once the system starts, confirm that the updated version is running and root access is enabled. Disable *USB Debugging* when you're done.

That's it!

-------------------------------------

## Further information

* [Magisk: OTA Upgrade Guide](https://topjohnwu.github.io/Magisk/ota.html)
* [A manual OTA for rooted hammerheads, quasi](https://gist.github.com/eyecatchup/ec0a852428c19705380e)
