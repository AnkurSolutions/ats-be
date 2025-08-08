@echo off
chcp 65001 >nul
setlocal
set PYTHONIOENCODING=utf-8
set LOGFILE=odoo_install_log.txt

echo -------------------------------------
echo ✅ STEP 1: Activating virtualenv
echo -------------------------------------
call env\Scripts\activate

echo -------------------------------------
echo ✅ STEP 2a: Installing Odoo 'base' module only (safe bootstrap)
echo -------------------------------------
echo [INFO] Installing base... > %LOGFILE%
python odoo-bin -c odoo.conf -d ats_db ^
 -i base ^
 --log-level=info --without-demo=all >> %LOGFILE% 2>&1

if %ERRORLEVEL% neq 0 (
    echo ❌ Error installing 'base'. Check %LOGFILE% for details.
    pause
    exit /b 1
)

echo -------------------------------------
echo ✅ STEP 2b: Installing other Odoo modules
echo -------------------------------------
echo [INFO] Installing other modules... >> %LOGFILE%
python odoo-bin -c odoo.conf -d ats_db ^
 -i mail,hr,hr_recruitment,hr_contract,calendar,ats_job, ats_applicant ^
 --log-level=info --without-demo=all >> %LOGFILE% 2>&1

if %ERRORLEVEL% neq 0 (
    echo ❌ Error installing other modules. Check %LOGFILE% for details.
    pause
    exit /b 1
)

echo -------------------------------------
echo ✅ STEP 3: Starting FastAPI REST API
echo -------------------------------------
uvicorn ats.main:app --reload

pause