# cours informatique fondamentale 2021-2022
# PROJET: repliage de proteines

# necessite l'installation de la librairie PySAT et de la librairie func_timeout
from pysat.solvers import Minisat22
from pysat.solvers import Glucose4
from pysat.formula import CNF
from pysat.formula import IDPool
from pysat.card import *
from optparse import OptionParser
import func_timeout


##### OPTIONS POUR L'UTILISATION EN LIGNE DE COMMANDE ###############

# Usage: folder.py [options]

# Options:
  # -h, --help            show this help message and exit
  # -s SEQ, --sequence=SEQ
                        # specify the input sequence
  # -b BOUND, --bound=BOUND
                        # specify a lower bound on the score
  # -p, --print           print solution
  # -i, --incremental     incremental mode: try small bounds first and increment
  # -v, --verbose         verbose mode
  # -t, --test            testing mode

# on doit TOUJOURS donner une sequence
# * lorsqu'une borne est donnee, votre programme doit tester que le meilleur score de la sequence est superieur ou egale a cette borne
# * lorsqu'aucune borne n'est donnee, alors votre programme doit calculer le meilleur score pour la sequence, par defaut en utilisant une recherche par dichotomie, et en utilisant une methode incrementale si l'option -i est active
#
# l'option -v vous permet de creer un mode 'verbose'
# si l'option -t est active, alors le code execute uniquement la fonction test_code() implementee ci-dessous, qui vous permet de tester votre code avec des exemples deja fournis. Si l'execution d'un test prend plus que TIMEOUT secondes (fixe a 10s ci-dessous), alors le test s'arrete et la fonction passe au test suivant

parser = OptionParser()
parser.add_option("-s", "--sequence", dest="seq", action="store", 
                  help="specify the input sequence")
parser.add_option("-b", "--bound", dest="bound", action="store", 
                  help="specify a lower bound on the score", type="int")
parser.add_option("-p", "--print", dest="affichage_sol", action="store_true", 
                  help="print solution",default=False)
parser.add_option("-i", "--incremental", dest="incremental", action="store_true", 
                  help="incremental mode: try small bounds first and increment",default=False)
parser.add_option("-v", "--verbose", dest="verbose", action="store_true", 
                  help="verbose mode",default=False)
parser.add_option("-t", "--test", dest="test", action="store_true", 
                  help="testing mode",default=False)

(options, args) = parser.parse_args()
    
affichage_sol = options.affichage_sol
verb = options.verbose
incremental = options.incremental
test = options.test

###############################################################################################
 

def exist_sol(seq,bound): # retourne True si et seulement si il existe un plongement de score au moins 'bound'
# A COMPLETER
    cnf = CNF() # construction d'un objet formule en forme normale conjonctive (Conjunctive Normal Form)
    vpool = IDPool(start_from=1) # pour le stockage des identifiants entiers des couples (i,j) ?
    length = len(seq)

    print(seq[0])
    print(bound)

    # Contrainte #1 
    # Chaque élement est au moins dans une case. Pour tout élement p , il existe une position ij
        
    for p, v in enumerate(options.seq):
        d = [] 
        for i in range(length):
            for j in range(length):
                d.append(vpool.id((i,j,p)))
        cnf.append(d)

    # Contrainte #2
    # Il y a au plus une case par élément. Chaque élément est au plus dans une case

    for i in range(length):
        for j in range(length):
            for k in range(length):
                for l in range(length):
                    for p, v in enumerate(options.seq):
                        if ((i != k) or (j != l)):
                            cnf.append([-vpool.id((i,j,p)),-vpool.id((k,l,p))])
    
    
    # Contrainte #3
    # Il y a au plus un élément par case
    
    for i in range(length):
        for j in range(length):
            for p1, v1 in enumerate(options.seq):
                for p2, v2 in enumerate(options.seq):
                    if not (p1 is p2):  
                        cnf.append([-vpool.id((i,j,p1)),-vpool.id((i,j,p2))])

    # A COMPLETER
    # Contrainte #4
    # Elément p est voisin directe de p+1
    
    for i in range(length):
        for j in range(length):
            for k in range(length):
                for l in range(length):
                    for p1, v1 in enumerate(seq):
                        for p2, v2 in enumerate(seq):
                            if ((p1+1 == p2) and ((abs(i-k)==0)and (abs(j-l)==1) or (abs(i-k)==1)and (abs(j-l)==0))): #(ij) (kl) voisins et p1 p2 se suivent
                                cnf.append([-vpool.id((i,j,p1)),vpool.id((k,l,p2))])

    # A COMPLETER
    # Contrainte : il faut au moins x Paires (élements voisins de valeur 1)
    # Y'ijkl' est vrai si ij et kl sont voisins et valeur 1 -> y ijkl l'ensemble des voisins qui sera l'ensemble des litéraux
    # TEST A COMPLETER
    lits = [0]

    for i in range(length):
        for j in range(length):
            for k in range(length):
                for l in range(length):
                    for p1, v1 in enumerate(seq):
                        for p2, v2 in enumerate(seq):
                            if ( ((abs(i-k)==0)and (abs(j-l)==1) or (abs(i-k)==1)and (abs(j-l)==0))):
                                lits.append(vpool.id([i,j,k,l])) # Veut une liste de litéraux , comment faire une liste de litéraux avec 4 int ?
                                if ((v1 == 1) and (v2 == 1)):
                                    cnf.append(-vpool.id((i,j,k,l),vpool.id((i,j,p1)))) # Correcte ?
                                    cnf.append(-vpool.id((i,j,k,l),vpool.id((i,j,p2)))) # Correcte ?
                                    cnf.append(vpool.id((i,j,k,l),-vpool.id((i,j,p1)),-vpool.id((i,j,p2)))) # Correcte ?
    
    cnf.extend(CardEnc.atleast(lits,bound,vpool=vpool,encoding=EncType.seqcounter))

    #Résolution
    s = Glucose4(use_timer=True) # pour utiliser le solveur Glucose
    s.append_formula(cnf.clauses, no_return=False)
    sat = s.solve()
    print("satisfaisable : " + str(sat))
    print(sat)

    print("Temps de resolution : " + '{0:.2f}s'.format(s.time()))

    return(True) # a modifier

    
