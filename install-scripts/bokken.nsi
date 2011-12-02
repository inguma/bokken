;Bokken Install script for NSIS
;Based on Basic Example Script by Joost Verburg

;--------------------------------
;Include Modern UI
  !include "MUI2.nsh"
;Include file functions.
  !include "FileFunc.nsh"
;--------------------------------
;General

  ;Name and file
  Name "Bokken"

  OutFile "bokken.exe"

  ;Default installation folder
  InstallDir "C:\Bokken"

  ;Get installation folder from registry if available
  InstallDirRegKey HKLM "Software\Bokken" ""

  ;Request application privileges for Windows Vista
  RequestExecutionLevel user

  ;Files to exclude.
  !define FilesToExclude "/x .hg* /x *~ /x *.pyc /x .*swp"
  !define UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\Bokken"

;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING

;--------------------------------
;Pages

  !insertmacro MUI_PAGE_LICENSE "..\LICENSE"
  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES

  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
  !insertmacro GetSize

;--------------------------------
;Languages

  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

Section "Bokken core" BokkenCore

  SetOutPath "$INSTDIR"

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

  CreateDirectory "$SMPROGRAMS\Bokken"
  WriteINIStr "$SMPROGRAMS\Bokken\Homepage.URL" "InternetShortcut" "URL" "http://bokken.inguma.eu"
  CreateShortCut "$SMPROGRAMS\Bokken\Bokken.lnk" "$INSTDIR\bokken.bat" '' "$INSTDIR\ui\data\icons\bokken.ico"
  CreateShortCut "$SMPROGRAMS\Bokken\Uninstall Bokken.lnk" "$INSTDIR\Uninstall.exe"

  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd

;--------------------------------
;Uninstaller Section

Section "Uninstall"

  MessageBox MB_OKCANCEL|MB_ICONINFORMATION $(ConfirmUninstall) IDOK +2
    Quit

  RMDir /r "$INSTDIR"
  RMDir /r "$SMPROGRAMS\Bokken"

  DeleteRegKey /ifempty HKCU "Software\Bokken"
  DeleteRegKey HKLM "${UNINST_KEY}"

SectionEnd

;--------------------------------
;Descriptions

  ;Language strings
  LangString DESC_BokkenCore ${LANG_ENGLISH} "This is the Bokken core.  You need it."

  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${BokkenCore} $(DESC_BokkenCore)
  !insertmacro MUI_FUNCTION_DESCRIPTION_END

  LangString ConfirmUninstall ${LANG_ENGLISH} "All existing files and folders under the $(^Name) installation directory ($INSTDIR) will be removed.$\r$\nThis includes any files and folders that have since been added after the installation of $(^Name).$\r$\n$\r$\nAre you sure you wish to continue?"
