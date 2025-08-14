I'm building a carnival-type target shooting game called 'snyper'. In this game, several targets will pop up, and the player will shoot them, and then they will lay down until prompted.

The basic architecture involves a network of Raspberry Pi Pico W microcontrollers. One device, the server, will run the game. It will communicate bidirectionally with the other picos, the "clients," which will manage the targets.

We'll get to the clients later, for now I want to focus on the server. It will need to manage three tasks concurrently:

- It will manage I/O from a connected st7789 display
- It will run a server that provides a wifi access point which the targets connect to. Within that network it will provide a server that remains in communication with all of the targets. All nodes in this network will communicate via HTTP requests, using the 'microdot' python library.
- It will run the game loop, and all logic contained within. At times this will mean routing signals from one of the routines to one of the others, for instance, a target gets hit, the player's score is updated, and the score will be printed on the display
