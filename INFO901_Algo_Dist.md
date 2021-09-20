# INFO 901
## Algorithme Distribué

### Professeur
    Flavien Vernier
    flavien.vernier@univ-smb.fr

#### Arbre / graphe de recouvrement

    Objectif : Broadcast un message
###
    Solution 1 : une node envoie a toutes les autres
    void BCast(from, msg) {
        if (myId == from) {
            for (i = 0; i < nbNodes-1; i++ ) {
                if (i != from)
                    send(i, msg)
            }
        } else {
            recieve(from, msg)
        }
    }
###
    Solution 2 : Une node envoie au suivant qui envoie au suivant ... (boucle)
    void BCast(from, msg) {
        last = (from + nbNodes-1) % nbNodes
        next = myId + 1 % nbNodes
        prev = (myId - 1 + nbNodes) % nbNodes

        if (myId == from) {
            send(next, msg)
        } else {
            recieve(prev, msg)
            if (myId != last)
                send(next, msg)
        }
    }
###
    Solution 3 : Une node envoie au suivant et au précédent qui envoient à leur suivant ou précédent (pince)
    void BCast(from, msg) {
        next = myId + 1 % nbNodes
        prev = (myId - 1 + nbNodes) % nbNodes

        if (myId == from) {
            send(next, msg)
            send(prev, msg)
        }
        // BUG : on va avoir un échange interminable entre les deux dernières nodes 
        // --> à débugger en TP dans le code
        if (myId < from + nbNodes/2) {
            recieve(prev, msg)
            send(next, msg)
        } else if (myId > from - nbNodes/2) {
            recieve(next, msg)
            send(prev, msg)
        }
    }
###
    Solution 4 : Grille / Grille régulière
###
    Solution 5 : Hypercube : Invocation du démon juif
###
    Solution 6 : Scatter / Gather
    void scatter(from, tab) {
        nbElem = int(size(tab)/nbNodes)
        chunk = nbElem / nbNodes
        reste = nbElem - chunk * (nbNodes - 1)

        if (me == 0) {
            for (i = 1; i < nbNodes - 1; i++) {
                send(i, tab[i*chunk .. (i+1)*chunk])
            }
            send(nbNodes-1, tab[(nbNodes-1)*chunk])
            return tab[0..chunk]
        } else {
            // Pas sur de cette partie //
            recieve(0, tab)
            return tab
        }
    }

    vois gather(to, tab):
        if me == to {
            bigTab = []
            for (i = 0; i < nbNodes; i++) {
                if me != to {
                    recieve(i, tab)
                    bigTab += tab
                }
            }
            return bigTab
        } else {
            send(to, tab)
        }


#### Section Critique

    request_SC() {
        state = "request"
        while(state != "SC") {
            sleep()
        }
    }

    release_SC() {
        state = "release"
    }

    manageToken() {
        if me == 0 {
            t = new Token
            send((me+1)%nbNodes, t)
        }

        while(alive) {
            recieve((me-1)%nbNodes, t)
            if state == "request" {
                state = "SC"
                while(state != "release") {
                    sleep()
                }
            }
            send((me+1)%nbNodes, t)
            state = null
        }
    }

    