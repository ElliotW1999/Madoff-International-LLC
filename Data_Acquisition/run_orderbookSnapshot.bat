@ECHO OFF 
TITLE Execute python script on anaconda environment
ECHO Please Wait...
:: Section 1: Activate the environment.
ECHO ============================
ECHO Conda Activate
ECHO ============================
@CALL "C:\Users\warne\Anaconda3\Scripts\activate.bat" trading
:: Section 2: Execute python script.
ECHO ============================
ECHO Python test.py
ECHO ============================
python C:\Users\warne\Documents\Github\Madoff-International-LLC\Data_Acquisition\orderbookSnapshot.py

ECHO ============================
ECHO End
ECHO ============================