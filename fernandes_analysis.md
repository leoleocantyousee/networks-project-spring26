Which city has the highest inefficiency ratio? Look it up on submarinecablemap.com — what cables serve it and how does that explain your result? 

From the terminal I can see that from Boston, London was the city that had the highest inefficiency ratio, which was 5.45. From here Frankfurt had the second highest with a ratio of 4.74. When I go look at the global infrastructure on submarinecablemap.com i can see that even though the distance across the Atlantic is relatively short compared to the other locations, the latency from somewhere like Boston to London is largely due to the amount of traffic going through their links. This can be seen on the Apollo link which goes from New York, United States to Bude, United Kingdom which are both densely packed regions which explains the amount of traffic going through this line. In a scenario like this it is very likely that the packets sent will have to go through lots of store-and-forward processing at explaining the large delay. 

Which city is closest to the theoretical minimum? What does that tell you about routing infrastructure there? 

 

The city that was closest to the theoretical minimum was Sydney as it only had an inefficiency ratio of 1.72 even though it was one of the farthest city being over 16,000 kilometers away. That tells me that the path taken by the internet from America to Australia must be very optimized. The internet traffic probably uses the fast fiber optics above the water which takes the information to the West Coast before getting into the fast underwater lines like the Southern Cross or Hawaiki lines. Since the paths taken across the Pacific Ocean have many fewer hops compared to the congested pathways in Europe, the packets end up spending most of the time moving at the speed of light. 

Your packet to Lagos almost certainly routes through Europe first. Why does Africa route through Europe, and what would need to change to fix it? 

For me Lagos had an inefficiency ratio of 3.26, which shows me there is some issue with geographical routing. A packet sent from Boston to Lagos does not travel directly across the Atlantic. What actually happens instead is that the traffic is routed through European hubs like London or Lisbon first. This detour creates an undirect physical path that is not the great circle math does not pick up. If they wanted to improve this then the global network would need more direct South Atlantic cables that would allow you to bypass Europe and help build a better local peering infrastructure in Africa that would help with stopping the regional traffic from leaving the continent. 

 