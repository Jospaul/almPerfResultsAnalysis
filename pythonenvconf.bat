@echo OFF
REM python libraries installation - environment config

cmd /c "python -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org pyyaml"

cmd /c "python -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org bs4"

cmd /c "python -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org numpy"

cmd /c "python -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org zipfile36"

cmd /c "python -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org datetime"

@echo ON

echo "Python environment setup"

exit