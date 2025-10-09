' VBA-Module für Excel-Übersetzungsfunktion
' Nutzt lokale LibreTranslate API auf Port 5000
' Verwendung: =TRANSLATE(A1) oder =TRANSLATE(A1, "en", "de")

Option Explicit

' Cache für Übersetzungen um wiederholte API-Aufrufe zu vermeiden
Private translateCache As Object

' Initialisiert den Cache beim ersten Aufruf
Private Sub InitializeCache()
    If translateCache Is Nothing Then
        Set translateCache = CreateObject("Scripting.Dictionary")
    End If
End Sub

' Hauptübersetzungsfunktion für Excel-Zellen
' Parameter:
'   textToTranslate: Der zu übersetzende Text (Pflicht)
'   sourceLanguage: Quellsprache (optional, Standard: "auto")
'   targetLanguage: Zielsprache (optional, Standard: "de")
Public Function TRANSLATE(textToTranslate As String, _
                         Optional sourceLanguage As String = "auto", _
                         Optional targetLanguage As String = "de") As String
    
    On Error GoTo ErrorHandler
    
    ' Cache initialisieren
    Call InitializeCache
    
    ' Leere Eingabe abfangen
    If Trim(textToTranslate) = "" Then
        TRANSLATE = ""
        Exit Function
    End If
    
    ' Cache-Key erstellen
    Dim cacheKey As String
    cacheKey = textToTranslate & "|" & sourceLanguage & "|" & targetLanguage
    
    ' Prüfen ob Übersetzung bereits im Cache existiert
    If translateCache.Exists(cacheKey) Then
        TRANSLATE = translateCache(cacheKey)
        Exit Function
    End If
    
    ' API-Aufruf durchführen
    Dim result As String
    result = CallTranslateAPI(textToTranslate, sourceLanguage, targetLanguage)
    
    ' Ergebnis in Cache speichern
    translateCache(cacheKey) = result
    
    ' Ergebnis zurückgeben
    TRANSLATE = result
    
    Exit Function
    
ErrorHandler:
    TRANSLATE = "ERROR: " & Err.Description
End Function

