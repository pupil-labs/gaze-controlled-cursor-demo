===================
Pupil Pointer
===================
This demo application of the `Pupil Labs Realtime Screen Gaze <https://github.com/pupil-labs/realtime-screen-gaze/>`_ package can be used to control a PC's mouse cursor using one's eyes. You will need an eyetracking device from Pupil Labs, such as the `Neon <https://pupil-labs.com/products/neon/>`_.

===================
Dependencies
===================
.. code:: bash

	pip install -r requirements.txt

===================
Usage
===================
.. code:: bash

	python3 -m pupil_pointer_qt

* Extract ``scene_camera.json`` from a recording downloaded from Pupil Cloud into this project's folder.
* Adjust the settings as needed until all four markers are tracked
* Markers that are not tracked will show a red border
* Right-click anywhere in the window or on any of the tags to show/hide the settings
