# EGB340 Oral Health Care Project

This software provides hardware and software control of a Raspberry Pi based Oral Health Care Station with an accompanying web-app.

The controlled hardware:
* Raspberry Pi 4
* Nokia 5510 LCD
* 4 Push Buttons
* 2 Lever Switches
* 2 LEDs

## Installation

Install the [Raspbian OS](https://www.raspberrypi.org/downloads/raspbian/) on your Raspberry Pi.

Optionally set up SSH with
```bash
sudo apt-get install openssh-client
```

Update the system

```bash
sudo apt-get update
sudo apt-get upgrade
sudo apt-get dist-update
```

Install [Node.js](https://nodejs.org/en/)

```bash
curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -
sudo apt-get install -y nodejs
```

*Clone or download this repository* and `cd` to the root folder, run

```bash
npm install -y
```

Connect the pins on the Raspberry Pi to the 5110 LCD, buttons, and LEDs.

## Usage

`cd` to the root folder and run

```bash
node server
```

The website will be available locally on `localhost:8080` and to other devices on the network at the Raspberry Pi's ip address, eg. `192.168.0.xxx:8080`.

The hardware has 4 navigation buttons used for the LCD menu - up, down, enter, exit. The nested file structure allows you to go up and down levels.

Use of the lever switches will override the LCD and display a timer. On timer end the website will be updated.

## License
[MIT](https://choosealicense.com/licenses/mit/)