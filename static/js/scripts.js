// Get daily quotes to share
const quoteGenerator = document.querySelector("#quotegenerator");
quoteGenerator.addEventListener("click", generateQuote);

const shareTweet = document.querySelector("#sharetweet");
shareTweet.addEventListener("click", tweetThis);

  const quotes = [
    {
    "quote": "Live in the moment and make it so beautiful that it will be worth remembering.",
    "author": "Fanny Crosby"
  },
  {
    "quote": "Sometimes the strength of motherhood is greater than natural laws.",
    "author": "Barbara Kingsolver"
  },
  {
    "quote": "Motherhood is the biggest gamble in the world. It is the glorious life force. It’s huge and scary – it’s an act of infinite optimism",
    "author": "Gilda Radner"
  },
  {
    "quote": "The days are long but the years are short.",
    "author": "Gretchen Rubin"
  },
  {
    "quote": "Whatever you do, do with determination. You have one life to live; do your work with passion and give your best. Whether you want to be a chef, doctor, actor, or a mother, be passionate to get the best result.",
    "author": "Alia Bhatt"
  },
  {
    "quote": "No language can express the power and beauty and heroism of a mother’s love.",
    "author": "Edwin Chapin"
  },
  {
    "quote": "Motherhood has a very humanizing effect. Everything gets reduced to essentials.",
    "author": "Meryl Streep"
  },
  {
    "quote": "Motherhood is tough. If you just want a wonderful little creature to love, you can get a puppy.",
    "author": "Barbara Walters"
  },
  {
    "quote": "The fastest way to break the cycle of perfectionism and become a fearless mother is to give up the idea of doing it perfectly—indeed to embrace uncertainty and imperfection.",
    "author": "Arianna Huffington"
  },
  {
    "quote": "Successful mothers are not the ones that have never struggled. They are the ones that never give up, despite the struggles.",
    "author": "Sharon Jaynes"
  },
  {
    "quote": "A mother continues to labor long after the baby is born.",
    "author": "Lisa Jo Baker"
  }
];


function generateQuote() {
    const randomNumber = Math.floor(Math.random() * quotes.length);
    const quote = quotes[randomNumber];
   document.getElementById("quote").textContent = quote.quote;
   document.getElementById("author").textContent = quote.author;
}

generateQuote();

function tweetThis() {
    const url = "https://twitter.com/intent/tweet";
    const text = document.getElementById('quote').textContent;
    const author = document.getElementById('author').textContent;
    window.open(url+"?text=" + "\"" + text + "\"" + " " + author);
}

tweetThis();

// Scroll bar for journal
var myCustomScrollbar = document.querySelector('.my-custom-scrollbar');
var ps = new PerfectScrollbar(myCustomScrollbar);

var scrollbarY = myCustomScrollbar.querySelector('.ps__rail-y');

myCustomScrollbar.onscroll = function () {
  scrollbarY.style.cssText = `top: ${this.scrollTop}px!important; height: 400px; right: ${-this.scrollLeft}px`;
}


// Scroll Back To Top Button:
const mybutton = document.getElementById("myBtn");

window.onscroll = function() {scrollFunction();};

function scrollFunction() {
  if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
    mybutton.style.display = "block";
  } else {
    mybutton.style.display = "none";
  }
}


function topFunction() {
  document.body.scrollTop = 0; 
  document.documentElement.scrollTop = 0;
}

topFunction();