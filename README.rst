===========================
Gaze-controlled Cursor Demo
===========================
This demo application of the `Real-time Screen Gaze <https://github.com/pupil-labs/real-time-screen-gaze/>`_ package can be used to control a PC's mouse cursor using one's eyes. You will need an eyetracking device from Pupil Labs, such as the `Neon <https://pupil-labs.com/products/neon/>`_.

===================
Dependencies
===================
.. code:: bash

	pip install -r requirements.txt

===================
Usage
===================
.. code:: bash

	python3 -m gaze_controlled_cursor_demo

* Adjust the settings as needed until all four markers are tracked
* Markers that are not tracked will show a red border
* Right-click anywhere in the window or on any of the tags to show/hide the settings

-----
MacOS
-----
Note for MacOS users: the first time you run this project, MacOS may prompt you to grant permission for the app to utilize the accessibility features of the operating system. If you do not see this message or fail to grant permission, mouse control functionality will not work.
To manually grant permission

* Open your System Settings and navigate to Privacy & Security
* Within that section go to Accessibility
* Find the terminal app you're using and allow control.
