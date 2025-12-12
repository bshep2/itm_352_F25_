import React, { useState, useEffect } from 'react';
import { Heart, Diamond, Club, Spade, BookOpen, Trophy, Users, Lightbulb, XCircle } from 'lucide-react';

const SUITS = ['♠', '♥', '♦', '♣'];
const RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'];
const RANK_VALUES = { 
  '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
  '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14 
};

const WINNING_SCORE = 300;

function SuitIcon({ suit, className = "" }) {
  const icons = { '♠': Spade, '♥': Heart, '♦': Diamond, '♣': Club };
  const Icon = icons[suit];
  const color = suit === '♥' || suit === '♦' ? 'text-red-600' : 'text-gray-900';
  return <Icon className={`${color} ${className}`} fill="currentColor" />;
}

function Card({ card, onClick, playable = true, highlight = false }) {
  const isRed = card.suit === '♥' || card.suit === '♦';
  
  return (
    <div
      onClick={playable ? onClick : undefined}
      className={`relative bg-white rounded-lg shadow-lg p-3 w-20 h-28 flex flex-col justify-between transition-all cursor-pointer
        ${playable ? 'hover:scale-105 hover:-translate-y-2' : 'opacity-50 cursor-not-allowed'}
        ${highlight ? 'ring-4 ring-yellow-400' : ''}`}
    >
      <div className="flex flex-col items-start">
        <span className={`text-xl font-bold ${isRed ? 'text-red-600' : 'text-gray-900'}`}>
          {card.rank}
        </span>
        <SuitIcon suit={card.suit} className="w-5 h-5" />
      </div>
      <div className="flex justify-end">
        <SuitIcon suit={card.suit} className="w-5 h-5" />
      </div>
    </div>
  );
}

