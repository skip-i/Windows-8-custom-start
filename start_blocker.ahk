#NoEnv
#SingleInstance Force
SendMode Input
SetWorkingDir %A_ScriptDir%

; Inizializza la variabile globale per tracciare l'istanza precedente
global LastPID := ""

; --- PATCH DI MASCHERAMENTO PER WINDOWS 11 ---
; Invia un tasto virtuale nullo (vkE8) per ingannare Explorer ed evitare che si apra lo Start nativo
; Questo mantiene funzionanti le combinazioni di tasti (come Win+E, Win+R, ecc.)
~LWin::Send {Blind}{vkE8}
~RWin::Send {Blind}{vkE8}

; --- INTERCETTAZIONE AL RILASCIO DEL TASTO ---
~LWin Up::
~RWin Up::
    ; Se l'ultimo tasto premuto è stato effettivamente solo il tasto WIN, gestisci l'istanza
    if (A_PriorKey = "LWin" or A_PriorKey = "RWin") {
        
        ; Se esiste un PID salvato da una pressione precedente, killa quel processo specifico
        if (LastPID) {
            Process, Close, %LastPID%
            LastPID := ""
            Sleep, 50 ; Brevissima pausa per dare tempo a Windows di liberare la memoria
        }
        
        ; Avvia il file Python e memorizza il suo nuovo PID nella variabile LastPID
        Run, pythonw.exe "C:\customstart\win8_start.py",,, LastPID
    }
return
