;Bokken Install script for NSIS
;Based on Basic Example Script by Joost Verburg

;--------------------------------
;Include Modern UI
  !include "MUI2.nsh"
;--------------------------------
;General

  ;Name and file
  Name "Bokken"
  OutFile "bokken.exe"

  ;Default installation folder
  InstallDir "C:\Bokken"
  
  ;Get installation folder from registry if available
  InstallDirRegKey HKCU "Software\Bokken" ""

  ;Request application privileges for Windows Vista
  RequestExecutionLevel user

  ;Files to exclude.
  !define FilesToExclude "/x .hg* /x *~ /x *.pyc /x .*swp"

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
  
;--------------------------------
;Languages
 
  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

Section "Bokken core" BokkenCore

  SetOutPath "$INSTDIR"
  
  File ${FilesToExclude} ..\bokken.bat ..\bokken.py
  File /r ${FilesToExclude} ..\ui

  ;Store installation folder
  WriteRegStr HKCU "Software\Bokken" "" $INSTDIR

  CreateDirectory "$SMPROGRAMS\Bokken"
  CreateShortCut "$SMPROGRAMS\Bokken\Bokken Homepage.lnk" "http://bokken.inguma.eu"
  CreateShortCut "$SMPROGRAMS\Bokken\Bokken.lnk" "$INSTDIR\bokken.bat"
  CreateShortCut "$SMPROGRAMS\Bokken\Uninstall Bokken.lnk" "$INSTDIR\Uninstall.exe"

  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

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

;--------------------------------
;Uninstaller Section

Section "Uninstall"

  MessageBox MB_OKCANCEL|MB_ICONINFORMATION $(ConfirmUninstall) IDOK +2
    Quit

  RMDir /r "$INSTDIR"

  DeleteRegKey /ifempty HKCU "Software\Bokken"

SectionEnd