export default function SpadesGame() {
  const [gameState, setGameState] = useState('tutorial');
  const [hands, setHands] = useState([[], [], [], []]);
  const [bids, setBids] = useState([null, null, null, null]);
  const [tricks, setTricks] = useState([0, 0, 0, 0]);
  const [currentTrick, setCurrentTrick] = useState([]);
  const [currentPlayer, setCurrentPlayer] = useState(0);
  const [leadSuit, setLeadSuit] = useState(null);
  const [spadesPlayed, setSpadesPlayed] = useState(false);
  const [scores, setScores] = useState([[0, 0], [0, 0]]);
  const [tutorialStep, setTutorialStep] = useState(0);
  const [message, setMessage] = useState('');
  const [showHintPanel, setShowHintPanel] = useState(false);
  const [hintMessage, setHintMessage] = useState('');
  const [hintsUsed, setHintsUsed] = useState(0);
  const [nilBids, setNilBids] = useState([false, false, false, false]);
  const [gameWinner, setGameWinner] = useState(null);

  const TUTORIAL_STEPS = [
    "Welcome to Spades! This game is played with 4 players in 2 teams. You and the player across from you are partners.",
    "Goal: First team to 300 points wins! Bid how many tricks you think you'll win, then try to make your bid exactly (or more). Spades are always trump!",
    "Each player gets 13 cards. You'll see your cards at the bottom. Your partner is 'North' (top), opponents are 'East' (right) and 'West' (left).",
    "First, everyone bids (0-13). Your team's bids are added together. Try to be accurate!",
    "Special bid: 'NIL' - Bet that you won't win ANY tricks! Success = +100 points, Failure = -100 points. Use this when you have a terrible hand!",
    "After bidding, the player left of dealer leads. You must follow suit if possible. If you can't, you can play any card.",
    "Spades are trump - they beat any other suit! But you can't lead spades until they've been 'broken' (played when you couldn't follow suit).",
    "Highest card of the led suit wins, unless a spade is played. Highest spade wins the trick!",
    "Scoring: Make your bid = 10 × bid + overtricks. Fail = -10 × bid. NIL success = +100, NIL fail = -100. 10 overtricks = -100 points (sandbagging penalty)!",
    "Ready to play? Click 'Start Game' to begin!"
  ];

  useEffect(() => {
    if (gameState === 'tutorial') {
      setMessage(TUTORIAL_STEPS[tutorialStep]);
    }
  }, [tutorialStep, gameState]);

  function createDeck() {
    const newDeck = [];
    for (let suit of SUITS) {
      for (let rank of RANKS) {
        newDeck.push({ suit: suit, rank: rank });
      }
    }
    return newDeck.sort(() => Math.random() - 0.5);
  }

  function dealCards() {
    const newDeck = createDeck();
    const newHands = [[], [], [], []];
    
    for (let i = 0; i < 52; i++) {
      const playerNumber = i % 4;
      newHands[playerNumber].push(newDeck[i]);
    }
    
    for (let hand of newHands) {
      hand.sort((cardA, cardB) => {
        if (cardA.suit !== cardB.suit) {
          return SUITS.indexOf(cardA.suit) - SUITS.indexOf(cardB.suit);
        }
        return RANK_VALUES[cardA.rank] - RANK_VALUES[cardB.rank];
      });
    }
    
    setHands(newHands);
    setGameState('bidding');
    setNilBids([false, false, false, false]);
    setMessage("Time to bid! Look at your cards. Bid how many tricks you'll win, or bid NIL if you think you won't win ANY tricks!");
  }

  function makeBid(player, bid, isNil = false) {
    const newBids = [...bids];
    const newNilBids = [...nilBids];
    
    newBids[player] = bid;
    newNilBids[player] = isNil;
    
    setBids(newBids);
    setNilBids(newNilBids);

    if (player === 0) {
      if (isNil) {
        setMessage(`You bid NIL! Try not to win any tricks. AI players are bidding...`);
      } else {
        setMessage(`You bid ${bid} tricks. AI players are bidding...`);
      }
      setTimeout(() => makeAIBids(newBids, newNilBids), 1000);
    }
  }

  function makeAIBids(currentBids, currentNilBids) {
    const newBids = [...currentBids];
    const newNilBids = [...currentNilBids];
    
    for (let i = 1; i < 4; i++) {
      if (newBids[i] === null) {
        const shouldBidNil = Math.random() < 0.15;
        if (shouldBidNil) {
          newBids[i] = 0;
          newNilBids[i] = true;
        } else {
          newBids[i] = Math.floor(Math.random() * 5) + 1;
          newNilBids[i] = false;
        }
      }
    }
    
    setBids(newBids);
    setNilBids(newNilBids);
    setGameState('playing');
    setCurrentPlayer(0);
    
    const team1Bid = newNilBids[0] ? 'NIL' : newBids[0];
    const team2Bid = newNilBids[2] ? `${team1Bid} + NIL` : `${team1Bid} + ${newBids[2]}`;
    
    let bidMessage = `Bidding complete! Your team: `;
    if (newNilBids[0] && newNilBids[2]) {
      bidMessage += `Double NIL!`;
    } else if (newNilBids[0]) {
      bidMessage += `NIL + ${newBids[2]}`;
    } else if (newNilBids[2]) {
      bidMessage += `${newBids[0]} + NIL`;
    } else {
      bidMessage += `${newBids[0] + newBids[2]}`;
    }
    
    setMessage(bidMessage + ` You lead!`);
  }

  function isCardPlayable(card) {
    if (currentPlayer !== 0) {
      return false;
    }
    
    const yourHand = hands[0];
    
    if (currentTrick.length === 0) {
      if (!spadesPlayed && card.suit === '♠') {
        const onlyHaveSpades = yourHand.every(c => c.suit === '♠');
        return onlyHaveSpades;
      }
      return true;
    }
    
    const youHaveLeadSuit = yourHand.some(c => c.suit === leadSuit);
    
    if (youHaveLeadSuit) {
      return card.suit === leadSuit;
    }
    
    return true;
  }

  function getHint() {
    const yourHand = hands[0];
    let hint = "";

    if (gameState === 'bidding') {
      const spades = yourHand.filter(c => c.suit === '♠');
      const highCards = yourHand.filter(c => RANK_VALUES[c.rank] >= 11);
      const lowCards = yourHand.filter(c => RANK_VALUES[c.rank] <= 5);
      const suggestedBid = Math.floor(spades.length / 3) + Math.floor(highCards.length / 2);
      
      hint = `Bidding Tip: You have ${spades.length} spades, ${highCards.length} high cards (J or better), and ${lowCards.length} low cards. `;
      
      if (lowCards.length >= 10 && highCards.length <= 2) {
        hint += `Your hand is very weak - consider bidding NIL for a chance at 100 points! `;
      } else {
        hint += `Consider bidding around ${Math.max(1, suggestedBid)} tricks. `;
      }
      hint += `Don't overbid - it's better to make your bid than to fail!`;
    }
    else if (gameState === 'playing') {
      const playableCards = yourHand.filter(card => isCardPlayable(card));
      
      if (nilBids[0]) {
        hint = "You bid NIL! Try to play your LOWEST cards to avoid winning tricks. ";
        if (currentTrick.length > 0) {
          hint += "Play lower than the cards already played if possible.";
        }
      } else if (currentTrick.length === 0) {
        hint = "You're leading! Try to lead with a suit where you have high cards. ";
        hint += "Save your spades for when you really need them (they're trump!). ";
        hint += `You have ${playableCards.length} cards you can play.`;
      } else {
        const youHaveLeadSuit = yourHand.some(c => c.suit === leadSuit);
        
        if (youHaveLeadSuit) {
          hint = `You must follow suit (play a ${leadSuit}). `;
          hint += `Try to win the trick if you need more tricks to make your bid, or play low to save your high cards.`;
        } else {
          hint = `You don't have any ${leadSuit}. You can play anything! `;
          hint += `Consider playing a spade to win the trick, or dump a low card from another suit.`;
        }
      }
    }

    const newScores = [...scores];
    newScores[0][0] -= 5;
    setScores(newScores);
    
    setHintsUsed(hintsUsed + 1);
    setHintMessage(hint);
    setShowHintPanel(true);
    
    setTimeout(() => setShowHintPanel(false), 8000);
  }

  function playCard(playerIndex, card) {
    const newHands = [...hands];
    newHands[playerIndex] = newHands[playerIndex].filter(c => c !== card);
    setHands(newHands);

    const newTrick = [...currentTrick, { player: playerIndex, card: card }];
    setCurrentTrick(newTrick);

    if (newTrick.length === 1) {
      setLeadSuit(card.suit);
    }

    if (card.suit === '♠' && leadSuit !== '♠') {
      setSpadesPlayed(true);
    }

    if (newTrick.length === 4) {
      setTimeout(() => finishTrick(newTrick), 1500);
    } else {
      setCurrentPlayer((playerIndex + 1) % 4);
      
      if (playerIndex === 0) {
        setTimeout(() => makeAIPlay(newTrick), 800);
      }
    }
  }

  function makeAIPlay(trick) {
    const player = trick.length % 4;
    const hand = hands[player];
    let playableCards = hand;

    if (trick.length > 0) {
      const hasLeadSuit = hand.some(c => c.suit === leadSuit);
      if (hasLeadSuit) {
        playableCards = hand.filter(c => c.suit === leadSuit);
      }
    } 
    else {
      if (!spadesPlayed) {
        const nonSpades = hand.filter(c => c.suit !== '♠');
        if (nonSpades.length > 0) {
          playableCards = nonSpades;
        }
      }
    }

    const randomCard = playableCards[Math.floor(Math.random() * playableCards.length)];
    playCard(player, randomCard);
  }

  function finishTrick(trick) {
    let winner = trick[0];
    
    for (let play of trick) {
      if (play.card.suit === '♠' && winner.card.suit !== '♠') {
        winner = play;
      } 
      else if (play.card.suit === winner.card.suit && 
               RANK_VALUES[play.card.rank] > RANK_VALUES[winner.card.rank]) {
        winner = play;
      }
    }

    const newTricks = [...tricks];
    newTricks[winner.player]++;
    setTricks(newTricks);

    setCurrentTrick([]);
    setLeadSuit(null);
    setCurrentPlayer(winner.player);

    const playerNames = ['You', 'East', 'North', 'West'];

    if (hands[0].length === 0) {
      calculateRoundScore();
    } else {
      let trickMessage = `${playerNames[winner.player]} won the trick!`;
      
      if (nilBids[winner.player]) {
        trickMessage += ` (${playerNames[winner.player]} bid NIL - this is bad for them!)`;
      }
      
      setMessage(trickMessage);
      
      if (winner.player !== 0) {
        setTimeout(() => makeAIPlay([]), 1000);
      }
    }
  }

  function calculateRoundScore() {
    const team1Bid = bids[0] + bids[2];
    const team1TricksWon = tricks[0] + tricks[2];
    const team2Bid = bids[1] + bids[3];
    const team2TricksWon = tricks[1] + tricks[3];

    let team1Points = 0;
    let team2Points = 0;

    // Calculate NIL bids first
    if (nilBids[0]) {
      if (tricks[0] === 0) {
        team1Points += 100;
      } else {
        team1Points -= 100;
      }
    } else {
      if (tricks[0] >= bids[0]) {
        team1Points += bids[0] * 10 + (tricks[0] - bids[0]);
      } else {
        team1Points -= bids[0] * 10;
      }
    }

    if (nilBids[2]) {
      if (tricks[2] === 0) {
        team1Points += 100;
      } else {
        team1Points -= 100;
      }
    } else {
      if (tricks[2] >= bids[2]) {
        team1Points += bids[2] * 10 + (tricks[2] - bids[2]);
      } else {
        team1Points -= bids[2] * 10;
      }
    }

    // Team 2 scoring
    if (nilBids[1]) {
      if (tricks[1] === 0) {
        team2Points += 100;
      } else {
        team2Points -= 100;
      }
    } else {
      if (tricks[1] >= bids[1]) {
        team2Points += bids[1] * 10 + (tricks[1] - bids[1]);
      } else {
        team2Points -= bids[1] * 10;
      }
    }

    if (nilBids[3]) {
      if (tricks[3] === 0) {
        team2Points += 100;
      } else {
        team2Points -= 100;
      }
    } else {
      if (tricks[3] >= bids[3]) {
        team2Points += bids[3] * 10 + (tricks[3] - bids[3]);
      } else {
        team2Points -= bids[3] * 10;
      }
    }

    const newScores = [
      [scores[0][0] + team1Points, scores[0][1]], 
      [scores[1][0] + team2Points, scores[1][1]]
    ];
    
    // Calculate bags (only for non-nil bids)
    let team1Bags = 0;
    let team2Bags = 0;
    
    if (!nilBids[0] && tricks[0] > bids[0]) {
      team1Bags += (tricks[0] - bids[0]);
    }
    if (!nilBids[2] && tricks[2] > bids[2]) {
      team1Bags += (tricks[2] - bids[2]);
    }
    if (!nilBids[1] && tricks[1] > bids[1]) {
      team2Bags += (tricks[1] - bids[1]);
    }
    if (!nilBids[3] && tricks[3] > bids[3]) {
      team2Bags += (tricks[3] - bids[3]);
    }
    
    newScores[0][1] += team1Bags;
    newScores[1][1] += team2Bags;

    // Sandbagging penalty
    if (newScores[0][1] >= 10) {
      newScores[0][0] -= 100;
      newScores[0][1] -= 10;
    }
    if (newScores[1][1] >= 10) {
      newScores[1][0] -= 100;
      newScores[1][1] -= 10;
    }

    setScores(newScores);
    
    // Check for game winner
    if (newScores[0][0] >= WINNING_SCORE || newScores[1][0] >= WINNING_SCORE) {
      if (newScores[0][0] >= WINNING_SCORE && newScores[1][0] >= WINNING_SCORE) {
        setGameWinner(newScores[0][0] > newScores[1][0] ? 'Team 1' : 'Team 2');
      } else {
        setGameWinner(newScores[0][0] >= WINNING_SCORE ? 'Team 1' : 'Team 2');
      }
      setGameState('gameOver');
    } else {
      setGameState('roundOver');
    }
    
    let resultMessage = `Round over! `;
    if (nilBids[0]) {
      resultMessage += `You bid NIL and ${tricks[0] === 0 ? 'SUCCESS (+100)' : 'FAILED (-100)'}! `;
    }
    setMessage(resultMessage);
  }

  function startNextRound() {
    setBids([null, null, null, null]);
    setTricks([0, 0, 0, 0]);
    setSpadesPlayed(false);
    setNilBids([false, false, false, false]);
    dealCards();
  }

  function restartGame() {
    setScores([[0, 0], [0, 0]]);
    setGameWinner(null);
    setHintsUsed(0);
    setBids([null, null, null, null]);
    setTricks([0, 0, 0, 0]);
    setSpadesPlayed(false);
    setNilBids([false, false, false, false]);
    dealCards();
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-800 via-green-700 to-green-900 p-4">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-6">
          <h1 className="text-5xl font-bold text-white mb-2 flex items-center justify-center gap-3">
            <Spade className="w-12 h-12" fill="white" />
            Spades to 300
            <Spade className="w-12 h-12" fill="white" />
          </h1>
          <p className="text-green-100 text-lg">First to 300 points wins!</p>
          {hintsUsed > 0 && (
            <p className="text-yellow-300 text-sm mt-2">
              Hints used: {hintsUsed} (5 points deducted per hint)
            </p>
          )}
        </div>

        {gameState === 'tutorial' && (
          <div className="bg-white rounded-xl shadow-2xl p-8 max-w-3xl mx-auto">
            <div className="flex items-start gap-4 mb-6">
              <BookOpen className="w-8 h-8 text-green-700 flex-shrink-0" />
              <div>
                <h2 className="text-2xl font-bold text-gray-800 mb-4">
                  Tutorial - Step {tutorialStep + 1} of {TUTORIAL_STEPS.length}
                </h2>
                <p className="text-lg text-gray-700 leading-relaxed">{message}</p>
              </div>
            </div>
            <div className="flex gap-4 justify-center">
              {tutorialStep > 0 && (
                <button
                  onClick={() => setTutorialStep(tutorialStep - 1)}
                  className="px-6 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                >
                  Previous
                </button>
              )}
              {tutorialStep < TUTORIAL_STEPS.length - 1 ? (
                <button
                  onClick={() => setTutorialStep(tutorialStep + 1)}
                  className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  Next
                </button>
              ) : (
                <button
                  onClick={dealCards}
                  className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-xl font-bold"
                >
                  Start Game!
                </button>
              )}
            </div>
          </div>
        )}

        {gameState !== 'tutorial' && (
          <>
            <div className="bg-white/10 backdrop-blur rounded-xl p-4 mb-6">
              <div className="grid grid-cols-2 gap-8 text-white">
                <div className="text-center">
                  <div className="flex items-center justify-center gap-2 mb-2">
                    <Users className="w-5 h-5" />
                    <h3 className="text-xl font-bold">Team 1 (You & North)</h3>
                  </div>
                  <p className="text-3xl font-bold">{scores[0][0]} / {WINNING_SCORE}</p>
                  <p className="text-sm">Bags: {scores[0][1]}</p>
                  {bids[0] !== null && (
                    <p className="text-sm mt-1">
                      {nilBids[0] ? 'NIL' : `Bid: ${bids[0]}`} | Won: {tricks[0]}
                      {bids[2] !== null && ` | Partner: ${nilBids[2] ? 'NIL' : bids[2]} (${tricks[2]})`}
                    </p>
                  )}
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center gap-2 mb-2">
                    <Users className="w-5 h-5" />
                    <h3 className="text-xl font-bold">Team 2 (East & West)</h3>
                  </div>
                  <p className="text-3xl font-bold">{scores[1][0]} / {WINNING_SCORE}</p>
                  <p className="text-sm">Bags: {scores[1][1]}</p>
                  {bids[1] !== null && (
                    <p className="text-sm mt-1">
                      East: {nilBids[1] ? 'NIL' : bids[1]} ({tricks[1]}) | West: {nilBids[3] ? 'NIL' : bids[3]} ({tricks[3]})
                    </p>
                  )}
                </div>
              </div>
            </div>

            <div className="bg-yellow-100 border-l-4 border-yellow-500 p-4 mb-6 rounded">
              <p className="text-gray-800 font-medium">{message}</p>
            </div>

            {showHintPanel && (
              <div className="bg-blue-100 border-l-4 border-blue-500 p-4 mb-6 rounded">
                <div className="flex items-start gap-3">
                  <Lightbulb className="w-6 h-6 text-blue-600 flex-shrink-0" />
                  <div>
                    <p className="text-blue-900 font-bold mb-1">Hint (-5 points):</p>
                    <p className="text-blue-800">{hintMessage}</p>
                  </div>
                </div>
              </div>
            )}

            {(gameState === 'bidding' || gameState === 'playing') && currentPlayer === 0 && (
              <div className="flex justify-center mb-6">
                <button
                  onClick={getHint}
                  className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center gap-2 font-bold"
                >
                  <Lightbulb className="w-5 h-5" />
                  Get Hint (-5 points)
                </button>
              </div>
            )}

            {gameState === 'bidding' && bids[0] === null && (
              <div className="bg-white rounded-xl shadow-2xl p-8 max-w-2xl mx-auto mb-6">
                <h3 className="text-2xl font-bold mb-4 text-center">Place Your Bid</h3>
                <p className="text-gray-600 mb-4 text-center">
                  How many tricks will you win? Or bid NIL for 100 points if you win ZERO tricks!
                </p>
                
                <div className="mb-6">
                  <button
                    onClick={() => makeBid(0, 0, true)}
                    className="w-full px-6 py-4 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-xl font-bold flex items-center justify-center gap-2"
                  >
                    <XCircle className="w-6 h-6" />
                    Bid NIL (+100 if you win 0 tricks, -100 if you win any)
                  </button>
                </div>
                
                <div className="grid grid-cols-7 gap-3">
                  {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13].map(bidAmount => (
                    <button
                      key={bidAmount}
                      onClick={() => makeBid(0, bidAmount, false)}
                      className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-lg font-bold"
                    >
                      {bidAmount}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {gameState === 'roundOver' && (
              <div className="bg-white rounded-xl shadow-2xl p-8 max-w-2xl mx-auto mb-6 text-center">
                <Trophy className="w-16 h-16 mx-auto mb-4 text-yellow-500" />
                <h3 className="text-2xl font-bold mb-4">Round Complete!</h3>
                <button
                  onClick={startNextRound}
                  className="px-8 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-xl font-bold"
                >
                  Next Round
                </button>
              </div>
            )}

            {gameState === 'gameOver' && (
              <div className="bg-white rounded-xl shadow-2xl p-8 max-w-2xl mx-auto mb-6 text-center">
                <Trophy className="w-20 h-20 mx-auto mb-4 text-yellow-500" />
                <h2 className="text-4xl font-bold mb-4 text-gray-800">🎉 {gameWinner} Wins! 🎉</h2>
                <p className="text-xl mb-2">Final Score:</p>
                <p className="text