def compute_max_score(seq): # calcul le meilleur score pour la sequence seq, il doit donc retourne un entier, methode utilisee: dichotomie par defaut, incrementale si l'option -i est active
# A COMPLETER
    max_Not_Found = True

    #Recherche incremental
    if (incremental):
        best_score = 0
        while(max_Not_Found):
            best_score =+ 1
            max_Not_Found = exist_sol(seq,best_score)
        
        return(best_score-1)

    #Recherche dichotomique
    else:
        best_score = len(seq)/2
    
        return(best_score)

    
####################################################################        
########### CE CODE NE DOIT PAS ETRE MODIFIE #######################
####################################################################
def test_code():
    examples = [('00',0), ('1', 0),('01000',0),('00110000',1),('11',1),('111',2),('1111',4),('1111111',8),("111111111111111",22), ("1011011011", 7), ("011010111110011", 12), ("01101011111000101",11), ("0110111001000101", 8), ("000000000111000000110000000",5), ('100010100', 0), ('01101011111110111', 17),('10', 0), ('10', 0), ('001', 0), ('000', 0), ('1001', 1), ('1111', 4), ('00111', 2), ('01001', 1), ('111010', 3), ('110110', 3), ('0010110', 2), ('0000001', 0), ('01101000', 2), ('10011111', 7), ('011001101', 5), ('000110111', 5), ('0011000010', 2), ('1000010100', 2), ('11000111000', 5), ('01010101110', 4), ('011001100010', 5), ('010011100010', 5), ('1110000110011', 8), ('1000101110001', 4), ('11010101011110', 10), ('01000101000101', 0), ('111011100100000', 8), ('000001100111010', 6), ('0110111110011000', 11), ('0011110010110110', 11), ('01111100010010101', 11), ('10011011011100101', 12), ('101111101100101001', 13), ('110101011010101010', 9), ('1111101010000111001', 14), ('0111000101001000111', 11), ('10111110100001010010', 12), ('10110011010010001110', 11)] # chaque couple de cette liste est formee d'une sequence et de son meilleur score

    TIMEOUT = 10

    # SAT TESTS
    total_sat_tests = 0
    total_unsat_tests = 0
    sat_tests_success = 0
    timeouts_sat_tests = 0
    exceptions_sat_tests = 0

    # UNSAT TESTS
    total_unsat_test = 0
    unsat_tests_success = 0
    timeouts_unsat_tests = 0
    exceptions_unsat_tests = 0

    # MAXSCORES TEST
    correct_maxscores = 0
    total_maxscores = 0
    timeouts_maxscores = 0
    exceptions_maxscores = 0


    
    # sur cet ensemble de tests, votre methode devrait toujours retourner qu'il existe une solution
    print("\n****** Test de satisfiabilite ******\n")
    for (seq,maxbound) in examples:
        total_sat_tests += 1
        bound = int(maxbound / 2)
        print("sequence: " + seq + " borne: " + str(bound), end='')
        try:
            if func_timeout.func_timeout(TIMEOUT, exist_sol, [seq,bound]):
                sat_tests_success += 1
                print(" ---> succes")
            else:
                print(" ---> echec")
        except func_timeout.FunctionTimedOut:
            timeouts_sat_tests += 1
            print(" ---> timeout")
        except Exception as e:
            exceptions_sat_tests += 1
            print(" ---> exception levee")

    # sur cet ensemble de tests, votre methode devrait toujours retourner qu'il n'existe pas de solution
    print("\n****** Test de d'insatisfiabilite ******\n")
    for (seq,maxbound) in examples:
        total_unsat_tests += 1
        bound = maxbound+1
        print("sequence: " + seq + " borne: " + str(bound), end='')
        try:
            if not func_timeout.func_timeout(TIMEOUT, exist_sol, [seq,bound]):
                unsat_tests_success += 1
                print(" ---> succes")
            else:
                print(" ---> echec")
        except func_timeout.FunctionTimedOut:
            timeouts_unsat_tests += 1
            print(" ---> timeout")
        except Exception as e:
            exceptions_unsat_tests += 1
            print(" ---> exception levee")

            
    # sur cet ensemble de tests, votre methode devrait retourner le meilleur score. Vous pouvez utiliser la methode par dichotomie ou incrementale, au choix
    print("\n****** Test de calcul du meilleur score ******\n")
    for (seq,maxbound) in examples:
        total_maxscores += 1
        print("sequence: " + seq + " borne attendue: " + str(maxbound), end='')
        try:
            found_max_score = func_timeout.func_timeout(TIMEOUT, compute_max_score, [seq])
            print(" borne retournee: " + str(found_max_score), end='')
            if maxbound == found_max_score:
                correct_maxscores += 1
                print(" ---> succes")
            else:
                print(" ---> echec")
        except func_timeout.FunctionTimedOut:
            timeouts_maxscores += 1
            print(" ---> timeout")
        except Exception as e:
            exceptions_maxscores += 1
            print(" ---> exception levee")

    print("\nRESULTATS TESTS\n")

    print("Instances avec solutions correctement repondues: " + str(sat_tests_success) + " sur " + str(total_sat_tests) + " tests realises")
    print("Nombre de timeouts: " + str(timeouts_sat_tests))
    print("Nombre d'exceptions: " + str(exceptions_sat_tests) + "\n")

    print("Instances sans solution correctement repondues: " + str(unsat_tests_success) + " sur " + str(total_unsat_tests) + " tests realises")
    print("Nombre de timeouts: " + str(timeouts_unsat_tests))
    print("Nombre d'exceptions: " + str(exceptions_unsat_tests) + "\n")
    
    print("Meilleurs scores correctement calcules: " + str(correct_maxscores) + " sur " + str(total_maxscores) + " tests realises")
    print("Nombre de timeouts: " + str(timeouts_maxscores))
    print("Nombre d'exceptions: " + str(exceptions_maxscores) + "\n")


