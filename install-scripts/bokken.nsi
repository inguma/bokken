;Bokken Install script for NSIS
;Based on Basic Example Script by Joost Verburg

;--------------------------------
;Include Modern UI
  !include "MUI2.nsh"
;Include file functions.
  !include "FileFunc.nsh"
;Include logical functions.
  !include "LogicLib.nsh"
;--------------------------------
;General

  ;Name and file
  Name "Bokken"

  OutFile "bokken.exe"

  ;Default installation folder
  InstallDir "C:\Bokken"

  ;Get installation folder from registry if available
  InstallDirRegKey HKLM "Software\$(^Name)" ""

  ;Request application privileges for Windows Vista
  RequestExecutionLevel user

  ;Files to exclude.
  !define FilesToExclude "/x .hg* /x *~ /x *.pyc /x .*swp"
  !define UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\$(^Name)"

;--------------------------------
;Variables

  Var PythonDir
  Var StartMenuFolder

;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING

;--------------------------------
;Pages

  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_LICENSE "..\LICENSE"
  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY

  ;Start Menu Folder Page Configuration
  !define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKLM"
  !define MUI_STARTMENUPAGE_REGISTRY_KEY "Software\$(^Name)"
  !define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"
  !insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder

  !insertmacro MUI_PAGE_INSTFILES

  !insertmacro MUI_UNPAGE_WELCOME
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES

;--------------------------------
;More macros
  !insertmacro GetSize

;--------------------------------
;Languages

  !insertmacro MUI_LANGUAGE "English"

;--------------------------------

;Installer Sections

Section "Bokken core" BokkenCore

  # We don't allow the user to remove Bokken.
  SectionIn RO

  SetOutPath "$INSTDIR"

  ReadRegStr $PythonDir HKLM Software\Python\PythonCore\2.7\InstallPath ""
  ${If} $PythonDir == ''
    MessageBox MB_OKCANCEL "Python has not been found on your system! \
      $\nChoose Cancel to abort the installation or OK to download \
      Python." IDOK downloadPython
      Abort
      Goto done
    downloadPython:
      ExecShell "open" "http://ftp.gnome.org/pub/GNOME/binaries/win32/pygtk/2.24/pygtk-all-in-one-2.24.0.win32-py2.7.msi"
    done:
  ${Endif}

  File ${FilesToExclude} ..\bokken.bat ..\bokken.py
  File /r ${FilesToExclude} ..\ui

  ;Store installation folder and other registry keys.
  WriteRegStr HKLM "Software\Bokken" "" $INSTDIR
  WriteRegStr HKLM "${UNINST_KEY}" "DisplayName" \
                   "Bokken: Reverse Engineering made easier and free"
  WriteRegStr HKLM "${UNINST_KEY}" "Publisher" \
                   "Bokken Development Team"
  WriteRegStr HKLM "${UNINST_KEY}" "DisplayVersion" \
                   "1.5"
  WriteRegStr HKLM "${UNINST_KEY}" "DisplayIcon" \
                   "$\"$INSTDIR\ui\data\icons\bokken.ico$\""
  WriteRegStr HKLM "${UNINST_KEY}" "URLInfoAbout" \
                   "http://bokken.inguma.eu/projects/bokken/wiki"
  WriteRegStr HKLM "${UNINST_KEY}" "UninstallString" \
                   "$\"$INSTDIR\Uninstall.exe$\""

  ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
  IntFmt $0 "0x%08X" $0
  WriteRegDWORD HKLM "${UNINST_KEY}" "EstimatedSize" "$0"

  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
    CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
    WriteINIStr "$SMPROGRAMS\$StartMenuFolder\Homepage.URL" "InternetShortcut" "URL" "http://bokken.inguma.eu"
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Bokken.lnk" "$INSTDIR\bokken.bat" '' "$INSTDIR\ui\data\icons\bokken.ico"
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Uninstall Bokken.lnk" "$INSTDIR\Uninstall.exe"
  !insertmacro MUI_STARTMENU_WRITE_END

  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd

Section "pyew" Pyew

  SetOutPath "$INSTDIR\pyew"

  ;Store installation folder and other registry keys.
  WriteRegStr HKLM "Software\Pyew" "" $INSTDIR

SectionEnd
;--------------------------------
;Uninstaller Section

Section "Uninstall"

  MessageBox MB_OKCANCEL|MB_ICONINFORMATION $(ConfirmUninstall) IDOK +2
    Quit

  RMDir /r "$INSTDIR"

  !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder

  Delete "$SMPROGRAMS\$StartMenuFolder\Uninstall Bokken.lnk"
  Delete "$SMPROGRAMS\$StartMenuFolder\Bokken.lnk"
  Delete "$SMPROGRAMS\$StartMenuFolder\Homepage.URL"
  Rmdir "$SMPROGRAMS\$StartMenuFolder"

  DeleteRegKey /ifempty HKLM "Software\$(^Name)"
  DeleteRegKey HKLM "${UNINST_KEY}"

  MessageBox MB_OK "$(^Name) has been succesfully removed from your system.$\r$\nPython and other applications need to be removed separately.$\r$\n$\r$\nYou may now continue without rebooting your machine." /SD IDOK

SectionEnd

;--------------------------------
;Descriptions

  ;Language strings
  LangString DESC_BokkenCore ${LANG_ENGLISH} "This is the Bokken core.  You need it."
  LangString DESC_Pyew ${LANG_ENGLISH} "A Python tool like radare2 or *iew for malware analysis.  It allows $(^Name) to analyze PDFs and some types of binaries."

  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${BokkenCore} $(DESC_BokkenCore)
    !insertmacro MUI_DESCRIPTION_TEXT ${Pyew} $(DESC_Pyew)
  !insertmacro MUI_FUNCTION_DESCRIPTION_END

  LangString ConfirmUninstall ${LANG_ENGLISH} "All existing files and folders under the $(^Name) installation directory ($INSTDIR) will be removed.$\r$\nThis includes any files and folders that have since been added after the installation of $(^Name).$\r$\n$\r$\nAre you sure you wish to continue?"
