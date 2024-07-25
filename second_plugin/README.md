# Installation

### 1. Open your KiCad Plugin Directory
* You can do this by opening the PCB Editor and clicking on **Tools** > **External Plugins** > **Open Plugin Directory**
* This should open the file location where plugins are stored

### 2. Copy plugin files into the directory
* Copy the **second_plugin** folder (name subject to change) from the repository and paste it into the plugin directory
* Make sure to copy the entire folder, not just its contents

### 3. Install Dependencies
* This plugin uses the **shapely** package
* KiCad has its own python installation, so the dependency must be intalled even if you have the package on your system's python
* Open the **KiCad 7.0 Command Prompt** (a different application from KiCad)
* type `pip install shapely` and press enter

### 4. Check if plugin works
* Click on **Tools** > **External Plugins** > **Refresh Plugins**
* You should see the plugin show up at the right of the toolbar (the one at the top)
* Click on the plugin icon to use it

# Troubleshooting
If you don't see the plugin, make sure that you:
* Can see the plugin folder when you open the Plugin Directory
* Have installed **shapely** on *KiCad's installation of python* (see step 3)
* Have refreshed the plugins (see step 4)

One other thing you can try is using the **Python Scripting Console**
* Click the button with the terminal icon at the top of the screen
* Type `import pcbnew` and press enter
* Type `print(pcbnew.FULL_BACK_TRACE)` and press enter
* The error message should be shown on the screen
* Report the error message to the developer
