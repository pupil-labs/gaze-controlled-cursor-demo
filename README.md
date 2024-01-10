# Gaze Control - Assistive Technology Based on Gaze-Interaction
This demo application of the `Real-time Screen Gaze <https://github.com/pupil-labs/real-time-screen-gaze/>`_ package can be used to control a PC's mouse cursor using one's eyes. You will need an eyetracking device from Pupil Labs, such as the `Neon <https://pupil-labs.com/products/neon/>`_.

# Dependencies
To run the software you need to install the following dependencies:
```bash
pip install -r requirements.txt
```

Also, this software only works with a sufficiently large monitor. We recommend ~24-26 inches.

## Ubuntu
If you are running this on Ubuntu you also need to install the following:
```bash
sudo apt install libxcb-cursor0
```

## MacOS
The first time you run this project, MacOS may prompt you to grant permission for the app to utilize the accessibility features of the operating system. If you do not see this message or fail to grant permission, mouse control functionality will not work.
To manually grant permission

- Open your System Settings and navigate to Privacy & Security
- Within that section go to Accessibility
- Find the terminal app you're using and allow control.

# Usage
Execute the following command to start the application:
```bash
python src/main.py
```

When the application starts, it first tries to connect to a Neon device in the local network. Once a connection is established, the main window opens up which displays markers in the corners of the screen as well as a real-time visualization of your detected gaze location on the screen.

In addition to the main window, a helper window for debugging opens up as well, which shows you the real-time feed of the Neon scene camera and the detected gaze position in that video feed.

The markers in the screen corners are used to track the screen and **it's critical they are detected well in the video**. If a marker is detected successfully it is shown with a green border, otherwise with a red border.

If you "dwell" on something on the screen long enough a click interaction will be performed at that location. This dwell time is visualized by the growing green circle inside of the red circle. You will also hear a click sound when a click is triggered. Depending on whether or not the keyboard is enabled, those clicks have different effects. See below for more details.

## Keyboard
The keyboard can be toggled by dwelling on the "KEYS" button in the bottom right. While the keyboard is enabled, you can only click on the keys of the keyboard by dwelling on them. Dwelling on something else on the screen will not trigger a mouse click.

If you click on one of the keys, the corresponding key will be pressed and send to the currently active application. This allows you to open e.g. a text editor and type text using the keyboard.

## Mouse
While the keyboard is disabled, you can click anywhere on the screen by dwelling on it. A mouse click will be triggered at the location you are dwelling on. 

# Calibration
If the gaze estimation results on the screen are insufficient in accuracy, you have the option to perform a calibration. To start a calibration execute the calibration program using the following command (the main Gaze Control app should not be running while calibrating):
```bash
python src/calibration.py
```

Similar to Gaze Control, this will open a main window as well as a debug window. The main window contains the same markers Gaze Control does, but it is not transparent.

To start the calibration process hit the Enter key. A series of gaze targets will then be presented on the screen. Your task is to look at them continuously one after the other.

Try not to blink while the target is green. It is fine to blink while a target is still red, so you can blink briefly between all targets.

Once all targets have been presented and the calibration result will be saved in a file called `predictor.pkl`. The application will automatically close down after the calibration is finished.

When you start Gaze Control again, it will automatically load the calibration result from the file and use it for improved gaze estimation.