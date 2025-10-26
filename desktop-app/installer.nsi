; NSIS Installer Script for 90dayChonThanh Desktop App
; All-in-One Installer: App + Python + Tesseract

!define APP_NAME "90dayChonThanh"
!define APP_VERSION "1.0.0"
!define PUBLISHER "90dayChonThanh"
!define APP_EXE "90dayChonThanh.exe"

; Modern UI
!include "MUI2.nsh"
!include "FileFunc.nsh"

; App info
Name "${APP_NAME}"
OutFile "90dayChonThanh-AllInOne-Setup.exe"
InstallDir "$PROGRAMFILES64\${APP_NAME}"
RequestExecutionLevel admin

; Modern UI Settings
!define MUI_ABORTWARNING
; !define MUI_ICON "assets\icon.ico"  ; Comment out - icon optional
!define MUI_WELCOMEPAGE_TITLE "Cài đặt ${APP_NAME}"
!define MUI_WELCOMEPAGE_TEXT "Installer này sẽ tự động cài:$\n$\n• Python 3.11$\n• Tesseract OCR (Vietnamese)$\n• ${APP_NAME} Desktop App$\n$\nClick Next để bắt đầu."

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Languages
!insertmacro MUI_LANGUAGE "English"

; Installer Sections
Section "Main Application" SecMain
    SetOutPath "$INSTDIR"
    
    ; Show status
    DetailPrint "Đang kiểm tra dependencies..."
    
    ; Check if Python installed
    nsExec::ExecToStack 'python --version'
    Pop $0
    Pop $1
    ${If} $0 != 0
        DetailPrint "Python chưa cài, đang cài đặt..."
        Call InstallPython
    ${Else}
        DetailPrint "Python đã cài: $1"
    ${EndIf}
    
    ; Check if Tesseract installed
    nsExec::ExecToStack 'tesseract --version'
    Pop $0
    Pop $1
    ${If} $0 != 0
        DetailPrint "Tesseract chưa cài, đang cài đặt..."
        Call InstallTesseract
    ${Else}
        DetailPrint "Tesseract đã cài"
    ${EndIf}
    
    ; Install pip packages
    DetailPrint "Đang cài Python packages..."
    nsExec::ExecToLog 'pip install pytesseract Pillow'
    
    ; Copy app files
    DetailPrint "Đang cài ${APP_NAME}..."
    File /r "dist\win-unpacked\*.*"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortcut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
    CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
    
    ; Write uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    ; Write registry
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" "$INSTDIR\Uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "${PUBLISHER}"
    
    DetailPrint "Cài đặt hoàn tất!"
SectionEnd

; Install Python Function
Function InstallPython
    ; Extract Python installer
    SetOutPath "$TEMP"
    File "installers\python-3.11.8-amd64.exe"
    
    ; Run silent install with PATH option
    DetailPrint "Đang cài Python 3.11 (có thể mất vài phút)..."
    ExecWait '"$TEMP\python-3.11.8-amd64.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0' $0
    
    ${If} $0 == 0
        DetailPrint "Python cài đặt thành công"
    ${Else}
        DetailPrint "Cảnh báo: Python install có thể cần restart"
    ${EndIf}
    
    ; Cleanup
    Delete "$TEMP\python-3.11.8-amd64.exe"
FunctionEnd

; Install Tesseract Function
Function InstallTesseract
    ; Extract Tesseract installer
    SetOutPath "$TEMP"
    File "installers\tesseract-ocr-w64-setup-5.3.3.exe"
    
    ; Run silent install with Vietnamese language
    DetailPrint "Đang cài Tesseract OCR với tiếng Việt..."
    ExecWait '"$TEMP\tesseract-ocr-w64-setup-5.3.3.exe" /S /L vie' $0
    
    ${If} $0 == 0
        DetailPrint "Tesseract cài đặt thành công"
    ${Else}
        DetailPrint "Cảnh báo: Tesseract install có thể cần restart"
    ${EndIf}
    
    ; Add Tesseract to PATH
    nsExec::ExecToLog 'setx /M PATH "%PATH%;C:\Program Files\Tesseract-OCR"'
    
    ; Cleanup
    Delete "$TEMP\tesseract-ocr-w64-setup-5.3.3.exe"
FunctionEnd

; Uninstaller Section
Section "Uninstall"
    ; Remove app files
    RMDir /r "$INSTDIR"
    
    ; Remove shortcuts
    Delete "$DESKTOP\${APP_NAME}.lnk"
    RMDir /r "$SMPROGRAMS\${APP_NAME}"
    
    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
    
    MessageBox MB_YESNO "Bạn có muốn gỡ Python và Tesseract không?$\n$\n(Chỉ gỡ nếu không cần cho app khác)" IDYES UninstallDeps IDNO SkipDeps
    
    UninstallDeps:
        ; Note: Python và Tesseract có uninstaller riêng
        DetailPrint "Vui lòng gỡ Python và Tesseract từ Control Panel"
        ExecShell "open" "appwiz.cpl"
    
    SkipDeps:
        DetailPrint "Gỡ cài đặt hoàn tất"
SectionEnd
