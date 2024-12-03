from itypes import *

continueButton = interactions.Button(
    label="▶",
    style=interactions.ButtonStyle.SUCCESS,
    custom_id="play"
)

stopButton = interactions.Button(
    label="| |",
    style=interactions.ButtonStyle.SUCCESS,
    custom_id="pause"
)


nextButton = interactions.Button(
    label="⏭",
    style=interactions.ButtonStyle.PRIMARY,
    custom_id="next"
)
previousButton = interactions.Button(
    label="⏮",
    style=interactions.ButtonStyle.PRIMARY,
    custom_id="previous"
)

VDButton = interactions.Button(
    label="🔉➖",
    style=interactions.ButtonStyle.SECONDARY,
    custom_id="volume_down"
)

VUButton = interactions.Button(
    label="🔊➕",
    style=interactions.ButtonStyle.SECONDARY,
    custom_id="volume_up"
)
