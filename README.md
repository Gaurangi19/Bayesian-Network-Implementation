# Bayesian-Network-Implementation

Implemented a decision-theoretic agent, using Python, that calculates specific joint, marginal and conditional probabilities, expected utilities and then selects a rational action for a given Bayesian network.

**Input**  
Given a Bayesian network and several queries in a text file ending with a .txt extension, in which all nodes only have two values: “+” (event occurred) or “-” (event not occurred).  
(sample01.txt)  
P(NightDefense = +, Infiltration = -)  
P(Demoralize = + | LeakIdea = +, Infiltration = +)  
******  
LeakIdea  
0.4  
***  
NightDefense | LeakIdea  
0.8 +  
0.3 -  
Infiltration  
0.5  
***  
Demoralize | NightDefense Infiltration  
0.3 + +  
0.6 + -  
0.95 - +  
0.05 - -  


**Output**  
The result is printed to a file called output.txt . Given the sample input above, the output content should be as follows:  
(sample01.output.txt)  
0.25  
0.43  

