from flask import Flask, request, render_template, redirect
import time
app = Flask(__name__)

# Restituisce l'ip dell'utente connesso alla pagina
def get_ip():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR']

# Converte secondi in formato HH:MM:SS
def secToHMS(sec):
    mins = sec // 60
    sec = sec % 60
    hours = mins // 60
    mins = mins % 60
    return f'{round(hours)}:{round(mins)}:{round(sec, 1)}'

# Restituisce il tempo più grande in cui una persona è rimasta fuori
def getMaxTimeOut(list):
    max_number = secToHMS(max(list.values(), key=lambda x: x.amountTimeOut_secs).amountTimeOut_secs)
    return max_number

# Restituisce il tempo più piccolo in cui una persona è rimasta fuori
def getMinTimeOut(list):
    min_number = secToHMS(min(list.values(), key=lambda x: x.amountTimeOut_secs).amountTimeOut_secs)
    return min_number
    
# Riconosce la persona con il tempo in cui è stata fuori più alto 
def getKeyForTimeOut(list, number):
    i = -1
    for item in list.values():
        i += 1
        if secToHMS(item.amountTimeOut_secs) == number:
            break
    count = 0
    for j in list.keys():
        if i == count:
            return j
        else:
            count += 1

class User:
    def __init__(self):
        self.ip = get_ip()              # IP dell'utente, utilizzato nel logging
        self.nome = ''                  # Nome dell'utente
        self.tipoUscita = ''            # Dove vuole andare l'utente
        self.canExit = False            # Se l'utente puo' uscire (perché primo della lista)
        self.isOut = False              # Se l'utente è fuori
        self.amountTimeOut_secs = 0     # Quantitativo di tempo in cui l'utente è stato fuori
        self.__whenExited = 0           # Quando è uscito l'utente
        self.__whenCameBack = 0         # Quando è rientrato l'utente

    def gotOut(self):
        self.isOut = True
        self.__whenExited = time.time()
    def cameBack(self):
        self.isOut = False
        self.canExit = False
        self.__whenCameBack = time.time()
        self.amountTimeOut_secs += self.__whenCameBack - self.__whenExited
        userQueue.remove(self.ip)

        

# Database degli utenti
userList = {}

# Fila degli utenti
userQueue = []

# Array di stringhe, utilizzato come log
log = []

# INIZIO FUNZIONI DI INDIRIZZAMENTO: PARTE LISTA

# Index
@app.route('/')
def start():
    return redirect('/prenotati') # Indirizzamento alla pagina di prenotazione

# Pagina di prenotazione
@app.route('/prenotati', methods=['POST', 'GET'])
def form_prenotazione():
    return render_template('index.html')
    
@app.route('/evaluatelist', methods=['POST', 'GET'])
def evaluatelist():
    try:
        # Se l'utente non è stato registrato nel database, viene registrato
        if get_ip() not in userList.keys():
            userList[get_ip()] = User()
            # LOG: Nuovo utente registrato
            log.append(f'{time.strftime("%H:%M:%S", time.localtime())} - Nuovo utente collegato IP: {userList[get_ip()].ip}')
        
        # Aggiornamento del campo del nome, se vuoto viene reindirizzato alla registrazione
        userList[get_ip()].nome = request.form['name']
        if userList[get_ip()].nome == '': return redirect('/')

        # Aggiornamento del campo del tipo di uscita
        userList[get_ip()].tipoUscita = request.form['tipo_uscita']

        # LOG: Nuovo nome e tipo di uscita dell'utente
        log.append(f'{time.strftime("%H:%M:%S", time.localtime())} - {get_ip()} si chiama {userList[get_ip()].nome} e deve andare al {userList[get_ip()].tipoUscita}')

        # L'utente viene aggiunto in fila
        if get_ip() not in userQueue: 
            userQueue.append(get_ip())
            # LOG: Utente viene inserito in lista
            log.append(f'{time.strftime("%H:%M:%S", time.localtime())} - {userList[get_ip()].nome} è il n.{userQueue.index(get_ip()) + 1} della lista')
        
        return redirect('/listaprenotati') # Indirizzamento alla pagina che mostra la lista
    except:
        return redirect('/')