' Führt den eigentlichen API-Aufruf durch
Private Function CallTranslateAPI(text As String, _
                                 sourceLanguage As String, _
                                 targetLanguage As String) As String
    
    On Error GoTo APIErrorHandler
    
    ' HTTP-Request Objekt erstellen (mit Fallback für verschiedene Systeme)
    Dim http As Object
    On Error Resume Next
    Set http = CreateObject("MSXML2.XMLHTTP.6.0")
    If http Is Nothing Then
        Set http = CreateObject("MSXML2.XMLHTTP.3.0")
    End If
    If http Is Nothing Then
        Set http = CreateObject("MSXML2.XMLHTTP")
    End If
    If http Is Nothing Then
        Set http = CreateObject("Microsoft.XMLHTTP")
    End If
    On Error GoTo APIErrorHandler
    
    If http Is Nothing Then
        CallTranslateAPI = "ERROR: Kein HTTP-Objekt verfügbar"
        Exit Function
    End If
    
    ' API-Endpunkt
    Dim apiUrl As String
    apiUrl = "http://192.168.178.185:5000/translate"
    
    ' JSON-Body zusammenstellen
    Dim jsonBody As String
    jsonBody = "{" & _
        """q"": """ & EscapeJSON(text) & """," & _
        """source"": """ & sourceLanguage & """," & _
        """target"": """ & targetLanguage & """," & _
        """format"": ""text""," & _
        """alternatives"": 3," & _
        """api_key"": """"" & _
        "}"
    
    ' HTTP-Request konfigurieren
    http.Open "POST", apiUrl, False
    http.setRequestHeader "Content-Type", "application/json"
    http.setRequestHeader "Accept", "application/json"
    
    ' Timeout setzen (nur wenn unterstützt)
    On Error Resume Next
    http.setTimeouts 5000, 5000, 10000, 30000  ' resolve, connect, send, receive
    On Error GoTo APIErrorHandler
    
    ' Request senden
    http.send jsonBody
    
    ' Antwort verarbeiten
    If http.Status = 200 Then
        Dim responseText As String
        responseText = http.responseText
        
        ' JSON-Antwort parsen und übersetzten Text extrahieren
        Dim translatedText As String
        translatedText = ExtractTranslatedText(responseText)
        
        CallTranslateAPI = translatedText
    Else
        CallTranslateAPI = "ERROR: HTTP " & http.Status & " - " & http.statusText
    End If
    
    Exit Function
    
APIErrorHandler:
    CallTranslateAPI = "ERROR: " & Err.Description
End Function

' Extrahiert den übersetzten Text aus der JSON-Antwort
Private Function ExtractTranslatedText(jsonResponse As String) As String
    On Error GoTo JSONErrorHandler
    
    ' DEBUG: Zeige die komplette API-Antwort (temporär für Fehlersuche)
    ' Entferne diese Zeile später wenn alles funktioniert:
    ' MsgBox "API Antwort: " & Left(jsonResponse, 500), vbInformation
    
    Dim startPos As Long
    Dim endPos As Long
    Dim result As String
    
    ' Suche nach verschiedenen möglichen JSON-Feldern
    ' Versuche zuerst "translatedText"
    startPos = InStr(jsonResponse, """translatedText"":")
    If startPos > 0 Then
        ' Finde den Wert nach dem Doppelpunkt
        startPos = InStr(startPos, jsonResponse, ":")
        If startPos > 0 Then
            startPos = startPos + 1
            ' Überspringe Leerzeichen
            Do While Mid(jsonResponse, startPos, 1) = " "
                startPos = startPos + 1
            Loop
            ' Überspringe das öffnende Anführungszeichen
            If Mid(jsonResponse, startPos, 1) = """" Then
                startPos = startPos + 1
            End If
            ' Finde das schließende Anführungszeichen
            endPos = InStr(startPos, jsonResponse, """")
            If endPos > startPos Then
                result = Mid(jsonResponse, startPos, endPos - startPos)
                ExtractTranslatedText = result
                Exit Function
            End If
        End If
    End If
    
    ' Alternativ: Suche nach "translation" (falls andere API-Version)
    startPos = InStr(jsonResponse, """translation"":")
    If startPos > 0 Then
        startPos = InStr(startPos, jsonResponse, ":")
        If startPos > 0 Then
            startPos = startPos + 1
            Do While Mid(jsonResponse, startPos, 1) = " "
                startPos = startPos + 1
            Loop
            If Mid(jsonResponse, startPos, 1) = """" Then
                startPos = startPos + 1
            End If
            endPos = InStr(startPos, jsonResponse, """")
            If endPos > startPos Then
                result = Mid(jsonResponse, startPos, endPos - startPos)
                ExtractTranslatedText = result
                Exit Function
            End If
        End If
    End If
    
    ' Alternativ: Suche nach "text" 
    startPos = InStr(jsonResponse, """text"":")
    If startPos > 0 Then
        startPos = InStr(startPos, jsonResponse, ":")
        If startPos > 0 Then
            startPos = startPos + 1
            Do While Mid(jsonResponse, startPos, 1) = " "
                startPos = startPos + 1
            Loop
            If Mid(jsonResponse, startPos, 1) = """" Then
                startPos = startPos + 1
            End If
            endPos = InStr(startPos, jsonResponse, """")
            If endPos > startPos Then
                result = Mid(jsonResponse, startPos, endPos - startPos)
                ExtractTranslatedText = result
                Exit Function
            End If
        End If
    End If
    
    ' Wenn alle Versuche fehlschlagen, gib die rohe Antwort zurück für Debug
    ExtractTranslatedText = "PARSE_ERROR: " & Left(jsonResponse, 100)
    
    Exit Function
    
JSONErrorHandler:
    ExtractTranslatedText = "ERROR: JSON parsing failed - " & Err.Description
End Function

' Hilfsfunktion zum Escapen von JSON-Strings
Private Function EscapeJSON(text As String) As String
    Dim result As String
    result = text
    
    ' Grundlegende JSON-Escape-Zeichen
    result = Replace(result, "\", "\\")    ' Backslash
    result = Replace(result, """", "\""")   ' Anführungszeichen
    result = Replace(result, Chr(10), "\n") ' Zeilenumbruch
    result = Replace(result, Chr(13), "\r") ' Wagenrücklauf
    result = Replace(result, Chr(9), "\t")  ' Tab
    
    EscapeJSON = result
End Function

' Hilfsfunktion zum Leeren des Übersetzungs-Cache
Public Sub ClearTranslateCache()
    If Not translateCache Is Nothing Then
        translateCache.RemoveAll
    End If
    MsgBox "Übersetzungs-Cache wurde geleert!", vbInformation
End Sub

' Hilfsfunktion zum Anzeigen der Cache-Statistiken
Public Sub ShowCacheStats()
    Call InitializeCache
    
    Dim stats As String
    stats = "Cache-Statistiken:" & vbCrLf & vbCrLf & _
            "Gespeicherte Übersetzungen: " & translateCache.Count
    
    MsgBox stats, vbInformation, "Translate Cache Stats"
End Sub

' Test-Funktion für Entwickler
Public Sub TestTranslateFunction()
    Dim testText As String
    testText = "Hello World"
    
    Dim result As String
    result = TRANSLATE(testText, "en", "de")
    
    MsgBox "Test-Übersetzung:" & vbCrLf & _
           "Original: " & testText & vbCrLf & _
           "Übersetzt: " & result, vbInformation
End Sub

' Vereinfachte TRANSLATE-Funktion (nach Ollama-Vorbild)
Public Function TRANSLATE_SIMPLE(text As String, _
                                Optional source As String = "en", _
                                Optional target As String = "de") As String
    Dim http As Object
    Dim url As String
    Dim payload As String
    Dim response As String
    Dim result As String
    
    On Error GoTo ErrorHandler
    
    ' Leere Eingabe abfangen
    If Trim(text) = "" Then
        TRANSLATE_SIMPLE = ""
        Exit Function
    End If
    
    ' Setze die API-URL
    url = "http://192.168.178.185:5000/translate"
    
    ' Erstelle das JSON-Payload (vereinfacht)
    payload = "{""q"": """ & text & """, ""source"": """ & source & """, ""target"": """ & target & """, ""format"": ""text"", ""alternatives"": 3, ""api_key"": """"}"
    
    ' Erstelle die HTTP-Anfrage
    Set http = CreateObject("MSXML2.XMLHTTP")
    http.Open "POST", url, False
    http.setRequestHeader "Content-Type", "application/json"
    http.setRequestHeader "Accept-Charset", "UTF-8"
    
    ' Sende die Anfrage
    http.send payload
    
    ' Hole die Antwort
    response = http.responseText
    
    ' Debugging: Ausgabe der Antwort im Direktbereich
    Debug.Print "LibreTranslate Response: " & response
    
    ' Einfaches JSON-Parsing ohne externe Bibliotheken
    ' Suche nach "translatedText":"
    Dim startPos As Long
    Dim endPos As Long
    
    startPos = InStr(response, """translatedText"":""")
    If startPos > 0 Then
        startPos = startPos + 18  ' Länge von "translatedText":"
        endPos = InStr(startPos, response, """")
        If endPos > startPos Then
            result = Mid(response, startPos, endPos - startPos)
            TRANSLATE_SIMPLE = result
        Else
            TRANSLATE_SIMPLE = "PARSE_ERROR: End position not found"
        End If
    Else
        ' Fallback: Gib die ganze Antwort zurück für Debug
        TRANSLATE_SIMPLE = "PARSE_ERROR: " & Left(response, 100)
    End If
    
    Exit Function
    
ErrorHandler:
    TRANSLATE_SIMPLE = "ERROR: " & Err.Description
End Function

' Test für die vereinfachte Funktion
Public Sub TestSimpleTranslate()
    Dim result As String
    result = TRANSLATE_SIMPLE("Hello World", "en", "de")
    
    MsgBox "🔄 Vereinfachte Übersetzung:" & vbCrLf & vbCrLf & _
           "Original: Hello World" & vbCrLf & _
           "Übersetzt: " & result, vbInformation, "Simple Translate Test"
End Sub

' DEBUG: Zeigt die rohe LibreTranslate API-Antwort an (vereinfacht)
Public Sub DebugAPIResponse()
    Dim http As Object
    Dim url As String
    Dim payload As String
    Dim response As String
    
    ' Setze die API-URL
    url = "http://192.168.178.185:5000/translate"
    
    ' Erstelle das JSON-Payload (vereinfacht ohne EscapeJSON)
    payload = "{""q"": ""Hello World"", ""source"": ""en"", ""target"": ""de"", ""format"": ""text"", ""alternatives"": 3, ""api_key"": """"}"
    
    ' Erstelle die HTTP-Anfrage (vereinfacht)
    Set http = CreateObject("MSXML2.XMLHTTP")
    http.Open "POST", url, False
    http.setRequestHeader "Content-Type", "application/json"
    http.setRequestHeader "Accept-Charset", "UTF-8"
    
    ' Sende die Anfrage
    On Error GoTo ErrorHandler
    http.send payload
    
    ' Hole die Antwort
    response = http.responseText
    
    ' Debugging: Ausgabe der Antwort
    Debug.Print "LibreTranslate Response: " & response
    
    ' Antwort in MessageBox anzeigen
    MsgBox "🔍 LIBRETRANSLATE DEBUG:" & vbCrLf & vbCrLf & _
           "Status: " & http.Status & vbCrLf & _
           "Status Text: " & http.statusText & vbCrLf & vbCrLf & _
           "Vollständige Antwort:" & vbCrLf & _
           response, vbInformation, "LibreTranslate API Debug"
    Exit Sub
    
ErrorHandler:
    MsgBox "❌ FEHLER beim API-Aufruf:" & vbCrLf & _
           "Fehler: " & Err.Description & vbCrLf & vbCrLf & _
           "Überprüfe ob LibreTranslate läuft auf:" & vbCrLf & _
           url, vbCritical, "Debug Fehler"
End Sub

' Einfacher Test für HTTP-Verbindung
Public Sub TestHTTPConnection()
    Dim http As Object
    Dim testUrl As String
    testUrl = "http://192.168.178.185:5000"
    
    On Error Resume Next
    Set http = CreateObject("MSXML2.XMLHTTP.6.0")
    If http Is Nothing Then Set http = CreateObject("MSXML2.XMLHTTP")
    If http Is Nothing Then Set http = CreateObject("Microsoft.XMLHTTP")
    
    If http Is Nothing Then
        MsgBox "FEHLER: Kein HTTP-Objekt verfügbar!" & vbCrLf & _
               "Überprüfe deine Windows/Office-Installation.", vbCritical
        Exit Sub
    End If
    
    http.Open "GET", testUrl, False
    http.send
    
    If Err.Number <> 0 Then
        MsgBox "VERBINDUNGSFEHLER:" & vbCrLf & _
               "Fehler: " & Err.Description & vbCrLf & vbCrLf & _
               "Überprüfe ob dein LibreTranslate-Server läuft auf:" & vbCrLf & _
               testUrl, vbExclamation
    Else
        MsgBox "✅ HTTP-VERBINDUNG OK!" & vbCrLf & _
               "Server Status: " & http.Status & vbCrLf & _
               "URL: " & testUrl, vbInformation
    End If
End Sub

' Batch-Übersetzungsfunktion für große Datenmengen
' Übersetzt einen Bereich von Zellen mit Verzögerung zwischen Anfragen
Public Sub BatchTranslate(sourceRange As Range, _
                         targetRange As Range, _
                         Optional sourceLanguage As String = "auto", _
                         Optional targetLanguage As String = "de", _
                         Optional delayMs As Long = 100)
    
    Dim i As Long
    Dim cell As Range
    Dim targetCell As Range
    
    ' Fortschrittsanzeige
    Application.ScreenUpdating = False
    
    i = 1
    For Each cell In sourceRange
        Set targetCell = targetRange.Cells(i, 1)
        
        If Not IsEmpty(cell.Value) Then
            targetCell.Value = TRANSLATE(CStr(cell.Value), sourceLanguage, targetLanguage)
            
            ' Kurze Verzögerung um API nicht zu überlasten
            If delayMs > 0 Then
                Application.Wait Now + TimeValue("00:00:00") + (delayMs / 86400000)
            End If
        End If
        
        i = i + 1
        
        ' Fortschritt in Statusleiste anzeigen
        Application.StatusBar = "Übersetze Zelle " & i & " von " & sourceRange.Count
    Next cell
    
    Application.ScreenUpdating = True
    Application.StatusBar = False
    
    MsgBox "Batch-Übersetzung abgeschlossen!" & vbCrLf & _
           "Übersetzt: " & sourceRange.Count & " Zellen", vbInformation
End Sub

' =============================================================================
' OLLAMA KI-ASSISTENT FUNKTIONEN
' =============================================================================

' Cache für Ollama-Anfragen um wiederholte API-Aufrufe zu vermeiden
Private ollamaCache As Object

' Initialisiert den Ollama-Cache beim ersten Aufruf
Private Sub InitializeOllamaCache()
    If ollamaCache Is Nothing Then
        Set ollamaCache = CreateObject("Scripting.Dictionary")
    End If
End Sub

' Hauptfunktion für Ollama KI-Anfragen in Excel-Zellen
' Parameter:
'   query: Die Frage/Anfrage an die KI (Pflicht)
'   model: Das zu verwendende Modell (optional, Standard: "llama3.2")
'   temperature: Kreativität der Antwort 0.0-1.0 (optional, Standard: 0.3)
Public Function OLLAMA(query As String, _
                       Optional model As String = "llama3.2", _
                       Optional temperature As Double = 0.3) As String
    
    On Error GoTo ErrorHandler
    
    ' Cache initialisieren
    Call InitializeOllamaCache
    
    ' Leere Eingabe abfangen
    If Trim(query) = "" Then
        OLLAMA = ""
        Exit Function
    End If
    
    ' Cache-Key erstellen (inklusive Modell und Temperatur)
    Dim cacheKey As String
    cacheKey = query & "|" & model & "|" & CStr(temperature)
    
    ' Prüfen ob Antwort bereits im Cache existiert
    If ollamaCache.Exists(cacheKey) Then
        OLLAMA = ollamaCache(cacheKey)
        Exit Function
    End If
    
    ' API-Aufruf durchführen
    Dim result As String
    result = CallOllamaAPI(query, model, temperature)
    
    ' Ergebnis in Cache speichern
    ollamaCache(cacheKey) = result
    
    ' Ergebnis zurückgeben
    OLLAMA = result
    
    Exit Function
    
ErrorHandler:
    OLLAMA = "ERROR: " & Err.Description
End Function

' Führt den eigentlichen Ollama API-Aufruf durch
Private Function CallOllamaAPI(query As String, _
                              model As String, _
                              temperature As Double) As String
    
    On Error GoTo APIErrorHandler
    
    ' HTTP-Request Objekt erstellen (mit Fallback für verschiedene Systeme)
    Dim http As Object
    On Error Resume Next
    Set http = CreateObject("MSXML2.XMLHTTP.6.0")
    If http Is Nothing Then
        Set http = CreateObject("MSXML2.XMLHTTP.3.0")
    End If
    If http Is Nothing Then
        Set http = CreateObject("MSXML2.XMLHTTP")
    End If
    If http Is Nothing Then
        Set http = CreateObject("Microsoft.XMLHTTP")
    End If
    On Error GoTo APIErrorHandler
    
    If http Is Nothing Then
        CallOllamaAPI = "ERROR: Kein HTTP-Objekt verfügbar"
        Exit Function
    End If
    
    ' API-Endpunkt
    Dim apiUrl As String
    apiUrl = "http://127.0.0.1:11434/v1/chat/completions"
    
    ' JSON-Body zusammenstellen
    Dim jsonBody As String
    jsonBody = "{" & _
        """model"": """ & model & """," & _
        """messages"": [" & _
            "{""role"": ""system"", ""content"": ""Du bist ein hilfreicher KI-Assistent. Antworte kurz und prägnant.""}," & _
            "{""role"": ""user"", ""content"": """ & EscapeJSON(query) & """}" & _
        "]," & _
        """temperature"": " & Replace(CStr(temperature), ",", ".") & _
        "}"
    
    ' HTTP-Request konfigurieren
    http.Open "POST", apiUrl, False
    http.setRequestHeader "Content-Type", "application/json"
    http.setRequestHeader "Accept", "application/json"
    
    ' Timeout setzen (nur wenn unterstützt) - Ollama braucht längere Timeouts
    On Error Resume Next
    http.setTimeouts 10000, 10000, 30000, 120000  ' resolve, connect, send, receive (2 Minuten)
    On Error GoTo APIErrorHandler
    
    ' Request senden
    http.send jsonBody
    
    ' Antwort verarbeiten
    If http.Status = 200 Then
        Dim responseText As String
        responseText = http.responseText
        
        ' JSON-Antwort parsen und KI-Antwort extrahieren
        Dim aiResponse As String
        aiResponse = ExtractOllamaResponse(responseText)
        
        CallOllamaAPI = aiResponse
    Else
        CallOllamaAPI = "ERROR: HTTP " & http.Status & " - " & http.statusText
    End If
    
    Exit Function
    
APIErrorHandler:
    CallOllamaAPI = "ERROR: " & Err.Description
End Function

' Extrahiert die KI-Antwort aus der Ollama JSON-Antwort
Private Function ExtractOllamaResponse(jsonResponse As String) As String
    On Error GoTo JSONErrorHandler
    
    ' DEBUG: Zeige die komplette API-Antwort (temporär für Fehlersuche)
    ' Entferne diese Zeile später wenn alles funktioniert:
    ' MsgBox "Ollama Antwort: " & Left(jsonResponse, 500), vbInformation
    
    Dim startPos As Long
    Dim endPos As Long
    Dim result As String
    Dim nestingLevel As Long
    
    ' Suche nach "choices" Array und dann nach "message" > "content"
    ' Typische Ollama-Antwort: {"choices":[{"message":{"content":"Antwort hier"}}]}
    
    ' Schritt 1: Finde "choices" Array
    startPos = InStr(jsonResponse, """choices"":")
    If startPos > 0 Then
        ' Schritt 2: Finde das erste "message" Objekt
        startPos = InStr(startPos, jsonResponse, """message"":")
        If startPos > 0 Then
            ' Schritt 3: Finde "content" innerhalb des message Objekts
            startPos = InStr(startPos, jsonResponse, """content"":")
            If startPos > 0 Then
                ' Position nach dem Doppelpunkt finden
                startPos = InStr(startPos, jsonResponse, ":")
                If startPos > 0 Then
                    startPos = startPos + 1
                    
                    ' Überspringe Leerzeichen
                    Do While startPos <= Len(jsonResponse) And Mid(jsonResponse, startPos, 1) = " "
                        startPos = startPos + 1
                    Loop
                    
                    ' Überspringe das öffnende Anführungszeichen
                    If Mid(jsonResponse, startPos, 1) = """" Then
                        startPos = startPos + 1
                        
                        ' Finde das schließende Anführungszeichen (beachte Escape-Zeichen)
                        Dim currentPos As Long
                        currentPos = startPos
                        Do While currentPos <= Len(jsonResponse)
                            If Mid(jsonResponse, currentPos, 1) = """" Then
                                ' Prüfe ob es ein Escape-Zeichen davor gibt
                                If currentPos > 1 And Mid(jsonResponse, currentPos - 1, 1) <> "\" Then
                                    endPos = currentPos
                                    Exit Do
                                End If
                            End If
                            currentPos = currentPos + 1
                        Loop
                        
                        If endPos > startPos Then
                            result = Mid(jsonResponse, startPos, endPos - startPos)
                            ' Entferne JSON-Escape-Zeichen
                            result = Replace(result, "\""", """")
                            result = Replace(result, "\\", "\")
                            result = Replace(result, "\n", vbCrLf)
                            result = Replace(result, "\r", "")
                            result = Replace(result, "\t", vbTab)
                            
                            ExtractOllamaResponse = result
                            Exit Function
                        End If
                    End If
                End If
            End If
        End If
    End If
    
    ' Fallback: Suche nach alternativen JSON-Strukturen
    startPos = InStr(jsonResponse, """response"":")
    If startPos > 0 Then
        startPos = InStr(startPos, jsonResponse, ":")
        If startPos > 0 Then
            startPos = startPos + 1
            Do While startPos <= Len(jsonResponse) And Mid(jsonResponse, startPos, 1) = " "
                startPos = startPos + 1
            Loop
            If Mid(jsonResponse, startPos, 1) = """" Then
                startPos = startPos + 1
                endPos = InStr(startPos, jsonResponse, """")
                If endPos > startPos Then
                    result = Mid(jsonResponse, startPos, endPos - startPos)
                    ExtractOllamaResponse = result
                    Exit Function
                End If
            End If
        End If
    End If
    
    ' Wenn alle Versuche fehlschlagen, gib die rohe Antwort zurück für Debug
    ExtractOllamaResponse = "PARSE_ERROR: " & Left(jsonResponse, 200)
    
    Exit Function
    
JSONErrorHandler:
    ExtractOllamaResponse = "ERROR: JSON parsing failed - " & Err.Description
End Function

' Test-Funktion für Ollama
Public Sub TestOllamaFunction()
    Dim testQuery As String
    testQuery = "Erkläre mir in einem Satz was Künstliche Intelligenz ist."
    
    Dim result As String
    result = OLLAMA(testQuery)
    
    MsgBox "🤖 Ollama Test:" & vbCrLf & vbCrLf & _
           "Frage: " & testQuery & vbCrLf & vbCrLf & _
           "Antwort: " & result, vbInformation, "Ollama KI-Test"
End Sub

' DEBUG: Zeigt die rohe Ollama API-Antwort an
Public Sub DebugOllamaResponse()
    Dim http As Object
    Dim testUrl As String
    Dim jsonBody As String
    
    testUrl = "http://127.0.0.1:11434/v1/chat/completions"
    
    ' HTTP-Objekt erstellen
    On Error Resume Next
    Set http = CreateObject("MSXML2.XMLHTTP.6.0")
    If http Is Nothing Then Set http = CreateObject("MSXML2.XMLHTTP")
    If http Is Nothing Then Set http = CreateObject("Microsoft.XMLHTTP")
    
    If http Is Nothing Then
        MsgBox "Kein HTTP-Objekt verfügbar!", vbCritical
        Exit Sub
    End If
    
    ' Test-Request zusammenstellen
    jsonBody = "{" & _
        """model"": ""llama3.2""," & _
        """messages"": [" & _
            "{""role"": ""system"", ""content"": ""Du bist ein hilfreicher KI-Assistent.""}," & _
            "{""role"": ""user"", ""content"": ""Hallo, wie geht es dir?""}" & _
        "]," & _
        """temperature"": 0.3" & _
        "}"
    
    On Error Resume Next
    http.Open "POST", testUrl, False
    http.setRequestHeader "Content-Type", "application/json"
    http.send jsonBody
    
    If Err.Number <> 0 Then
        MsgBox "FEHLER beim Senden: " & Err.Description, vbCritical
        Exit Sub
    End If
    
    ' Antwort anzeigen
    MsgBox "🔍 OLLAMA DEBUG INFO:" & vbCrLf & vbCrLf & _
           "Status: " & http.Status & vbCrLf & _
           "Status Text: " & http.statusText & vbCrLf & vbCrLf & _
           "Antwort (erste 800 Zeichen):" & vbCrLf & _
           Left(http.responseText, 800), vbInformation, "Ollama API Debug"
End Sub

' Test für Ollama-Verbindung
Public Sub TestOllamaConnection()
    Dim http As Object
    Dim testUrl As String
    testUrl = "http://127.0.0.1:11434/api/tags"  ' Ollama Model-Liste-Endpoint
    
    On Error Resume Next
    Set http = CreateObject("MSXML2.XMLHTTP.6.0")
    If http Is Nothing Then Set http = CreateObject("MSXML2.XMLHTTP")
    If http Is Nothing Then Set http = CreateObject("Microsoft.XMLHTTP")
    
    If http Is Nothing Then
        MsgBox "FEHLER: Kein HTTP-Objekt verfügbar!" & vbCrLf & _
               "Überprüfe deine Windows/Office-Installation.", vbCritical
        Exit Sub
    End If
    
    http.Open "GET", testUrl, False
    http.send
    
    If Err.Number <> 0 Then
        MsgBox "VERBINDUNGSFEHLER:" & vbCrLf & _
               "Fehler: " & Err.Description & vbCrLf & vbCrLf & _
               "Überprüfe ob Ollama läuft:" & vbCrLf & _
               "1. Terminal: ollama serve" & vbCrLf & _
               "2. URL: " & testUrl, vbExclamation
    Else
        MsgBox "✅ OLLAMA-VERBINDUNG OK!" & vbCrLf & _
               "Server Status: " & http.Status & vbCrLf & _
               "URL: " & testUrl & vbCrLf & vbCrLf & _
               "Verfügbare Modelle:" & vbCrLf & _
               Left(http.responseText, 300), vbInformation
    End If
End Sub

' Cache für Ollama-Anfragen leeren
Public Sub ClearOllamaCache()
    If Not ollamaCache Is Nothing Then
        ollamaCache.RemoveAll
    End If
    MsgBox "Ollama-Cache wurde geleert!", vbInformation
End Sub

' Ollama Cache-Statistiken anzeigen
Public Sub ShowOllamaCacheStats()
    Call InitializeOllamaCache
    
    Dim stats As String
    stats = "Ollama Cache-Statistiken:" & vbCrLf & vbCrLf & _
            "Gespeicherte KI-Antworten: " & ollamaCache.Count
    
    MsgBox stats, vbInformation, "Ollama Cache Stats"
End Sub
