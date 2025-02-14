# PCB Renewal
PCB Renewal is a sustainable fabrication technique that enables renewal and reconfiguration of obsolete PCBs. This is an accompanying repository of a [research paper](https://doi.org/10.1145/3706598.3714276) published in ACM CHI 2025.

![teaser](https://github.com/user-attachments/assets/58f8236a-d523-42a7-9e07-9fa38232be9e)

## KiCad Plugin
A plugin for the circuit design software, KiCad, that facilitates this reconfiguring process. It can be used to compare two circuit designs, crosschecking the traces and pads to figure out an efficient way to remove certain traces to transform one circuit into another.

### Installation

##### 1. Open your KiCad Plugin Directory
* You can do this by opening the PCB Editor and clicking on **Tools** > **External Plugins** > **Open Plugin Directory**
* This should open the file location where plugins are stored

##### 2. Copy plugin files into the directory
* Copy the **renewal_plugin** folder from the repository and paste it into the plugin directory
* Make sure to copy the entire folder, not just its contents

##### 3. Install Dependencies
* This plugin uses the **shapely** package
* KiCad has its own python installation, so the dependency must be intalled even if you have the package on your system's python
* Open the **KiCad 7.0 Command Prompt** (a different application from KiCad)
* type `pip install shapely` and press enter

##### 4. Check if plugin works
* Click on **Tools** > **External Plugins** > **Refresh Plugins**
* You should see the plugin show up at the right of the toolbar (the one at the top)
* Click on the plugin icon to use it

### Troubleshooting
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

### Version Information
* KiCad: 7.0.10
* Python: 3.9.16
* numpy: 1.26.1
* shapely: 2.0.4
* wxPython: 4.2.1

## Examples
Various circuit board designs that were used and reconfigured into other designs, e.g turning a PCB for a watch into one for a cat toy.

## Archive
Arudino code and old examples used during the project development.