@app.route('/listaprenotati', methods=['POST', 'GET'])
def showList():
    try:
        # Trova il primo delle due liste e setta l'attributo self.canExit a vero
        for ip in userQueue:
            if userList[ip].tipoUscita == 'bar':
                userList[ip].canExit = True
                break
        for ip in userQueue:
            if userList[ip].tipoUscita == 'bagno':
                userList[ip].canExit = True
                break
        
        return render_template('lista.html', userList = userList, userQueue = userQueue, ip = get_ip()) # Rende la pagina .html della lista
    except:
        return redirect('/')

# Pagina per la richiesta di uscita della pagina .html
@app.route('/listaprenotati/esci', methods=['POST', 'GET'])
def esci():
    userList[get_ip()].gotOut()
    log.append(f'{time.strftime("%H:%M:%S", time.localtime())} - {userList[get_ip()].nome} è uscito (IP: {get_ip()})')
    return redirect('/listaprenotati')

# Pagina per la richiesta di rientro della pagina .html
@app.route('/listaprenotati/torna', methods=['POST', 'GET'])
def torna():
    userList[get_ip()].cameBack()
    log.append(f'{time.strftime("%H:%M:%S", time.localtime())} - {userList[get_ip()].nome} è rientrato (IP: {get_ip()})')
    log.append(f'Finora, è stato fuori {secToHMS(userList[get_ip()].amountTimeOut_secs)} (Ore:Minuti:Secondi)')
    return redirect('/rimosso')

# Pagina per la richiesta di rimozione dalla lista
@app.route('/rimosso', methods=['POST', 'GET'])
def rimozione():
    if get_ip() in userQueue:
        userQueue.remove(get_ip())
        log.append(f'{time.strftime("%H:%M:%S", time.localtime())} - {userList[get_ip()].nome} è stato rimosso dalla lista (IP: {userList[get_ip()].ip})')
    if userList[get_ip()].isOut: # Se prima di rimuoversi dalla lista, l'utente era fuori, viene settata falsa la flag self.isOut
        userList[get_ip()].isOut = False
    
    return redirect('/prenotati')



# INIZIO FUNZIONI DI INDIRIZZAMENTO: PARTE LOGGING

allowList = []

# Log index
@app.route('/log')
def logstart():
    return redirect('/login') # Reindirizza alla pagina di login
    
@app.route('/login', methods=['POST', 'GET'])
def login():
    return render_template('log_login.html') # Rende la pagina di login

@app.route('/evaluatelogin', methods=['POST', 'GET'])
def checkPassword():
    try:
        password = request.form['password'] # Raccoglie la password inserita
        correct_password = 'password1234'

        if get_ip() not in allowList:
            if password == correct_password:
                allowList.append(get_ip())
                return redirect('/show')    # Se la password è corretta, reindirizza alla pagina di log
            else:
                return redirect('/login')   # Altrimenti, ritorna alla pagina di login
    except:
        return redirect('/log')

@app.route('/show', methods=['POST', 'GET'])
def showLog():
    try:
        if get_ip() in allowList:
            return render_template('log.html', log = log)      # Rende la pagina di login
        else:
            return redirect('/login')
    except:
        return redirect('/log')
    
@app.route('/getMVP', methods=['POST', 'GET'])
def showMVP():
    try:
        log.append(f'{time.strftime("%H:%M:%S", time.localtime())} - È stato richiesto chi è uscito di più e chi di meno')
        if len(userList) != 0:
            log.append(f'La persona che è stata più tempo fuori è stata {userList[getKeyForTimeOut(userList, getMaxTimeOut(userList))].nome} con {getMaxTimeOut(userList)}, invece quella con meno tempo fuori è stata {userList[getKeyForTimeOut(userList, getMinTimeOut(userList))].nome} con {getMinTimeOut(userList)}')
        else:
            log.append('La lista è vuota, non posso decretare un MVP e un LVP')
        return redirect('show')
    except:
        return redirect('/log')