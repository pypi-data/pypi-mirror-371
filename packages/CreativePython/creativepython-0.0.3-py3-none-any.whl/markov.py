################################################################################################################
# markov.py     Version 1.4          04-Aug-2022       Bill Manaris, David Johnson, Dana Hughes

###########################################################################
#
# This file is part of Jython Music.
#
# Copyright (C) 2011-2022 Bill Manaris, David Johnson, Dana Hughes
#
#    Jython Music is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Jython Music is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Jython Music.  If not, see <http://www.gnu.org/licenses/>.
#
###########################################################################

#
# Creates a markov model (of arbitrary order).  Order is specified at object construction time.
#
# Some Definitions:
#
# First-order (order = 1) means symbol to symbol transition, i.e., bigram probabiities.
# Second-order (order = 2) means pair-symbols to symbol transition, i.e., trigram probabilities.
#
# Two main functions:
#
#    learn(sequence) - extracts n-grams from the list of symbols and updates the model accordingly.
#
#    generate(startSequence) - synthesize a phrase of events, given a starting sequence, using transition 
#                              probabiities found in the model.
#

# REVISIONS:
#
# 1.4   03-Aug-2022 (bm)   Changed function analyze() to learn() - more meaningful / appropriate.  Also, added default
#              option for startSymbol in generate(), since that's usually the first symbol in the learning corpus.
# 
# Earlier notes:
#
# 1.  Quick and dirty version replaced with a much more memory-efficient version.  Maintains a list of
#     the number of occurances of each symbol, rather than a list of (possibly duplicate) symbols
#
#     Data Structure summarized below:
#
#     model = { tupleOfSymbols: [ transitionDictionary, totalCount] }
#     transitionDictionary = { transitionSymbol: occuranceCount }
#     totalCount = sum(occranceCounts)
#
# 2.  Although we support arbitrarily large Markov orders, anything more than 2-3 is perhaps unnecessary for most
#     musical applications.  If a large order is used, the model simply memorizes the piece, as there isn't
#     much variety (alternatives) following a large 'key' (sequence of symbols).
#
# Code adopted from http://code.activestate.com/recipes/194364-the-markov-chain-algorithm/
#

from random import *

class MarkovModel():
   """Creates a markov model of arbitrary order.
   
      First-order (order = 1) means symbol to symbol transition, i.e., bigram probabiities.
      Second-order (order = 2) means pair-symbols to symbol transition, i.e., trigram probabiities.

      Two main functions:

          learn(sequence) - extracts n-grams from the list of symbols and updates the model accordingly.

          generate(startSequence) - synthesize a phrase of events, given a starting sequence, using transition 
                                    probabiities found in the model.
   """
   
   def __init__(self, order=1):

      self.model = {}             # holds symbol transition probabilities (see Data Structure note above...)

      self.startSequence = None   # holds the first symbol in the learning corpus 

      if order < 1:
         raise NotImplementedError("MarkovModel: Order should be 1 or larger.")
      else:
         self.order = order     # remember this model's order (also see notes above...)
      
      
   def clear(self):
      """It reinitializes the markov model."""

      self.model = {}
          

   def learn(self, listOfSymbols):
      """Extracts n-grams from the list of symbols and updates the model accordingly with the corresponding transitions.
      """
      # We want to remember which symbols may appear at the end of a 'phrase'.  
      # Thus, we make the last symbol transition to 'None'.
      # When we are generating from the model, whenever a transition leads us to 'None', we stop.

      previous = listOfSymbols[0:self.order]   # extract first key

      # if this is the first symbol ever, then remember it (makes generation phase easier...)
      if self.model == {}:           # is this the first symbol to learn?
         self.startSequence = previous   # yes, so remember it...

      for current in (listOfSymbols[self.order:] + [None]):   # loop through remaining symbols
         self.put(tuple(previous), current)                      # add this transition
         previous = previous[1:] + [current]                     # advance to next tuple

      
   # *** Is this needed anymore?
