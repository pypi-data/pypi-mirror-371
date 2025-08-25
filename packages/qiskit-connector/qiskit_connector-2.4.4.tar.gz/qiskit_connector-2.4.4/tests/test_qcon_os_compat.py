# @Author: Dr. Jeffrey Chijioke-Uche
# @Date: 2023-10-01
# @Last Modified by: Dr. Jeffrey Chijioke-Uche
"""
Test for OS compatibility of the Qiskit Connector package.

This test script verifies the installation, import, and uninstallation
of the `qiskit-connector` package across different operating systems.
It ensures that the package can be installed, its modules can be imported,
and it can be cleanly uninstalled without errors.

Functions:
    test_qiskit_connector_install_and_import(install_cycle):
        Tests the installation, import, and uninstallation of the
        `qiskit-connector` package for a single test cycle on the
        current operating system.

Parameters:
    install_cycle (int): The current test cycle number. This is used
        to parameterize the test for multiple runs if needed.

Raises:
    pytest.fail: If any step (installation, import, or uninstallation)
        fails during the test cycle.

Dependencies:
    - subprocess: For running shell commands to install, import, and
      uninstall the package.
    - sys: To access the Python executable for running commands.
    - platform: To determine the operating system type.
    - pytest: For test parameterization and failure handling.
"""

import subprocess
import sys
import platform
import pytest


# ##############################################################################
# # Suite 1: Installation and Import Test.  Lastest Qiskit Connector
# # This suite tests the installation, import, and uninstallation of the
# # Qiskit Connector package. It is designed to ensure that the package
# # can be installed and imported successfully across different operating
# # systems. The test is parameterized to run 2 times for each OS.
# ##############################################################################
@pytest.mark.parametrize("install_cycle", range(1, 3))  
def test_qiskit_connector_install_and_import(install_cycle):
    os_type = platform.system()
    print(f"🖥️ Running OS Compatibility Test on: {os_type}")

    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "qiskit-connector"],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        subprocess.run([sys.executable, "-c",
                        "from qiskit_connector import QConnectorV2 as connector; from qiskit_connector import QPlanV2 as plan"],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "qiskit-connector"],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        assert True, f"✅ Success on {os_type}"

    except subprocess.CalledProcessError as e:
        print(e.stderr.decode())
        pytest.fail(f"❌ Failed import on {os_type} during test cycle {install_cycle}")

####################################################################################
# Suite 2: Test for OS Compatibility: Version below latest.
# This suite is a repeat of the first one but with a different number of runs.
# It is included to ensure that the package works across different OS types
# and configurations. The test is parameterized to run once for each OS.
# This is useful for testing different environments or configurations.
####################################################################################
@pytest.mark.parametrize("install_cycle", range(1, 2))  
def test_qiskit_connector_install_and_import_r1(install_cycle):
    os_type = platform.system()
    print(f"🖥️ Running OS Compatibility Test on: {os_type}")

    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "qiskit-connector==2.2.5"],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        subprocess.run([sys.executable, "-c",
                        "from qiskit_connector import QConnectorV2 as connector; from qiskit_connector import QPlanV2 as plan"],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "qiskit-connector"],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        assert True, f"✅ Success on {os_type}"

    except subprocess.CalledProcessError as e:
        print(e.stderr.decode())
        pytest.fail(f"❌ Failed import on {os_type} during test cycle {install_cycle}")

####################################################################################
@pytest.mark.parametrize("install_cycle", range(1, 2))  
def test_qiskit_connector_install_and_import_r2(install_cycle):
    os_type = platform.system()
    print(f"🖥️ Running OS Compatibility Test on: {os_type}")

    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "qiskit-connector==2.2.4"],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        subprocess.run([sys.executable, "-c",
                        "from qiskit_connector import QConnectorV2 as connector; from qiskit_connector import QPlanV2 as plan"],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "qiskit-connector"],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        assert True, f"✅ Success on {os_type}"

    except subprocess.CalledProcessError as e:
        print(e.stderr.decode())
        pytest.fail(f"❌ Failed import on {os_type} during test cycle {install_cycle}")

####################################################################################
@pytest.mark.parametrize("install_cycle", range(1, 2))  
def test_qiskit_connector_install_and_import_r3(install_cycle):
    os_type = platform.system()
    print(f"🖥️ Running OS Compatibility Test on: {os_type}")

    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "qiskit-connector==2.2.3"],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        subprocess.run([sys.executable, "-c",
                        "from qiskit_connector import QConnectorV2 as connector; from qiskit_connector import QPlanV2 as plan"],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "qiskit-connector"],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        assert True, f"✅ Success on {os_type}"

    except subprocess.CalledProcessError as e:
        print(e.stderr.decode())
        pytest.fail(f"❌ Failed import on {os_type} during test cycle {install_cycle}")
