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