#   def analyzeCopeEvents(self, copeEvents):
#      """Extracts n-grams from the list of copeEvents, using pitch as 'key', and updates the model accordingly with the corresponding transitions.
#      """
#      # We want to remember which copeEvents may appear at the end of a 'phrase'.  
#      # Thus, we make the last symbol transition to 'None'.
#      # When we are generating from the model, whenever a transition leads us to 'None', we stop.
#
#      previous = copeEvents[0:self.order]   # extract first copeEvent
#      for current in (copeEvents[self.order:] + [None]):   # loop through remaining symbols
#         self.put(tuple(previous), current)                      # add this transition
#         previous = previous[1:] + [current]                     # advance to next tuple
      
   def put(self, tupleOfSymbols, symbol = None):
      """Adds a transition between 'tupleOfSymbols' and 'symbol' into the model.  
      """     

      # Each entry in the model consists of a dictionary of next potential symbols, and the total number of 
      # occurances in all next symbols.  If the tuple is not in the model, start a new transition dictionary and total
      # count.

      transitions, total = self.model.get(tupleOfSymbols, [{}, 0])        
      transitions[symbol] = transitions.get(symbol, 0) + 1           # Increment this symbol's count
      total = total + 1                                              # Increment the total count
      self.model[tupleOfSymbols] = (transitions, total)              # Reassign these changes to the Markov Model

   def get(self, tupleOfSymbols):
      """Returns a random transition (symbol), given the list of possible transitions from tupleOfSymbols.
         It assumes that tupleOfSymbols exists in the model; if not, we simply crash (for efficiency, i.e., no error checking/handling)."""

      transitions, total = self.model[tupleOfSymbols]
      
      symbols = transitions.keys()              # Parallel lists of transition symbols
      counts = transitions.values()             # and how often they occur
      
      # Select a random point between 0 and the total count.  Traverse the list, subtracting
      # counts from this selection.  Once the selection is below zero, stop.  This will 
      # efficiently select a symbol from the weighted list
      
      selection = random() * total              # [0, total)
      symbolIndex = 0                           # For indexing purposes while transversing the lists
      
      while selection > 0:                      
          symbol = symbols[symbolIndex]
          selection = selection - counts[symbolIndex]
          symbolIndex = symbolIndex + 1
      
      # symbol now contains a randomly selected symbol from the available lists, biased by 
      # its total count.
      
      return symbol


   def getTransitions(self, tupleOfSymbols):
      """Returns all transitions (symbols), how often they occur (counts) and the total count, as parallel lists, given the list 
         of possible transitions from tupleOfSymbols.
         It assumes that tupleOfSymbols exists in the model; if not, we simply crash (for efficiency, i.e., no error checking/handling)."""

      transitions, total = self.model[tupleOfSymbols]
      
      symbols = transitions.keys()              # Parallel lists of transition symbols
      counts = transitions.values()             # and how often they occur
      
      return symbols, counts, total
      

   def generate(self, startSequence=None):
      """Returns a random sequence of symbols, based on the model's transitions, starting with 'startSequence'.
      """
      
      # if no startSequence provided, use the original first sequence encountered during learning
      if startSequence == None:
         startSequence = self.startSequence

      # is the start sequence well formatted?
      if len(startSequence) != self.order:
         raise ValueError("Start sequence has length " + str(len(startSequence)) + \
                          ". Its length should be the same as the Markov model's order, "+ str(self.order) +".")
                  
      # generate a random sequence of symbols, based on the model's transitions 
      chain = startSequence       # initialize
      key = startSequence 
      current = self.get( tuple(key) )   # get first symbol
      #current = choice(self.model[tuple(key)])   # get first symbol
      while current != None:                     # generate until we find a transition to the end-symbol
         chain = chain + [current]                  # add next symbol to output
         key = key[1:] + [current]                  # construct next key
         current = self.get( tuple(key) )           # get next symbol
         #current = choice(self.model[tuple(key)])   # get next symbol
      # now, chain contains a random sequence of symbols, based on the model's transitions
      
      return chain

   def getNumberOfSymbols(self):
      """Return how many symbols are in the Markov model's memory"""

      return len(self.model.keys())

   def getNumberOfTransitions(self):
      """Return how many transitions are in the Markov model's memory"""
      
      numTransitions = 0
      for i in self.model.values():
         numTransitions = numTransitions + len(i[0].values())
      
      return numTransitions

   def __str__(self):
      """How we want to appear when treated as a string."""

      # return str(self.model)
      text = ""
      for key, value in self.model.iteritems():
         text = text + str(key) + ":  " + str(value) + "\n"
      return text

#-----
# unit tests
if __name__ == "__main__":

   order = 1
   #markov = MarkovModel()    # create a model
   markov = MarkovModel(order)    # create a model
  
   # let's try some tests 
   #listOfSymbols = [60]
   listOfSymbols = [69, 67, 64, 62, 60, 63, 62, 60, 62, 60, 61, 57, 60, 50, 57, 57, 5, 55, 51, 52, 54, 56, 57, 58, 45, 52, 59, 60, 64, 69]
   #startSymbol = listOfSymbols[0]
   startSymbol = listOfSymbols[0:order]
   print "Input = ", listOfSymbols
   print
   
   # let's build the model
   markov.learn(listOfSymbols)
   
   # let's see the model
   print "Model = \n", markov
   print
   
   # let's return the list of transitions from a specific symbol
   #startSymbol = input("Enter start symbol: ")
   #startSymbol = (56,)
   #print "List of transitions and counts are: ", markov.getTransitions(startSymbol)
      
   # now, let's generate a chain, based on the random model (all proabilities should be more or less equal
   print "Output = ", markov.generate(startSymbol)
   #print "Output = ", markov.generate([3,4])
   