##################################################################################################################################################
##################################################################################################################################################
##################################################################################################################################################
##################################################################################################################################################
##################################################################################################################################################


if test:
    print("Let's test your code")
    test_code()
elif options.bound!=None:
    # cas ou la borne est fournie en entree: on test si la sequence (qui doit etre donnee en entree) a un score superieur ou egal a la borne donnee
    # si oui, on affiche "SAT". Si l'option d'affichage est active, alors il faut egalement afficher une solution
    print("Exist Sol")
    exist_sol(options.seq,options.bound)

    print("DEBUT DU TEST DE SATISFIABILITE")
    # A COMPLETER
    print("FIN DU TEST DE SATISFIABILITE")


elif not (incremental):
    # on affiche le score maximal qu'on calcule par dichotomie
    # on affiche egalement un plongement de score maximal si l'option d'affichage est active
    print("DEBUT DU CALCUL DU MEILLEUR SCORE PAR DICHOTOMIE")
    # A COMPLETER
    print("FIN DU CALCUL DU MEILLEUR SCORE")
    
elif not test:
    # Pareil que dans le cas precedent mais avec la methode incrementale
    # A COMPLETER
    print("DEBUT DU CALCUL DU MEILLEUR SCORE PAR METHODE INCREMENTALE")
    # A COMPLETER
    print("FIN DU CALCUL DU MEILLEUR SCORE")
