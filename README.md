# WfCfg
Workflows Configurator: Scripts to help us configure Sirsi Workflows
client through Group Policy.

## Problem statement

At our organization, we have several departments, and in each
department we have several staff computers. This is represented in
Active Directory with Organizational Units (for each department)
containing Computer objects (for each staff computer). We maintain an
installation of Sirsi Workflows client on each staff computer, and
different department managers want the client to be configured
somewhat differently from others. Generally, staff do not log into
Windows using their own credentials, and, even when they do, they are
usually not interested in personalizing the Workflows
client. Therefore, we want to declare and maintain some subset of
Workflows preferences across user accounts within a
department. **WfCfg** provides a Python-based solution that can be
deployed and administered through Active Directory and Group Policy.

## Downloading WfCfg

Choose one of two suggested methods:

* [Download as a ZIP file](../../archive/refs/heads/main.zip)
* [git clone](https://github.com/git-guides/git-clone)
  `https://github.com/jgferrell/WfCfg.git`
  
## WfCfg operation and command line interface

### Operational summary
The Workflows client stores its settings in folders called
`Property`. Default preferences are stored in `C:\Program Files
(x86)\Sirsi\JWF\Property` and user preferences are stored in
`C:\Users\%username%\Sirsi\Workflows\Property`. Most client
preferences are stored in the `preferences` file in the `Property`
folder; however, the GUI font settings are stored in the `font` file
in the `Property` folder.

WfCfg is configured to update files in all `Property` folders
described above.

### Command line interface
To manually execute WfCfg, open a terminal and navigate to the
directory where you installed the `wfcfg.py` script. To execute WfCfg,
enter `python wfcfg.py` followed by arguments.

There are three primary methods of operation:

* `main`: The primary means of configurating Workflows' `preference`
  file, and thereby most of its configurable settings. From here there
  are three optional arguments:
  * `update`: Use `python wfcfg.py main --update "key1=value1"
    "key2=value2"` to update the value of `key1` and `key2` in the
    preference file to `value1` and `value2` respectively.
  * `delete`: Use `python wfcfg.py main --delete "key3"` to remove `key3`
    from the preference file.
  * `find-printer`: Use `python wfcfg.py main --find-printer "Office
    Printer" "Office Copier" "Department Printer"` to set the client's
    general purpose "screen" printer (*not* the receipt printer) to
    one of the provided printers if one of them is locally installed
    in Windows.
    * If, as in the example here, more than one printer name is
      provided, the resulting printer is **chosen arbitrarily** from
      amongst those printers which have been both named in the call to
      `find-printer` *and* have been found locally installed in the
      Windows system. In other words, we're saying "Just find one of
      these printers—any one of them, it doesn't matter which—and set
      it to be the screen printer."
    * Network printers will not be found.
    * Printer names are sought without case sensitivity.
    * Printer names that contain spaces should be enclosed in "double
      quotes".
    * If no matching printer is found, nothing is changed.
  * `add-printer`: Use `python wfcfg.py main --add-printer "Office
    Printer"` to add "Office Printer" as the screen printer,
    regardless of whether it is available.
* `font`: This allows modification of the GUI font. After choosing
  `font`, there are four positional arguments, so `python wfcfg.py font
  ALL "Comic Sans MS" 18 bold` sets the text of all GUI components to
  display as Comic Sans, 18 point, bold.
  * `component`: Specify a GUI component to update or choose `ALL` to
    update all GUI components.
  * `type`: Set the typeface by providing the name of the desired
    font; font names that contain spaces should be enclosed in "double
    quotes".
  * `size`: Set the size of the font, as measured in points.
  * `style`: Valid styles recognized by Workflows are as follows:
    `plain`, `bold`, and `italic`.
* `receipt-printer`: This allows adding, removing, or setting
  preferences related to receipt printers and receipts.
  * `find`: Use `python wfcfg.py receipt-printer --find "Itherm 9000w"
    "Itherm 280w"` to set the receipt printer to one of the provided
    printers if one of them is locally installed in Windows. A few
    notes:
    * If, as in the example here, more than one printer name is
      provided, the resulting printer is **chosen arbitrarily** from
      amongst those printers which have been both named in the call to
      `find` *and* have been found locally installed in the Windows
      system. In other words, we're saying "Just find one of these
      printers—any one of them, it doesn't matter which—and set it to
      be the receipt printer."
    * Printer names are sought without case sensitivity.
    * Printer names that contain spaces should be enclosed in "double
      quotes".
    * If no matching printer is found, the preference file is updated
      to disable receipt printing.
  * `add`: Use `python wfcfg.py receipt-printer --add "Itherm 9000w"` to
    add "Itherm 9000w" as the receipt printer, regardless of whether
    it is available.
  * `remove`: Use `python wfcfg.py receipt-printer --remove` to disable
    receipt printing.
  * Arguments in the "font" group modify the font used on printed
    receipts, such as `python wfcfg.py receipt-printer --font-type "Comic
    Sans" --font-size 18 --font-style bold` to set the font the Comic
    Sans, 18 point, bold.
    * `font-type`: Set the typeface by providing the name of the
      desired font; font names that contain spaces should be enclosed
      in "double quotes".
    * `font-size`: Set the size of the font, as measured in points.
    * `font-style`: Valid styles recognized by Workflows are as
      follows: `regular`, `bold`, and `italic`.

## Figuring out what settings to change by using filediff.py

Sometimes it's possible to look at the `preference` file and quickly
find the key/value pair that needs to be updated. Sometimes it's less
straightforward. The script `filediff.py`, located in the WfCfg
directory, is a simple utility for identifying which key/value pairs
correspond to the desired configuration changes. Here's how to use it:

1. Log into Windows at a workstation with Python, WfCfg, and Sirsi
   Workflows. Look for `C:\Users\%username%\Sirsi\Workflows`. If it's
   not there, start Workflows, log into it, *and then exit*. This
   should create your personal Workflows directory.
2. Make a copy of your Workflows directory. Name it something like
   `Workflows_Original`.
3. Start and log into Workflows.
4. Make the desired configuration changes.
5. Exit Workflows.
6. Open a command prompt and navigate to your WfCfg directory.
7. Enter a command like `python filediff.py
   "C:\Users\%username%\Sirsi\Workflows_Original"
   "C:\Users\%username%\Sirsi\Workflows"`, where the first path is the
   directory containing the original, unmodified content of your
   Workflows directory, and the second path is the directory
   containing the desired configuration changes.
8. The `filediff.py` script will list files that have been added,
   deleted, and modified. It will also provide a summary of changes
   made to any files, allowing you to specify those changes in a BAT
   file call to `wfcfg.py`.
9. Delete `C:\Users\%username%\Sirsi\Workflows_Original`.

### filediff.py: Example output

Here is output that I generated by following the procedure above. In
addition to manually creating a file in each directory for completely
illustrative purposes, I used the GUI to change the theme (Preference
-> Desktop Setup -> Themes) from "Fall" to "Purple."

```
C:\Program Files\Python311\usr\WfCfg>python filediff.py "C:\Users\jferrell\Sirsi\Workflows_Original" "C:\Users\jferrell\Sirsi\Workflows"

Deleted files:
 --- \file_to_be_deleted.txt

New files:
 +++ \a_file_i_created.txt

Looking for changed files...
*** C:\Users\jferrell\Sirsi\Workflows_Original\Property\preference
--- C:\Users\jferrell\Sirsi\Workflows\Property\preference
***************
*** 17,23 ****
  desktop.display_flyby_help=Y
  desktop.frame.height=738
  desktop.frame.laf=sirsi
! desktop.frame.laf.theme=fall
  desktop.frame.location_x=-2
  desktop.frame.location_y=-2
  desktop.frame.maximized=Y
--- 17,23 ----
  desktop.display_flyby_help=Y
  desktop.frame.height=738
  desktop.frame.laf=sirsi
! desktop.frame.laf.theme=purple
  desktop.frame.location_x=-2
  desktop.frame.location_y=-2
  desktop.frame.maximized=Y

C:\Program Files\Python311\usr\WfCfg>
```

So you can see that `filediff.py` has detected that:

1. `file_to_be_deleted.txt` is in the `Workflows_Original` directory
   but not the modified `Workflows` directory;
2. `a_file_i_created.txt` is in the modified `Workflows` directory but
   not the `Workflows_Original` directory; and
3. I changed the GUI theme from "Fall" colors to "Purple" as described
   above.

Now that I know the key/value pair which sets the desktop theme to
Purple, I can impose this on everyone in my organization with a BAT
file that does `python wfcfg.py main --update
"desktop.frame.laf.theme=purple"`.

## Implementation guide for Active Directory

Please consider basic Active Directory and Group Policy administration
to be a prerequisite of installation and use.

### Shared folder contents and organization

The following sections dealing with administration of Python and of
WfCfg suggest putting files into a shared folder. I would recommend
using a structure like:

* `\\server\share$\Python\`
  * `\\server\share$\Python\3.11.0\`: version-specific folder for
installation file and [python_install](./python_install) BAT files
  * `\\server\share$\Python\scripts\WfCfg\`: folder containing the
contents of this repository.

### Python administration via Group Policy

Three BAT files are included with WfCfg to help with Python
deployment. [python.bat](./python_install/python.bat) is intended to
be called as a Startup script. It accepts one of two parameters:
`install`, which installs Python by calling
[python_install.bat](./python_install/python_install.bat); and
`uninstall`, which uninstalls Python by calling
[python_uninstall.bat](./python_install/python_uninstall.bat). No
customization should be necessary if you adhere to the setup outlined
herein; however, you may need to change the first two variable
declarations in `python.bat` if you're attempting to use a different
version of Python.

#### Preliminary setup

1. [Download Python
   3.11](https://www.python.org/downloads/release/python-3110/)
   (you'll want the 64-bit Windows installer).
2. Move the installer to a shared folder on your Windows server.
3. Move all three BAT files in [python_install](./python_install) *to
   the same shared folder* as your Python installer.

#### Installing Python to workstations

1. Open your Group Policy Management console (e.g., run `gpmc.msc` on
   your domain controller) and navigate to the appropriate OU. The OU
   should contain Active Directory Computer objects you wish to target
   for software installation.
2. Create a new GPO called something like "Software Install: Python
   3.11" and edit it.
3. Navigate in the left column as follows: Computer Configuration ->
   Policies -> Windows Settings -> Scripts (Startup/Shutdown).
4. In the right column, double click "Startup" to open "Startup
   Properties" dialog.
5. Click "Add..." to open "Add a Script" dialog.
6. Click "Browse..." to open the standard file browser dialog and
   browse to the shared folder containing the Python installer and the
   BAT files.
7. Click "python.bat" and then click "Open".
8. In the "Script Parameters" field, type `install` and click "OK" to
    close the "Add a Script" dialog and return to "Startup
    Properties".
9. You should see the full path to the script in the "Name" column and
    "install" in the Parameters column.
10. Click "OK" to close "Startup Properties".

#### Uninstalling Python from workstations

1. Open your Group Policy Management console (e.g., run `gpmc.msc` on
   your domain controller) and navigate to the appropriate OU. The OU
   should contain Active Directory Computer objects you wish to target
   for software removal.
2. Create a new GPO called something like "Software Removal: Python
   3.11" and edit it.
3. Navigate in the left column as follows: Computer Configuration ->
   Policies -> Windows Settings -> Scripts (Startup/Shutdown).
4. In the right column, double click "Startup" to open "Startup
   Properties" dialog.
5. Click "Add..." to open "Add a Script" dialog.
6. Click "Browse..." to open the standard file browser dialog and
   browse to the shared folder containing the Python installer and the
   BAT files.
7. Click "python.bat" and then click "Open".
8. In the "Script Parameters" field, type `uninstall` and click "OK"
    to close the "Add a Script" dialog and return to "Startup
    Properties".
9. You should see the full path to the script in the "Name" column and
    "uninstall" in the Parameters column.
10. Click "OK" to close "Startup Properties".

### WfCfg administration via Group Policy

Like with Python administration, we'll handle WfCfg administration by
calling a BAT file that will then run other software as needed. In
this case, we'll be using [wfcfg.bat](./wfcfg.bat) which will pass all
parameters to [wfcfg.py](./wfcfg.py).

See the sections on [downloading WfCfg](#downloading-wfcfg) and [shared
folder organization](#shared-folder-contents-and-organization)for
preliminary setup and related advice.

#### Workflows configuration via Group Policy

There are multiple ways to do this, of course. I will focus on using
Group Policy's Computer Configuration startup scripts to call
`wfcfg.bat` which then calls `wfcfg.py`.

Calls to `wfcfg.bat` can be made
[*directly*](#direct-method-dispreferred) by adding `wfcfg.bat`
itself as a startup script. This doesn't work well. Multiple calls to
`wfcfg.bat` in the same GPO will result in the GPO calling `wfcfg.bat`
again before the previous call terminates which results in unexpected
behavior. Furthermore, there seems to be an issue with "quoted
parameters" being passed and ultimately interpretted correctly.

It's better to make calls from a GPO to `wfcfg.bat`
[*indirectly*](#indirect-method-preferred) by making a single call
to a helper BAT file that lives in the GPO's "Scripts\Startup" folder.

##### Indirect method (preferred)

Here we create a GPO *and* a BAT file unique to that GPO (stored in
the GPO's "Scripts\Startup" folder). This procedure has proven
reliable.

1. Open your Group Policy Management console (e.g., run `gpmc.msc` on
   your domain controller) and navigate to the appropriate OU. The OU
   should contain Active Directory Computer objects you wish to target
   for this particular Workflows configuration.
2. Create a new GPO called something like "Workflows Configuration:
   Terrible Choices" and edit it.
3. Navigate in the left column as follows: Computer Configuration ->
   Policies -> Windows Settings -> Scripts (Startup/Shutdown).
4. In the right column, double click "Startup" to open "Startup
   Properties" dialog.
5. Click "Show Files..." to open the "Scripts\Startup" folder of the
   GPO you just created.
6. In the "Scripts\Startup" folder, create a new file call something
   like `wfcfg_terrible_config.bat` and open it for editing.
   * **Note:** If you get a permission error when attempting to create
     a file, the "Show Files..." button may not be opening File
     Explorer with sufficient administrative privileges. You may need
     to copy the path and paste it in another instance of File
     Explorer in order to complete this procedure.
7. Add a line to the BAT file like `call
   "\\server\share$\Python\scripts\WfCfg\wfcfg.bat" font ALL "Comic
   Sans MS" 18 bold` providing parameters to wfcfg.cfg as you would to
   WfCfg's [command line interface](#command-line-interface).
   * Repeat as needed (up to three times; once per primary mode of
     operation as outlined in the [command line
     interface](#command-line-interface) section). So if we wanted to,
     for example, change the GUI theme to "Purple" color *in addition
     to* setting the GUI font (done in the preceding step), we would
     make a second call to `wfcfg.bat` but this time provide the
     following parameters: `main --update
     "desktop.frame.laf.theme=purple"`.
8. Save `wfcfg_terrible_config.bat` and return to "Startup Properties"
   of the GPO.
9. Click "Add..." to open "Add a Script" dialog.
10. Click `wfcfg_terrible_config.bat` in the file browser and click
    "Open".
11. Click "OK" to close "Add a Script" dialog.
12. Click "OK" to close "Startup Properties" dialog.

#### Direct method (dispreferred)

This procedure is less reliable compared to the previous procedure. 

1. Open your Group Policy Management console (e.g., run `gpmc.msc` on
   your domain controller) and navigate to the appropriate OU. The OU
   should contain Active Directory Computer objects you wish to target
   for this particular Workflows configuration.
2. Create a new GPO called something like "Workflows Configuration:
   Comic Sans" and edit it.
3. Navigate in the left column as follows: Computer Configuration ->
   Policies -> Windows Settings -> Scripts (Startup/Shutdown).
4. In the right column, double click "Startup" to open "Startup
   Properties" dialog.
5. Click "Add..." to open "Add a Script" dialog.
   1. Click "Browse..." to open the standard file browser dialog and
   browse to the shared folder containing WfCfg script files.
   2. Click "wfcfg.bat" and then click "Open".
   3. In the "Script Parameters" field, provide parameters as you
   would to WfCfg's [command line
   interface](#command-line-interface). For example, `font ALL "Comic
   Sans MS" 18 bold` paramter to set the font of all GUI components to
   use 18 point, bold, Comic Sans.
   4. Repeat as needed (up to three times; once per primary mode of
   operation as outline in the [command line
   interface](#command-line-interface) section). So if we wanted to,
   for example, change the GUI theme to "Fall" colors *in addition to*
   setting the GUI font (done in the preceding steps), we would make a
   second call to `wfcfg.bat` but this time provide the following
   parameters: `main --update "desktop.frame.laf.theme=fall"`.
6. You should see the full path to the script in the "Name" column and
   configuration instructions in the Parameters column.
7. Click "OK" to close "Startup Properties".
