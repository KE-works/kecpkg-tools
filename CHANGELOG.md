# Changelog

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
