# Changelog

## 1.0.0 (28MAY19)
Version 1.0.0 release of the `kecpkg-tools` as in the past year no updates were deemed necessary and it is heavily used internally by KE-works BV and at customers to manage ke-chain script packages (KECPKG's). 

 * Added the ability to manage signatures and keys. We built a Publick Key Infrastructure to sign packages and have the ability to trust packages signed with a developer key. The process of creating and submitting a key to be included in the trusted keyring of KE-chain will be on our [support portal](https://support.ke-chain.com) later when it is all available in KE-chain production. Please check out the documentation of the commandline interface using `kecpkg sign --help` for further information.
 * The build process is does now provide a list of artifacts (ARTIFACTS) that are included in a kecpkg. The list of artifacts consist out of the (relative pathname), the hash of the file (normally sha256) and the filesize. KE-chain is able to check the contents of the kecpkgs after upload against this file and will determine of the kecpkgs is untempered on disk.
 * The build process also now provides an optional `kecpkg build --sign` command flag to include a signature inside the keckpg. When package signing is enabled using the `--sign` flag, the list of artifacts (ARTIFACTS file) is signed with the cryptographic signature of the developer (ARTIFACTS.SIG). This signature can be checked by KE-chain after upload when the public key of the developer is known and trusted by KE-chain. This might enable running the contained scripts on higher than scope manager permissions.
 * Adding dependent permission on GPG on linux or windows in order to enable the package signing features.
 * Added dependent packages tabulate, appdirs and python-gnupg.
 

## 0.9.0 (16JAN18)
 * added the ability to add multiple configurations. You can use this to create multiple settings files and build for each setting file another kecpkg. Use `kecpkg build --settings <anothersettings.json>` to create a new kecpkg in the `dist` directory. The `package-info.json` will be recreated based on what is set in the `settings` and stored inside the kecpkg. Use `kecpkg upload --settings <anothersettings.json>` to upload this kecpkg to KE-chain. You can now use a cmd or batch script with multiple setting files to create a multitude of kecpkgs and automatically upload (and even replace) them in a KE-chain project.
 * added `--update` and `--no-update` flags to `kecpkg build`. The `package-info.json` file is needed for the KE-crunch server to understand what module and what function inside the kecpkg to execute. Normally this is re-rendered (updated) in each build sessions based on the contents of the settings file. If you have a custom `package-info.json`, you can use the `--no-update` flag on `kecpkg build --no-update` to prevent the updating the `package-info.json`. You might want to consider updating the settings file with the correct values for the `package-info.json` instead.

## 0.8.0 (15JAN18)
 * added the ability to add additional ignores to the builder. Use `kecpkg config` to set additional list of pathnames or filenames to ignore. One can use eg. 'data' (for subdirectories) or '*.txt' as suitable values.
 * added an option `kecpkg build --prune` to the list of option for the builder. `--prune` is an alternative to `--clean`.

## 0.7.1 (6DEC17)
 * removed the '.git' directory from the packaged kecpkg

## 0.7.0 (6DEC17)
 * The `config` command is now more robust. Added options `--init` to initialise a new settingsfile and added option `--interactive` to walk throug the current settings file and be able to redefine settings.
 * Also the loading of the settings is now more robust and does not fail when a settings file is not found

## 0.6.1 (6DEC17)
 * The `upload` command now properly checks if an build is made in the build directory and gives a proper warning

## 0.6.0 (5DEC17)

 * the `upload` command is fully functional and can even replace uploaded packages. It will guide you through the setup process.
 * added command `config` to check the configuration
 * the `build` command ignores more files and prevents those from being packaged.
  
## 0.5.1 (4DEC17)
 * bugfix release
  
## 0.5.0 (4DEC17)
 * removed shutil for py2.7 compatibility
 * improved upload handling
 * added build and upload runners on the tests
 * updated the `create` command to include the creation of the virtualenv
  
## 0.3.0 (1NOV17)

Third prerelease.
 * The following commands are functional: `new`, `build`, `upload`.
