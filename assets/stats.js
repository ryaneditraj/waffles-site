var ratings = [
    "Tiny Potato",
    "Average Potato",
    "Mega Potato",
    "Potato King",
    "Supreme Potato Wizard"
];

var colors = [
    "pink",
    "lightgreen",
    "orange",
    "lightblue",
    "lavender"
];

function ratePotato() {
    var randomPotatoThing = Math.floor(Math.random() * ratings.length);
    document.getElementById("ratingText").textContent = ratings[randomPotatoThing];
}

function changeWorld() {
    var mysteryColor = Math.floor(Math.random() * colors.length);
    document.body.style.backgroundColor = colors[mysteryColor];
}

function checkStuff() {
    var whatTheyTyped = document.getElementById("coolBox").value;

    if (whatTheyTyped.length < 5) {
        document.getElementById("coolAnswer").textContent = "that is a short thing";
    } else {
        document.getElementById("coolAnswer").textContent = "wow long thing";
    }
}

document.getElementById("ratePotatoButton").addEventListener("click", ratePotato);
document.getElementById("changeWorldButton").addEventListener("click", changeWorld);
document.getElementById("coolBox").addEventListener("keyup", checkStuff);
