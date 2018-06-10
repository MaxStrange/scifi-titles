# scifi-titles
Neural Networks to make Scifi Book Titles

## To Use
The data is contained in the data.csv file, contained in this repo. Here's
how to use the repo:

1. Clone this repo
1. Train a network with: `python(3) ./charmodel.py --mode train`. You will likely have to up the number of epochs (it defaults to 5).

Once you have a few models trained (they will be autosaved as you train them), you can use them like so:

`python(3) ./charmodel.py --mode use --n 15 --temperature 0.4 --model models/whichever_one_you_want`

This will get you a reasonable list of scifi titles, depending on how well trained your network is and how
high your temperature is.

## Examples

Here's a few examples after just a few epochs and a temperature of 0.4:
Note that this list has been curated a bit to remove total nonsense and super repetitive stuff. Also,
some of these are likely real things that the network hit on on accident or memorized.

```
The Serving of the Consorger
The Stars of the Gates
The Time of the Story
The Story of the Story
The Silver in the Moon
Stars of the Eggination
Sea-Kings of Man
The Science Fiction of the Space Little Princess
Songer of the Stars
The Last Cat Who War of the Last Space
The Songing Story
The Servic Flobit
The Worlds of the Reviem
The Summor Captation
The Best Animal Stories of the Ganter
Phantom Enemy
The Down Who War of the Beast
Memory
Bright Segment
The Bard Stories
The Worlds of the Science Fiction
The Stars of the Dock
The Star in the Secret
The Stories of the Secret
Earth
The Moon of the Dead
The Fantastic
The Ancient Fire
Dead of the Cat Come Time
The Space of the Stories
The Mental Assassins
The War of the Stars
The Best Spirits
The Space of the Wain
The Paradinan Encounter
elvet Eyes
The Star of the Science Fiction Man
The Star Dreams
Star in the Last War Beast
```
