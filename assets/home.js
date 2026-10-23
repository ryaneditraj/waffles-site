var superPotatoNumberThing = 0;

var weirdFacts = [
    "Potatoes are awesome.",
    "Some potatoes are bigger than your head.",
    "French fries come from potatoes.",
    "Potatoes have eyes but cannot see.",
    "A potato never pays taxes."
];

function clickPotato() {
    superPotatoNumberThing++;
    document.getElementById("potatoNum").textContent = superPotatoNumberThing;
}

function giveFact() {
    var randomThing = Math.floor(Math.random() * weirdFacts.length);
    document.getElementById("factArea").textContent = weirdFacts[randomThing];
}

function joinClub() {
    var funnyName = document.getElementById("nameBox").value;
    document.getElementById("joinMsg").textContent =
        funnyName + " is now officially a potato fan.";
}

document.getElementById("clickPotatoButton").addEventListener("click", clickPotato);
document.getElementById("giveFactButton").addEventListener("click", giveFact);
document.getElementById("joinClubButton").addEventListener("click", joinClub);
