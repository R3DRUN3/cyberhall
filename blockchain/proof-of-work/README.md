# PROOF OF WORK 🔎 💪

## Abstract 
<a href="https://en.wikipedia.org/wiki/Proof_of_work">Proof of Work</a> is a decentralized consensus mechanism that requires members
<br/>
of a network to expend effort solving an arbitrary mathematical puzzle
<br/>
in order to prevent anybody from gaming the system.

<br/>

Proof of Work (*PoW*) is one of the two main families of consensus algorithms behind blockchains,
<br/>
the other one being <a href="https://en.wikipedia.org/wiki/Proof_of_stake">Proof of Stake</a>.
<br/>

## Criticisms and personal considerations
*Proof of Work* is currently in the crosshairs of a global debate as it is considered by many to be
<br/>
an environmentally unfriendly and energy-intensive method.
<br/>
This is precisely why PoS was born as a replacement.

<br/>

My opinion is that PoW is theoretically and practically superior to the alternative.
<br/>
The reasons for affirming this are many and it would take an essay of thousands of pages to dissect them and do them all justice
<br/>
however, I will try to compose a short list of those that for me are the main ones:
<br/>

- It exploits the most fundamental resources we have always used to protect property since the dawn of time
 <br/>
(energy / power / labor) and applies them for the protection of assets in a new domain: cyberspace.
- It is simple and elegant
- It imposes prohibitive physical costs on any malicious actor who wants to attack the system.
- It is *economically* and *game-theoretically* **sound**
- Proof of Work **is** work
  * entrepreneurs and validators need to reinvest the resources earned from mining in new equipment and people, creating values and jobs.
- Compared to *PoS* it is less exposed to the creation of monopolies (achieving a monopoly has a much greater physical cost).
- The environmental and ecological argument does not stand up to scrutiny as the same thing can be said of any other industry ever conceived by man
<br/>
but this has never been a valid reason not to produce cars, chips, financial circuits and so on.
<br>
It could also be a good incentive for the mass adoption of cleaner energy sources.
- PoS is the child of modern economic theory, which supports a paradigm of infinite growth in which value is totally disconnected from the underlying physical resources and laws, essentially violating the laws of thermodynamics.
- PoS it is nothing new, every digital and centralized asset we own and participate in use a PoS system in a way or another.

<br/> 

PoW is a relatively modern methodology and I don't think its implications have been fully conceived.  
The thing that fascinates me most about this technique is the fact that we can build **truly secure digital systems**, In a way that was not conceivable before.  
<br/>

This repo contains a python PoW demo script that show how the `speed` of the work increase with the increase of the computing power.  

<br/>

You can play with it by modifying it's parameters and launching it with
<br/>

```console
python3 adversarial_proof_of_work.py
```


NON-ADVERSARIAL MODE (single thread):
```console
STARTING IN NON-ADVERSARIAL MODE ===>

 ################### Work took 4.1682212352752686 seconds ###################
```

ADVERSARIAL MODE (multi thread):
```console
STARTING IN ADVERSARIAL MODE ===>

 ################### Work took 0.7425260543823242 seconds ###################
```